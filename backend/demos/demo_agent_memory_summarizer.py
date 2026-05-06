import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

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
    middleware=[
        SummarizationMiddleware(llm, trigger=("tokens", 4000), keep=("messages", 20))
    ],
    checkpointer=InMemorySaver(),
    system_prompt="Please be concise and to the point.",
)


config: RunnableConfig = {"configurable": {"thread_id": "1"}}
agent.invoke({"messages": "hi, my name is Ali"}, config)
agent.invoke({"messages": "write a wisdom about reading"}, config)
agent.invoke({"messages": "give me a quote about science"}, config)
final_response = agent.invoke({"messages": "what does my name means?"}, config)

final_response["messages"][-1].pretty_print()
