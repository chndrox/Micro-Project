# ThinkForge AI Backend Integration - Implementation Tasks

## Phase 1: Foundation - Test Data & Models

### 1.1 Create Two Sum Test Cases
**File:** `Micro-Project/backend/knowledge_base/two_sum/test_cases.json`
**Type:** CREATE
**Description:** Create test case repository with 5 test cases (3 sample, 2 hidden)
**Acceptance Criteria:**
- File contains valid JSON array
- 5 test cases total
- Each test case has: id, input, expected, is_sample
- Input format: "nums = [2,7,11,15]\ntarget = 9"
- Expected format: "[0,1]"
- First 3 cases have is_sample: true
- Last 2 cases have is_sample: false
**Dependencies:** None

### 1.2 Add Code Analysis Request/Response Models
**File:** `Micro-Project/backend/models/schemas.py`
**Type:** MODIFY
**Description:** Add AnalyzeCodeRequest and AnalyzeCodeResponse models for continuous code analysis
**Acceptance Criteria:**
- AnalyzeCodeRequest has: session_id, problem_id, student_code, milestone_id (default "brute_force")
- AnalyzeCodeResponse has: status, milestone, hint_available, confidence, reason
- Both inherit from BaseModel
- All fields have correct types (str, bool, float)
**Dependencies:** None

### 1.3 Add Code Execution Request/Response Models
**File:** `Micro-Project/backend/models/schemas.py`
**Type:** MODIFY
**Description:** Add RunCodeRequest and RunCodeResponse models
**Acceptance Criteria:**
- RunCodeRequest has: problem_id, student_code, test_cases (list[dict])
- RunCodeResponse has: status, passed, total, cases (list[dict]), runtime (Optional[str]), memory (Optional[str])
- Status type is string for frontend compatibility
- Optional fields use Optional[str] from typing
**Dependencies:** Task 1.2

### 1.4 Add Submit Request/Response Models
**File:** `Micro-Project/backend/models/schemas.py`
**Type:** MODIFY
**Description:** Add SubmitRequest and SubmitResponse models
**Acceptance Criteria:**
- SubmitRequest has: problem_id, student_code
- SubmitResponse has: status, passed, total, cases (Optional), runtime (Optional[str]), memory (Optional[str])
- cases field is optional to hide hidden test details
**Dependencies:** Task 1.3

### 1.5 Add Hint Response Model
**File:** `Micro-Project/backend/models/schemas.py`
**Type:** MODIFY
**Description:** Add HintResponse model for RAG hint generation
**Acceptance Criteria:**
- HintResponse has: milestone, hint_level, hint
- All fields are strings except hint_level (int)
- Matches existing RAG generate_hint() return format
**Dependencies:** Task 1.4

## Phase 2: Code Execution Service

### 2.1 Implement CodeRunner.run() Method
**File:** `Micro-Project/backend/execution/code_runner.py`
**Type:** MODIFY
**Description:** Implement main run() method to execute code against test cases
**Acceptance Criteria:**
- Method signature: run(code: str, test_cases: list[dict]) -> dict
- Loops through all test cases
- Calls _run_single_test() for each case
- Aggregates results (passed, failed, total)
- Determines overall status using status determination logic
- Returns dict matching RunCodeResponse schema
**Dependencies:** Task 1.3

### 2.2 Implement CodeRunner._run_single_test() Method
**File:** `Micro-Project/backend/execution/code_runner.py`
**Type:** MODIFY
**Description:** Implement subprocess execution for single test case
**Acceptance Criteria:**
- Method signature: _run_single_test(code: str, test_case: dict) -> dict
- Parses test input using _parse_test_input()
- Creates wrapper code with test data injection
- Writes code to temporary file
- Executes using subprocess.run() with timeout=5s, shell=False
- Captures stdout, stderr, return code
- Normalizes output using _normalize_output()
- Compares expected vs actual
- Handles subprocess.TimeoutExpired exception
- Cleans up temporary file in finally block
- Returns dict with: passed, input, expected, actual, error
**Dependencies:** Task 2.1

