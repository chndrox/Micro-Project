#!/usr/bin/env python
"""
Phase 2 Manual Test Suite - CodeRunner Execution Service
Tests all critical functionality without requiring pytest
"""

import sys
sys.path.insert(0, '.')

from backend.execution.code_runner import CodeRunner
import json

def print_test_result(test_name, passed, details=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"       {details}")
    return passed

# Initialize test counter
total_tests = 0
passed_tests = 0

print("=" * 60)
print("PHASE 2: CODE EXECUTION SERVICE TEST SUITE")
print("=" * 60)
print()

# Create runner
runner = CodeRunner(timeout_seconds=5.0)

# =============================================================================
# TEST 1: Correct Solution
# =============================================================================
print("TEST 1: Correct Solution")
print("-" * 40)

correct_solution = """
class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, num in enumerate(nums):
            complement = target - num
            if complement in seen:
                return [seen[complement], i]
            seen[num] = i
        return []
"""

test_case = {
    "id": 1,
    "input": "nums = [2,7,11,15]\ntarget = 9",
    "expected": "[0, 1]"
}

result = runner.run(correct_solution, [test_case])
total_tests += 1
if (result['status'] == 'Accepted' and result['passed'] == 1 and result['total'] == 1):
    passed_tests += 1
    passed = print_test_result(
        "Correct solution passes",
        True,
        f"Status: {result['status']}, Passed: {result['passed']}/{result['total']}"
    )
else:
    passed = print_test_result(
        "Correct solution passes",
        False,
        f"Status: {result['status']}, Passed: {result['passed']}/{result['total']} (expected Accepted, 1/1)"
    )
print()

# =============================================================================
# TEST 2: Incorrect Solution
# =============================================================================
print("TEST 2: Incorrect Solution")
print("-" * 40)

incorrect_solution = """
class Solution:
    def twoSum(self, nums, target):
        return [0, 0]
"""

result = runner.run(incorrect_solution, [test_case])
total_tests += 1
if result['status'] == 'Wrong Answer' and result['passed'] == 0 and result['total'] == 1:
    passed_tests += 1
    passed = print_test_result(
        "Incorrect solution fails",
        True,
        f"Status: {result['status']}, Passed: {result['passed']}/{result['total']}"
    )
else:
    passed = print_test_result(
        "Incorrect solution fails",
        False,
        f"Status: {result['status']}, Passed: {result['passed']}/{result['total']} (expected Wrong Answer, 0/1)"
    )
print()

# =============================================================================
# TEST 3: Multiple Test Cases
# =============================================================================
print("TEST 3: Multiple Test Cases")
print("-" * 40)

test_cases = [
    {
        "id": 1,
        "input": "nums = [2,7,11,15]\ntarget = 9",
        "expected": "[0, 1]"
    },
    {
        "id": 2,
        "input": "nums = [3,2,4]\ntarget = 6",
        "expected": "[1, 2]"
    }
]

result = runner.run(correct_solution, test_cases)
total_tests += 1
if result['status'] == 'Accepted' and result['passed'] == 2 and result['total'] == 2:
    passed_tests += 1
    passed = print_test_result(
        "All test cases pass",
        True,
        f"Passed: {result['passed']}/{result['total']}"
    )
else:
    passed = print_test_result(
        "All test cases pass",
        False,
        f"Passed: {result['passed']}/{result['total']} (expected 2/2)"
    )
print()

# =============================================================================
# TEST 4: Output Normalization
# =============================================================================
print("TEST 4: Output Normalization")
print("-" * 40)

test_case_normalized = {
    "id": 1,
    "input": "nums = [2,7]\ntarget = 9",
    "expected": "  [0, 1]  "  # Extra whitespace
}

simple_solution = """
class Solution:
    def twoSum(self, nums, target):
        return [0, 1]
"""

result = runner.run(simple_solution, [test_case_normalized])
total_tests += 1
if result['status'] == 'Accepted' and result['passed'] == 1:
    passed_tests += 1
    passed = print_test_result(
        "Whitespace normalization works",
        True,
        f"Status: {result['status']}"
    )
else:
    passed = print_test_result(
        "Whitespace normalization works",
        False,
        f"Status: {result['status']} (expected Accepted)"
    )
print()

# =============================================================================
# TEST 5: Parse Test Input
# =============================================================================
print("TEST 5: Parse Test Input")
print("-" * 40)

parsed = runner._parse_test_input("nums = [2,7,11,15]\ntarget = 9")
total_tests += 1
if parsed.get('nums') == [2, 7, 11, 15] and parsed.get('target') == 9:
    passed_tests += 1
    passed = print_test_result(
        "Parse list and integer",
        True,
        f"nums={parsed['nums']}, target={parsed['target']}"
    )
else:
    passed = print_test_result(
        "Parse list and integer",
        False,
        f"Got: {parsed}"
    )

