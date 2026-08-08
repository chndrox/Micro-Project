import { useCallback, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Lightbulb, Sparkles } from 'lucide-react'

import Navbar from '../components/Navbar'
import ProblemPanel from '../components/ProblemPanel'
import Editor, { INITIAL_CODE } from '../components/Editor'
import TestCases, { SAMPLE_CASES } from '../components/TestCases'
import OutputPanel from '../components/OutputPanel'
import BottomBar from '../components/BottomBar'
import HintCard from '../components/HintCard'

import * as api from '../services/api'

const PROBLEM_ID = 'two_sum'
const ANALYSIS_DEBOUNCE_MS = 1000 // Debounce continuous analysis to avoid hammering the backend

export default function SolveProblem() {
  const [theme, setTheme] = useState('dark')
  const [code, setCode] = useState(INITIAL_CODE)

  const [result, setResult] = useState(null)
  const [runningAction, setRunningAction] = useState(null)
  const [runningCaseId, setRunningCaseId] = useState(null)

  // Continuous analysis state
  const [analysis, setAnalysis] = useState(null) // { status, milestone, hint_available, confidence, reason }
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const analysisDebouncerRef = useRef(null)

  // Hint progression is owned by the frontend, but the backend decides content.
  const [milestone, setMilestone] = useState('brute_force')
  const [hintLevel, setHintLevel] = useState(0)
  const [hintCard, setHintCard] = useState(null) // { hint, error, loading }

  // Generate a session ID (in a real app, this would come from authentication)
  const sessionIdRef = useRef(`session_${Date.now()}`)
  const sessionId = sessionIdRef.current

  // --- Theme ---------------------------------------------------------
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])
  const toggleTheme = () => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))

  // --- Continuous Analysis with Debounce ---------------------------------
  const performAnalysis = useCallback(async (codeToAnalyze) => {
    setIsAnalyzing(true)
    try {
      const data = await api.analyzeCode({
        sessionId,
        problemId: PROBLEM_ID,
        studentCode: codeToAnalyze,
        milestoneId: milestone,
      })
      setAnalysis(data)
      // Update milestone if backend detected a new one
      if (data.milestone) {
        setMilestone(data.milestone)
      }
    } catch (error) {
      // Swallow analysis errors — don't disrupt UX
      console.warn('Analysis failed:', error.message)
    } finally {
      setIsAnalyzing(false)
    }
  }, [sessionId, milestone])

  // Debounced analysis on code change
  const handleCodeChange = useCallback((value) => {
    setCode(value)

    // Clear previous debounce timer
    if (analysisDebouncerRef.current) {
      clearTimeout(analysisDebouncerRef.current)
    }

    // Set new debounce timer
    analysisDebouncerRef.current = setTimeout(() => {
      performAnalysis(value)
    }, ANALYSIS_DEBOUNCE_MS)
  }, [performAnalysis])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (analysisDebouncerRef.current) {
        clearTimeout(analysisDebouncerRef.current)
      }
    }
  }, [])

  // --- Hint request (manual only — never automatic) -------------------
  const requestHint = useCallback(async () => {
    const nextLevel = hintLevel + 1
    setRunningAction('hint')
    setHintCard({ hintLevel: nextLevel, loading: true })
    try {
      const data = await api.generateHint({
        problemId: PROBLEM_ID,
        milestoneId: milestone,
        hintLevel: nextLevel,
        studentCode: code,
      })
      setMilestone(data.milestone ?? milestone)
      setHintLevel(data.hint_level ?? nextLevel)
      setHintCard({ hintLevel: data.hint_level ?? nextLevel, hint: data.hint, loading: false })
    } catch (error) {
      console.error('Hint generation failed:', error.message)
      setHintCard({ hintLevel: nextLevel, error: true, loading: false })
    } finally {
      setRunningAction(null)
    }
  }, [code, milestone, hintLevel])

  // --- Run / Submit -----------------------------------------------------
  const handleRun = useCallback(async () => {
    setRunningAction('run')
    try {
      const data = await api.runCode({ problemId: PROBLEM_ID, studentCode: code, testCases: SAMPLE_CASES })
      setResult(data)
    } catch (error) {
      console.error('Run failed:', error.message)
      setResult({ status: 'Runtime Error', passed: 0, total: SAMPLE_CASES.length, cases: [] })
    } finally {
      setRunningAction(null)
    }
  }, [code])

  const handleRunOne = async (testCase) => {
    setRunningCaseId(testCase.id)
    try {
      await api.runCode({ problemId: PROBLEM_ID, studentCode: code, testCases: [testCase] })
    } catch (error) {
      console.warn('Single test run failed:', error.message)
    } finally {
      setRunningCaseId(null)
    }
  }

  const handleSubmit = useCallback(async () => {
    setRunningAction('submit')
    try {
      const data = await api.submitSolution({ problemId: PROBLEM_ID, studentCode: code })
      setResult(data)
    } catch (error) {
      console.error('Submit failed:', error.message)
      setResult({ status: 'Runtime Error', passed: 0, total: SAMPLE_CASES.length, cases: [] })
    } finally {
      setRunningAction(null)
    }
  }, [code])

  // --- Keyboard shortcuts ------------------------------------------------
  useEffect(() => {
    function handleKeyDown(e) {
      const cmd = e.ctrlKey || e.metaKey
      if (cmd && e.key === 'Enter' && e.shiftKey) {
        e.preventDefault()
        handleSubmit()
      } else if (cmd && e.key === 'Enter') {
        e.preventDefault()
        handleRun()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleRun, handleSubmit])

  return (
    <div className="flex h-screen flex-col bg-bg">
      <Navbar theme={theme} onToggleTheme={toggleTheme} />

      <main className="grid min-h-0 flex-1 grid-cols-1 gap-4 overflow-y-auto p-4 lg:grid-cols-[38%_1fr] lg:overflow-hidden">
        {/* Left: Problem + Test Cases */}
        <div className="flex min-h-0 flex-col gap-4 lg:overflow-hidden">
          <div className="h-[420px] lg:h-[62%] lg:min-h-0">
            <ProblemPanel />
          </div>
          <div className="h-[320px] lg:h-[38%] lg:min-h-0">
            <TestCases onRunOne={handleRunOne} runningId={runningCaseId} />
          </div>
        </div>

        {/* Right: Editor + Output, with the hint popup anchored to this column */}
        <div className="relative flex min-h-0 flex-col gap-4 lg:overflow-hidden">
          <div className="h-[420px] lg:h-[62%] lg:min-h-0">
            <Editor code={code} onChange={handleCodeChange} />
          </div>
          <div className="h-[320px] lg:h-[38%] lg:min-h-0">
            <OutputPanel result={result} running={runningAction === 'run' || runningAction === 'submit'} onClear={() => setResult(null)} />
          </div>

          {/* Floating hint card (shown when hint is available or requested) */}
          <div className="pointer-events-none absolute inset-x-0 top-0 flex justify-end px-1 lg:top-2 lg:right-2 lg:px-0">
            <div className="pointer-events-auto flex flex-col items-end gap-3">
              <AnimatePresence>
                {hintCard && (
                  <HintCard
                    hintLevel={hintCard.hintLevel}
                    hint={hintCard.hint}
                    error={hintCard.error}
                    loading={hintCard.loading}
                    onDismiss={() => setHintCard(null)}
                  />
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </main>

      <BottomBar 
        onRun={handleRun} 
        onSubmit={handleSubmit} 
        onHint={requestHint} 
        runningAction={runningAction}
        hintAvailable={analysis?.hint_available ?? false}
      />
    </div>
  )
}
