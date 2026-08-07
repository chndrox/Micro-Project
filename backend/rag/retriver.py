"""
backend/rag/retriver.py

Single entry point the Learning Engine (and generate_hint.py) calls
into RAG. Combines two retrieval strategies on purpose:

1. EXACT lookup for the hint itself -- (milestone, hint_level) always
   maps to exactly one predetermined hint. This must stay deterministic,
   never similarity-based: the Learning Engine already decided the hint
   level (see architecture doc §6 on why that logic lives in code, not
   the LLM). RAG must not second-guess that choice by picking a "close
   enough" hint via embedding similarity.

2. SEMANTIC search (via vector_store) for supporting context -- which
   concept explanations, common mistakes, and complexity notes are most
   relevant to what THIS student is stuck on right now. Two students on
   the same milestone can be confused about different things; their
   current code is the signal for which supporting note is worth
   surfacing. This is where chunker/embedder/vector_store earn their
   place, instead of being RAG machinery for its own sake.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .knowledge_load import load_problem_knowledge
from .chunker import chunk_knowledge
from .embedder import Embedder
from .vector_store import VectorStore


class KnowledgeNotFoundError(Exception):
    """Raised when a problem/milestone/hint-level combination has no
    matching entry in the knowledge base. Should never be silently
    swallowed -- it means either the caller passed a bad milestone id,
    or the knowledge base is incomplete."""
    pass


@dataclass(frozen=True)
class RetrievalQuery:
    problem: str
    milestone: str
    hint_level: int
    student_signal: str = ""  # optional: student's current code or a short
                                  # description of what they're stuck on.
                                  # Used ONLY for ranking supporting context,
                                  # never for selecting which hint to return.


@dataclass(frozen=True)
class RetrievedContext:
    problem_id: str
    milestone_id: str
    hint_level: int
    hint_text: str
    supporting_concepts: list[dict] = field(default_factory=list)
    supporting_mistakes: list[dict] = field(default_factory=list)
    complexity_note: dict | None = None


# One (VectorStore, Embedder) pair per problem, built lazily and kept in
# memory for the process lifetime. Rebuilding on every request would mean
# re-chunking and re-embedding the whole knowledge base per hint request --
# unnecessary work, since the knowledge base only changes when someone
# edits the JSON files. Call clear_cache() after such edits.
_STORE_CACHE: dict[str, tuple[VectorStore, Embedder]] = {}


def _get_or_build_store(problem_id: str) -> tuple[VectorStore, Embedder]:
    if problem_id in _STORE_CACHE:
        return _STORE_CACHE[problem_id]

    knowledge = load_problem_knowledge(problem_id)
    chunks = chunk_knowledge(problem_id, knowledge)

    embedder = Embedder()
    vectors = embedder.fit_transform([c.text for c in chunks])

    store = VectorStore()
    store.build(chunks, vectors)

    _STORE_CACHE[problem_id] = (store, embedder)
    return store, embedder


def retrieve(query: RetrievalQuery) -> RetrievedContext:
    knowledge = load_problem_knowledge(query.problem)
    store, embedder = _get_or_build_store(query.problem)

    hint_entry = _find_hint(knowledge["hints"], query.milestone, query.hint_level)
    if hint_entry is None:
        raise KnowledgeNotFoundError(
            f"No hint at level {query.hint_level} for milestone "
            f"'{query.milestone}' in problem '{query.problem}'"
        )

    # Rank supporting context against the student's own signal if given
    # (their code, or a short description of their confusion); otherwise
    # fall back to the hint text itself so results still bias toward
    # this milestone's topic.
    ranking_text = query.student_signal.strip() or hint_entry["text"]
    query_vector = embedder.embed_query(ranking_text)

    concept_hits = store.search(
        query_vector, top_k=2, milestone=query.milestone, chunk_type="concept"
    )
    mistake_hits = store.search(
        query_vector, top_k=2, milestone=query.milestone, chunk_type="mistake"
    )
    complexity_hits = store.search(
        query_vector, top_k=1, milestone=query.milestone, chunk_type="complexity"
    )

    return RetrievedContext(
        problem_id=query.problem,
        milestone_id=query.milestone,
        hint_level=query.hint_level,
        hint_text=hint_entry["text"],
        supporting_concepts=[h.chunk.payload for h in concept_hits],
        supporting_mistakes=[h.chunk.payload for h in mistake_hits],
        complexity_note=complexity_hits[0].chunk.payload if complexity_hits else None,
    )


def _find_hint(hints: list[dict], milestone: str, level: int) -> dict | None:
    return next(
        (h for h in hints if h["milestone"] == milestone and h["level"] == level),
        None,
    )


def clear_cache() -> None:
    """Call after editing knowledge base JSON files during local
    development, or between tests, so stale chunks/vectors aren't reused."""
    _STORE_CACHE.clear()
    load_problem_knowledge.cache_clear()