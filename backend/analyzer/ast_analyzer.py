import ast


class ASTAnalyzer:

    def __init__(self, code: str):
        self.code = code
        self.tree = None

        self.features = {
            "has_function": False,
            "has_loop": False,
            "has_nested_loop": False,
            "uses_nums": False,
            "uses_target": False,
            "has_comparison": False,
            "has_pair_sum": False,
            "has_return": False,
            "has_dictionary": False,
            "has_seen_variable": False,
            "has_membership_check": False,
            "has_complement": False,
            "has_seen_lookup": False,
        }

    def analyze(self) -> dict:

        if not self.code.strip():
            return {
                "syntax_valid": True,
                "empty": True,
                "features": self.features,
            }

        try:
            self.tree = ast.parse(self.code)

        except SyntaxError as error:
            return {
                "syntax_valid": False,
                "empty": False,
                "syntax_error": str(error),
                "features": self.features,
            }

        self._inspect()

        return {
            "syntax_valid": True,
            "empty": False,
            "features": self.features,
        }

    def _inspect(self):

        for node in ast.walk(self.tree):

            if isinstance(node, ast.FunctionDef):
                self.features["has_function"] = True

            elif isinstance(node, (ast.For, ast.While)):
                self.features["has_loop"] = True

            elif isinstance(node, ast.Return):
                self.features["has_return"] = True

            elif isinstance(node, ast.Dict):
                self.features["has_dictionary"] = True

            elif isinstance(node, ast.Name):

                if node.id == "nums":
                    self.features["uses_nums"] = True

                elif node.id == "target":
                    self.features["uses_target"] = True

                elif node.id == "seen":
                    self.features["has_seen_variable"] = True

            elif isinstance(node, ast.Compare):

                self.features["has_comparison"] = True

                for operator in node.ops:

                    if isinstance(
                        operator,
                        (ast.In, ast.NotIn)
                    ):
                        self.features["has_membership_check"] = True

            elif isinstance(node, ast.BinOp):

                if self._is_pair_sum(node):
                    self.features["has_pair_sum"] = True

                if self._is_complement(node):
                    self.features["has_complement"] = True

            elif isinstance(node, ast.Subscript):

                if self._contains_name(node.value, "seen"):
                    self.features["has_seen_lookup"] = True

        self._detect_nested_loops()

    def _contains_name(self, node, name):

        return any(
            isinstance(child, ast.Name)
            and child.id == name
            for child in ast.walk(node)
        )

    def _is_pair_sum(self, node):

        if not isinstance(node.op, ast.Add):
            return False

        return (
            self._contains_name(node.left, "nums")
            and self._contains_name(node.right, "nums")
        )

    def _is_complement(self, node):

        if not isinstance(node.op, ast.Sub):
            return False

        left_is_target = (
            isinstance(node.left, ast.Name)
            and node.left.id == "target"
        )

        right_uses_nums = self._contains_name(
            node.right,
            "nums"
        )

        return left_is_target and right_uses_nums

    def _detect_nested_loops(self):

        for node in ast.walk(self.tree):

            if not isinstance(
                node,
                (ast.For, ast.While)
            ):
                continue

            for child in ast.walk(node):

                if child is node:
                    continue

                if isinstance(
                    child,
                    (ast.For, ast.While)
                ):
                    self.features["has_nested_loop"] = True
                    return