from src.ai.question_generator import QuestionGenerator
from src.ai.tutor_agent import TutorAgent
from src.components.query_runner import QueryRunner
import json

class LearningPipeline:
    def __init__(self):
        self.question_gen = QuestionGenerator()
        self.tutor_agent = TutorAgent()
        self.runner = QueryRunner()

    def start_bulk_session(self, difficulty, concept, count=10):
        """
        Optimized: Fetches 10 questions in a single API call.
        Returns a list of question objects.
        """
        # 1. Generate lesson content
        lesson = self.question_gen.generate_lesson(concept, difficulty)
        
        # 2. Bulk generate questions (Cost-optimized)
        raw_json = self.question_gen.generate_bulk_questions(difficulty, concept, count)
        
        try:
            questions = json.loads(raw_json)
            return {
                "lesson": lesson,
                "questions": questions
            }
        except Exception as e:
            # Fallback if JSON parsing fails
            return {"error": f"Failed to load challenges: {str(e)}"}

    def process_submission(self, question, expected, user_sql, attempt_count):
        """
        Optimized: Uses local result-set validation before calling the AI Tutor.
        """
        # 1. Fast Path: Local Validation (Free)
        # Compares user result set vs expected result set in the local database
        validation = self.runner.validate_locally(user_sql, expected)
        
        # 2. Smart Path: AI Feedback (Only if needed)
        # If the local check fails, we use the TutorAgent to explain WHY
        hint = None
        is_correct = validation["is_correct"]
        feedback = "Correct! Well done." if is_correct else ""
        
        if not is_correct:
            # Only call the LLM API if the user is wrong to save costs
            tutor_res = self.tutor_agent.validate_answer(
                question, 
                expected, 
                user_sql, 
                attempt_count,
                is_locally_correct=False
            )
            feedback = tutor_res["feedback"]

        return {
            "is_correct": is_correct,
            "db_result": validation["result"],
            "sql_error": validation["error"],
            "feedback": feedback,
            "attempts": attempt_count + 1
        }