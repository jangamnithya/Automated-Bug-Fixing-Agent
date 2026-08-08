from pathlib import Path


class RepositoryScanner:

    def __init__(self):
        self.ignore_dirs = {
            "__pycache__",
            ".venv",
            "site-packages",
            "tests"
        }

    def scan(self, project_path):
        python_files = []

        project_path = Path(project_path)

        for path in project_path.rglob("*.py"):

            # Ignore unwanted directories
            if any(folder in self.ignore_dirs for folder in path.parts):
                continue

            # Ignore Python test files
            if path.name.startswith("test_") or path.name.endswith("_test.py"):
                continue

            python_files.append(str(path))

        return python_files