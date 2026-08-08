from src.repair.repair_generator import RepairGenerator


def test_zero_division_repair_suggestion():
    generator = RepairGenerator()

    fault_analysis = {
        "file_path": "sample_project/calculator.py",
        "line_number": 2,
        "exception_type": "ZeroDivisionError",
        "issue": "Division operation may be causing the failure.",
        "evidence": [
            "The suspicious line contains a division operation.",
            "The exception indicates division by zero.",
        ],
    }

    suggestion = generator.generate(fault_analysis)

    assert suggestion.file_path == "sample_project/calculator.py"
    assert suggestion.line_number == 2
    assert suggestion.problem == (
        "Division operation may be causing the failure."
    )
    assert "zero" in suggestion.suggested_fix.lower()
    assert suggestion.confidence >= 0.9
    assert len(suggestion.reasoning) >= 2

    print("\nREPAIR GENERATOR TEST PASSED")