# Requirements Document

## Introduction

This document specifies the requirements for completing the ThinkForge AI backend integration. The system is a coding tutor with a React frontend and FastAPI backend. The analyzer service and RAG hint generation system are complete and working. This integration adds the missing problem service, code execution service, and API routes needed for the frontend to function as a complete coding tutor.

## Glossary

- **Backend**: The FastAPI server providing REST endpoints for problem data, code execution, analysis, and hint generation
- **Frontend**: The React application that students interact with to solve coding problems
- **Problem_Service**: Backend component responsible for loading and serving problem metadata, descriptions, and test cases
- **Execution_Service**: Backend component that runs student code in isolated subprocesses against test cases
- **Analyzer_Service**: Existing backend component that performs AST and LLM analysis on student code (already implemented)
- **RAG_Service**: Existing backend component that generates adaptive hints using retrieval-augmented generation (already implemented)
- **Test_Case**: A data structure containing input values, expected output, and optional metadata for validating code correctness
- **Subprocess**: An isolated operating system process used to execute untrusted student code safely
- **Round_Trip_Property**: A correctness property asserting that serializing then deserializing produces equivalent data

## Requirements

### Requirement 1: Problem Metadata Service

**User Story:** As a student, I want to view problem details including description, examples, and constraints, so that I understand what I need to solve.

#### Acceptance Criteria

1. THE Problem_Service SHALL load problem metadata from the knowledge base directory structure
2. WHEN the problem metadata file is malformed, THE Problem_Service SHALL raise a descriptive error with the file path and parsing issue
3. THE Problem_Service SHALL parse and validate all required fields: id, title, difficulty, description, input_format, output_format, constraints, examples, starter_code
4. WHERE a problem file is missing required fields, THE Problem_Service SHALL return an error indicating which fields are missing
5. THE Problem_Service SHALL cache loaded problem data to avoid redundant file reads

### Requirement 2: Problem List API

**User Story:** As a student, I want to see all available problems with their difficulty levels, so that I can choose what to work on.

#### Acceptance Criteria

1. THE Backend SHALL expose GET /api/problems endpoint
2. WHEN a GET request is received at /api/problems, THE Backend SHALL return a JSON list of all available problems
3. THE Backend SHALL include id, title, and difficulty for each problem in the list response
4. THE Backend SHALL return HTTP 200 status for successful problem list retrieval
5. IF the knowledge base directory is empty or inaccessible, THEN THE Backend SHALL return HTTP 500 with an error message

### Requirement 3: Problem Detail API

**User Story:** As a student, I want to fetch full problem details including examples and starter code, so that I can begin solving the problem.

#### Acceptance Criteria

1. THE Backend SHALL expose GET /api/problems/{problem_id} endpoint
2. WHEN a GET request is received at /api/problems/{problem_id}, THE Backend SHALL return complete problem details as JSON
3. THE Backend SHALL include id, title, difficulty, description, input_format, output_format, constraints, examples, and starter_code in the response
4. IF the problem_id does not exist, THEN THE Backend SHALL return HTTP 404 with a "Problem not found" message
5. THE Backend SHALL return HTTP 200 status for successful problem detail retrieval

### Requirement 4: Test Case Repository

**User Story:** As a developer, I want official test cases stored separately from problem metadata, so that test data is maintainable and extensible.

#### Acceptance Criteria

1. THE Backend SHALL store official test cases in a dedicated test case data structure or file per problem
2. THE Backend SHALL include sample test cases (visible to students) and hidden test cases (for final submission)
3. WHEN test cases are loaded, THE Backend SHALL validate that each case contains input and expected_output fields
4. THE Backend SHALL support test case metadata including case_id, description, is_sample, and timeout_ms
5. WHERE test case data is corrupted or missing required fields, THE Backend SHALL raise a descriptive validation error

### Requirement 5: Code Execution Sandbox

**User Story:** As a system administrator, I want student code executed in isolated subprocesses, so that malicious or buggy code cannot harm the server.

#### Acceptance Criteria

