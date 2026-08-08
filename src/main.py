from pathlib import Path

from src.runner.test_runner import TestRunner
from src.localizer.repository_scanner import RepositoryScanner
from src.localizer.candidate import CandidateFinder
from src.localizer.bug_localizer import BugLocalizer


def main():
    print("========== Bug Fixing Agent ==========\n")

    # ---------------------------------------------------------
    # 1. Project path
    # ---------------------------------------------------------
    project_path = Path(__file__).parent.parent / "sample_project"

    # ---------------------------------------------------------
    # 2. Run tests
    # ---------------------------------------------------------
    runner = TestRunner(
        project_source_dirs=[""],
        test_dirs=["tests/"]
    )

    report = runner.run_tests(str(project_path))

    print("\n===== Bug Report =====")
    print(f"Total Tests : {report.total_tests}")
    print(f"Passed      : {report.passed}")
    print(f"Failed      : {report.failed}")

    # ---------------------------------------------------------
    # 3. Show failed test details
    # ---------------------------------------------------------
    if report.failed_tests:
        print("\nFailed Test Details:")

        for test in report.failed_tests:
            print("\n==============================")
            print(f"Test Name      : {test.name}")
            print(f"Error          : {test.error}")
            print(f"Exception Type : {test.exception_type}")
            print(f"File Path      : {test.file_path}")
            print(f"Function Name  : {test.function_name}")
            print(f"Line Number    : {test.line_number}")
            print(f"Frame Status   : {test.frame_status.value}")
            print("==============================")

    else:
        print("\nNo failed tests found.")
        return

    # ---------------------------------------------------------
    # 4. Repository scanning
    # ---------------------------------------------------------
    scanner = RepositoryScanner()

    repository_files = scanner.scan(str(project_path))

    print("\n===== Repository Scan =====")
    print(f"Python Files Found : {len(repository_files)}")

    for file_path in repository_files:
        print(file_path)

    # ---------------------------------------------------------
    # 5. Candidate finding
    # ---------------------------------------------------------
    candidate_finder = CandidateFinder()

    candidates = candidate_finder.find_candidates(
        report,
        repository_files
    )

    print("\n===== Bug Candidates =====")

    if candidates:
        for candidate in candidates:
            print(candidate)
    else:
        print("No candidates found.")
        return

    # ---------------------------------------------------------
    # 6. Candidate ranking
    # ---------------------------------------------------------
    localizer = BugLocalizer()

    print("\n===== Ranked Candidates =====")

    for failed_test in report.failed_tests:

        ranked_candidates = localizer.rank_candidates(
            failed_test,
            candidates
        )

        if not ranked_candidates:
            print("No ranked candidates found.")
            continue

        for index, candidate in enumerate(
            ranked_candidates,
            start=1
        ):
            print("\n------------------------------")
            print(f"Rank       : {index}")
            print(f"File       : {candidate['file_path']}")
            print(f"Score      : {candidate['score']}")
            print(f"Reasons    :")

            for reason in candidate["reasons"]:
                print(f"  - {reason}")

        print("------------------------------")


if __name__ == "__main__":
    main()