### 2.3 Implement CodeRunner._parse_test_input() Method
**File:** `Micro-Project/backend/execution/code_runner.py`
**Type:** MODIFY
**Description:** Parse frontend test input string format
**Acceptance Criteria:**
- Method signature: _parse_test_input(input_str: str) -> dict
- Parses "nums = [2,7,11,15]\ntarget = 9" format
- Splits by newline
- Extracts variable names and values
- Returns dict like {"nums": [2,7,11,15], "target": 9}
- Handles edge cases (negative numbers, empty arrays)
**Dependencies:** Task 2.2

### 2.4 Implement CodeRunner._normalize_output() Method
**File:** `Micro-Project/backend/execution/code_runner.py`
**Type:** MODIFY
**Description:** Strip whitespace from output for comparison
**Acceptance Criteria:**
- Method signature: _normalize_output(output: str) -> str
- Strips leading/trailing whitespace
- Returns normalized string
- Handles empty strings
**Dependencies:** Task 2.2

### 2.5 Implement Status Determination Logic
**File:** `Micro-Project/backend/execution/code_runner.py`
**Type:** MODIFY
**Description:** Add helper method to determine overall execution status
**Acceptance Criteria:**
- Returns "Time Limit Exceeded" if any case timed out
- Returns "Runtime Error" if any case has non-timeout error
- Returns "Wrong Answer" if any case failed comparison
- Returns "Accepted" if all cases passed
- Priority order matches design specification
**Dependencies:** Task 2.1

## Phase 3: API Routes - Analyzer Integration

### 3.1 Add _load_test_cases() Helper Function
**File:** `Micro-Project/backend/main.py`
**Type:** MODIFY
**Description:** Add helper to load test cases from knowledge base
**Acceptance Criteria:**
- Function signature: _load_test_cases(problem_id: str, include_hidden: bool = False) -> list[dict]
- Loads from backend/knowledge_base/{problem_id}/test_cases.json
- Returns all cases if include_hidden=True
- Returns only is_sample=True cases if include_hidden=False
- Raises FileNotFoundError if test_cases.json doesn't exist
**Dependencies:** Task 1.1

### 3.2 Import and Initialize AnalyzerService
**File:** `Micro-Project/backend/main.py`
**Type:** MODIFY
**Description:** Import AnalyzerService and create instance
**Acceptance Criteria:**
- Import: from analyzer import AnalyzerService
- Create global instance: analyzer_service = AnalyzerService()
- Instance available for /api/analyze endpoint
- No modifications to analyzer code itself
**Dependencies:** None

### 3.3 Import and Initialize CodeRunner
**File:** `Micro-Project/backend/main.py`
**Type:** MODIFY
**Description:** Import CodeRunner and create instance
**Acceptance Criteria:**
- Import: from execution import CodeRunner
- Create global instance: execution_service = CodeRunner(timeout_seconds=5.0)
- Instance available for /api/run and /api/submit endpoints
**Dependencies:** Task 2.1

### 3.4 Implement POST /api/analyze Endpoint
**File:** `Micro-Project/backend/main.py`
**Type:** MODIFY
**Description:** Add continuous code analysis endpoint using existing AnalyzerService
**Acceptance Criteria:**
- Route decorator: @app.post("/api/analyze")
- Request type: AnalyzeCodeRequest
- Response type: AnalyzeCodeResponse
- Calls analyzer_service.analyze(session_id, code, milestone)
- Transforms result to AnalyzeCodeResponse format
- Extracts: status, milestone, hint_available, confidence (from llm), reason (from llm)
- Wraps in try/except with HTTPException on error
- Logs errors using logger.exception()
- Returns HTTP 500 with "Code analysis failed" on exception
**Dependencies:** Tasks 1.2, 3.2

### 3.5 Implement POST /api/run Endpoint
**File:** `Micro-Project/backend/main.py`
**Type:** MODIFY
**Description:** Add code execution endpoint for sample test cases
**Acceptance Criteria:**
- Route decorator: @app.post("/api/run")
- Request type: RunCodeRequest
- Response type: RunCodeResponse
- Calls execution_service.run(student_code, test_cases)
- Returns RunCodeResponse from result dict
- Wraps in try/except with HTTPException on error
- Logs errors using logger.exception()
- Returns HTTP 500 with "Code execution failed" on exception
**Dependencies:** Tasks 1.3, 2.1, 3.3

