import streamlit as st
import pandas as pd
import json
from src.ai.question_generator import QuestionGenerator
from src.ai.tutor_agent import TutorAgent
from src.components.query_runner import QueryRunner
from database.db_connection import get_db_connection
from database.db_setup import initialize_database

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI SQL Tutor Pro", page_icon="🎓", layout="wide")

# --- INITIALIZE COMPONENTS ---
@st.cache_resource
def load_components():
    return QuestionGenerator(), TutorAgent(), QueryRunner()

que_gen, tutor_agent, db_runner = load_components()

# --- SESSION STATE MANAGEMENT ---
if "mode" not in st.session_state:
    st.session_state.update({
        "mode": "setup",
        "question_buffer": [],
        "current_idx": 0,
        "lesson_content": "",
        "current_q": None,
        "expected_sql": None,
        "feedback": "",
        "attempts": 0,
        "last_result": None
    })

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.title("📂 Learning Path")
    
    data_choice = st.radio("Data Source:", ["In-built Datasets", "Upload Custom CSVs"])
    
    if data_choice == "Upload Custom CSVs":
        uploaded_files = st.file_uploader("Upload CSVs", type="csv", accept_multiple_files=True)
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
    
    concept = st.selectbox("Topic", ["Basic SELECT", "Joins", "Aggregates (GROUP BY)", "Subqueries"])
    difficulty = st.select_slider("Difficulty", options=["Beginner", "Intermediate", "Advanced"])

    if st.button("🚀 Start 10-Question Session", use_container_width=True):
        with st.spinner("Generating 10 custom challenges (Optimizing API usage...)..."):
            # 1. Generate Lesson Explanation
            st.session_state.lesson_content = que_gen.generate_lesson(concept, difficulty)
            
            # 2. Bulk Generate 10 Questions in 1 API Call
            raw_json = que_gen.generate_bulk_questions(difficulty, concept, count=10)
            try:
                questions = json.loads(raw_json)
                st.session_state.question_buffer = questions
                st.session_state.current_idx = 0
                
                # Load first question from buffer
                first = questions[0]
                st.session_state.current_q = first["question"]
                st.session_state.expected_sql = first["expected_sql"]
                
                st.session_state.mode = "lesson"
                st.session_state.feedback = ""
                st.session_state.attempts = 0
            except Exception as e:
                st.error("Failed to parse bulk questions. Resetting...")

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
    curr_i = st.session_state.current_idx
    total_q = len(st.session_state.question_buffer)
    
    st.subheader(f"Challenge {curr_i + 1} of {total_q}")
    st.progress((curr_i + 1) / total_q)

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
                st.divider()

    st.info(f"**Task:** {st.session_state.current_q}")
    user_sql = st.text_area("Write your SQL Query:", height=150, key=f"sql_input_{curr_i}")

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 3])
    
    with col_btn1:
        if st.button("🚀 Submit & Validate", use_container_width=True):
            # 1. LOCAL VALIDATION (Instant & Free)
            res = db_runner.validate_locally(user_sql, st.session_state.expected_sql)
            st.session_state.last_result = res
            
            if res["is_correct"]:
                st.session_state.feedback = "CORRECT"
                st.balloons()
            else:
                # 2. CALL AI ONLY ON FAILURE (For pedagogical hint)
                with st.spinner("AI Tutor is analyzing your mistake..."):
                    check_res = tutor_agent.validate_answer(
                        st.session_state.current_q, 
                        st.session_state.expected_sql, 
                        user_sql, 
                        st.session_state.attempts,
                        is_locally_correct=False
                    )
                    st.session_state.feedback = check_res["feedback"]
                    st.session_state.attempts = check_res["attempts_count"]

    # --- DISPLAY RESULTS ---
    if st.session_state.last_result:
        res = st.session_state.last_result
        if res["error"]:
            st.error(f"❌ SQL Error: {res['error']}")
        elif res["result"] is not None:
            st.success("Query executed successfully!")
            st.dataframe(res["result"], use_container_width=True)

    if st.session_state.feedback == "CORRECT":
        st.success("✅ Perfect! Your result matches the expected output.")
        with col_btn3:
            if st.button("➕ Practice Next Question", type="primary"):
                if curr_i + 1 < total_q:
                    next_q = st.session_state.question_buffer[curr_i + 1]
                    st.session_state.update({
                        "current_idx": curr_i + 1,
                        "current_q": next_q["question"],
                        "expected_sql": next_q["expected_sql"],
                        "feedback": "",
                        "last_result": None,
                        "attempts": 0
                    })
                    st.rerun()
                else:
                    st.success("🏆 All 10 challenges complete! Reset in the sidebar for more.")
    elif st.session_state.feedback:
        st.warning(f"🤖 AI Tutor Hint: {st.session_state.feedback}")

    with col_btn2:
        if st.button("⬅️ Back to Lesson", use_container_width=True):
            st.session_state.mode = "lesson"
            st.rerun()