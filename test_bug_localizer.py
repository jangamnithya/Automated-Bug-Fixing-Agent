from src.localizer.bug_localizer import BugLocalizer
from src.models.bug_report import FailedTest


def test_bug_localizer():
    failed_test = FailedTest(
        name="test_add",
        error="ZeroDivisionError: division by zero",
        traceback="calculator.py:2",
        file_path="sample_project/calculator.py",
        line_number=2,
        function_name="add",
        exception_type="ZeroDivisionError",
    )

    candidate_files = [
        "sample_project/calculator.py"
    ]

    localizer = BugLocalizer()

    ranked = localizer.rank_candidates(
        failed_test,
        candidate_files
    )

    assert len(ranked) == 1

    assert ranked[0]["file_path"] == "sample_project/calculator.py"

    assert ranked[0]["score"] == 100

    assert "traceback file match" in ranked[0]["reasons"]

    assert "function match" in ranked[0]["reasons"]

    assert "line number available" in ranked[0]["reasons"]
