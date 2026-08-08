import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.analyzer import AnalyzerService
from backend.models import (
    AnalyzeRequest, HintRequest,
    AnalyzeCodeRequest, AnalyzeCodeResponse,
    RunCodeRequest, RunCodeResponse,
    SubmitRequest, SubmitResponse,
    HintResponse
)
from backend.rag.generate_hint import generate_hint
from backend.execution import CodeRunner

logger = logging.getLogger("thinkforge")


app = FastAPI(
    title="ThinkForge AI",
    version="1.0.0",
)


# -----------------------------------------
# CORS
# -----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------
# Services
# -----------------------------------------

analyzer_service = AnalyzerService()
execution_service = CodeRunner(timeout_seconds=5.0)


# -----------------------------------------
# Helpers
# -----------------------------------------

def _load_test_cases(problem_id: str, include_hidden: bool = False) -> list[dict]:
    """Load test cases from knowledge base."""
    path = Path(__file__).parent / "knowledge_base" / problem_id / "test_cases.json"
    with open(path) as f:
        all_cases = json.load(f)
    
    if include_hidden:
        return all_cases
    else:
        return [c for c in all_cases if c.get("is_sample", False)]


# -----------------------------------------
# Root
# -----------------------------------------

@app.get("/")
def root():

    return {
        "message": "ThinkForge AI backend running"
    }


# -----------------------------------------
# Analyze code (NEW - CONTINUOUS ANALYSIS)
# -----------------------------------------

@app.post("/api/analyze")
def analyze_code(
    request: AnalyzeCodeRequest
) -> AnalyzeCodeResponse:
    """
    Continuously analyze student code for progress and hint availability.
    Uses existing AnalyzerService with AST + Groq LLM analysis.
    """
    try:
        # Call existing analyzer service
        result = analyzer_service.analyze(
            session_id=request.session_id,
            code=request.student_code,
            milestone=request.milestone_id
        )
        
        # Transform analyzer result to match frontend expectations
        return AnalyzeCodeResponse(
            status=result.get("status", "WAITING"),
            milestone=result.get("milestone", request.milestone_id),
            hint_available=result.get("hint_available", False),
            confidence=result.get("llm", {}).get("confidence", 0.5) if result.get("llm") else 0.5,
            reason=result.get("llm", {}).get("reason", "") if result.get("llm") else ""
        )
    except Exception as e:
        logger.exception(f"Error in /api/analyze: {e}")
        raise HTTPException(status_code=500, detail="Code analysis failed")


# -----------------------------------------
# Run code (NEW - TEST EXECUTION)
# -----------------------------------------

@app.post("/api/run")
def run_code(request: RunCodeRequest) -> RunCodeResponse:
    """
    Execute code against provided test cases (sample tests only).
    Uses CodeRunner for subprocess isolation.
    """
    try:
        result = execution_service.run(
            code=request.student_code,
            test_cases=request.test_cases
        )
        return RunCodeResponse(**result)
    except Exception as e:
        logger.exception(f"Error in /api/run: {e}")
        raise HTTPException(status_code=500, detail="Code execution failed")


# -----------------------------------------
# Submit solution (NEW - GRADING)
# -----------------------------------------

@app.post("/api/submit")
def submit_solution(request: SubmitRequest) -> SubmitResponse:
    """
    Execute code against all official test cases (sample + hidden).
    Returns grading result without exposing hidden test details.
    """
    try:
        # Load official test cases (including hidden)
        test_cases = _load_test_cases("two_sum", include_hidden=True)
        
        result = execution_service.run(
            code=request.student_code,
            test_cases=test_cases
        )
        
        # Format as submit response (no case details for hidden tests)
        return SubmitResponse(
            status=result["status"],
            passed=result["passed"],
            total=result["total"],
            runtime=result.get("runtime"),
            memory=result.get("memory")
        )
    except Exception as e:
        logger.exception(f"Error in /api/submit: {e}")
        raise HTTPException(status_code=500, detail="Submission failed")


# -----------------------------------------
# Generate hint (NEW - RAG-BASED HINTS)
# -----------------------------------------

@app.post("/api/hint")
def generate_hint_endpoint(request: HintRequest) -> HintResponse:
    """
    Generate adaptive hint using existing RAG system.
    Only called when user explicitly requests a hint.
    """
    try:
        result = generate_hint(
            problem_id=request.problem_id,
            milestone_id=request.milestone_id,
            hint_level=request.hint_level,
            student_code=request.student_code
        )
        return HintResponse(**result)
    except Exception as e:
        logger.exception(f"Error in /api/hint: {e}")
        raise HTTPException(status_code=500, detail="Hint generation failed")


# -----------------------------------------
# Analyze code (LEGACY - BACKWARD COMPATIBILITY)
# -----------------------------------------

@app.post("/analyze")
def analyze(
    request: AnalyzeRequest
):

    return analyzer_service.analyze(
        session_id=request.session_id,
        code=request.code,
        milestone=request.milestone,
    )


# -----------------------------------------
# Generate hint (LEGACY - BACKWARD COMPATIBILITY)
# -----------------------------------------

@app.post("/hint")
def hint(
    request: HintRequest
):

    return generate_hint(
        problem_id=request.problem_id,
        milestone_id=request.milestone_id,
        hint_level=request.hint_level,
        student_code=request.student_code,
    )


# -----------------------------------------
# Reset learning session
# -----------------------------------------

@app.post("/reset/{session_id}")
def reset(session_id: str):

    analyzer_service.reset(
        session_id
    )

    return {
        "success": True
    }