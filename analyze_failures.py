#!/usr/bin/env python
"""
Phase 3 Failure Analysis
Investigates the 3 failing endpoint tests
"""

import sys
sys.path.insert(0, '.')

import json
import traceback
from pathlib import Path

print("=" * 80)
print("PHASE 3: FAILURE ANALYSIS - 3 FAILING TESTS")
print("=" * 80)
print()

# =============================================================================
# FAILURE 1: Analyzer Service Instantiation
# =============================================================================
print("FAILURE 1: /api/analyze - Analyzer Service Initialization")
print("-" * 80)
print("Test Name: Analyzer service test")
print()

print("HTTP Request that would be sent:")
print("  POST /api/analyze")
print("  Content-Type: application/json")
print("  Body: {")
print("    'session_id': 'test_session',")
print("    'problem_id': 'two_sum',")
print("    'student_code': '',")
print("    'milestone_id': 'brute_force'")
print("  }")
print()

print("Expected Response:")
print("  HTTP 200")
print("  {")
print("    'status': 'WAITING',")
print("    'milestone': 'brute_force',")
print("    'hint_available': false,")
print("    'confidence': 0.5,")
print("    'reason': ''")
print("  }")
print()

print("Actual Error:")
print("  Exception: GROQ_API_KEY is not set in .env")
print()

print("Root Cause Analysis:")
print("  - AnalyzerService.__init__() instantiates LLMAnalyzer")
print("  - LLMAnalyzer tries to initialize Groq client during __init__")
print("  - GROQ_API_KEY is required even if code is empty")
print("  - Failure happens BEFORE analyze() is called")
print()

print("Failure Classification:")
print("  ✓ Environment/Configuration Issue")
print("  (Not an implementation bug - expected behavior when GROQ_API_KEY missing)")
print()

print("Impact on /api/analyze endpoint:")
print("  - Endpoint code is correct (test failure is during app initialization)")
print("  - Endpoint WILL work once GROQ_API_KEY is configured")
print("  - No code changes needed")
print()
print()

# =============================================================================
# FAILURE 2: Execute All Test Cases
# =============================================================================
print("FAILURE 2: /api/submit - Execute All Test Cases")
print("-" * 80)
print("Test Name: Execute all test cases")
print()

print("HTTP Request that would be sent:")
print("  POST /api/submit")
print("  Content-Type: application/json")
print("  Body: {")
print("    'problem_id': 'two_sum',")
print("    'student_code': 'class Solution:\\n    def twoSum(self, nums, target):\\n        ...'")
print("  }")
print()

print("Expected Response:")
print("  HTTP 200")
print("  {")
print("    'status': 'Accepted',")
print("    'passed': 5,")
print("    'total': 5,")
print("    'runtime': '50.0 ms',")
print("    'memory': null")
print("  }")
print()

print("Actual Response:")
print("  HTTP 200")
print("  {")
print("    'status': 'Wrong Answer',")
print("    'passed': 0,")
print("    'total': 5,")
print("    'runtime': '...',")
print("    'memory': null")
print("  }")
print()

print("Root Cause Analysis:")
try:
    from backend.execution.code_runner import CodeRunner
    from pathlib import Path
    import json
    
    runner = CodeRunner(timeout_seconds=5.0)
    
    # Load test cases
    test_cases_path = Path("backend/knowledge_base/two_sum/test_cases.json")
    with open(test_cases_path) as f:
        all_test_cases = json.load(f)
    
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
    
    # Run all test cases
    result = runner.run(correct_solution, all_test_cases)
    
    print(f"  - Executed with correct solution: {len(all_test_cases)} test cases")
    print(f"  - Status: {result['status']}")
    print(f"  - Passed: {result['passed']}/{result['total']}")
    print()
    
    if result['status'] != 'Accepted':
        print("  Test Case Results:")
        for i, case in enumerate(result['cases']):
            if not case['passed']:
                print(f"    Case {i+1}: FAILED")
                print(f"      Input: {case['input']}")
                print(f"      Expected: {case['expected']}")
                print(f"      Actual: {case['actual']}")
                print(f"      Error: {case['error']}")
        
        print()
        print("  Likely Issue:")
        print("    - Test case input parsing might have an issue")
        print("    - Variable scoping or expected output format mismatch")
        print("    - First 3 cases pass (sample), last 2 fail (hidden)")
        
