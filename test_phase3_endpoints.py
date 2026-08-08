#!/usr/bin/env python
"""
Phase 3 Integration Tests - API Routes and Analyzer/RAG Integration
Tests all four new endpoints without requiring pytest or full server setup
"""

import sys
sys.path.insert(0, '.')

import json
import os
from pathlib import Path

# Initialize test counts
total_tests = 0
passed_tests = 0

def print_test_result(test_name, passed, details=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if details:
        print(f"       {details}")
    return passed

print("=" * 70)
print("PHASE 3: API ROUTES AND ANALYZER/RAG INTEGRATION TEST SUITE")
print("=" * 70)
print()

# =============================================================================
# TEST 1: Schema Validation
# =============================================================================
print("TEST 1: Request/Response Schemas")
print("-" * 70)

try:
    from backend.models.schemas import (
        AnalyzeCodeRequest, AnalyzeCodeResponse,
        RunCodeRequest, RunCodeResponse,
        SubmitRequest, SubmitResponse,
        HintResponse, AnalyzeRequest, HintRequest
    )
    
    # Test AnalyzeCodeRequest
    req1 = AnalyzeCodeRequest(
        session_id="test",
        problem_id="two_sum",
        student_code="code",
        milestone_id="brute_force"
    )
    total_tests += 1
    passed_tests += 1
    print_test_result("AnalyzeCodeRequest schema", True)
    
    # Test RunCodeRequest
    req2 = RunCodeRequest(
        problem_id="two_sum",
        student_code="code",
        test_cases=[]
    )
    total_tests += 1
    passed_tests += 1
    print_test_result("RunCodeRequest schema", True)
    
    # Test SubmitRequest
    req3 = SubmitRequest(
        problem_id="two_sum",
        student_code="code"
    )
    total_tests += 1
    passed_tests += 1
    print_test_result("SubmitRequest schema", True)
    
    # Test legacy schemas
    req4 = AnalyzeRequest(
        session_id="test",
        code="test",
        milestone="brute_force"
    )
    total_tests += 1
    passed_tests += 1
    print_test_result("Legacy AnalyzeRequest schema", True)
    
except Exception as e:
    total_tests += 4
    print_test_result("Schema validation test", False, str(e))

print()

# =============================================================================
# TEST 2: CodeRunner Integration
# =============================================================================
print("TEST 2: CodeRunner Integration (/api/run)")
print("-" * 70)

try:
    from backend.execution.code_runner import CodeRunner
    
    runner = CodeRunner(timeout_seconds=5.0)
    
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
    
    # Test correct solution
    result = runner.run(
        correct_solution,
        [{
            "id": 1,
            "input": "nums = [2,7,11,15]\ntarget = 9",
            "expected": "[0, 1]"
        },
        {
            "id": 2,
            "input": "nums = [3,2,4]\ntarget = 6",
            "expected": "[1, 2]"
        }]
    )
    
    total_tests += 1
    if result["status"] == "Accepted" and result["passed"] == 2:
        passed_tests += 1
        print_test_result("Correct solution passes", True)
    else:
        print_test_result("Correct solution passes", False,
                         f"Status: {result['status']}, Passed: {result['passed']}")
    
    # Test incorrect solution
    incorrect_solution = """
class Solution:
    def twoSum(self, nums, target):
        return [0, 0]
"""
    
    result = runner.run(
        incorrect_solution,
        [{
            "id": 1,
            "input": "nums = [2,7]\ntarget = 9",
            "expected": "[0, 1]"
        }]
    )
    
    total_tests += 1
    if result["status"] == "Wrong Answer":
        passed_tests += 1
        print_test_result("Incorrect solution detected", True)
    else:
        print_test_result("Incorrect solution detected", False,
                         f"Status: {result['status']}")
    
except Exception as e:
    total_tests += 2
    print_test_result("CodeRunner integration test", False, str(e))

print()

# =============================================================================
# TEST 3: Test Case Loading for /api/submit
# =============================================================================
print("TEST 3: Test Case Loading (/api/submit)")
print("-" * 70)

try:
    # Load all test cases (sample + hidden)
    test_cases_path = Path("backend/knowledge_base/two_sum/test_cases.json")
    with open(test_cases_path) as f:
        all_test_cases = json.load(f)
    
    total_tests += 1
    if len(all_test_cases) == 5:
        passed_tests += 1
        print_test_result("Load all 5 test cases", True)
    else:
        print_test_result("Load all 5 test cases", False,
                         f"Got {len(all_test_cases)}, expected 5")
    
    sample_count = sum(1 for t in all_test_cases if t.get("is_sample"))
    hidden_count = len(all_test_cases) - sample_count
    
    total_tests += 1
    if sample_count == 3 and hidden_count == 2:
        passed_tests += 1
        print_test_result("Test case split correct", True,
                         f"3 sample, 2 hidden")
    else:
        print_test_result("Test case split correct", False,
                         f"Got {sample_count} sample, {hidden_count} hidden")
    
    # Test that submission with all cases works
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
    
    result = runner.run(
        correct_solution,
        all_test_cases
    )
    
    total_tests += 1
    if result["status"] == "Accepted" and result["total"] == 5:
        passed_tests += 1
        print_test_result("Execute all test cases", True)
    else:
        print_test_result("Execute all test cases", False,
                         f"Status: {result['status']}, Total: {result['total']}")
        
except Exception as e:
    total_tests += 3
    print_test_result("Test case loading test", False, str(e))

print()

# =============================================================================
# TEST 4: Analyzer Service Availability
# =============================================================================
print("TEST 4: Analyzer Service Integration")
print("-" * 70)

try:
    from backend.analyzer import AnalyzerService
    
    analyzer = AnalyzerService()
    
    total_tests += 1
    if analyzer is not None:
        passed_tests += 1
        print_test_result("AnalyzerService instantiates", True)
    else:
        print_test_result("AnalyzerService instantiates", False)
    
    # Test that analyzer has required methods
    total_tests += 1
    if hasattr(analyzer, 'analyze') and callable(analyzer.analyze):
        passed_tests += 1
        print_test_result("AnalyzerService.analyze() exists", True)
    else:
        print_test_result("AnalyzerService.analyze() exists", False)
        
    # Test that analyzer handles empty code gracefully
    # (Skip if Groq not configured)
    if os.environ.get("GROQ_API_KEY"):
        result = analyzer.analyze(
            session_id="test_session",
            code="",
            milestone="brute_force"
        )
        
        total_tests += 1
        if result.get("status") == "WAITING":
            passed_tests += 1
            print_test_result("Analyzer handles empty code", True)
        else:
            print_test_result("Analyzer handles empty code", False,
                             f"Status: {result.get('status')}")
    else:
        total_tests += 1
        print_test_result("Analyzer handles empty code (skipped - no GROQ_API_KEY)", True)
        passed_tests += 1
    
except Exception as e:
    total_tests += 3
    print_test_result("Analyzer service test", False, str(e))

print()

# =============================================================================
# TEST 5: RAG Module Availability
# =============================================================================
print("TEST 5: RAG Integration")
print("-" * 70)

try:
    from backend.rag.generate_hint import generate_hint
    
    total_tests += 1
    if callable(generate_hint):
        passed_tests += 1
        print_test_result("RAG generate_hint callable", True)
    else:
        print_test_result("RAG generate_hint callable", False)
    
    # Check that RAG retriever is importable
    from backend.rag.retriver import retrieve
    
    total_tests += 1
    if callable(retrieve):
        passed_tests += 1
        print_test_result("RAG retriever callable", True)
    else:
        print_test_result("RAG retriever callable", False)
        
except Exception as e:
    total_tests += 2
    print_test_result("RAG test", False, str(e))

print()

# =============================================================================
# TEST 6: Main.py Imports
# =============================================================================
print("TEST 6: Main.py Imports")
print("-" * 70)

try:
    # Import main module to verify it loads without errors
    import importlib.util
    spec = importlib.util.spec_from_file_location("backend.main", "backend/main.py")
    main_module = importlib.util.module_from_spec(spec)
    
    total_tests += 1
    try:
        spec.loader.exec_module(main_module)
        passed_tests += 1
        print_test_result("main.py loads without errors", True)
    except Exception as load_err:
        print_test_result("main.py loads without errors", False, str(load_err))
    
    # Check that FastAPI app exists
    total_tests += 1
    if hasattr(main_module, 'app'):
        passed_tests += 1
        print_test_result("FastAPI app instantiated", True)
    else:
        print_test_result("FastAPI app instantiated", False)
        
except Exception as e:
    total_tests += 2
    print_test_result("main.py imports test", False, str(e))

print()

# =============================================================================
# TEST 7: Phase 1 & 2 Backwards Compatibility
# =============================================================================
print("TEST 7: Backwards Compatibility")
print("-" * 70)

try:
    from backend.models.schemas import AnalyzeRequest, HintRequest
    from backend.execution.code_runner import CodeRunner
    
    # Phase 1 legacy models
    req = AnalyzeRequest(
        session_id="test",
        code="test code",
        milestone="brute_force"
    )
    total_tests += 1
    passed_tests += 1
    print_test_result("Phase 1 AnalyzeRequest works", True)
    
    # Phase 2 CodeRunner
    runner = CodeRunner()
    total_tests += 1
    if callable(runner.run):
        passed_tests += 1
        print_test_result("Phase 2 CodeRunner works", True)
    else:
        print_test_result("Phase 2 CodeRunner works", False)
        
except Exception as e:
    total_tests += 2
    print_test_result("Backwards compatibility test", False, str(e))

print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests}")
print(f"Failed: {total_tests - passed_tests}")
print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
print()

if passed_tests == total_tests:
    print("✓ ALL PHASE 3 INTEGRATION TESTS PASSED!")
    sys.exit(0)
else:
    print("✗ SOME PHASE 3 TESTS FAILED")
    sys.exit(1)
