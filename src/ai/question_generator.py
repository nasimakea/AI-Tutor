import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from config.config import Config
from database.db_connection import get_db_connection

class QuestionGenerator:
    def __init__(self):
        # Initialize the LangChain Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model=Config.MODEL_NAME,
            google_api_key=Config.GOOGLE_API_KEY,
            temperature=0.3 
        )

    def _get_schema_info(self):
        """Extracts database schema for the AI context."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        
        schema_text = ""
        for table in tables:
            t_name = table[0]
            cursor.execute(f"PRAGMA table_info({t_name});")
            columns = [col[1] for col in cursor.fetchall()]
            schema_text += f"Table {t_name} has columns: {', '.join(columns)}\n"
        conn.close()
        return schema_text

    def generate_lesson(self, concept, level):
        """Generates a tutorial based on the selected concept and active database tables."""
        schema = self._get_schema_info()
        
        prompt = ChatPromptTemplate.from_template("""
        You are a supportive SQL Teacher. 
        
        Active Database Tables:
        {schema}
        
        Task: Explain the SQL concept of '{concept}' at a '{level}' level.
        
        Instructions:
        1. Explain the theory simply.
        2. Use the ACTUAL tables and columns listed above to provide a code example.
        3. Format everything in clear Markdown.
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({"schema": schema, "concept": concept, "level": level})
        return response.content

    def generate_bulk_questions(self, difficulty="Beginner", concept="Basic SELECT", count=10):
        """Generates 10 challenges in a single API call to optimize cost and latency."""
        schema = self._get_schema_info()
        
        prompt = ChatPromptTemplate.from_template("""
        Role: Senior SQL Pedagogical Expert.
        
        Database Schema:
        {schema}
        
        Task: Generate {count} distinct SQL challenges for the concept '{concept}' at a '{difficulty}' level.
        
        Guidelines:
        1. Ensure every question is solvable using the schema provided.
        2. The 'expected_sql' must be a valid, executable SELECT statement.
        3. Align difficulty strictly: {difficulty}.
        
        Response Format:
        Return ONLY a JSON list of objects with the following keys: "question", "expected_sql".
        Example:
        [
          {{"question": "Get all emails from users", "expected_sql": "SELECT email FROM users"}}
        ]
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({
            "schema": schema, 
            "difficulty": difficulty, 
            "concept": concept, 
            "count": count
        })
        
        # Clean the response in case the AI wraps it in markdown code blocks
        clean_content = response.content.replace("```json", "").replace("```", "").strip()
        return clean_content