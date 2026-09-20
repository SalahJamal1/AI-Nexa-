from graph.chains.hallucination_chain import GradHallucination, hallucination_chain
from graph.state import GraphState


def hallucination(state: GraphState):
    print("--- Hallucination ---")
    documents = state.get("documents")
    generation = state.get("generation")
    retry_count = state.get("retry_count", 0)
    if retry_count >= 3:
        print(f"--- Max retries (3) reached, accepting generation ---")
        return "failed"
    grad_hallucination: GradHallucination = hallucination_chain.invoke(
        {"documents": documents, "generation": generation})
    if grad_hallucination.binary_score:
        print("--- Generation is grounded in documents ---")
        return "useful"

    print("--- Generation contains hallucination ---")
    return "not useful"
