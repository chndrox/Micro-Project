# pyrefly: ignore [missing-import]
from rag.knowledge_load import KnowledgeLoader
# pyrefly: ignore [missing-import]
from rag.chunker import Chunker

loader = KnowledgeLoader("../knowledge_base")

knowledge = loader.load_problem("two_sum")

chunker = Chunker()

documents = chunker.create_chunks(knowledge)

for doc in documents:
    print("=" * 60)
    print(doc)