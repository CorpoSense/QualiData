import os
from time import sleep
from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import before_model
from langchain.messages import RemoveMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    messages = state["messages"]

    if len(messages) <= 3:
        return None  # No changes needed

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *new_messages]}


load_dotenv()

# Custom OpenAI-compatible endpoint
llm = ChatOpenAI(
    model="openai/gpt-oss-120b",  # or your model name (or 'moonshotai/kimi-k2-instruct-0905')
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=1,
)

agent = create_agent(
    llm,
    tools=[],
    middleware=[trim_messages],
    checkpointer=InMemorySaver(),
    system_prompt="Always respond in one short paragaph as a max.",
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

agent.invoke({"messages": "hi, my name is Ali."}, config)
agent.invoke({"messages": "write a wisdom about reading"}, config)
agent.invoke({"messages": "give me a quote about science"}, config)
final_response = agent.invoke({"messages": "what does my name means?"}, config)

final_response["messages"][-1].pretty_print()
