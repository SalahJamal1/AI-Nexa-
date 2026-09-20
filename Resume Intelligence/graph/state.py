from typing import TypedDict, NotRequired


class GraphState(TypedDict):
    question: NotRequired[str]
    generation: NotRequired[str]
    documents: NotRequired[list[str]]
    retry_count: NotRequired[int]
    file_path: NotRequired[str]
    job_role: NotRequired[str]
