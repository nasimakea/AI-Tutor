sql_tutor_project/
│
├── app.py                  # Streamlit UI
├── main.py                 # Entry point
│
├── config/
│   ├── __init__.py
│   └── config.py           # Configuration & API settings
│
├── database/
│   ├── __init__.py
│   ├── db_setup.py         # Sample datasets (employees, sales)
│   └── db_connection.py    # Database connection
│
├── src/
│   ├── __init__.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── tutor_agent.py        # Explain concepts
│   │   ├── question_generator.py # Generate SQL problems
│   │   └── answer_checker.py     # Validate user SQL
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── query_runner.py
│   │   ├── feedback_generator.py
│   │   └── hint_generator.py
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── learning_pipeline.py  # End-to-end learning flow
│   │
│   └── utils/
│       └── __init__.py
│
├── datasets/
│   ├── employees.csv
│   └── sales.csv
│
├── tests/
│   ├── __init__.py
│   └── test_pipeline.py
│
├── requirements.txt
└── README.md"# AI-Tutor" 
"# AI-Tutor" 
