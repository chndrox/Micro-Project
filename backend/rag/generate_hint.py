"""
backend/rag/generate_hint.py

Top-level entry point for the whole RAG pipeline: given
(problem, milestone, hint_level, student_code), retrieves the right
context and calls an LLM to phrase the final hint.

This is what the Learning Engine / main.py should import and call --
everything else in rag/ (knowledge_load, chunker, embedder, vector_store,
retriver, prompt_builder) is an implementation detail behind this
single function.

LLM provider is swappable via the LLM_PROVIDER env var:
    LLM_PROVIDER=groq    (default) -- uses GROQ_API_KEY, Llama 3.3 70B
    LLM_PROVIDER=gemini            -- uses GEMINI_API_KEY, Gemini 2.0 Flash

Both are free-tier friendly, which is why they're the default here
instead of a paid-only provider. Swapping providers never touches
retriver.py or prompt_builder.py -- only the _call_llm dispatch below.
"""
from __future__ import annotations

import os

from .retriver import retrieve, RetrievalQuery, RetrievedContext
from .prompt_builder import build_prompt

_GROQ_MODEL = "llama-3.3-70b-versatile"
_GEMINI_MODEL = "gemini-2.0-flash"
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
    provider = os.environ.get("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        return _call_groq(prompt)
    elif provider == "gemini":
        return _call_gemini(prompt)
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Use 'groq' or 'gemini'."
        )


def _call_groq(prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free key at https://console.groq.com/keys "
            "and export it before calling generate_hint()."
        )

    from groq import Groq

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=_GROQ_MODEL,
        max_tokens=_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def _call_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com/apikey "
            "and export it before calling generate_hint()."
        )

    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(_GEMINI_MODEL)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(max_output_tokens=_MAX_TOKENS),
    )
    return response.text.strip()