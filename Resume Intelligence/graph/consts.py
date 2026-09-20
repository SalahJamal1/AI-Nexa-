from langchain_ollama import ChatOllama

llm=ChatOllama(model="qwen3:1.7b",temperature=0)

INGESTION="ingestion"
ANALYZE="analyze"

MAX_RETRIES=3