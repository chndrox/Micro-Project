"""backend/rag package -- adaptive hint generation via structured + semantic retrieval."""
from .generate_hint import generate_hint
from .retriver import retrieve, RetrievalQuery, RetrievedContext, KnowledgeNotFoundError, clear_cache
from .knowledge_load import load_problem_knowledge, list_available_problems

__all__ = [
    "generate_hint",
    "retrieve",
    "RetrievalQuery",
    "RetrievedContext",
    "KnowledgeNotFoundError",
    "clear_cache",
    "load_problem_knowledge",
    "list_available_problems",
]