1. THE Execution_Service SHALL execute student code using subprocess isolation
2. THE Execution_Service SHALL enforce a configurable timeout for each execution (default 5 seconds)
3. WHEN the subprocess exceeds the timeout, THE Execution_Service SHALL terminate the process and return a timeout error
4. THE Execution_Service SHALL capture stdout, stderr, and return code from the subprocess
5. THE Execution_Service SHALL prevent the student code from executing shell commands, file operations, or network access through subprocess configuration
6. IF the subprocess terminates with a non-zero return code, THEN THE Execution_Service SHALL classify the result as a runtime error

### Requirement 6: Code Runner with Test Case Execution

**User Story:** As a student, I want to run my code against test cases and see detailed results, so that I can verify my solution works correctly.

#### Acceptance Criteria

1. WHEN student code is executed against a test case, THE Execution_Service SHALL inject the test case input into the code execution environment
2. THE Execution_Service SHALL capture the actual output produced by the student code
3. THE Execution_Service SHALL normalize both expected and actual outputs by stripping leading and trailing whitespace
4. THE Execution_Service SHALL compare normalized outputs for equality
5. THE Execution_Service SHALL record execution time in milliseconds for each test case
6. THE Execution_Service SHALL return a result object containing: passed (boolean), input, expected, actual, error (if any), and execution_time_ms

### Requirement 7: Run Code API

**User Story:** As a student, I want to test my code against sample cases before submitting, so that I can iterate on my solution with fast feedback.

#### Acceptance Criteria

1. THE Backend SHALL expose POST /api/run endpoint
2. WHEN a POST request is received at /api/run, THE Backend SHALL accept problem_id, student_code, and test_cases in the request body
3. THE Backend SHALL execute the student code against each provided test case using the Execution_Service
4. THE Backend SHALL return a JSON response with: status, passed (count), failed (count), total (count), cases (array of case results), and execution_time_ms
5. WHERE status is "Accepted", all test cases SHALL have passed
6. WHERE status is "Wrong Answer", at least one test case SHALL have failed with mismatched output
7. WHERE status is "Runtime Error", at least one test case SHALL have raised an exception or crashed
8. WHERE status is "Time Limit Exceeded", at least one test case SHALL have exceeded the timeout
9. THE Backend SHALL return HTTP 200 status for both successful and failed code execution (errors in student code are not HTTP errors)

### Requirement 8: Submit Solution API

**User Story:** As a student, I want to submit my final solution for grading against all official test cases, so that I can verify my solution is fully correct.

#### Acceptance Criteria

1. THE Backend SHALL expose POST /api/submit endpoint
2. WHEN a POST request is received at /api/submit, THE Backend SHALL accept problem_id and student_code in the request body
3. THE Backend SHALL load all official test cases for the specified problem_id
4. THE Backend SHALL execute the student code against all official test cases including hidden cases
5. THE Backend SHALL return a JSON response with: accepted (boolean), passed (count), failed (count), total (count), execution_time_ms, and message
6. WHERE accepted is true, THE Backend SHALL set message to "All test cases passed!"
7. WHERE accepted is false, THE Backend SHALL set message indicating which test case failed (e.g., "Failed on test case 3")
8. THE Backend SHALL return HTTP 200 status for both accepted and rejected submissions

### Requirement 9: API Route Alignment

**User Story:** As a frontend developer, I want all API routes to use the /api prefix consistently, so that the frontend can communicate with the backend without route mismatches.

#### Acceptance Criteria

1. THE Backend SHALL expose the hint generation endpoint at POST /api/hint (not /hint)
2. THE Backend SHALL preserve the existing /analyze endpoint functionality while maintaining backward compatibility
3. THE Backend SHALL accept HintRequest schema at /api/hint with fields: session_id, problem_id, milestone_id, hint_level, student_code
4. THE Backend SHALL return hint response with fields: milestone, hint_level, hint
5. WHERE an existing client calls /hint without the /api prefix, THE Backend SHALL return HTTP 404

### Requirement 10: Request and Response Schema Validation

**User Story:** As a backend developer, I want request and response schemas strictly validated, so that API contracts are enforced and errors are caught early.

#### Acceptance Criteria

