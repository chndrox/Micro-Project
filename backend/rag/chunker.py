"""
backend/rag/chunker.py

Turns loaded knowledge-base entries into small, retrievable "chunks":
one chunk per concept, per mistake, per complexity note, per hint.
Each chunk carries metadata (type, milestone, source id) so retrieval
can filter by milestone before -- or instead of -- ranking by
embedding similarity.

This is deliberately NOT paragraph-splitting long documents, which is
the usual RAG chunking problem. Every entry in our knowledge base is
already short and atomic by design (see architecture doc): one
knowledge-base entry = one chunk, always. No sliding windows, no
overlap logic needed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ChunkType = Literal["concept", "mistake", "complexity", "hint"]


@dataclass(frozen=True)
class Chunk:
    id: str                  # stable id, e.g. "concept:hash_map_lookup"
    type: ChunkType
    milestone: str | None     # which milestone this chunk belongs to
    text: str                  # the text that actually gets embedded
    payload: dict = field(default_factory=dict)  # original JSON entry, for reconstruction


def chunk_knowledge(problem_id: str, knowledge: dict) -> list[Chunk]:
    """
    knowledge is the dict returned by knowledge_load.load_problem_knowledge.
    Returns a flat list of Chunks ready to be embedded.
    """
    chunks: list[Chunk] = []
    chunks.extend(_chunk_concepts(knowledge.get("concepts", [])))
    chunks.extend(_chunk_mistakes(knowledge.get("mistake", [])))
    chunks.extend(_chunk_complexity(knowledge.get("complexity", [])))
    chunks.extend(_chunk_hints(knowledge.get("hints", [])))
    return chunks


def _chunk_concepts(concepts: list[dict]) -> list[Chunk]:
    return [
        Chunk(
            id=f"concept:{c['id']}",
            type="concept",
            milestone=c.get("milestone"),
            text=f"{c['title']}. {c['explanation']}",
            payload=c,
        )
        for c in concepts
    ]


def _chunk_mistakes(mistakes: list[dict]) -> list[Chunk]:
    return [
        Chunk(
            id=f"mistake:{m['id']}",
            type="mistake",
            milestone=m.get("milestone"),
            text=f"Common mistake: {m['description']}",
            payload=m,
        )
        for m in mistakes
    ]


def _chunk_complexity(entries: list[dict]) -> list[Chunk]:
    return [
        Chunk(
            id=f"complexity:{e['id']}",
            type="complexity",
            milestone=e.get("milestone"),
            text=f"Time {e.get('time', '?')}, space {e.get('space', '?')}. {e.get('explanation', '')}",
            payload=e,
        )
        for e in entries
    ]


def _chunk_hints(hints: list[dict]) -> list[Chunk]:
    # Hints are chunked too so they can be part of the searchable corpus
    # (used for TF-IDF vocabulary fitting and as a semantic fallback),
    # but retriver.py always fetches the exact hint by (milestone, level)
    # rather than relying on similarity search for hint selection itself.
    return [
        Chunk(
            id=f"hint:{h['milestone']}:{h['level']}",
            type="hint",
            milestone=h.get("milestone"),
            text=h["text"],
            payload=h,
        )
        for h in hints
    ]