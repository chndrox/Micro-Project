import { motion } from 'framer-motion'
import { Play, CheckCheck, Lightbulb } from 'lucide-react'

function Spinner() {
  return (
    <motion.span
      className="inline-flex"
      animate={{ rotate: 360 }}
      transition={{ repeat: Infinity, duration: 0.8, ease: 'linear' }}
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="3" strokeOpacity="0.3" />
        <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      </svg>
    </motion.span>
  )
}

export default function BottomBar({ onRun, onSubmit, onHint, runningAction, hintAvailable = false }) {
  return (
    <motion.footer
      initial={{ y: 16, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="flex shrink-0 flex-col gap-2 border-t border-borderc bg-bg-alt px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
    >
      <div className="flex flex-1 flex-col gap-2 sm:flex-row">
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={onRun}
          disabled={runningAction === 'run'}
          className="btn-press flex flex-1 items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-hover disabled:opacity-60 sm:flex-none"
        >
          {runningAction === 'run' ? <Spinner /> : <Play size={15} />}
          Run Code
          <span className="hidden text-xs font-normal text-blue-100/80 md:inline">Ctrl + Enter</span>
        </motion.button>

        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={onSubmit}
          disabled={runningAction === 'submit'}
          className="btn-press flex flex-1 items-center justify-center gap-2 rounded-lg bg-success px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-success-hover disabled:opacity-60 sm:flex-none"
        >
          {runningAction === 'submit' ? <Spinner /> : <CheckCheck size={15} />}
          Submit Solution
          <span className="hidden text-xs font-normal text-emerald-100/80 md:inline">Ctrl + Shift + Enter</span>
        </motion.button>
      </div>

      {/* Hint button only shown when hint is available */}
      {hintAvailable && (
        <motion.button
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          whileTap={{ scale: 0.97 }}
          onClick={onHint}
          disabled={runningAction === 'hint'}
          className="btn-press flex items-center justify-center gap-2 rounded-lg border border-warning/40 bg-transparent px-4 py-2.5 text-sm font-semibold text-warning transition-colors hover:bg-warning/10 disabled:opacity-60"
        >
          {runningAction === 'hint' ? <Spinner /> : <Lightbulb size={15} />}
          Need a Hint?
        </motion.button>
      )}
    </motion.footer>
  )
}
