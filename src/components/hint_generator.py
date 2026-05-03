import google.generativeai as genai
from config.config import Config

class HintGenerator:
    def __init__(self):
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(Config.MODEL_NAME)

    def get_hint(self, question, expected_sql, user_attempt):
        prompt = f"""
        User is struggling with this SQL question: {question}
        The correct query is: {expected_sql}
        Their last attempt was: {user_attempt}
        
        Provide a short, helpful hint. 
        Don't give the SQL code. Instead, point them toward the right keywords (e.g., 'Look into the WHERE clause' or 'Try using a JOIN').
        """
        response = self.model.generate_content(prompt)
        return response.text