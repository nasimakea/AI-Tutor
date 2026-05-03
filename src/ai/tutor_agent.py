import operator
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from config.config import Config

# 1. Define the State
class TutorState(TypedDict):
    question: str
    expected_sql: str
    user_attempt: str
    feedback: str
    attempts_count: int
    is_correct: bool

class TutorAgent:
    def __init__(self):
        # Initialize the LLM - Only used for hints now to save costs
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME, 
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.graph = self._create_graph()

    def provide_hint_node(self, state: TutorState):
        """
        Node to provide a hint using Gemini only when the local check fails.
        This optimizes costs by only calling the API when the user actually needs help.
        """
        prompt = f"""
        You are an expert SQL Tutor. 
        Question: {state['question']}
        The Correct SQL is: {state['expected_sql']}
        The User's Incorrect Attempt: {state['user_attempt']}
        
        Task: Do NOT provide the correct code. Instead, identify the logical error 
        (e.g., wrong column, missing JOIN, incorrect filter) and provide a helpful 
        pedagogical hint to guide the student.
        """
        
        response = self.llm.invoke(prompt)
        return {
            "feedback": response.content,
            "is_correct": False,
            "attempts_count": state["attempts_count"] + 1
        }

    def _create_graph(self):
        """Builds the LangGraph workflow."""
        workflow = StateGraph(TutorState)
        
        # Add the hint node
        workflow.add_node("hinter", self.provide_hint_node)
        
        # Set entry point
        workflow.set_entry_point("hinter")
        workflow.add_edge("hinter", END)
        
        return workflow.compile()

    def validate_answer(self, question, expected, attempt, count, is_locally_correct=False):
        """
        Modified helper method.
        If is_locally_correct is True, we return success without calling the Graph (API).
        """
        if is_locally_correct:
            return {
                "feedback": "CORRECT! Well done.",
                "is_correct": True,
                "attempts_count": count + 1
            }
        
        # If not locally correct, we run the graph to get an AI hint
        initial_state = {
            "question": question,
            "expected_sql": expected,
            "user_attempt": attempt,
            "attempts_count": count,
            "is_correct": False,
            "feedback": ""
        }
        return self.graph.invoke(initial_state)