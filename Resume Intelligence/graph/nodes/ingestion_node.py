from graph.rag.ingestion import ingestion
from graph.state import GraphState


async def ingestion_node(state: GraphState) -> GraphState:
    print("--- INGESTION NODE ---")
    file_path = state.get("file_path")

    if not file_path:
        raise ValueError("file_path is required for ingestion")

    documents = await ingestion(file_path)
    return {"documents": documents}
