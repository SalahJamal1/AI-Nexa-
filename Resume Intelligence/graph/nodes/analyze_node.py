from graph.chains.analyze_chain import analyze_chain
from graph.state import GraphState


def analyze_node(state: GraphState) -> GraphState:
    print("--- Analyzing Node ---")
    documents = state.get("documents", [])
    job_role = state.get("job_role", None)
    if not job_role:
        raise ValueError("job_role is required")

    if not documents:
        raise ValueError("documents are required")
    retry_count = state.get("retry_count", 0) + 1
    generation = analyze_chain.invoke({"documents": documents, "job_role": job_role})
    return {"generation": generation, "retry_count": retry_count}
