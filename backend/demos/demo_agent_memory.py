import os
from time import sleep

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

# from langchain.tools import tool, ToolRuntime


# @tool
# def get_user_info(runtime: ToolRuntime) -> str:
#     """Look up user info."""
#     user_id = runtime.state["user_id"]
#     return "User is John Smith" if user_id == "user_123" else "Unknown user"


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
    checkpointer=InMemorySaver(),
    system_prompt="Always respond in one short sentence.",
)

# Run the agent
result1 = agent.invoke(
    {"messages": [{"role": "user", "content": "Hi! I'm Ali"}]},
    {"configurable": {"thread_id": "1"}},
)
# print(result1)
print(result1["messages"][-1].content)

# To avoid throttling
sleep(3)

result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "What do you know about my name?"}]},
    {"configurable": {"thread_id": "1"}},
)
# print(result2)
print(result2["messages"][-1].content)
