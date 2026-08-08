import axios from 'axios'

// FastAPI + RAG backend.

const BASE_URL = "http://127.0.0.1:8000";
const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Analyze the student's code for progress and determine if they are stuck.
 * The backend uses AST analysis + Groq LLM to determine if a hint should be available.
 *
 * POST /api/analyze
 * { session_id, problem_id, student_code, milestone_id }
 * -> { status, milestone, hint_available, confidence, reason }
 */
export async function analyzeCode({ sessionId, problemId, studentCode, milestoneId }) {
  const { data } = await client.post('/api/analyze', {
    session_id: sessionId,
    problem_id: problemId,
    student_code: studentCode,
    milestone_id: milestoneId,
  })
  return data
}

/**
 * Ask the RAG pipeline for the next hint.
 * Sends the student's current code and hint progress; the backend decides
 * everything about the hint content — nothing is generated on the client.
 *
 * POST /api/hint
 * { problem_id, milestone_id, hint_level, student_code }
 * -> { milestone, hint_level, hint }
 */
export async function generateHint({ problemId, milestoneId, hintLevel, studentCode }) {
  const { data } = await client.post('/api/hint', {
    problem_id: problemId,
    milestone_id: milestoneId,
    hint_level: hintLevel,
    student_code: studentCode,
  })
  return data
}

/**
 * Run the student's code against the sample test cases.
 *
 * POST /api/run
 * { problem_id, student_code, test_cases }
 */
export async function runCode({ problemId, studentCode, testCases }) {
  const { data } = await client.post('/api/run', {
    problem_id: problemId,
    student_code: studentCode,
    test_cases: testCases,
  })
  return data
}

/**
 * Submit the final solution for grading.
 *
 * POST /api/submit
 * { problem_id, student_code }
 */
export async function submitSolution({ problemId, studentCode }) {
  const { data } = await client.post('/api/submit', {
    problem_id: problemId,
    student_code: studentCode,
  })
  return data
}

export default client
