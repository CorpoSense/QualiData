# We'll try use `langchain-chroma` (because of some issues while installing "faiss-cpu" locally)
# We'll use HuggingFace's endpoint (hosted models) for embeddings rather than local embedding
# Must install either:
# pip install -qU langchain-openai langchain-community langchain-huggingface pypdf langchain-chroma
# pip install -qU sentence-transformers # for local embedding (heavy ~150Mb)
import os

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

# from langchain_nomic import NomicEmbeddings # for NOMIC embedding (model="nomic-embed-text-v1.5", requires: pip install -qU langchain-nomic)
# from langchain_ollama import OllamaEmbeddings # for Ollama embedding (model="nomic-embed-text-v2-moe" or "nomic-embed-text", requires: `pip install -qU langchain-ollama` and "ollama" instance running)
# from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader

# from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.tools.retriever import create_retriever_tool

# from langchain_openai import OpenAIEmbeddings # for OpenAI Embeddings (e.g. "text-embedding-3-large")
from langchain_nvidia_ai_endpoints import (
    NVIDIAEmbeddings,  # for NVIDIA Embeddings (model: "NV-Embed-QA", requires: pip install -qU langchain-nvidia-ai-endpoints)
)

# from langchain_huggingface import (
#     HuggingFaceEndpointEmbeddings,  # , HuggingFaceEmbeddings
# )
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# from langchain_community.document_loaders import FileSystemBlobLoader
# from langchain_community.document_loaders.generic import GenericLoader
# from langchain_community.document_loaders.parsers import PyPDFParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


file_path = "./ticket.pdf"
# You can split it in two different ways: "page" or a "single" text flow using "mode", you can also set: pages_delimiter="\n"
loader = PyPDFLoader(file_path)  # mode="page",)

# Generic loader for any other file format (binary pdf, markdown, text...)
# loader = GenericLoader(
#     blob_loader=FileSystemBlobLoader(
#         path="./example_data/",
#         glob="*.pdf",
#     ),
#     blob_parser=PyPDFParser(),
# )

docs = loader.load()

# print(docs[0])
# import pprint
# pprint.pp(docs[0].metadata)

pages = []
for doc in loader.lazy_load():
    pages.append(doc)
    if len(pages) >= 10:
        # do some paged operation, e.g.
        # index.upsert(page)

        pages = []

print(f"Nbr of pages: {len(pages)}")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
splits = text_splitter.split_documents(docs)

# Initialize Hugging Face embeddings

#  through OpenRouter API
# embeddings = OpenAIEmbeddings(
#     base_url=os.getenv("OPENAI_BASE_URL"),
#     api_key=os.getenv("OPENAI_API_KEY"),
#     model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
#     check_embedding_ctx_length=False,  # for OpenRouter
#     encoding_format="float",  # for OpenRouter
#     dimensions=384,  # for "nvidia/llama-nemotron-embed-vl-1b-v2:free" model
# )

# NVIDIA
embeddings = NVIDIAEmbeddings(
    model="nvidia/llama-nemotron-embed-vl-1b-v2",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    dimensions=384,
)


# embeddings = HuggingFaceEmbeddings( # local embedding
# embeddings = HuggingFaceEndpointEmbeddings(
#     model="BAAI/bge-small-en-v1.5",  # intfloat/multilingual-e5-large-instruct',
#     task="feature-extraction",
#     huggingfacehub_api_token=os.getenv("HF_API_KEY"),
# )

# Create the vector store using these embeddings
#
# In-Memory vector store
# vectorstore = InMemoryVectorStore.from_texts( [text], embedding=embeddings)
#
# Index into a vector store
# vectorstore = FAISS.from_documents(splits, OpenAIEmbeddings()) # Using OpenAI embedding
# vector_db = FAISS.from_documents(splits, embeddings) # Using HF embedding
# Initialize and persist locally in a folder
vector_db = Chroma.from_documents(
    documents=splits, embedding=embeddings, persist_directory="./chroma_db"
)

retriever = vector_db.as_retriever()

# Custom OpenAI-compatible endpoint
llm = ChatOpenAI(
    # model="openai/gpt-oss-120b", # Groq has no embedding support at the current time
    # model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",  # OpenRouter
    model="nvidia/nemotron-3-super-120b-a12b",  # NVIDIA
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0,
)


search_my_document = create_retriever_tool(
    retriever,
    "pdf_search",
    "Search for information within the uploaded PDF document. Use this for any questions about the content of the file.",
)
# Now use 'search_my_document' in your list of tools
tools = [search_my_document]
agent = create_agent(llm, tools)


events = agent.stream(
    {"messages": [("user", "What's the provided document is about?")]},
    stream_mode="values",
)

for event in events:
    print(event["messages"][-1].content)


# more details at: https://docs.langchain.com/oss/python/integrations/document_loaders/pypdfloader
# Need to try:
# - OpenRouter's models for both inference and embeddings to reduce cost, latency
# - LanceDB: for large files, builtin, file-based (need to pip install lancedb)
# - Qdrant: for Scalability and production-level features, it supports both: Memory or Disk (need to pip install langchain-qdrant)
