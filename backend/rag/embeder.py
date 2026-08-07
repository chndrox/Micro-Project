"""
backend/rag/embedder.py

Turns chunk text into numeric vectors so vector_store.py can run
similarity search.

Uses TF-IDF (scikit-learn) rather than a neural embedding model on
purpose for this MVP: it runs fully offline with no model download,
which is exactly right for a knowledge base this small (a few dozen
short teaching chunks per problem) where keyword-level matching is
plenty to distinguish "hash map" from "nested loop" from "complement".

The interface (fit / transform / embed_query) is intentionally the
same shape a sentence-transformers or hosted embedding API would
expose. Swapping the implementation later touches only this file --
chunker.py, vector_store.py, and retriver.py never need to change.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class Embedder:
    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self._fitted = False

    def fit(self, texts: list[str]) -> None:
        self._vectorizer.fit(texts)
        self._fitted = True

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        vectors = self._vectorizer.fit_transform(texts).toarray()
        self._fitted = True
        return vectors

    def transform(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Embedder.fit()/fit_transform() must run before transform().")
        return self._vectorizer.transform(texts).toarray()

    def embed_query(self, text: str) -> np.ndarray:
        """Embed a single piece of text -- e.g. the student's current code
        or a short description of what they're stuck on -- against the
        already-fit vocabulary."""
        return self.transform([text])[0]

    def save(self, path: str | Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(self._vectorizer, f)

    def load(self, path: str | Path) -> None:
        with open(path, "rb") as f:
            self._vectorizer = pickle.load(f)
        self._fitted = True