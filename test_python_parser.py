from pathlib import Path

from src.parser.python_parser import PythonParser


def test_python_parser():
    parser = PythonParser()

    result = parser.parse_file(
        "sample_project/calculator.py"
    )

    expected_path = str(
        Path("sample_project/calculator.py")
    )

    assert result["file_path"] == expected_path

    assert "add" in result["functions"]
    assert "validate_and_add" in result["functions"]

    assert result["classes"] == []
    assert result["methods"] == []