from dotenv import load_dotenv

load_dotenv()

from rag.generate_hint import generate_hint

result = generate_hint(
    problem_id="two_sum",
    milestone_id="brute_force",
    hint_level=1,
    student_code="""
nums = [2,7,11,15]
target = 9

for i in range(len(nums)):
    pass
"""
)

print(result)