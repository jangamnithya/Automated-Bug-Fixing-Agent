from pathlib import Path

from src.runner.test_runner import TestRunner
from src.localizer.repository_scanner import RepositoryScanner
from src.localizer.candidate import CandidateFinder
from src.localizer.bug_localizer import BugLocalizer
from src.analyzer.code_context import CodeContextExtractor
from src.analyzer.fault_analyzer import FaultAnalyzer


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
        test_dirs=["tests/"],
    )

    report = runner.run_tests(str(project_path))

    print("\n===== Bug Report =====")
    print(f"Total Tests : {report.total_tests}")
    print(f"Passed      : {report.passed}")
    print(f"Failed      : {report.failed}")

    # ---------------------------------------------------------
    # 3. Show failed test details
    # ---------------------------------------------------------
    if not report.failed_tests:
        print("\nNo failed tests found.")
        return

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
        repository_files,
    )

    print("\n===== Bug Candidates =====")

    if not candidates:
        print("No candidates found.")
        return

    for candidate in candidates:
        print(candidate)

    # ---------------------------------------------------------
    # 6. Candidate ranking
    # ---------------------------------------------------------
    localizer = BugLocalizer()

    print("\n===== Ranked Candidates =====")

    for failed_test in report.failed_tests:

        ranked_candidates = localizer.rank_candidates(
            failed_test,
            candidates,
        )

        if not ranked_candidates:
            print("No ranked candidates found.")
            continue

        for index, candidate in enumerate(
            ranked_candidates,
            start=1,
        ):
            print("\n------------------------------")
            print(f"Rank       : {index}")
            print(f"File       : {candidate['file_path']}")
            print(f"Score      : {candidate['score']}")
            print("Reasons    :")

            for reason in candidate["reasons"]:
                print(f"  - {reason}")

        print("------------------------------")

        # -----------------------------------------------------
        # 7. Code context extraction
        # -----------------------------------------------------
        top_candidate = ranked_candidates[0]

        file_path = top_candidate["file_path"]
        line_number = failed_test.line_number

        print("\n===== Code Context =====")

        if line_number is None:
            print(
                "Cannot extract context: "
                "line number is unavailable."
            )
            continue

        context_extractor = CodeContextExtractor()

        context_result = context_extractor.extract(
            file_path=file_path,
            line_number=line_number,
            context_lines=3,
        )

        print(
            f"File Path      : "
            f"{context_result['file_path']}"
        )
        print(
            f"Target Line    : "
            f"{context_result['target_line']}"
        )
        print("Source Context :")

        for line in context_result["context"]:
            marker = ">>>" if line["is_target"] else "   "

            print(
                f"{marker} "
                f"{line['line_number']:>4} | "
                f"{line['code']}"
            )

        # -----------------------------------------------------
        # 8. Fault analysis
        # -----------------------------------------------------
        exception_type = failed_test.exception_type

        if exception_type is None:
            print("\n===== Fault Analysis =====")
            print(
                "Cannot analyze fault: "
                "exception type is unavailable."
            )
            continue

        analyzer = FaultAnalyzer()

        analysis = analyzer.analyze(
            file_path=file_path,
            line_number=line_number,
            exception_type=exception_type,
        )

        print("\n===== Fault Analysis =====")
        print(
            f"File Path      : "
            f"{analysis['file_path']}"
        )
        print(
            f"Line Number    : "
            f"{analysis['line_number']}"
        )
        print(
            f"Exception Type : "
            f"{analysis['exception_type']}"
        )
        print(
            f"Issue          : "
            f"{analysis['issue']}"
        )

        print("Evidence       :")

        for evidence in analysis["evidence"]:
            print(f"  - {evidence}")


if __name__ == "__main__":
    main()