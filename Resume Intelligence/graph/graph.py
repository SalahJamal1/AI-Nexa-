from langgraph.graph import StateGraph, END

from graph.consts import INGESTION, ANALYZE
from graph.nodes.analyze_node import analyze_node
from graph.nodes.hallucination import hallucination
from graph.nodes.ingestion_node import ingestion_node
from graph.state import GraphState

flow = StateGraph(GraphState)

flow.set_entry_point(INGESTION)
flow.add_node(INGESTION, ingestion_node)
flow.add_node(ANALYZE, analyze_node)

flow.add_edge(INGESTION, ANALYZE)

flow.add_conditional_edges(ANALYZE, hallucination, {
    "useful": END,
    "not useful": ANALYZE,
    "failed": END
})

app = flow.compile()

if __name__ == "__main__":
    app.get_graph().draw_mermaid_png(output_file_path="graph.png")
