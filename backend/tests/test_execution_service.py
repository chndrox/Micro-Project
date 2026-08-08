"""
Unit tests for CodeRunner execution service.
Tests subprocess isolation, timeout enforcement, output normalization, and error handling.
"""

import pytest
from backend.execution.code_runner import CodeRunner


@pytest.fixture
def runner():
    """Create a CodeRunner instance for testing."""
    return CodeRunner(timeout_seconds=5.0)


@pytest.fixture
def correct_solution():
    """Correct Two Sum solution."""
    return """
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


@pytest.fixture
def incorrect_solution():
    """Incorrect solution that returns wrong indices."""
    return """
class Solution:
    def twoSum(self, nums, target):
        return [0, 1]  # Always return first two indices
"""


@pytest.fixture
def timeout_solution():
    """Solution with infinite loop."""
    return """
class Solution:
    def twoSum(self, nums, target):
        while True:
            pass
        return []
"""


@pytest.fixture
def runtime_error_solution():
    """Solution that raises an exception."""
    return """
class Solution:
    def twoSum(self, nums, target):
        raise ValueError("Intentional error")
        return []
"""


@pytest.fixture
def sample_test_case_1():
    """Sample test case 1."""
    return {
        "id": 1,
        "input": "nums = [2,7,11,15]\ntarget = 9",
        "expected": "[0, 1]"
    }


@pytest.fixture
def sample_test_case_2():
    """Sample test case 2."""
    return {
        "id": 2,
        "input": "nums = [3,2,4]\ntarget = 6",
        "expected": "[1, 2]"
    }


# ============================================
# Test 1: Correct Solution
# ============================================

def test_correct_solution_single_case(runner, correct_solution, sample_test_case_1):
    """Test that correct solution passes single test case."""
    result = runner.run(correct_solution, [sample_test_case_1])
    
    assert result["status"] == "Accepted", f"Expected 'Accepted' but got '{result['status']}'"
    assert result["passed"] == 1
    assert result["total"] == 1
    assert len(result["cases"]) == 1
    assert result["cases"][0]["passed"] is True


def test_correct_solution_multiple_cases(runner, correct_solution, sample_test_case_1, sample_test_case_2):
    """Test that correct solution passes multiple test cases."""
    test_cases = [sample_test_case_1, sample_test_case_2]
    result = runner.run(correct_solution, test_cases)
    
    assert result["status"] == "Accepted"
    assert result["passed"] == 2
    assert result["total"] == 2
    assert all(c["passed"] for c in result["cases"])


# ============================================
# Test 2: Incorrect Solution
# ============================================

def test_incorrect_solution(runner, incorrect_solution, sample_test_case_1):
    """Test that incorrect solution fails comparison."""
    result = runner.run(incorrect_solution, [sample_test_case_1])
    
    assert result["status"] == "Wrong Answer", f"Expected 'Wrong Answer' but got '{result['status']}'"
    assert result["passed"] == 0
    assert result["total"] == 1
    assert result["cases"][0]["passed"] is False
    assert result["cases"][0]["actual"] == "[0, 1]"
    assert result["cases"][0]["expected"] == "[0, 1]"  # Normalized


def test_incorrect_solution_partial_pass(runner, correct_solution, sample_test_case_1, sample_test_case_2):
    """Test mix of passing and failing test cases."""
    # First case passes, second fails
    test_cases = [sample_test_case_1, sample_test_case_2]
    
    # Use correct solution but wrong expected value for second case
    modified_case_2 = {
        "id": 2,
        "input": "nums = [3,2,4]\ntarget = 6",
        "expected": "[0, 0]"  # Wrong expected value
    }
    
    result = runner.run(correct_solution, [sample_test_case_1, modified_case_2])
    
    assert result["status"] == "Wrong Answer"
    assert result["passed"] == 1
    assert result["failed"] == 1
    assert result["total"] == 2


# ============================================
# Test 3: Timeout Enforcement
# ============================================

def test_timeout_infinite_loop(runner, timeout_solution, sample_test_case_1):
    """Test that infinite loops are caught and timed out."""
    result = runner.run(timeout_solution, [sample_test_case_1])
    
    assert result["status"] == "Time Limit Exceeded"
    assert result["passed"] == 0
    assert result["total"] == 1
    assert result["cases"][0]["error"] == "Time Limit Exceeded"
    # Execution should take around 5 seconds
    assert 4500 <= result["cases"][0]["execution_time_ms"] <= 6000


# ============================================
# Test 4: Runtime Error
# ============================================

def test_runtime_error_exception(runner, runtime_error_solution, sample_test_case_1):
    """Test that exceptions are caught and reported."""
    result = runner.run(runtime_error_solution, [sample_test_case_1])
    
    assert result["status"] == "Runtime Error"
    assert result["passed"] == 0
    assert result["total"] == 1
    assert result["cases"][0]["error"] is not None
    assert "ValueError" in result["cases"][0]["error"] or "Intentional error" in result["cases"][0]["error"]


# ============================================
# Test 5: Output Normalization
# ============================================

def test_output_normalization_with_whitespace(runner):
    """Test that whitespace differences are normalized."""
    solution = """
