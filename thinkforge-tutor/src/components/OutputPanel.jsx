import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle2, XCircle, Trash2, Loader2 } from 'lucide-react'

function Spinner({ size = 12 }) {
  return (
    <motion.span
      className="inline-flex"
      animate={{ rotate: 360 }}
      transition={{ repeat: Infinity, duration: 0.8, ease: 'linear' }}
    >
      <Loader2 size={size} />
    </motion.span>
  )
}

const STATUS_STYLES = {
  Accepted: 'text-success bg-success/10 border-success/30',
  'Wrong Answer': 'text-rose-400 bg-rose-500/10 border-rose-500/30',
  'Runtime Error': 'text-rose-400 bg-rose-500/10 border-rose-500/30',
  Running: 'text-primary bg-primary/10 border-primary/30',
  Idle: 'text-slate-400 bg-card-alt border-borderc',
}

export default function OutputPanel({ result, running, onClear }) {
  const status = running ? 'Running' : result?.status || 'Idle'

  return (
    <div className="panel flex h-full flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-borderc px-4 py-2.5">
        <span className="text-sm font-semibold text-slate-200">Output</span>
        <button
          onClick={onClear}
          className="btn-press flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium text-slate-500 hover:bg-card-alt hover:text-slate-300"
          aria-label="Clear output"
        >
          <Trash2 size={13} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <span className={`flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs font-semibold ${STATUS_STYLES[status]}`}>
            {running && <Spinner size={11} />}
            {status}
          </span>
          {result && !running && (
            <>
              <span className="text-xs font-medium text-slate-400">
                <b className={result.passed === result.total ? 'text-success' : 'text-rose-400'}>
                  {result.passed} / {result.total} Passed
                </b>
              </span>
              {result.runtime && <span className="text-xs text-slate-500">Runtime: {result.runtime}</span>}
              {result.memory && <span className="text-xs text-slate-500">Memory: {result.memory}</span>}
            </>
          )}
        </div>

        <AnimatePresence initial={false}>
          {result?.cases?.length ? (
            <motion.div className="space-y-2">
              {result.cases.map((c, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex items-center gap-2 rounded-lg border border-borderc bg-card-alt px-3 py-2 text-sm"
                >
                  {c.passed ? (
                    <CheckCircle2 size={15} className="shrink-0 text-success" />
                  ) : (
                    <XCircle size={15} className="shrink-0 text-rose-400" />
                  )}
                  <span className="text-slate-300">Test Case {i + 1}:</span>
                  <span className={c.passed ? 'font-semibold text-success' : 'font-semibold text-rose-400'}>
                    {c.passed ? 'Passed' : 'Failed'}
                  </span>
                </motion.div>
              ))}
            </motion.div>
          ) : (
            !running && <p className="py-8 text-center text-sm text-slate-500">Run your code to see results here.</p>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
