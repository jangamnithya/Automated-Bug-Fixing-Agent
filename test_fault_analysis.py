from src.models.fault_analysis import FaultAnalysis


def test_fault_analysis():
    analysis = FaultAnalysis(
        file_path="sample_project/calculator.py",
        line_number=2,
        exception_type="ZeroDivisionError",
        issue="Division operation may be causing the failure.",
        evidence=[
            "The suspicious line contains a division operation.",
            "The exception indicates division by zero.",
        ],
        confidence="HIGH",
    )

    assert analysis.file_path.endswith("calculator.py")
    assert analysis.line_number == 2
    assert analysis.exception_type == "ZeroDivisionError"
    assert len(analysis.evidence) == 2
    assert analysis.confidence == "HIGH"


if __name__ == "__main__":
    test_fault_analysis()
    print("FAULT ANALYSIS MODEL TEST PASSED")