### 3.6 Implement POST /api/submit Endpoint
**File:** `Micro-Project/backend/main.py`
**Type:** MODIFY
**Description:** Add solution submission endpoint using all test cases
**Acceptance Criteria:**
- Route decorator: @app.post("/api/submit")
- Request type: SubmitRequest
- Response type: SubmitResponse
- Calls _load_test_cases(problem_id, include_hidden=True)
- Calls execution_service.run(student_code, test_cases)
- Formats as SubmitResponse (no case details for hidden tests)
- Returns: status, passed, total, runtime, memory
- Wraps in try/except with HTTPException on error
- Logs errors using logger.exception()
- Returns HTTP 500 with "Submission failed" on exception
**Dependencies:** Tasks 1.4, 2.1, 3.1, 3.3

### 3.7 Implement POST /api/hint Endpoint
**File:** `Micro-Project/backend/main.py`
**Type:** MODIFY
**Description:** Add hint generation endpoint using existing RAG system
**Acceptance Criteria:**
- Route decorator: @app.post("/api/hint")
- Request type: HintRequest (existing model)
- Response type: HintResponse
- Imports: from rag import generate_hint as rag_generate_hint
- Calls rag_generate_hint(problem_id, milestone_id, hint_level, student_code)
- Returns HintResponse from result dict
- Wraps in try/except with HTTPException on error
- Logs errors using logger.exception()
- Returns HTTP 500 with "Hint generation failed" on exception
**Dependencies:** Task 1.5

### 3.8 Verify Existing POST /analyze Endpoint
**File:** `Micro-Project/backend/main.py`
**Type:** VERIFY
**Description:** Ensure legacy /analyze endpoint is preserved
**Acceptance Criteria:**
- Route decorator: @app.post("/analyze")
- Kept for backward compatibility
- Calls analyzer_service.analyze()
- No changes to existing implementation
**Dependencies:** None

### 3.9 Verify Existing POST /reset Endpoint
**File:** `Micro-Project/backend/main.py`
**Type:** VERIFY
**Description:** Ensure session reset endpoint is preserved
**Acceptance Criteria:**
- Route decorator: @app.post("/reset/{session_id}")
- Calls analyzer_service.reset(session_id)
- Returns {"success": True}
- No changes to existing implementation
**Dependencies:** None

### 3.10 Verify CORS Configuration
**File:** `Micro-Project/backend/main.py`
**Type:** VERIFY
**Description:** Ensure CORS is configured for frontend access
**Acceptance Criteria:**
- CORSMiddleware is added to app
- allow_origins includes "http://localhost:5173"
- allow_credentials=True
- allow_methods=["*"]
- allow_headers=["*"]
- No changes needed if already correct
**Dependencies:** None

## Phase 4: Frontend Integration (Optional)

### 4.1 Add analyzeCode() Function to API Service
**File:** `Micro-Project/thinkforge-tutor/src/services/api.js`
**Type:** MODIFY
**Description:** Add function to call POST /api/analyze endpoint
**Acceptance Criteria:**
- Function: analyzeCode(sessionId, problemId, studentCode, milestoneId)
- Makes POST request to /api/analyze
- Sends: {session_id, problem_id, student_code, milestone_id}
- Returns: {status, milestone, hint_available, confidence, reason}
- Uses axios or fetch
- Handles errors gracefully
**Dependencies:** Task 3.4
**Note:** Only add if not already present in frontend

### 4.2 Integrate Debounced Code Analysis in SolveProblem Component
**File:** `Micro-Project/thinkforge-tutor/src/pages/SolveProblem.jsx`
**Type:** MODIFY
**Description:** Add debounced calls to analyzeCode() when student types
**Acceptance Criteria:**
- Debounce time: 500ms-1s
- Calls analyzeCode() when code changes
- Updates hint_available state based on response
- Enables/disables "Need a Hint?" button based on hint_available
- Does NOT automatically generate hint
**Dependencies:** Task 4.1
**Note:** Only add if not already present in frontend

### 4.3 Verify generateHint() Function
**File:** `Micro-Project/thinkforge-tutor/src/services/api.js`
**Type:** VERIFY
**Description:** Ensure existing hint generation function works with new endpoint
**Acceptance Criteria:**
- Function: generateHint(problemId, milestoneId, hintLevel, studentCode)
- Makes POST request to /api/hint
- Matches HintRequest schema
- Returns hint data
**Dependencies:** Task 3.7

