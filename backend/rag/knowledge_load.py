"""
backend/rag/knowledge_load.py

Loads the JSON teaching knowledge base for a given problem from disk
and caches it in memory. This is the only file in rag/ that touches
the filesystem for knowledge content -- chunker.py, embedder.py,
vector_store.py and retriver.py all work off the dict this returns.
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

# backend/rag/knowledge_load.py -> backend/knowledge_base
KNOWLEDGE_BASE_ROOT = Path(__file__).resolve().parent.parent / "knowledge_base"

# Files expected inside each problem's knowledge base folder.
# "mistake" is singular to match the on-disk filename (mistake.json).
_FILES = ("metadata", "concepts", "hints", "mistakes", "complexity")


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing knowledge base file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=None)
def load_problem_knowledge(problem_id: str) -> dict:
    """
    Returns:
        {
            "metadata": {...},
            "concepts": [...],
            "hints": [...],
            "mistake": [...],
            "complexity": [...],
        }

    Cached since these files change rarely but are read on every hint
    request. Call load_problem_knowledge.cache_clear() after editing
    knowledge base JSON files during local development, or in tests.
    """
    problem_dir = KNOWLEDGE_BASE_ROOT / problem_id
    if not problem_dir.is_dir():
        raise FileNotFoundError(
            f"No knowledge base found for problem '{problem_id}' "
            f"(expected directory: {problem_dir})"
        )
    return {name: _read_json(problem_dir / f"{name}.json") for name in _FILES}


def list_available_problems() -> list[str]:
    """Returns problem ids that have a knowledge base directory."""
    if not KNOWLEDGE_BASE_ROOT.is_dir():
        return []
    return sorted(
        p.name for p in KNOWLEDGE_BASE_ROOT.iterdir()
        if p.is_dir() and (p / "hints.json").exists()
    )