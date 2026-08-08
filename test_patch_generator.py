from pathlib import Path

from src.models.repair_suggestion import RepairSuggestion
from src.repair.patch_generator import PatchGenerator


def test_patch_generator_zero_division():
    suggestion = RepairSuggestion(
        file_path="sample_project/calculator.py",
        line_number=2,
        problem="Division operation may be causing the failure.",
        suggested_fix=(
            "Check that the divisor is not zero "
            "before performing the division."
        ),
        confidence=0.95,
        reasoning=[
            "The fault analysis identified a division operation.",
            "ZeroDivisionError indicates that the divisor evaluated to zero.",
            "A zero-value check can prevent the exception.",
        ],
    )

    generator = PatchGenerator()

    patch = generator.generate(suggestion)

    assert patch["file_path"] == str(
        Path("sample_project/calculator.py")
    )
    assert patch["line_number"] == 2
    assert "if b == 0:" in patch["replacement"]
    assert "Cannot divide by zero" in patch["replacement"]

    print("\nPATCH GENERATOR TEST PASSED")