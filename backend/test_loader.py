# pyrefly: ignore [missing-import]
from rag.knowledge_load import KnowledgeLoader

loader = KnowledgeLoader("../knowledge_base")

data = loader.load_problem("two_sum")

print(data)