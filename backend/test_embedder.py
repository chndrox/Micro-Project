# pyrefly: ignore [missing-import]
from rag.knowledge_load import KnowledgeLoader
# pyrefly: ignore [missing-import]
from rag.chunker import Chunker
# pyrefly: ignore [missing-import]
from rag.embeder import Embedder

loader = KnowledgeLoader("../knowledge_base")

knowledge = loader.load_problem("two_sum")

chunker = Chunker()

documents = chunker.create_chunks(knowledge)

embedder = Embedder()

embeddings = embedder.embed_documents(documents)

print("=" * 60)
print("Number of Documents:", len(documents))
print("Embedding Shape:", embeddings.shape)
print("=" * 60)

print("\nFirst Embedding:\n")
print(embeddings[0])