from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np


class Embedder:
    """
    Generates embeddings for RAG documents.
    """

    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        print(f"Loading embedding model: {model_name}")

        self.model = SentenceTransformer(model_name)

        print("Embedding model loaded successfully!")

    def embed_documents(self, documents: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for all documents.
        """

        texts = [doc["text"] for doc in documents]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query.
        """

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding