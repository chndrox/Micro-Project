"""
backend/rag/prompt_builder.py

Builds the exact prompt sent to the LLM for hint generation.

All pedagogical guardrails (never reveal beyond this hint level, never
write full code, tutor persona) live here as instructions -- backed up
by the fact that hint_level itself was already chosen deterministically
upstream in retriver.py (see architecture doc §6). This file only
controls PHRASING of the pre-selected hint, never which hint gets used.
"""
from __future__ import annotations

from .retriver import RetrievedContext

_SYSTEM_PERSONA = (
    "You are an experienced, encouraging coding mentor helping a student "
    "solve a problem on their own. You are NOT allowed to write the "
    "student's code for them, and you must not reveal ideas beyond the "
    "exact hint level given below. Rephrase the base hint in a natural, "
    "conversational way, in 1-3 sentences. Never include a full code "
    "solution, even if asked."
)


def build_prompt(context: RetrievedContext, student_code: str = "") -> str:
    concept_lines = "\n".join(
        f"- {c.get('title', c.get('id'))}: {c.get('explanation', '')}"
        for c in context.supporting_concepts
    ) or "None"

    mistake_lines = "\n".join(
        f"- {m.get('description', '')} (Tip: {m.get('tip', '')})"
        for m in context.supporting_mistakes
    ) or "None"

    complexity_line = (
        context.complexity_note.get("explanation", "")
        if context.complexity_note else "None"
    )

    return f"""{_SYSTEM_PERSONA}

Problem: {context.problem_id}
Current learning milestone: {context.milestone_id}
Hint level: {context.hint_level} of 5 (1 = vague nudge, 5 = almost the implementation)

Base hint to rephrase (do not go beyond this level of detail):
"{context.hint_text}"

Relevant concepts (background for your own understanding -- do not just
recite these verbatim to the student):
{concept_lines}

Common mistakes to watch for (mention ONLY if the student's code shows
this exact mistake, otherwise ignore):
{mistake_lines}

Relevant complexity note:
{complexity_line}

Student's current code:
{student_code or "(no code written yet)"}

Write ONE hint at exactly the specified level. Do not reveal anything
from a higher level."""