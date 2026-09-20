from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

embedding = OllamaEmbeddings(
    model="nomic-embed-text"
)
vectorstore = Chroma(persist_directory="./chroma_db", collection_name="resumes", embedding_function=embedding)
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=150)
