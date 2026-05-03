import os
import subprocess
import sys
from database.db_setup import initialize_database
from config.config import Config

def setup_environment():
    """Ensure all necessary directories and the database exist."""
    print("🔧 Setting up SQL Tutor Environment...")
    
    # 1. Create necessary directories if they don't exist
    directories = [
        Config.DATASETS_PATH,
        os.path.dirname(Config.DB_PATH),
        "src/ai",
        "src/components",
        "src/utils"
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

    # 2. Check for .env file
    if not os.path.exists(".env"):
        print("⚠️ Warning: .env file not found. AI features will require a GOOGLE_API_KEY.")

    # 3. Initialize Database if it doesn't exist
    if not os.path.exists(Config.DB_PATH):
        print("🗄️ Database not found. Initializing with sample data...")
        try:
            initialize_database()
            print("✅ Database initialized successfully.")
        except Exception as e:
            print(f"❌ Failed to initialize database: {e}")
    else:
        print("✅ Database found.")

def start_app():
    """Launch the Streamlit interface."""
    print("🚀 Launching Streamlit UI...")
    try:
        # This calls the streamlit command as if you typed it in the terminal
        subprocess.run(["streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 SQL Tutor shutting down. See you next time!")
    except FileNotFoundError:
        print("❌ Error: Streamlit is not installed. Run 'pip install streamlit'.")

if __name__ == "__main__":
    setup_environment()
    start_app()