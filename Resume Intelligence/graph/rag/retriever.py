import asyncio
import hashlib

from langchain_core.documents import Document

from graph.rag.vectorstore import vectorstore

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})


def document_idx(document: Document) -> str:
    source = document.metadata.get("source", "")
    page = document.metadata.get("page", "")
    return hashlib.sha256(f"{source}:{page}:{document.page_content}".encode()).hexdigest()


async def index_async(document: list[Document], batch_size: int = 50):
    batches = [document[i:batch_size + i] for i in range(0, len(document), batch_size)]

    async def add_doc(docs: list[Document], num_batches: int):
        try:
            ids = [document_idx(d) for d in docs]
            await vectorstore.aadd_documents(docs, ids=ids)
            return True
        except Exception as e:
            print(f"Error adding document: {num_batches} - {e}")
            return False

    tasks = [add_doc(d, i) for i, d in enumerate(batches)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    successful = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    print(
        f"Indexing completed: "
        f"{successful} successful, "
        f"{failed} failed, "
        f"{len(document)} total documents"
    )
