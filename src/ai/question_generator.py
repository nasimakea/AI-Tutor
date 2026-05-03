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
            temperature=0.3 # Lower temperature for more consistent teaching logic
        )

    def _get_schema_info(self):
        """Extracts database schema for the AI context."""
        conn = get_db_connection()
        cursor = conn.cursor()
        # Filter out internal sqlite tables
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
        3. Explain what the example code does.
        4. Format everything in clear Markdown (use bolding and code blocks).
        """)
        
        chain = prompt | self.llm
        response = chain.invoke({"schema": schema, "concept": concept, "level": level})
        return response.content

    def generate_question(self, difficulty="Beginner", concept="Basic SELECT"):
        """Generates a challenge based on the specific concept and active schema."""
        schema = self._get_schema_info()
        
        prompt = ChatPromptTemplate.from_template("""
    Role: You are a Senior Data Engineer and SQL Pedagogical Expert. 
    Context: You are designing a curriculum for a student learning SQL.
    
    Database Schema:
    {schema}
    
    Task: 
    Generate a {difficulty} level SQL challenge centered on the concept of '{concept}'.
    
    Guidelines:
    1. Clarity: The question must be unambiguous. Define exactly which columns should be returned and any specific ordering required.
    2. Realism: Create a scenario that reflects a real-world business use case.
    3. Technical Accuracy: Ensure the Expected_SQL is optimized and compatible with standard SQL (PostgreSQL/DuckDB/SQLite).
    4. Difficulty Alignment: 
       - Beginner: Single table, basic filters, or simple aggregations.
       - Intermediate: Joins, subqueries, or GROUP BY with HAVING.
       - Advanced: Window functions, CTEs, or complex conditional logic.

    Response Constraints:
    - Do NOT include any introductory or concluding text.
    - Do NOT use markdown code blocks inside the Expected_SQL section.
    - Return exactly two lines starting with the prefixes below.

    Question: [Insert natural language task here]
    Expected_SQL: [Insert executable SQL query here]
    """)
        
        chain = prompt | self.llm
        response = chain.invoke({"schema": schema, "difficulty": difficulty, "concept": concept})
        return response.content