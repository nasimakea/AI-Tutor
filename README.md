# 🎓 AI SQL Tutor Pro

An **AI-powered SQL learning platform** that combines **local query validation + LLM-based tutoring** to deliver fast, cost-efficient, and interactive SQL practice.

---

## 🚀 What Makes This Project Different

Unlike typical AI tutors that rely entirely on APIs, this system is **optimized for performance and cost**:

* ⚡ **Local SQL validation (0 cost)** using SQLite + Pandas
* 🤖 **AI used only when needed** (for hints & explanations)
* 📦 **Bulk question generation (10 at once)** to reduce API calls
* 🧠 **Schema-aware teaching** using real database tables
* 🔄 **End-to-end learning pipeline**

---

## 🧠 Core Architecture

### 1. Hybrid Validation System

* First checks user query locally using result comparison
* Only calls AI if the answer is incorrect

### 2. AI Tutor (LangGraph Workflow)

* Uses **Gemini via LangChain**
* Provides **hints instead of answers**
* Designed for **pedagogical learning**

### 3. Cost Optimization Strategy

* Bulk generation of questions
* Avoid unnecessary LLM calls
* Lightweight SQLite backend

---

## 📂 Project Structure

```bash
sql_tutor_project/
│
├── app.py                  # Streamlit UI (interactive tutor)
├── main.py                 # Setup + app launcher
│
├── config/
│   └── config.py           # API keys, paths
│
├── database/
│   ├── db_connection.py    # SQLite connection handler
│   └── db_setup.py         # CSV → SQL table loader
│
├── src/
│   ├── ai/
│   │   ├── tutor_agent.py        # LangGraph-based AI hint system
│   │   ├── question_generator.py # Schema-aware question generation
│   │   └── answer_checker.py     # Hybrid validation logic
│   │
│   ├── components/
│   │   ├── query_runner.py       # Query execution + validation
│   │   ├── hint_generator.py     # Lightweight hint system
│   │
│   ├── pipeline/
│   │   └── learning_pipeline.py  # Full learning workflow
│
├── datasets/
│   ├── employees.csv
│   └── sales.csv
│
├── tests/
│   └── test_pipeline.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works (Flow)

1. User selects:

   * Topic (SELECT, JOIN, GROUP BY, etc.)
   * Difficulty level

2. System:

   * Generates **lesson explanation**
   * Generates **10 SQL challenges in one API call**

3. User writes SQL query

4. System validates:

   * ✅ Local DB comparison (fast)
   * ❌ If wrong → AI gives hint (not solution)

---

## 💡 Key Components Explained

### 🗄️ Database Layer

* SQLite database initialized from CSV files
* Dynamic schema extraction for AI context
* Safe execution (only SELECT queries allowed)

---

### ⚡ Query Runner

* Executes SQL queries safely
* Compares results using Pandas
* Provides schema + sample data preview

---

### 🤖 Question Generator

* Uses **LangChain + Gemini**
* Injects real database schema into prompts
* Generates:

  * Lessons
  * Bulk SQL problems (JSON format)

---

### 🧠 Tutor Agent (LangGraph)

* Graph-based AI workflow
* Provides **hints only (no answers)**
* Triggered **only on incorrect attempts**

---

### 🔄 Learning Pipeline

* Orchestrates:

  * Lesson generation
  * Question generation
  * Answer validation
  * Feedback loop

---

### 🌐 Streamlit UI

Source: 

* Sidebar:

  * Dataset selection (built-in or custom CSV)
  * Topic & difficulty selection
* Main Interface:

  * Lesson → Practice flow
  * SQL editor
  * Result visualization
  * AI hints
  * Progress tracking (10-question session)

---

## 🛠️ Installation

```bash
git clone https://github.com/your-username/sql_tutor_project.git
cd sql_tutor_project
```

```bash
python -m venv venv
venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key_here
```

---

## ▶️ Run the Project

```bash
python main.py
```

---

## 📊 Features

* 📚 AI-generated lessons
* 🧪 Real SQL practice with datasets
* 🔍 Schema + sample data preview
* 💬 AI hints (not answers)
* ⚡ Instant validation
* 📈 Progress tracking (10-question sessions)
* 📂 Upload custom datasets

---

## 🧪 Testing

```bash
pytest
```

---

## 🚧 Future Improvements

* User authentication
* Progress dashboard
* Leaderboard / gamification
* More datasets (real-world scenarios)
* Query performance analysis

---

## 👨‍💻 Author

**Nasim**

---

## ⭐ Why This Project Stands Out

This is not just a CRUD app. It demonstrates:

* AI system design (LangChain + LangGraph)
* Cost-aware LLM architecture
* Backend + data engineering skills
* Interactive product thinking

---

"# AI-Tutor" 
