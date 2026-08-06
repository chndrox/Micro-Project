import json
from pathlib import Path


class KnowledgeLoader:
    def __init__(self, knowledge_base_path: str):
        self.base_path = Path(knowledge_base_path)

    def load_problem(self, problem_name: str):
        problem_path = self.base_path / problem_name

        knowledge = {}

        for file in problem_path.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                knowledge[file.stem] = json.load(f)

        return knowledge