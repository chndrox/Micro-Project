from pydantic import BaseModel
from typing import Optional


# ============================================
# EXISTING MODELS (KEEP UNCHANGED)
# ============================================

class AnalyzeRequest(BaseModel):
    session_id: str
    code: str
    milestone: str = "brute_force"


class HintRequest(BaseModel):
    session_id: str
    problem_id: str
    milestone_id: str
    hint_level: int
    student_code: str = ""


# ============================================
# NEW MODELS FOR CONTINUOUS CODE ANALYSIS
# ============================================

class AnalyzeCodeRequest(BaseModel):
    """Frontend POST /api/analyze request for continuous code analysis."""
    session_id: str
    problem_id: str
    student_code: str
    milestone_id: str = "brute_force"


class AnalyzeCodeResponse(BaseModel):
    """Frontend expects this structure from POST /api/analyze."""
    status: str  # "WAITING", "TYPING", "RELEVANT", "PROGRESSING", "STUCK"
    milestone: str
    hint_available: bool
    confidence: float
    reason: str


# ============================================
# NEW MODELS FOR CODE EXECUTION
# ============================================

class RunCodeRequest(BaseModel):
    """Frontend POST /api/run request."""
    problem_id: str
    student_code: str
    test_cases: list[dict]  # [{id, input, expected}, ...]


class RunCodeResponse(BaseModel):
    """Frontend expects this structure from POST /api/run."""
    status: str  # "Accepted", "Wrong Answer", "Runtime Error", "Time Limit Exceeded"
    passed: int
    total: int
    cases: list[dict]  # [{passed: bool, ...}, ...]
    runtime: Optional[str] = None  # e.g., "45 ms"
    memory: Optional[str] = None   # e.g., "14.2 MB"


class SubmitRequest(BaseModel):
    """Frontend POST /api/submit request."""
    problem_id: str
    student_code: str


class SubmitResponse(BaseModel):
    """Frontend expects this structure from POST /api/submit."""
    status: str  # "Accepted", "Wrong Answer", "Runtime Error"
    passed: int
    total: int
    cases: Optional[list[dict]] = None  # Optional: hide details for hidden tests
    runtime: Optional[str] = None
    memory: Optional[str] = None


class HintResponse(BaseModel):
    """Frontend expects this structure from POST /api/hint."""
    milestone: str
    hint_level: int
    hint: str