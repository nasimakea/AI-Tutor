from src.ai.tutor_agent import tutor_app

class AnswerChecker:
    def validate(self, question, expected, attempt, count):
        inputs = {
            "question": question,
            "expected_sql": expected,
            "user_attempt": attempt,
            "attempts_count": count,
            "is_correct": False
        }
        return tutor_app.invoke(inputs)