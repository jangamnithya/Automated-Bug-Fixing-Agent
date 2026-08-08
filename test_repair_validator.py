from src.repair.repair_validator import RepairValidator


def test_repair_validator_passes_for_valid_project(tmp_path):
    project = tmp_path / "sample_project"
    project.mkdir()

    (project / "calculator.py").write_text(
        """def add(a, b):
    return a + b
""",
        encoding="utf-8",
    )

    (project / "test_calculator.py").write_text(
        """from calculator import add


def test_add():
    assert add(2, 3) == 5
""",
        encoding="utf-8",
    )

    validator = RepairValidator()

    result = validator.validate(project)

    assert result["passed"] is True
    assert result["return_code"] == 0

    print("\nREPAIR VALIDATOR TEST PASSED")