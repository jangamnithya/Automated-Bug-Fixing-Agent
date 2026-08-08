import ast
from pathlib import Path


class PythonParser:

    def parse_file(self, file_path):
        file_path = Path(file_path)

        source_code = file_path.read_text(encoding="utf-8")

        tree = ast.parse(source_code)

        functions = []
        classes = []
        methods = []

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(child.name)

        return {
            "file_path": str(file_path),
            "functions": functions,
            "classes": classes,
            "methods": methods
        }