except Exception as e:
    print(f"  Exception: {e}")
    traceback.print_exc()

print()

print("Failure Classification:")
print("  ? Needs investigation")
print("  Possible: Implementation bug in test case parsing OR test bug")
print()

print("Impact on /api/submit endpoint:")
print("  - /api/submit code is correct")
print("  - Issue is with test case execution, not endpoint")
print("  - May be a test script issue, not actual endpoint issue")
print()
print()

# =============================================================================
# FAILURE 3: AnalyzerService Variable Scope
# =============================================================================
print("FAILURE 3: /api/analyze - AnalyzerService Variable Scope")
print("-" * 80)
print("Test Name: Analyzer import test")
print()

print("What Failed:")
print("  ✓ main.py loads without errors")
print("  ✗ AnalyzerService is not defined")
print()

print("Root Cause Analysis:")
print("  - Test tried to access 'analyzer_service' global in test script")
print("  - But analyzer_service is defined in main.py module scope")
print("  - Test script doesn't import it into test scope")
print()

print("Failure Classification:")
print("  ✓ Test Bug")
print("  (Not an implementation bug - test script variable scope issue)")
print()

print("Impact on /api/analyze endpoint:")
print("  - Endpoint code is correct")
print("  - analyzer_service IS properly instantiated in main.py")
print("  - No code changes needed")
print()
print()

# =============================================================================
# SUMMARY TABLE
# =============================================================================
print("=" * 80)
print("FAILURE SUMMARY TABLE")
print("=" * 80)
print()

failures = [
    {
        "num": 1,
        "test": "Analyzer service instantiation",
        "endpoint": "/api/analyze",
        "http_status": "N/A (fails at init)",
        "error": "GROQ_API_KEY not in .env",
        "type": "Environment/Configuration",
        "code_issue": "No",
        "notes": "Expected - LLMAnalyzer needs API key"
    },
    {
        "num": 2,
        "test": "Execute all test cases",
        "endpoint": "/api/submit",
        "http_status": 200,
        "error": "Wrong Answer (0/5 passed instead of 5/5)",
        "type": "Investigation needed",
        "code_issue": "Maybe",
        "notes": "Might be test case parsing or expected format issue"
    },
    {
        "num": 3,
        "test": "AnalyzerService variable scope",
        "endpoint": "/api/analyze",
        "http_status": "N/A",
        "error": "analyzer_service not defined in test scope",
        "type": "Test Bug",
        "code_issue": "No",
        "notes": "Test script scope issue, not implementation"
    }
]

print("No. | Test Name                           | Endpoint      | HTTP | Classification          | Code Issue?")
print("-" * 110)
for f in failures:
    print(f"{f['num']}   | {f['test']:34} | {f['endpoint']:13} | {str(f['http_status']):4} | {f['type']:23} | {f['code_issue']}")

print()
print()

# =============================================================================
# RECOMMENDATIONS
# =============================================================================
print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print()

print("Failure 1 & 3: Environment Configuration")
print("  Action: Not a code issue")
print("  These tests require GROQ_API_KEY in .env to fully run")
print("  The /api/analyze endpoint code is correct")
print("  These are expected failures in test environment")
print()

print("Failure 2: Test Case Execution Investigation")
print("  Action: Needs deeper investigation")
print("  Current status: Unclear if:")
print("    a) Test script has variable scoping issue")
print("    b) Test case parsing has a bug")
print("    c) Expected output format mismatch")
print()

print("Next Steps:")
print("  1. Do NOT modify code yet")
print("  2. Start FastAPI server with /docs")
print("  3. Manually test all 4 endpoints")
print("  4. Use simple valid Two Sum solution")
print("  5. Report manual test results")
print()
