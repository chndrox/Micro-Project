import { motion } from 'framer-motion'
import { Code2, Moon, Sun, ChevronDown } from 'lucide-react'

export default function Navbar({ theme, onToggleTheme }) {
  const isDark = theme === 'dark'

  return (
    <motion.header
      initial={{ y: -12, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.25 }}
      className="flex h-14 shrink-0 items-center justify-between border-b border-borderc bg-bg-alt px-4 sm:h-16"
    >
      <div className="flex items-center gap-3">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-white">
          <Code2 size={17} />
        </span>
        <span className="text-[15px] font-bold tracking-tight text-white">ThinkForge AI</span>
        <span className="hidden h-5 w-px bg-borderc sm:block" />
        <span className="hidden text-sm font-medium text-slate-400 sm:block">Two Sum</span>
      </div>

      <div className="flex items-center gap-2.5">
        <button className="btn-press flex items-center gap-1.5 rounded-lg border border-borderc bg-card px-3 py-1.5 text-sm font-medium text-slate-200 hover:bg-card-alt">
          Python
          <ChevronDown size={14} className="text-slate-500" />
        </button>

        <button
          onClick={onToggleTheme}
          aria-label="Toggle theme"
          className="btn-press flex h-9 w-9 items-center justify-center rounded-lg border border-borderc bg-card text-slate-300 hover:bg-card-alt"
        >
          {isDark ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </motion.header>
  )
}
