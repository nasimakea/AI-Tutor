

import streamlit as st
import pandas as pd
from src.ai.question_generator import QuestionGenerator
from src.ai.tutor_agent import TutorAgent
from src.components.query_runner import QueryRunner
from database.db_connection import get_db_connection
from database.db_setup import initialize_database

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI SQL Tutor", page_icon="🎓", layout="wide")

# --- INITIALIZE COMPONENTS ---
@st.cache_resource
def load_components():
    return QuestionGenerator(), TutorAgent(), QueryRunner()

que_gen, tutor_agent, db_runner = load_components()

# --- SESSION STATE MANAGEMENT ---
if "mode" not in st.session_state:
    st.session_state.mode = "setup" # setup, lesson, or practice
    st.session_state.lesson_content = ""
    st.session_state.current_q = None
    st.session_state.expected_sql = None
    st.session_state.feedback = ""
    st.session_state.attempts = 0

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.title("📂 Learning Path")
    
    # 1. Data Selection
    data_choice = st.radio("Data Source:", ["In-built Datasets", "Upload Custom CSVs"])
    
    if data_choice == "Upload Custom CSVs":
        uploaded_files = st.file_uploader("Upload 1 or 2 CSVs", type="csv", accept_multiple_files=True)
        if uploaded_files:
            conn = get_db_connection()
            for f in uploaded_files:
                df = pd.read_csv(f)
                t_name = f.name.split('.')[0].lower()
                df.to_sql(t_name, conn, if_exists="replace", index=False)
            conn.close()
            st.success("Custom tables loaded!")
    else:
        if st.button("Reset to In-built Data"):
            initialize_database()
            st.info("In-built data restored.")

    st.divider()
    
    # 2. Learning Parameters
    concept = st.selectbox("Topic", ["Basic SELECT", "Joins", "Aggregates (GROUP BY)", "Subqueries"])
    difficulty = st.select_slider("Difficulty", options=["Beginner", "Intermediate", "Advanced"])

    if st.button("🚀 Start Learning Session", use_container_width=True):
        with st.spinner("Generating your lesson..."):
            st.session_state.lesson_content = que_gen.generate_lesson(concept, difficulty)
            raw_q = que_gen.generate_question(difficulty, concept=concept)
            try:
                st.session_state.current_q = raw_q.split("Expected_SQL:")[0].replace("Question:", "").strip()
                st.session_state.expected_sql = raw_q.split("Expected_SQL:")[1].strip()
                st.session_state.mode = "lesson"
                st.session_state.feedback = ""
                st.session_state.attempts = 0
            except:
                st.error("AI formatting error. Try again!")

# --- MAIN UI ---
st.title("🎓 Personal SQL Tutor")

if st.session_state.mode == "setup":
    st.write("### Welcome! Configure your session in the sidebar to begin.")
    st.image("https://img.icons8.com/clouds/200/database.png")

elif st.session_state.mode == "lesson":
    st.markdown("## 📖 Concept Explanation")
    st.markdown(st.session_state.lesson_content)
    
    if st.button("I understand, let's practice! ➡️"):
        st.session_state.mode = "practice"
        st.rerun()

elif st.session_state.mode == "practice":
    st.markdown(f"### ✍️ Practice: {concept}")

    # --- SCHEMA & DATA PREVIEW ---
    with st.expander("🔍 View Database Schema & Data Samples", expanded=True):
        schema_data = db_runner.get_schema_dict()
        if not schema_data:
            st.info("No tables found in the database.")
        else:
            for table_name, info in schema_data.items():
                st.markdown(f"**Table:** `{table_name}`")
                if info.get("sample"):
                    sample_df = pd.DataFrame(info["sample"], columns=info["columns"])
                    st.dataframe(sample_df, use_container_width=True, hide_index=True)
                else:
                    st.caption(f"Columns: {', '.join(info['columns'])}")
                    st.warning("Table is currently empty.")
                st.divider()

    # --- CHALLENGE DISPLAY ---
    st.info(f"**Task:** {st.session_state.current_q}")
    user_sql = st.text_area("Write your SQL Query:", height=150, placeholder="SELECT ... FROM ...", key="sql_input_area")

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
    
    with col_btn1:
        if st.button("🚀 Submit Answer", use_container_width=True):
            run_res = db_runner.run_query(user_sql)
            check_res = tutor_agent.validate_answer(
                st.session_state.current_q, 
                st.session_state.expected_sql, 
                user_sql, 
                st.session_state.attempts
            )
            st.session_state.feedback = check_res["feedback"]
            st.session_state.attempts = check_res["attempts_count"]

            if run_res["success"]:
                st.success("Query executed successfully!")
                st.dataframe(run_res["result"], use_container_width=True)
            else:
                st.error(f"Execution Error: {run_res['error']}")

            if "CORRECT" in st.session_state.feedback.upper():
                st.balloons()
                st.success(st.session_state.feedback)
            else:
                st.warning(f"🤖 AI Tutor: {st.session_state.feedback}")
    
    with col_btn2:
        if st.button("⬅️ Back to Lesson", use_container_width=True):
            st.session_state.mode = "lesson"
            st.rerun()

    # --- FIXED PRACTICE MORE LOGIC ---
    if st.session_state.feedback and "CORRECT" in st.session_state.feedback.upper():
        with col_btn3:
            if st.button("🔄 Practice More", type="primary"):
                with st.spinner("Generating another challenge..."):
                    # Call generation
                    new_raw_q = que_gen.generate_question(difficulty, concept=concept)
                    
                    # Robust Parsing
                    if "Expected_SQL:" in new_raw_q:
                        parts = new_raw_q.split("Expected_SQL:")
                        st.session_state.current_q = parts[0].replace("Question:", "").strip()
                        st.session_state.expected_sql = parts[1].strip()
                        # Reset states for the new question
                        st.session_state.feedback = ""
                        st.session_state.attempts = 0
                        st.rerun()
                    else:
                        st.error("The AI gave a non-standard response. Please click 'Practice More' again.")