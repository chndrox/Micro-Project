from typing import List, Dict, Any


class Chunker:
    """
    Converts loaded knowledge into standardized chunks
    that can be embedded into a vector database.
    """

    def __init__(self):
        self.documents = []
        self.doc_id = 1

    def _create_document(
        self,
        problem: str,
        category: str,
        title: str,
        text: str,
        metadata: Dict[str, Any]
    ):
        """Creates one standardized document."""

        document = {
            "id": self.doc_id,
            "problem": problem,
            "category": category,
            "title": title,
            "text": text,
            "metadata": metadata
        }

        self.documents.append(document)
        self.doc_id += 1

    def create_chunks(self, knowledge: Dict[str, Any]) -> List[Dict]:
        """
        Converts loaded JSON knowledge into
        standardized documents.
        """

        self.documents = []
        self.doc_id = 1

        metadata = knowledge["metadata"]

        problem = metadata["title"]

        common_metadata = {
            "difficulty": metadata["difficulty"],
            "topic": metadata["topic"],
            "pattern": metadata["pattern"]
        }

        # --------------------------
        # Concepts
        # --------------------------

        for concept in knowledge.get("concepts", []):

            self._create_document(
                problem=problem,
                category="concept",
                title=concept["concept"],
                text=concept["description"],
                metadata=common_metadata
            )

        # --------------------------
        # Hints
        # --------------------------

        for hint in knowledge.get("hints", []):

            self._create_document(
                problem=problem,
                category="hint",
                title=f"Hint Level {hint['level']}",
                text=hint["hint"],
                metadata=common_metadata
            )

        # --------------------------
        # Mistakes
        # --------------------------

        for mistake in knowledge.get("mistakes", []):

            self._create_document(
                problem=problem,
                category="mistake",
                title=mistake["mistake"],
                text=mistake["feedback"],
                metadata=common_metadata
            )

        # --------------------------
        # Complexity
        # --------------------------

        complexity = knowledge.get("complexity", {})

        if complexity:

            brute = complexity.get("bruteforce", {})
            opt = complexity.get("optimized", {})

            self._create_document(
                problem=problem,
                category="complexity",
                title="Brute Force Complexity",
                text=f"Time Complexity: {brute.get('time')} | Space Complexity: {brute.get('space')}",
                metadata=common_metadata
            )

            self._create_document(
                problem=problem,
                category="complexity",
                title="Optimized Complexity",
                text=f"Time Complexity: {opt.get('time')} | Space Complexity: {opt.get('space')}",
                metadata=common_metadata
            )

        return self.documents