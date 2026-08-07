"""
backend/rag/generate_hint.py

Top-level entry point for the whole RAG pipeline: given
(problem, milestone, hint_level, student_code), retrieves the right
context and calls the LLM to phrase the final hint.

This is what the Learning Engine / main.py should import and call --
everything else in rag/ (knowledge_load, chunker, embedder, vector_store,
retriver, prompt_builder) is an implementation detail behind this
single function.
"""
from __future__ import annotations

import os

import anthropic

from .retriver import retrieve, RetrievalQuery, RetrievedContext
from .prompt_builder import build_prompt

_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 300


def generate_hint(
    problem_id: str,
    milestone_id: str,
    hint_level: int,
    student_code: str = "",
) -> dict:
    """
    Returns:
        {
            "milestone": str,
            "hint_level": int,
            "hint": str,
        }

    Raises KnowledgeNotFoundError (from retriver) if the milestone/level
    combination doesn't exist in the knowledge base -- this is NOT caught
    here, since a bad milestone id is a caller bug that should surface,
    not be silently papered over with a generic hint.
    """
    query = RetrievalQuery(
        problem=problem_id,
        milestone=milestone_id,
        hint_level=hint_level,
        student_signal=student_code,
    )
    context: RetrievedContext = retrieve(query)
    prompt = build_prompt(context, student_code=student_code)

    hint_text = _call_llm(prompt)

    return {
        "milestone": context.milestone_id,
        "hint_level": context.hint_level,
        "hint": hint_text,
    }


def _call_llm(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Export it in your environment "
            "before calling generate_hint()."
        )

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )

    text_blocks = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_blocks).strip()