import { motion } from 'framer-motion'

const PROBLEM = {
  title: 'Two Sum',
  difficulty: 'Easy',
  tags: ['Array', 'Hash Table'],
  description:
    'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
  note: 'You may assume that each input would have exactly one solution, and you may not use the same element twice.',
  examples: [
    { input: 'nums = [2,7,11,15], target = 9', output: '[0,1]', explanation: 'Because nums[0] + nums[1] == 9.' },
    { input: 'nums = [3,2,4], target = 6', output: '[1,2]', explanation: 'Because nums[1] + nums[2] == 6.' },
    { input: 'nums = [3,3], target = 6', output: '[0,1]', explanation: 'Because nums[0] + nums[1] == 6.' },
  ],
  constraints: ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9', '-10^9 <= target <= 10^9'],
}

export default function ProblemPanel() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="panel flex h-full flex-col overflow-hidden"
    >
      <div className="flex-1 overflow-y-auto p-5">
        <h1 className="text-xl font-bold text-white">{PROBLEM.title}</h1>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="rounded-md border border-success/30 bg-success/10 px-2 py-0.5 text-xs font-semibold text-success">
            {PROBLEM.difficulty}
          </span>
          {PROBLEM.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-md border border-borderc bg-card-alt px-2 py-0.5 text-xs font-medium text-slate-300"
            >
              {tag}
            </span>
          ))}
        </div>

        <p className="mt-4 text-[15px] leading-relaxed text-slate-300">{PROBLEM.description}</p>
        <p className="mt-3 text-[15px] leading-relaxed text-slate-300">{PROBLEM.note}</p>

        <div className="mt-5 space-y-4">
          {PROBLEM.examples.map((ex, i) => (
            <div key={i}>
              <p className="mb-1.5 text-sm font-semibold text-white">Example {i + 1}:</p>
              <div className="rounded-lg border border-borderc bg-card-alt p-3 font-mono text-[13px] leading-relaxed text-slate-300">
                <p>
                  <span className="font-semibold text-white">Input: </span>
                  {ex.input}
                </p>
                <p>
                  <span className="font-semibold text-white">Output: </span>
                  {ex.output}
                </p>
                <p className="mt-1 text-slate-400">
                  <span className="font-semibold text-slate-300">Explanation: </span>
                  {ex.explanation}
                </p>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-5">
          <p className="mb-2 text-sm font-semibold text-white">Constraints:</p>
          <ul className="space-y-1.5">
            {PROBLEM.constraints.map((c, i) => (
              <li key={i} className="flex items-start gap-2 font-mono text-[13px] text-slate-400">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-slate-600" />
                {c}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </motion.div>
  )
}