1. THE Backend SHALL define RunCodeRequest schema with fields: problem_id (string), student_code (string), test_cases (list)
2. THE Backend SHALL define RunCodeResponse schema with fields: status (string), passed (int), failed (int), total (int), cases (list), execution_time_ms (float)
3. THE Backend SHALL define SubmitRequest schema with fields: problem_id (string), student_code (string)
4. THE Backend SHALL define SubmitResponse schema with fields: accepted (boolean), passed (int), failed (int), total (int), execution_time_ms (float), message (string)
5. THE Backend SHALL define ProblemListResponse schema containing a list of objects with fields: id (string), title (string), difficulty (string)
6. THE Backend SHALL define ProblemDetailResponse schema with fields: id, title, difficulty, description, input_format, output_format, constraints (list), examples (list), starter_code
7. WHEN a request does not conform to the expected schema, THE Backend SHALL return HTTP 422 with validation error details

### Requirement 11: Error Handling and Logging

**User Story:** As a system operator, I want errors logged with sufficient context, so that I can diagnose issues quickly.

#### Acceptance Criteria

1. WHEN a subprocess execution fails, THE Backend SHALL log the problem_id, student_code length, error message, and stack trace
2. WHEN a problem file fails to load, THE Backend SHALL log the file path and parsing error
3. WHEN a test case validation fails, THE Backend SHALL log which fields are invalid and their values
4. THE Backend SHALL return user-friendly error messages in API responses without exposing internal implementation details
5. THE Backend SHALL distinguish between client errors (HTTP 4xx) and server errors (HTTP 5xx)

### Requirement 12: Code Execution Output Parser

**User Story:** As a student, I want my code output compared correctly even with trailing newlines or extra spaces, so that formatting differences don't cause false failures.

#### Acceptance Criteria

1. THE Execution_Service SHALL implement an output normalization function
2. THE Execution_Service SHALL strip leading and trailing whitespace from both expected and actual outputs
3. THE Execution_Service SHALL compare normalized outputs using string equality
4. WHERE outputs differ only in whitespace, THE Execution_Service SHALL mark the test case as passed
5. WHERE outputs differ in content after normalization, THE Execution_Service SHALL mark the test case as failed and include both normalized outputs in the result

### Requirement 13: Test Case for Two Sum Problem

**User Story:** As a developer, I want official test cases for Two Sum defined and loadable, so that students can validate their solutions against known correct outputs.

#### Acceptance Criteria

1. THE Backend SHALL include test cases for Two Sum problem: [2,7,11,15] target 9 expecting [0,1]
2. THE Backend SHALL include test case: [3,2,4] target 6 expecting [1,2]
3. THE Backend SHALL include test case: [3,3] target 6 expecting [0,1]
4. THE Backend SHALL mark the first two test cases as sample cases (visible to students)
5. THE Backend SHALL mark the third test case as a hidden case (only run on submit)
6. THE Backend SHALL format test case inputs and outputs as JSON-compatible structures

### Requirement 14: Pretty Printer and Parser for Test Cases

**User Story:** As a developer, I want test cases serialized and deserialized consistently, so that test data integrity is maintained.

#### Acceptance Criteria

1. THE Backend SHALL parse test case JSON files into TestCase data structures
2. THE Backend SHALL serialize TestCase data structures back into JSON format
3. WHERE a TestCase is parsed from JSON, THE Pretty_Printer SHALL format it back into valid JSON
4. FOR ALL valid TestCase objects, parsing then printing then parsing SHALL produce an equivalent TestCase object (round-trip property)
5. WHEN test case JSON is malformed, THE Backend SHALL raise a parsing error with line and column information

### Requirement 15: Integration Testing Support

**User Story:** As a developer, I want to run integration tests that verify end-to-end API behavior, so that I can ensure the frontend and backend work together correctly.

#### Acceptance Criteria

1. THE Backend SHALL provide a test fixture that starts a test server with all routes registered
2. THE Backend SHALL reset in-memory state between integration tests
3. THE Backend SHALL support testing with mock LLM responses to avoid external API dependencies during tests
4. THE Backend SHALL validate that /api/run returns expected response structure when given valid sample code
5. THE Backend SHALL validate that /api/submit correctly distinguishes passing and failing solutions
