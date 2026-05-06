"""Agent factory for creating LangGraph agents with memory middleware.

Supports three memory strategies:
- sliding_window: Removes oldest messages when count exceeds threshold
- summarizer: Summarizes older messages when token threshold is hit
- trim_tokens: Keeps only system message + recent N messages
"""

import hashlib
import logging
from typing import Any

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import (
    SummarizationMiddleware,
    after_model,
    before_model,
)
from langchain.messages import RemoveMessage
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES

logger = logging.getLogger(__name__)

# Module-level InMemorySaver (shared across all agents)
_checkpointer = InMemorySaver()


def get_checkpointer() -> InMemorySaver:
    """Get the shared InMemorySaver checkpointer."""
    return _checkpointer


def _make_sliding_window_middleware(max_messages: int):
    """Create a sliding window middleware that removes oldest messages.

    Keeps the most recent `max_messages` messages (plus system message).
    """
    @after_model
    def delete_old_messages(state: AgentState, runtime) -> dict | None:
        """Remove oldest messages to keep conversation manageable."""
        messages = state["messages"]
        if len(messages) > max_messages:
            # Remove the oldest messages, but always keep the first (system) message
            # Count messages beyond the limit
            to_remove = len(messages) - max_messages
            # Don't remove the system message (index 0)
            removable = [m for m in messages[1:] if hasattr(m, 'id') and m.id]
            if len(removable) > to_remove:
                removable = removable[:to_remove]
            if removable:
                return {"messages": [RemoveMessage(id=m.id) for m in removable]}
        return None

    return delete_old_messages


def _make_trim_tokens_middleware(keep_recent: int):
    """Create a trim tokens middleware that keeps only recent messages.

    Keeps the system message (first) + the most recent `keep_recent` messages.
    """
    @before_model
    def trim_messages(state: AgentState, runtime) -> dict[str, Any] | None:
        """Keep only the last few messages to fit context window."""
        messages = state["messages"]

        if len(messages) <= keep_recent + 1:  # +1 for system message
            return None  # No changes needed

        first_msg = messages[0]  # Keep system message
        recent_messages = messages[-keep_recent:]
        new_messages = [first_msg, *recent_messages]

        return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *new_messages]}

    return trim_messages


def create_agent_with_memory(
    llm: BaseChatModel,
    memory_config: dict | None,
    system_prompt: str,
    tools: list | None = None,
):
    """Create a LangGraph agent with optional memory middleware.

    Args:
        llm: The chat model to use
        memory_config: Memory configuration dict with 'type' and strategy params.
                       None = no memory management.
        system_prompt: System prompt for the agent
        tools: Optional list of tools

    Returns:
        A compiled LangGraph agent
    """
    middleware = []

    if memory_config:
        mtype = memory_config.get("type")
        if mtype == "sliding_window":
            max_messages = memory_config.get("max_messages", 20)
            middleware.append(_make_sliding_window_middleware(max_messages))
            logger.info(f"Agent created with sliding_window memory (max_messages={max_messages})")
        elif mtype == "summarizer":
            trigger_tokens = memory_config.get("trigger_tokens", 4000)
            keep_messages = memory_config.get("keep_messages", 20)
            middleware.append(
                SummarizationMiddleware(
                    llm,
                    trigger=("tokens", trigger_tokens),
                    keep=("messages", keep_messages),
                )
            )
            logger.info(f"Agent created with summarizer memory (trigger_tokens={trigger_tokens}, keep_messages={keep_messages})")
        elif mtype == "trim_tokens":
            keep_recent = memory_config.get("keep_recent", 4)
            middleware.append(_make_trim_tokens_middleware(keep_recent))
            logger.info(f"Agent created with trim_tokens memory (keep_recent={keep_recent})")
        else:
            logger.warning(f"Unknown memory type: {mtype}, creating agent without memory middleware")

    agent = create_agent(
        llm,
        tools=tools or [],
        middleware=middleware,
        checkpointer=_checkpointer,
        system_prompt=system_prompt,
    )
    return agent


# --- Agent instance cache ---

_agent_cache: dict[str, tuple] = {}  # cache_key -> (agent, config_hash)


def _config_hash(memory_config: dict | None) -> str:
    """Generate a hash for the memory config to detect changes."""
    if memory_config is None:
        return "none"
    return hashlib.md5(str(sorted(memory_config.items())).encode()).hexdigest()


def get_or_create_agent(
    llm: BaseChatModel,
    agent_id: str,
    memory_config: dict | None,
    system_prompt: str,
    tools: list | None = None,
):
    """Get a cached agent or create a new one if config changed.

    Args:
        llm: The chat model to use
        agent_id: Unique agent identifier for caching
        memory_config: Memory configuration dict
        system_prompt: System prompt for the agent
        tools: Optional list of tools

    Returns:
        A compiled LangGraph agent
    """
    cfg_hash = _config_hash(memory_config)

    if agent_id in _agent_cache:
        cached_agent, cached_hash = _agent_cache[agent_id]
        if cached_hash == cfg_hash:
            return cached_agent

    agent = create_agent_with_memory(llm, memory_config, system_prompt, tools)
    _agent_cache[agent_id] = (agent, cfg_hash)
    return agent


def clear_agent_cache(agent_id: str | None = None):
    """Clear the agent cache.

    Args:
        agent_id: If provided, clear only this agent. Otherwise clear all.
    """
    if agent_id:
        _agent_cache.pop(agent_id, None)
    else:
        _agent_cache.clear()