class Solution:
    def twoSum(self, nums, target):
        return [0, 1]
"""
    
    # Expected with different whitespace formatting
    test_case = {
        "id": 1,
        "input": "nums = [2,7]\ntarget = 9",
        "expected": "  [0, 1]  "  # Extra whitespace
    }
    
    result = runner.run(solution, [test_case])
    
    assert result["status"] == "Accepted"
    assert result["cases"][0]["passed"] is True


def test_output_normalization_newlines(runner):
    """Test that trailing newlines are normalized."""
    solution = """
class Solution:
    def twoSum(self, nums, target):
        print("[0, 1]")
        return None
"""
    
    test_case = {
        "id": 1,
        "input": "nums = [2,7]\ntarget = 9",
        "expected": "[0, 1]"
    }
    
    result = runner.run(solution, [test_case])
    
    assert result["status"] == "Accepted"
    assert result["cases"][0]["passed"] is True


# ============================================
# Test 6: Test Case Loading
# ============================================

def test_empty_test_cases(runner, correct_solution):
    """Test with empty test case list."""
    result = runner.run(correct_solution, [])
    
    assert result["status"] == "Accepted"
    assert result["passed"] == 0
    assert result["total"] == 0
    assert len(result["cases"]) == 0


# ============================================
# Test 7: Parse Test Input
# ============================================

def test_parse_test_input_basic(runner):
    """Test parsing of basic test input."""
    input_str = "nums = [2,7,11,15]\ntarget = 9"
    parsed = runner._parse_test_input(input_str)
    
    assert parsed["nums"] == [2, 7, 11, 15]
    assert parsed["target"] == 9


def test_parse_test_input_negative_numbers(runner):
    """Test parsing with negative numbers."""
    input_str = "nums = [-1,-2,-3]\ntarget = -5"
    parsed = runner._parse_test_input(input_str)
    
    assert parsed["nums"] == [-1, -2, -3]
    assert parsed["target"] == -5


def test_parse_test_input_empty(runner):
    """Test parsing empty input."""
    input_str = ""
    parsed = runner._parse_test_input(input_str)
    
    assert parsed == {}


# ============================================
# Test 8: Normalize Output
# ============================================

def test_normalize_output_whitespace(runner):
    """Test output normalization removes whitespace."""
    assert runner._normalize_output("  [0, 1]  ") == "[0, 1]"
    assert runner._normalize_output("[0, 1]\n") == "[0, 1]"
    assert runner._normalize_output("\t[0, 1]\n") == "[0, 1]"


def test_normalize_output_empty(runner):
    """Test output normalization with empty strings."""
    assert runner._normalize_output("") == ""
    assert runner._normalize_output("   ") == ""


def test_normalize_output_none(runner):
    """Test output normalization with None."""
    assert runner._normalize_output(None) == ""


# ============================================
# Test 9: Status Determination
# ============================================

def test_status_all_passed(runner):
    """Test status when all cases pass."""
    cases = [
        {"passed": True, "error": None},
        {"passed": True, "error": None}
    ]
    status = runner._determine_status(cases)
    assert status == "Accepted"


def test_status_some_failed(runner):
    """Test status when some cases fail."""
    cases = [
        {"passed": True, "error": None},
        {"passed": False, "error": None}
    ]
    status = runner._determine_status(cases)
    assert status == "Wrong Answer"


def test_status_runtime_error(runner):
    """Test status when runtime error occurs."""
    cases = [
        {"passed": False, "error": "ValueError: bad value"}
    ]
    status = runner._determine_status(cases)
    assert status == "Runtime Error"


def test_status_timeout(runner):
    """Test status when timeout occurs."""
    cases = [
        {"passed": False, "error": "Time Limit Exceeded"}
    ]
    status = runner._determine_status(cases)
    assert status == "Time Limit Exceeded"


def test_status_timeout_priority(runner):
    """Test that timeout takes priority over other errors."""
    cases = [
        {"passed": False, "error": "Time Limit Exceeded"},
        {"passed": False, "error": "ValueError: bad value"}
    ]
    status = runner._determine_status(cases)
    assert status == "Time Limit Exceeded"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
