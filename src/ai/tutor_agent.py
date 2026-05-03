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
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME, 
            google_api_key=Config.GOOGLE_API_KEY
        )
        self.graph = self._create_graph()

    def check_answer_node(self, state: TutorState):
        """Node to validate SQL logic using Gemini."""
        prompt = f"""
        Question: {state['question']}
        Correct SQL: {state['expected_sql']}
        User Attempt: {state['user_attempt']}
        
        Compare these queries. If they are functionally equivalent, start your response with 'CORRECT'.
        If not, provide a helpful hint without giving the full code.
        """
        
        response = self.llm.invoke(prompt)
        content = response.content
        is_correct = content.strip().upper().startswith("CORRECT")
        
        return {
            "feedback": content,
            "is_correct": is_correct,
            "attempts_count": state["attempts_count"] + 1
        }

    def _create_graph(self):
        """Builds the LangGraph workflow."""
        workflow = StateGraph(TutorState)
        
        # Add the checking node
        workflow.add_node("checker", self.check_answer_node)
        
        # Set entry point
        workflow.set_entry_point("checker")
        
        # Logical Routing: 
        # In a more complex app, you'd route back to the user here.
        # For now, we finish after the check, but the state is preserved.
        workflow.add_edge("checker", END)
        
        return workflow.compile()

    def validate_answer(self, question, expected, attempt, count):
        """Helper method for the UI to call."""
        initial_state = {
            "question": question,
            "expected_sql": expected,
            "user_attempt": attempt,
            "attempts_count": count,
            "is_correct": False,
            "feedback": ""
        }
        return self.graph.invoke(initial_state)