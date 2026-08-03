from pathlib import Path

from src.runner.test_runner import TestRunner


def main():
    print("========== Bug Fixing Agent ==========\n")

    project_path = Path(__file__).parent.parent / "sample_project"

    runner = TestRunner()

    report = runner.run_tests(str(project_path))

    print("\n===== Bug Report =====")

    print(f"Total Tests : {report.total_tests}")
    print(f"Passed      : {report.passed}")
    print(f"Failed      : {report.failed}")

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


if __name__ == "__main__":
    main()