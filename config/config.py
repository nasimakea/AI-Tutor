import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DB_PATH = "database/sql_tutor.db"
    DATASETS_PATH = "datasets/"
    MODEL_NAME = "gemini-2.5-flash" # High speed, great for tutoring