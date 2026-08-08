from pathlib import Path

from src.analyzer.fault_analyzer import FaultAnalyzer


def test_wrong_comparison_operator():
    file_path = Path("sample_project/comparison_bug.py")

    file_path.write_text(
        """def is_valid(value):
    return value > 10
""",
        encoding="utf-8",
    )

    analyzer = FaultAnalyzer()

    result = analyzer.analyze(
        file_path=str(file_path),
        line_number=2,
        exception_type="AssertionError",
    )

    print("\n===== COMPARISON OPERATOR TEST =====")
    print(f"File       : {result['file_path']}")
    print(f"Line       : {result['line_number']}")
    print(f"Exception  : {result['exception_type']}")
    print(f"Issue      : {result['issue']}")
    print(f"Evidence   : {result['evidence']}")

    assert result["file_path"] == str(file_path)
    assert result["line_number"] == 2
    assert result["exception_type"] == "AssertionError"

    file_path.unlink()


if __name__ == "__main__":
    test_wrong_comparison_operator()
    print("\nCOMPARISON OPERATOR TEST PASSED")