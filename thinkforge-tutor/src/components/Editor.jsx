import { useState } from 'react'
import MonacoEditor from '@monaco-editor/react'
import { motion } from 'framer-motion'
import { RotateCcw, Copy, Check, Minus, Plus, FileCode2 } from 'lucide-react'

export const INITIAL_CODE = `class Solution:
    def twoSum(self, nums, target):
        pass
`

export default function Editor({ code, onChange }) {
  const [fontSize, setFontSize] = useState(14)
  const [copied, setCopied] = useState(false)

  const handleReset = () => onChange(INITIAL_CODE)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.2 }}
      className="panel flex h-full flex-col overflow-hidden"
    >
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-borderc px-4 py-2.5">
        <span className="flex items-center gap-2 text-sm font-medium text-slate-300">
          <FileCode2 size={14} className="text-primary" />
          solution.py
        </span>

        <div className="flex items-center gap-1.5">
          <div className="mr-1 flex items-center overflow-hidden rounded-md border border-borderc">
            <button
              onClick={() => setFontSize((f) => Math.max(11, f - 1))}
              className="flex h-7 w-7 items-center justify-center text-slate-400 hover:bg-card-alt"
              aria-label="Decrease font size"
            >
              <Minus size={12} />
            </button>
            <span className="px-1.5 text-xs text-slate-500">{fontSize}</span>
            <button
              onClick={() => setFontSize((f) => Math.min(22, f + 1))}
              className="flex h-7 w-7 items-center justify-center text-slate-400 hover:bg-card-alt"
              aria-label="Increase font size"
            >
              <Plus size={12} />
            </button>
          </div>

          <button
            onClick={handleReset}
            className="btn-press flex items-center gap-1.5 rounded-md border border-borderc px-2.5 py-1.5 text-xs font-medium text-slate-300 hover:bg-card-alt"
          >
            <RotateCcw size={13} /> Reset Code
          </button>
          <button
            onClick={handleCopy}
            className="btn-press flex items-center gap-1.5 rounded-md border border-borderc px-2.5 py-1.5 text-xs font-medium text-slate-300 hover:bg-card-alt"
          >
            {copied ? <Check size={13} className="text-success" /> : <Copy size={13} />}
            {copied ? 'Copied' : 'Copy Code'}
          </button>
        </div>
      </div>

      {/* Monaco */}
      <div className="min-h-0 flex-1">
        <MonacoEditor
          height="100%"
          defaultLanguage="python"
          value={code}
          theme="vs-dark"
          onChange={(value) => onChange(value ?? '')}
          options={{
            fontSize,
            fontFamily: '"JetBrains Mono", monospace',
            minimap: { enabled: false },
            padding: { top: 16 },
            scrollBeyondLastLine: false,
            smoothScrolling: true,
            cursorBlinking: 'smooth',
            automaticLayout: true,
            tabSize: 4,
            lineNumbers: 'on',
            autoIndent: 'full',
          }}
        />
      </div>
    </motion.div>
  )
}
