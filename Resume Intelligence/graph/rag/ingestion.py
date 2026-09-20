from langchain_community.document_loaders import PyPDFLoader

from graph.rag.retriever import index_async
from graph.rag.vectorstore import splitter


async def ingestion(file_path: str):
    if file_path is None:
        raise Exception("file path is None")
    documents = PyPDFLoader(file_path).load()
    chunks = splitter.split_documents(documents)

    print(
        f"Processing {len(chunks)} chunks "
        f"out of {len(documents)} pages"
    )

    print("--- Start ingesting ---")

    await index_async(chunks)
    print("--- Ingestion completed ---")
    return documents
