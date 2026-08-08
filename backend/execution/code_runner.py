import subprocess
import tempfile
import time
import logging
from pathlib import Path

logger = logging.getLogger("thinkforge")


class CodeRunner:
    """
    Executes Python code in isolated subprocesses.
    
    WARNING: This provides basic isolation only (timeout, process separation).
    NOT suitable for production without additional sandboxing (Docker, seccomp, etc.).
    """
    
    def __init__(self, timeout_seconds: float = 5.0):
        """Initialize with default execution timeout."""
        self._timeout = timeout_seconds
    
    def run(
        self,
        code: str,
        test_cases: list[dict],
    ) -> dict:
        """
        Execute code against test cases.
        
        Args:
            code: Python source code (string)
            test_cases: List of dicts with {id, input, expected}
        
        Returns:
            {
                "status": "Accepted" | "Wrong Answer" | "Runtime Error" | "Time Limit Exceeded",
                "passed": int,
                "failed": int,
                "total": int,
                "cases": [
                    {
                        "passed": bool,
                        "input": str,
                        "expected": str,
                        "actual": str,
                        "error": str | null
                    }
                ],
                "runtime": str (optional),
                "memory": str (optional)
            }
        """
        if not test_cases:
            return {
                "status": "Accepted",
                "passed": 0,
                "failed": 0,
                "total": 0,
                "cases": [],
                "runtime": "0 ms",
                "memory": None
            }
        
        results = []
        total_time = 0
        
        for test_case in test_cases:
            result = self._run_single_test(code, test_case)
            results.append(result)
            total_time += float(result.get("execution_time_ms", 0))
        
        passed = sum(1 for r in results if r.get("passed", False))
        failed = len(results) - passed
        
        status = self._determine_status(results)
        
        return {
            "status": status,
            "passed": passed,
            "failed": failed,
            "total": len(results),
            "cases": results,
            "runtime": f"{total_time:.1f} ms" if total_time > 0 else "0 ms",
            "memory": None
        }
    
    def _run_single_test(
        self,
        code: str,
        test_case: dict
    ) -> dict:
        """Execute code for one test case in isolated subprocess."""
        try:
            # Parse test input
            test_data = self._parse_test_input(test_case.get("input", ""))
            
            # Create wrapper code that calls student function
            wrapper = self._create_wrapper_code(code, test_data)
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(wrapper)
                temp_path = f.name
            
            try:
                start_time = time.time()
                
                # Run subprocess with timeout (NOT using shell for security)
                result = subprocess.run(
                    ['python', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=self._timeout,
                    shell=False
                )
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Normalize outputs
                actual = self._normalize_output(result.stdout)
                expected = self._normalize_output(test_case.get("expected", ""))
                
                return {
                    "passed": actual == expected,
                    "input": test_case.get("input", ""),
                    "expected": expected,
                    "actual": actual,
                    "error": result.stderr if result.returncode != 0 else None,
                    "execution_time_ms": execution_time_ms
                }
                
            except subprocess.TimeoutExpired:
                return {
                    "passed": False,
                    "input": test_case.get("input", ""),
                    "expected": test_case.get("expected", ""),
                    "actual": "",
                    "error": "Time Limit Exceeded",
                    "execution_time_ms": self._timeout * 1000
                }
            except Exception as e:
                logger.exception(f"Error executing test case: {e}")
                return {
                    "passed": False,
                    "input": test_case.get("input", ""),
                    "expected": test_case.get("expected", ""),
                    "actual": "",
                    "error": str(e),
                    "execution_time_ms": 0
                }
            finally:
                # Cleanup temporary file
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception as e:
            logger.exception(f"Unexpected error in _run_single_test: {e}")
            return {
                "passed": False,
                "input": test_case.get("input", ""),
                "expected": test_case.get("expected", ""),
                "actual": "",
                "error": f"Setup error: {str(e)}",
                "execution_time_ms": 0
            }
    
    def _create_wrapper_code(self, code: str, test_data: dict) -> str:
        """Create wrapper code that injects test data and calls the student solution."""
        # Build variable assignments from test data
        var_assignments = "\n".join(
            f"{name} = {repr(value)}" for name, value in test_data.items()
        )
        
        wrapper = f"""{code}

# Inject test data
{var_assignments}

# Call student solution
import sys
try:
    sol = Solution()
    result = sol.twoSum(nums, target)
    print(result)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        return wrapper
    
    def _parse_test_input(self, input_str: str) -> dict:
        """
        Parse frontend test input format:
        'nums = [2,7,11,15]\\ntarget = 9'
        
        Returns: {"nums": [2,7,11,15], "target": 9}
        """
        result = {}
        
        if not input_str:
            return result
        
        lines = input_str.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or '=' not in line:
                continue
            
            parts = line.split('=', 1)
            if len(parts) != 2:
                continue
            
            var_name = parts[0].strip()
            var_value_str = parts[1].strip()
            
            try:
                # Use eval to parse Python literals (safe for test data)
                var_value = eval(var_value_str)
                result[var_name] = var_value
            except Exception as e:
                logger.warning(f"Could not parse test input '{line}': {e}")
                continue
        
        return result
    
    def _normalize_output(self, output: str) -> str:
        """
        Normalize output for comparison.
        - Strip leading/trailing whitespace
        - Remove spaces around commas in lists/dicts for format-agnostic comparison
        """
        if output is None:
            return ""
        output = output.strip()
        # Remove spaces after commas and before/after brackets for Python list/dict format flexibility
        # E.g., "[0, 1]" becomes "[0,1]" to match "[0,1]"
        output = output.replace(", ", ",")
        return output
    
    def _determine_status(self, cases: list[dict]) -> str:
        """
        Determine overall status from test case results.
        
        Priority:
        1. Time Limit Exceeded - if any case timed out
        2. Runtime Error - if any case has non-timeout error
        3. Wrong Answer - if any case failed comparison
        4. Accepted - all cases passed
        """
        # Check for timeout
        has_timeout = any(
            c.get("error") == "Time Limit Exceeded" 
            for c in cases
        )
        if has_timeout:
            return "Time Limit Exceeded"
        
        # Check for other errors
        has_error = any(
            c.get("error") is not None and c.get("error") != "Time Limit Exceeded"
            for c in cases
        )
        if has_error:
            return "Runtime Error"
        
        # Check if all passed
        all_passed = all(c.get("passed", False) for c in cases)
        if all_passed:
            return "Accepted"
        else:
            return "Wrong Answer"
