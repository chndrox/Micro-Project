import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play } from 'lucide-react'

const SAMPLE_CASES = [
  { id: 1, input: 'nums = [2,7,11,15]\ntarget = 9', expected: '[0,1]' },
  { id: 2, input: 'nums = [3,2,4]\ntarget = 6', expected: '[1,2]' },
  { id: 3, input: 'nums = [3,3]\ntarget = 6', expected: '[0,1]' },
]

export { SAMPLE_CASES }

export default function TestCases({ onRunOne, runningId }) {
  const [activeId, setActiveId] = useState(1)
  const active = SAMPLE_CASES.find((c) => c.id === activeId)

  return (
    <div className="panel flex h-full flex-col overflow-hidden">
      <div className="border-b border-borderc px-4 py-2.5">
        <span className="text-sm font-semibold text-slate-200">Test Cases</span>
      </div>

      <div className="flex gap-1 border-b border-borderc px-3 pt-2">
        {SAMPLE_CASES.map((c) => (
          <button
            key={c.id}
            onClick={() => setActiveId(c.id)}
            className={`relative px-3 pb-2 text-sm font-medium transition-colors ${
              activeId === c.id ? 'text-primary' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            Case {c.id}
            {activeId === c.id && (
              <motion.span layoutId="testcase-tab" className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-primary" />
            )}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">Input:</p>
        <pre className="mb-4 whitespace-pre-wrap rounded-lg border border-borderc bg-card-alt p-3 font-mono text-[13px] text-slate-300">
          {active.input}
        </pre>

        <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">Expected Output:</p>
        <pre className="mb-4 rounded-lg border border-borderc bg-card-alt p-3 font-mono text-[13px] text-slate-300">
          {active.expected}
        </pre>

        <button
          onClick={() => onRunOne(active)}
          disabled={runningId === active.id}
          className="btn-press flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-semibold text-white hover:bg-primary-hover disabled:opacity-60"
        >
          <Play size={12} /> {runningId === active.id ? 'Running...' : 'Run'}
        </button>
      </div>
    </div>
  )
}