### 4.4 Verify runCode() Function
**File:** `Micro-Project/thinkforge-tutor/src/services/api.js`
**Type:** VERIFY
**Description:** Ensure existing code execution function works with new endpoint
**Acceptance Criteria:**
- Function: runCode(problemId, studentCode, testCases)
- Makes POST request to /api/run
- Matches RunCodeRequest schema
- Returns execution results
**Dependencies:** Task 3.5

### 4.5 Verify submitSolution() Function
**File:** `Micro-Project/thinkforge-tutor/src/services/api.js`
**Type:** VERIFY
**Description:** Ensure existing submission function works with new endpoint
**Acceptance Criteria:**
- Function: submitSolution(problemId, studentCode)
- Makes POST request to /api/submit
- Matches SubmitRequest schema
- Returns submission results
**Dependencies:** Task 3.6

## Phase 5: Testing - Unit Tests

### 5.1 Test CodeRunner with Correct Solution
**File:** `Micro-Project/backend/tests/test_execution_service.py`
**Type:** CREATE
**Description:** Unit test for correct solution execution
**Acceptance Criteria:**
- Test runs correct Two Sum solution
- Verifies status = "Accepted"
- Verifies passed = total
- Verifies all cases have passed=True
- No errors in any case
**Dependencies:** Task 2.1

### 5.2 Test CodeRunner with Wrong Solution
**File:** `Micro-Project/backend/tests/test_execution_service.py`
**Type:** CREATE
**Description:** Unit test for incorrect solution execution
**Acceptance Criteria:**
- Test runs incorrect Two Sum solution
- Verifies status = "Wrong Answer"
- Verifies passed < total
- Verifies at least one case has passed=False
- Actual output differs from expected
**Dependencies:** Task 2.1

### 5.3 Test CodeRunner with Timeout
**File:** `Micro-Project/backend/tests/test_execution_service.py`
**Type:** CREATE
**Description:** Unit test for timeout enforcement
**Acceptance Criteria:**
- Test runs infinite loop code
- Verifies status = "Time Limit Exceeded"
- Verifies error = "Time Limit Exceeded"
- Execution completes within reasonable time (< 10s)
**Dependencies:** Task 2.2

### 5.4 Test CodeRunner with Runtime Error
**File:** `Micro-Project/backend/tests/test_execution_service.py`
**Type:** CREATE
**Description:** Unit test for code that raises exception
**Acceptance Criteria:**
- Test runs code that raises exception
- Verifies status = "Runtime Error"
- Verifies error field contains exception message
- passed = 0
**Dependencies:** Task 2.2

### 5.5 Test Output Normalization
**File:** `Micro-Project/backend/tests/test_execution_service.py`
**Type:** CREATE
**Description:** Unit test for whitespace normalization
**Acceptance Criteria:**
- Test with output containing leading/trailing whitespace
- Verifies normalized outputs match
- Test passes despite whitespace differences
**Dependencies:** Task 2.4

### 5.6 Test Test Case Loading
**File:** `Micro-Project/backend/tests/test_data_loading.py`
**Type:** CREATE
**Description:** Unit test for _load_test_cases() helper
**Acceptance Criteria:**
- Test loading with include_hidden=False returns only sample cases
- Test loading with include_hidden=True returns all cases
- Verifies correct number of cases returned
- Verifies is_sample field filtering works
**Dependencies:** Task 3.1

## Phase 6: Testing - API Integration Tests

### 6.1 Test POST /api/analyze with Empty Code
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for analyze endpoint with empty code
**Acceptance Criteria:**
- Send POST /api/analyze with empty student_code
- Verify status = "WAITING"
- Verify hint_available = false
- Verify HTTP 200 response
**Dependencies:** Task 3.4

### 6.2 Test POST /api/analyze with Valid Code
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for analyze endpoint with valid code
**Acceptance Criteria:**
- Send POST /api/analyze with valid Two Sum solution
- Verify response contains: status, milestone, hint_available, confidence, reason
- Verify HTTP 200 response
- Verify AnalyzerService was called
**Dependencies:** Task 3.4

