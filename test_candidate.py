from src.localizer.candidate import CandidateFinder
from src.models.bug_report import BugReport, FailedTest


def test_candidate_finder():
    bug_report = BugReport(
        total_tests=1,
        passed=0,
        failed=1,
        failed_tests=[
            FailedTest(
                name="test_add",
                error="division by zero",
                traceback="calculator.py:2",
                file_path="sample_project\\calculator.py",
                line_number=2,
                function_name="add",
                exception_type="ZeroDivisionError",
            )
        ],
    )

    repository_files = [
        "sample_project\\calculator.py",
    ]

    finder = CandidateFinder()

    candidates = finder.find_candidates(
        bug_report,
        repository_files,
    )

    assert len(candidates) == 1
    assert candidates[0] == "sample_project\\calculator.py"