from analyzer.code_analyzer import analyze_code


code = """
def twoSum(nums, target):

    name = "hello"
    age = 20

    print(name)
    print(age)

    for i in range(10):
        print(i)

    return None
"""

result = analyze_code(
    code=code,
    milestone="brute_force",
)

print("\n========== ANALYZER RESULT ==========\n")

for key, value in result.items():
    print(f"{key}: {value}")