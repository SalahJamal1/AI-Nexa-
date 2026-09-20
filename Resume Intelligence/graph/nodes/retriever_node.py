from graph.rag.retriever import retriever
from graph.state import GraphState


def retriever_node(state: GraphState) -> GraphState:
    print("--- Retriever Node ---")
    question = state.get("question")
    documents = retriever.invoke({"question": question})
    return {"documents": documents}
