from pathlib import Path
import shutil

from src.models.repair_suggestion import RepairSuggestion
from src.repair.patch_generator import PatchGenerator


def test_generated_patch_fixes_zero_division(tmp_path):
    source_file = tmp_path / "calculator.py"

    source_file.write_text(
        """def add(a, b):
    return a / b
""",
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

    lines = source_file.read_text(encoding="utf-8").splitlines()

    replacement_lines = patch["replacement"].splitlines()

    lines[
        patch["line_number"] - 1:
        patch["line_number"]
    ] = replacement_lines

    source_file.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )

    updated_code = source_file.read_text(encoding="utf-8")

    assert "if b == 0:" in updated_code
    assert "Cannot divide by zero" in updated_code

    compile(updated_code, str(source_file), "exec")

    namespace = {}
    exec(updated_code, namespace)

    try:
        namespace["add"](10, 0)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert str(error) == "Cannot divide by zero"

    assert namespace["add"](10, 2) == 5

    print("\nPATCH APPLICATION TEST PASSED")