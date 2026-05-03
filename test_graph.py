from src.ai.tutor_agent import TutorAgent

agent = TutorAgent()

# Simulate a correct answer
result = agent.validate_answer(
    question="Show all employees",
    expected="SELECT * FROM employees",
    attempt="SELECT * FROM employees",
    count=0
)

print(f"Test 1 (Correct) - Is Correct: {result['is_correct']}")
print(f"Feedback: {result['feedback'][:50]}...")

# Simulate a wrong answer
result_wrong = agent.validate_answer(
    question="Show all employees",
    expected="SELECT * FROM employees",
    attempt="DROP TABLE employees",
    count=1
)

print(f"\nTest 2 (Wrong) - Is Correct: {result_wrong['is_correct']}")
print(f"Feedback: {result_wrong['feedback']}")