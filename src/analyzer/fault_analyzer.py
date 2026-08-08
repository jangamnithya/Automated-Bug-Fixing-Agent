import ast
from pathlib import Path


class FaultAnalyzer:
    """Analyze suspicious source code using AST information."""

    def analyze(
        self,
        file_path: str,
        line_number: int,
        exception_type: str,
    ) -> dict:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Source file not found: {file_path}"
            )

        source = path.read_text(encoding="utf-8")

        tree = ast.parse(source)

        target_node = self._find_node_at_line(
            tree,
            line_number,
        )

        evidence = []
        issue = "Unable to determine a specific issue."

        if isinstance(target_node, ast.Return):
            operation = target_node.value

            if isinstance(operation, ast.BinOp):
                operator = type(operation.op).__name__

                if operator == "Div":
                    issue = "Division operation may be causing the failure."
                    evidence.append(
                        "The suspicious line contains a division operation."
                    )

        if exception_type == "ZeroDivisionError":
            evidence.append(
                "The exception indicates division by zero."
            )

        return {
            "file_path": str(path),
            "line_number": line_number,
            "exception_type": exception_type,
            "issue": issue,
            "evidence": evidence,
        }

    def _find_node_at_line(
        self,
        tree: ast.AST,
        line_number: int,
    ):
        for node in ast.walk(tree):
            if getattr(node, "lineno", None) == line_number:
                return node

        return None