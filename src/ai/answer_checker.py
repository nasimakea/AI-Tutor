from src.ai.tutor_agent import tutor_app

class AnswerChecker:
    def __init__(self, db_runner, tutor_agent):
        self.db_runner = db_runner
        self.tutor_agent = tutor_agent

    def validate(self, question, expected, attempt, count):
        # 1. Perform Local Validation (Cost: $0)
        local_res = self.db_runner.validate_locally(attempt, expected)
        
        # 2. If correct locally, skip the AI and return success
        if local_res["is_correct"]:
            return {
                "feedback": "CORRECT! Your query produced the exact right data.",
                "is_correct": True,
                "attempts_count": count + 1,
                "result": local_res["result"]
            }
        
        # 3. If wrong or SQL error, call AI for a pedagogical hint
        # Pass the local error to the AI so it can explain the syntax mistake
        ai_res = self.tutor_agent.validate_answer(
            question, 
            expected, 
            attempt, 
            count, 
            is_locally_correct=False
        )
        
        return {
            "feedback": ai_res["feedback"],
            "is_correct": False,
            "attempts_count": ai_res["attempts_count"],
            "result": local_res["result"], # Might be None if SQL was invalid
            "error": local_res["error"]
        }