### 6.3 Test POST /api/analyze with Syntax Error
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for analyze endpoint with syntax error
**Acceptance Criteria:**
- Send POST /api/analyze with code containing syntax error
- Verify status indicates syntax issue
- Verify hint_available = false (don't hint on syntax errors)
- Verify HTTP 200 response
**Dependencies:** Task 3.4

### 6.4 Test POST /api/run with Sample Cases
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for run endpoint
**Acceptance Criteria:**
- Send POST /api/run with correct solution and sample cases
- Verify status = "Accepted"
- Verify passed = total
- Verify cases array contains results
- Verify HTTP 200 response
**Dependencies:** Task 3.5

### 6.5 Test POST /api/run with Wrong Answer
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for run endpoint with failing solution
**Acceptance Criteria:**
- Send POST /api/run with incorrect solution
- Verify status = "Wrong Answer"
- Verify passed < total
- Verify cases array shows which tests failed
- Verify HTTP 200 response (NOT 4xx/5xx)
**Dependencies:** Task 3.5

### 6.6 Test POST /api/submit with All Test Cases
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for submit endpoint
**Acceptance Criteria:**
- Send POST /api/submit with correct solution
- Verify status = "Accepted"
- Verify passed = 5 (all test cases)
- Verify total = 5
- Verify HTTP 200 response
**Dependencies:** Task 3.6

### 6.7 Test POST /api/submit Hides Hidden Test Details
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Verify hidden test cases are not exposed in response
**Acceptance Criteria:**
- Send POST /api/submit with failing solution
- Verify response contains passed, total, status
- Verify response does NOT contain detailed case information
- Hidden test inputs remain hidden
**Dependencies:** Task 3.6

### 6.8 Test POST /api/hint Generation
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for hint endpoint using RAG
**Acceptance Criteria:**
- Send POST /api/hint with valid parameters
- Verify response contains: milestone, hint_level, hint
- Verify hint is non-empty string
- Verify HTTP 200 response
- Verify RAG generate_hint() was called
**Dependencies:** Task 3.7

### 6.9 Test POST /api/hint with Invalid Milestone
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for hint endpoint error handling
**Acceptance Criteria:**
- Send POST /api/hint with invalid milestone_id
- Verify appropriate error response
- Verify HTTP 404 or 400 response
**Dependencies:** Task 3.7

### 6.10 Test Error Handling - Invalid Request Schema
**File:** `Micro-Project/backend/tests/test_api_integration.py`
**Type:** CREATE
**Description:** Integration test for Pydantic validation errors
**Acceptance Criteria:**
- Send malformed request to any endpoint
- Verify HTTP 422 Unprocessable Entity response
- Verify error message indicates validation failure
**Dependencies:** Tasks 3.4, 3.5, 3.6, 3.7

## Phase 7: End-to-End Testing

### 7.1 Test Complete Student Workflow - Success Path
**File:** Manual testing checklist
**Type:** MANUAL
**Description:** End-to-end test of successful problem solving
**Acceptance Criteria:**
1. Start frontend and backend servers
2. Navigate to Two Sum problem page
3. Type incomplete code → Verify no hint button appears
4. Type progressing code → Verify /api/analyze called, no hint shown
5. Type stuck code → Verify hint button appears (hint_available=true)
6. Click "Need a Hint?" → Verify POST /api/hint called, hint displays
7. Complete correct solution
8. Click "Run" → Verify POST /api/run called, all tests pass
9. Click "Submit" → Verify POST /api/submit called, solution accepted
10. Verify congratulations message displays
**Dependencies:** All previous tasks

### 7.2 Test Complete Student Workflow - Failure Path
**File:** Manual testing checklist
**Type:** MANUAL
**Description:** End-to-end test of failing solution
**Acceptance Criteria:**
1. Start frontend and backend servers
2. Navigate to Two Sum problem page
3. Write incorrect solution
4. Click "Run" → Verify "Wrong Answer" status
5. Verify test case details show which tests failed
6. Verify expected vs actual output displayed
7. Fix one test case
8. Click "Run" → Verify partial pass (some tests pass)
9. Click "Submit" with wrong solution → Verify rejection message
10. Verify failure count displayed
**Dependencies:** All previous tasks

### 7.3 Test Analyzer + Groq Integration
**File:** Manual testing checklist
**Type:** MANUAL
**Description:** Verify analyzer uses Groq LLM when appropriate
**Acceptance Criteria:**
1. Start backend with valid GROQ_API_KEY in .env
2. Send code to POST /api/analyze
3. Verify AnalyzerService → ASTAnalyzer → LLMAnalyzer → Groq
4. Verify Groq response used for progress interpretation
5. Verify confidence and reason in response
6. Test with invalid GROQ_API_KEY
7. Verify fallback to AST-only analysis works
8. Verify system doesn't crash on Groq failure
**Dependencies:** Task 3.4

### 7.4 Test RAG Hint Generation Integration
**File:** Manual testing checklist
**Type:** MANUAL
**Description:** Verify RAG system generates progressive hints
**Acceptance Criteria:**
1. Call POST /api/hint with milestone="brute_force", hint_level=1
2. Verify hint retrieved from knowledge base
3. Verify Groq used to phrase hint naturally
4. Verify hint is relevant to brute_force milestone
5. Call again with hint_level=2
6. Verify hint progression (more detailed)
7. Verify different milestones produce different hints
**Dependencies:** Task 3.7

### 7.5 Test Timeout Enforcement
**File:** Manual testing checklist
**Type:** MANUAL
**Description:** Verify infinite loops are caught
**Acceptance Criteria:**
1. Submit code with infinite loop to POST /api/run
2. Verify execution terminates within ~5 seconds
3. Verify status = "Time Limit Exceeded"
4. Verify error message indicates timeout
5. Verify server remains responsive after timeout
**Dependencies:** Task 3.5

### 7.6 Test Subprocess Isolation
**File:** Manual testing checklist
**Type:** MANUAL
**Description:** Verify subprocess isolation prevents system issues
**Acceptance Criteria:**
1. Submit code that attempts file system access
2. Verify code runs in isolated subprocess
3. Verify temporary files are cleaned up
4. Submit code that attempts network access
5. Verify execution completes without affecting server
6. Note: This is prototype-level isolation, not production-secure
**Dependencies:** Task 2.2

### 7.7 Test CORS Configuration
**File:** Manual testing checklist
**Type:** MANUAL
**Description:** Verify frontend can access backend APIs
**Acceptance Criteria:**
1. Start backend on localhost:8000
2. Start frontend on localhost:5173
3. Make API call from frontend to backend
4. Verify no CORS errors in browser console
5. Verify preflight OPTIONS requests succeed
6. Verify credentials are properly sent
**Dependencies:** Task 3.10

### 7.8 Performance Test - Multiple Sequential Requests
**File:** Manual testing checklist
**Type:** MANUAL
**Description:** Verify system handles multiple requests
**Acceptance Criteria:**
1. Send 10 sequential POST /api/analyze requests
2. Verify all complete successfully
3. Send 10 sequential POST /api/run requests
4. Verify all complete successfully
5. Verify session state maintained correctly
6. Verify no memory leaks or performance degradation
**Dependencies:** All previous tasks

## Summary

**Total Tasks:** 78
- Phase 1 (Foundation): 5 tasks
- Phase 2 (Execution Service): 5 tasks
- Phase 3 (API Routes): 10 tasks
- Phase 4 (Frontend Integration): 5 tasks
- Phase 5 (Unit Tests): 6 tasks
- Phase 6 (Integration Tests): 10 tasks
- Phase 7 (End-to-End Tests): 8 manual tests

**Critical Path:**
1. Test Data (1.1) → Models (1.2-1.5) → Execution Service (2.1-2.5) → API Routes (3.1-3.7) → Testing (5.1-7.8)

**Key Integration Points:**
- Task 3.4: Analyzer integration via /api/analyze
- Task 3.7: RAG integration via /api/hint
- Task 3.5: Code execution via /api/run
- Task 3.6: Submission via /api/submit

**Files to Create:**
- `Micro-Project/backend/knowledge_base/two_sum/test_cases.json`
- `Micro-Project/backend/tests/test_execution_service.py`
- `Micro-Project/backend/tests/test_data_loading.py`
- `Micro-Project/backend/tests/test_api_integration.py`

**Files to Modify:**
- `Micro-Project/backend/models/schemas.py`
- `Micro-Project/backend/execution/code_runner.py`
- `Micro-Project/backend/main.py`
- `Micro-Project/thinkforge-tutor/src/services/api.js` (optional)
- `Micro-Project/thinkforge-tutor/src/pages/SolveProblem.jsx` (optional)

**Files to Keep Unchanged:**
- All files in `Micro-Project/backend/analyzer/`
- All files in `Micro-Project/backend/rag/`
- All existing knowledge base files except test_cases.json
