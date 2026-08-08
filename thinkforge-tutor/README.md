# ThinkForge AI — Two Sum Tutor (Frontend)

A focused, single-problem coding tutor UI. Not a LeetCode clone — no
sidebar, no problem list, no chatbot, no permanent AI panel. Just the
problem, the editor, and a hint you can ask for when you're stuck.

## Tech stack

- React + Vite (JavaScript)
- Tailwind CSS (dark coding-environment palette, no gradients)
- Framer Motion
- Axios
- Lucide React
- Monaco Editor (`@monaco-editor/react`)

## Getting started

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`. The FastAPI + RAG backend is expected at
`http://localhost:8000` (see `src/services/api.js`).

**No fake hints.** If the backend isn't reachable, the hint card shows
"Unable to connect to ThinkForge AI." instead of any locally generated text.

## Build

```bash
npm run build
npm run preview
```

## How the hint flow works

- The frontend tracks `milestone` and `hintLevel` locally.
- Clicking **Need a Hint?** (or the floating pill, or the "Stuck on this
  step?" prompt) sends `{ problem_id, milestone_id, hint_level, student_code }`
  to `POST /api/hint`.
- The backend's RAG pipeline decides the actual hint text, milestone, and
  hint level — the response overwrites local state so the next request
  stays in sync.
- If the student hasn't edited the code for 60 seconds, a subtle "Stuck on
  this step?" prompt appears. It never calls the backend automatically —
  only a click does.

## Folder structure

```
src/
  components/
    Navbar.jsx
    ProblemPanel.jsx
    Editor.jsx
    HintCard.jsx
    TestCases.jsx
    OutputPanel.jsx
    BottomBar.jsx
  pages/
    SolveProblem.jsx
  services/
    api.js
  App.jsx
  main.jsx
  index.css
```

## Shortcuts

- `Ctrl/Cmd + Enter` — Run Code
- `Ctrl/Cmd + Shift + Enter` — Submit Solution
