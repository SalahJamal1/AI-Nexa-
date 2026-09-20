from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from graph.consts import llm


class GradHallucination(BaseModel):
    binary_score: bool = Field(description="Answer is grounded in / supported by the set of facts, 'yes' or 'no'")


system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
])

llm_with_structured = llm.with_structured_output(GradHallucination)

hallucination_chain = prompt | llm_with_structured
