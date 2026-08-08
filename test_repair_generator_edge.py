from src.repair.repair_generator import RepairGenerator


def test_assertion_error_repair_suggestion():
    generator = RepairGenerator()

    fault_analysis = {
        "file_path": "sample_project/comparison_bug.py",
        "line_number": 2,
        "exception_type": "AssertionError",
        "issue": "Comparison operation may be causing the failure.",
        "evidence": [
            "The suspicious line contains a comparison operation.",
            "Comparison operator(s): Gt",
            "The exception indicates that an assertion condition failed.",
        ],
    }

    suggestion = generator.generate(fault_analysis)

    assert suggestion.file_path == "sample_project/comparison_bug.py"
    assert suggestion.line_number == 2
    assert suggestion.problem == (
        "Comparison operation may be causing the failure."
    )
    assert "comparison" in suggestion.suggested_fix.lower()
    assert suggestion.confidence >= 0.8
    assert len(suggestion.reasoning) >= 2

    print("\nASSERTION ERROR REPAIR TEST PASSED")