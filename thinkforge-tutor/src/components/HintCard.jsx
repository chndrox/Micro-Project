import { motion } from 'framer-motion'
import { Lightbulb, X, AlertTriangle } from 'lucide-react'

export default function HintCard({ hintLevel, hint, error, loading, onDismiss }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10, scale: 0.97 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className="panel w-[300px] p-4 shadow-lg sm:w-[320px]"
    >
      <div className="mb-2.5 flex items-center justify-between">
        <span className="flex items-center gap-2 text-sm font-semibold text-warning">
          {error ? <AlertTriangle size={16} /> : <Lightbulb size={16} />}
          {error ? 'Hint unavailable' : `Hint ${hintLevel}`}
        </span>
        <button
          onClick={onDismiss}
          className="text-slate-500 hover:text-slate-300"
          aria-label="Close hint"
        >
          <X size={15} />
        </button>
      </div>

      {loading ? (
        <div className="space-y-2">
          <div className="h-3 w-full animate-pulse rounded bg-card-alt" />
          <div className="h-3 w-4/5 animate-pulse rounded bg-card-alt" />
        </div>
      ) : (
        <p className="text-sm leading-relaxed text-slate-300">
          {error ? 'Unable to connect to ThinkForge AI.' : hint}
        </p>
      )}

      <div className="mt-3 flex justify-end">
        <button
          onClick={onDismiss}
          className="btn-press rounded-md bg-primary px-3 py-1.5 text-xs font-semibold text-white hover:bg-primary-hover"
        >
          {error ? 'Close' : 'Got it, thanks!'}
        </button>
      </div>
    </motion.div>
  )
}
