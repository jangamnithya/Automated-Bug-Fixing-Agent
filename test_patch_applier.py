from pathlib import Path

from src.models.repair_suggestion import RepairSuggestion
from src.repair.patch_generator import PatchGenerator
from src.repair.patch_applier import PatchApplier


def test_patch_applier_apply_and_rollback(tmp_path):
    source_file = tmp_path / "calculator.py"

    original_code = """def add(a, b):
    return a / b
"""

    source_file.write_text(
        original_code,
        encoding="utf-8",
    )

    suggestion = RepairSuggestion(
        file_path=str(source_file),
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

    applier = PatchApplier()

    result = applier.apply(patch)

    assert result["applied"] is True

    updated_code = source_file.read_text(
        encoding="utf-8"
    )

    assert "if b == 0:" in updated_code
    assert "Cannot divide by zero" in updated_code

    assert Path(result["backup_path"]).exists()

    applier.rollback(result)

    restored_code = source_file.read_text(
        encoding="utf-8"
    )

    assert restored_code == original_code
    assert not Path(result["backup_path"]).exists()

    print("\nPATCH APPLIER TEST PASSED")