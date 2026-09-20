from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from graph.consts import llm


class GradAnswer(BaseModel):
    binary_score: bool = Field(description="Answer addresses the question, 'yes' or 'no'")


system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""

prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
])

llm_with_structured = llm.with_structured_output(GradAnswer)

answer_chain = prompt | llm_with_structured
