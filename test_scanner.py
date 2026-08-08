from pathlib import Path

from src.localizer.repository_scanner import RepositoryScanner


def test_repository_scanner():
    project_path = Path("sample_project")

    scanner = RepositoryScanner()
    files = scanner.scan(project_path)

    file_names = {Path(file).name for file in files}

    assert "calculator.py" in file_names

    assert "test_calculator.py" not in file_names

    for file in files:
        path = Path(file)

        assert "__pycache__" not in path.parts
        assert ".venv" not in path.parts
        assert "tests" not in path.parts