parsed = runner._parse_test_input("nums = [-1,-2,-3]\ntarget = -5")
total_tests += 1
if parsed.get('nums') == [-1, -2, -3] and parsed.get('target') == -5:
    passed_tests += 1
    passed = print_test_result(
        "Parse negative numbers",
        True,
        f"nums={parsed['nums']}, target={parsed['target']}"
    )
else:
    passed = print_test_result(
        "Parse negative numbers",
        False,
        f"Got: {parsed}"
    )
print()

# =============================================================================
# TEST 6: Normalize Output
# =============================================================================
print("TEST 6: Normalize Output")
print("-" * 40)

tests = [
    ("  [0, 1]  ", "[0,1]", "Strip leading/trailing whitespace and normalize commas"),
    ("[0, 1]\n", "[0,1]", "Strip newline and normalize commas"),
    ("\t[0, 1]\n", "[0,1]", "Strip tab and newline and normalize commas"),
    ("", "", "Empty string"),
]

for input_str, expected, description in tests:
    result_str = runner._normalize_output(input_str)
    total_tests += 1
    if result_str == expected:
        passed_tests += 1
        print_test_result(description, True)
    else:
        print_test_result(description, False, f"Got '{result_str}', expected '{expected}'")
print()

# =============================================================================
# TEST 7: Status Determination
# =============================================================================
print("TEST 7: Status Determination")
print("-" * 40)

status_tests = [
    ([{"passed": True, "error": None}, {"passed": True, "error": None}], "Accepted", "All pass"),
    ([{"passed": True, "error": None}, {"passed": False, "error": None}], "Wrong Answer", "Some fail"),
    ([{"passed": False, "error": "ValueError"}], "Runtime Error", "Runtime error"),
    ([{"passed": False, "error": "Time Limit Exceeded"}], "Time Limit Exceeded", "Timeout"),
    ([{"passed": False, "error": "Time Limit Exceeded"}, {"passed": False, "error": "ValueError"}], "Time Limit Exceeded", "Timeout takes priority"),
]

for cases, expected, description in status_tests:
    result_status = runner._determine_status(cases)
    total_tests += 1
    if result_status == expected:
        passed_tests += 1
        print_test_result(description, True, f"Status: {result_status}")
    else:
        print_test_result(description, False, f"Got '{result_status}', expected '{expected}'")
print()

# =============================================================================
# TEST 8: Test Case Loading from JSON
# =============================================================================
print("TEST 8: Test Case Loading from JSON")
print("-" * 40)

with open('backend/knowledge_base/two_sum/test_cases.json') as f:
    test_cases_data = json.load(f)

total_tests += 1
if len(test_cases_data) == 5:
    passed_tests += 1
    print_test_result("Load 5 test cases", True, f"Loaded {len(test_cases_data)} cases")
else:
    print_test_result("Load 5 test cases", False, f"Loaded {len(test_cases_data)}, expected 5")

sample_count = sum(1 for t in test_cases_data if t['is_sample'])
hidden_count = sum(1 for t in test_cases_data if not t['is_sample'])

total_tests += 1
if sample_count == 3:
    passed_tests += 1
    print_test_result("3 sample cases", True)
else:
    print_test_result("3 sample cases", False, f"Found {sample_count}")

total_tests += 1
if hidden_count == 2:
    passed_tests += 1
    print_test_result("2 hidden cases", True)
else:
    print_test_result("2 hidden cases", False, f"Found {hidden_count}")
print()

# =============================================================================
# TEST 9: Empty Test Cases
# =============================================================================
print("TEST 9: Empty Test Cases")
print("-" * 40)

result = runner.run(correct_solution, [])
total_tests += 1
if result['status'] == 'Accepted' and result['total'] == 0:
    passed_tests += 1
    print_test_result("Empty test case list", True, "Status: Accepted, Total: 0")
else:
    print_test_result("Empty test case list", False, f"Status: {result['status']}, Total: {result['total']}")
print()

# =============================================================================
# TEST 10: Phase 1 Models Still Work
# =============================================================================
print("TEST 10: Phase 1 Pydantic Models")
print("-" * 40)

try:
    from backend.models.schemas import (
        AnalyzeCodeRequest, AnalyzeCodeResponse,
        RunCodeRequest, RunCodeResponse,
        SubmitRequest, SubmitResponse, HintResponse
    )
    total_tests += 1
    passed_tests += 1
    print_test_result("All Phase 1 models import", True)
except Exception as e:
    total_tests += 1
    print_test_result("All Phase 1 models import", False, str(e))
print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {total_tests - passed_tests}")
print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
print()

if passed_tests == total_tests:
    print("✓ ALL TESTS PASSED!")
    sys.exit(0)
else:
    print("✗ SOME TESTS FAILED")
    sys.exit(1)
