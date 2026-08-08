from src.analyzer.fault_analyzer import FaultAnalyzer


def test_fault_analyzer():
    analyzer = FaultAnalyzer()

    result = analyzer.analyze(
        "sample_project/calculator.py",
        2,
        "ZeroDivisionError",
    )

    assert result["file_path"].endswith("calculator.py")
    assert result["line_number"] == 2
    assert result["exception_type"] == "ZeroDivisionError"

    assert "division" in result["issue"].lower()

    assert len(result["evidence"]) >= 1


if __name__ == "__main__":
    test_fault_analyzer()
    print("FAULT ANALYZER TEST PASSED")