from src.ai.question_generator import QuestionGenerator
from src.ai.answer_checker import AnswerChecker
from src.components.hint_generator import HintGenerator
from src.components.query_runner import QueryRunner

class LearningPipeline:
    def __init__(self):
        self.question_gen = QuestionGenerator()
        self.checker = AnswerChecker()
        self.hinter = HintGenerator()
        self.runner = QueryRunner()

    def new_session(self, difficulty):
        raw_q = self.question_gen.generate_question(difficulty)
        # Basic parsing
        parts = raw_q.split("Expected_SQL:")
        return {
            "question": parts[0].replace("Question:", "").strip(),
            "expected_sql": parts[1].strip() if len(parts) > 1 else ""
        }

    def process_submission(self, question, expected, user_sql, attempt_count):
        # 1. Execute SQL
        db_res = self.runner.run_query(user_sql)
        
        # 2. Check Logic via LangGraph
        check_res = self.checker.validate(question, expected, user_sql, attempt_count)
        
        # 3. Logic for Hint: If they fail more than once, add a hint
        hint = None
        if not check_res["is_correct"] and attempt_count >= 1:
            hint = self.hinter.get_hint(question, expected, user_sql)
            
        return {
            "db_result": db_res,
            "check_result": check_res,
            "hint": hint
        }