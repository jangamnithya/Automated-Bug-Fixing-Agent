from src.localizer.bug_localizer import BugLocalizer
from src.models.bug_report import FailedTest


def test_multi_file_candidate_ranking():
    failed_test = FailedTest(
        name="test_add",
        error="ZeroDivisionError: division by zero",
        traceback="calculator.py:2",
        file_path="calculator.py",
        line_number=2,
        function_name="add",
        exception_type="ZeroDivisionError",
    )

    candidate_files = [
        "sample_project/calculator.py",
        "sample_project/helper.py",
    ]

    localizer = BugLocalizer()

    ranked = localizer.rank_candidates(
        failed_test,
        candidate_files,
    )

    print("\n===== MULTI-FILE TEST =====")

    for candidate in ranked:
        print("File:", candidate["file_path"])
        print("Score:", candidate["score"])
        print("Reasons:", candidate["reasons"])

    assert ranked[0]["file_path"].endswith("calculator.py")
    assert ranked[0]["score"] == 100


if __name__ == "__main__":
    test_multi_file_candidate_ranking()
    print("\nMULTI-FILE TEST PASSED")