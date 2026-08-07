"""
backend/rag/vector_store.py

In-memory vector store: holds chunk vectors alongside their Chunk
metadata, and supports cosine similarity search with optional
filtering by milestone and/or chunk type BEFORE ranking. Filtering
first matters here: a "hash map" concept chunk should never outrank a
"complement" concept chunk just because it scores higher globally, if
the student is currently on the discover_complement milestone and the
introduce_hash_map chunk hasn't been reached yet.

Persistable to disk as a single pickle file per problem, so the store
doesn't need to be rebuilt (re-chunked, re-embedded) on every server
restart.
"""
from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .chunker import Chunk


@dataclass(frozen=True)
class ScoredChunk:
    chunk: Chunk
    score: float


class VectorStore:
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._vectors: np.ndarray | None = None

    def build(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        if len(chunks) != vectors.shape[0]:
            raise ValueError("chunks and vectors must be the same length")
        self._chunks = chunks
        self._vectors = vectors

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 3,
        milestone: str | None = None,
        chunk_type: str | None = None,
    ) -> list[ScoredChunk]:
        if self._vectors is None:
            raise RuntimeError("VectorStore.build() must be called before search().")

        candidate_idx = [
            i for i, c in enumerate(self._chunks)
            if _matches_milestone(c, milestone) and _matches_type(c, chunk_type)
        ]
        if not candidate_idx:
            return []

        candidate_vectors = self._vectors[candidate_idx]
        scores = _cosine_similarity(query_vector, candidate_vectors)

        ranked = sorted(zip(candidate_idx, scores), key=lambda pair: pair[1], reverse=True)
        top = ranked[:top_k]

        return [ScoredChunk(chunk=self._chunks[i], score=float(s)) for i, s in top]

    def save(self, path: str | Path) -> None:
        with open(path, "wb") as f:
            pickle.dump({"chunks": self._chunks, "vectors": self._vectors}, f)

    def load(self, path: str | Path) -> None:
        with open(path, "rb") as f:
            data = pickle.load(f)
        self._chunks = data["chunks"]
        self._vectors = data["vectors"]


def _matches_milestone(chunk: Chunk, milestone: str | None) -> bool:
    if milestone is None:
        return True
    if chunk.milestone is None:
        return True  # untagged chunks (e.g. problem-level info) match any query
    return chunk.milestone == milestone


def _matches_type(chunk: Chunk, chunk_type: str | None) -> bool:
    return chunk_type is None or chunk.type == chunk_type


def _cosine_similarity(query_vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query_norm = np.linalg.norm(query_vector) or 1e-9
    matrix_norms = np.linalg.norm(matrix, axis=1)
    matrix_norms[matrix_norms == 0] = 1e-9
    return (matrix @ query_vector) / (matrix_norms * query_norm)