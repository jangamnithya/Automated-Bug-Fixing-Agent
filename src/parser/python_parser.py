import re

from src.models.bug_report import FailedTest


class StackTraceParser:

    def parse(self, failed_test: FailedTest) -> FailedTest:

        traceback = failed_test.traceback


        # File path + line number
        file_match = re.search(
            r"([\w\\\/.\-_]+\.py):(\d+)",
            traceback
        )

        if file_match:
            failed_test.file_path = file_match.group(1)
            failed_test.line_number = int(file_match.group(2))


        # Function name
        function_match = re.search(
            r"def\s+(\w+)",
            traceback
        )

        if function_match:
            failed_test.function_name = function_match.group(1)


        # Exception type
        exception_match = re.search(
            r"(\w+(?:Error|Exception))",
            traceback
        )

        if exception_match:
            failed_test.exception_type = exception_match.group(1)


        # Error message
        error_match = re.search(
            r"E\s+(.+)",
            traceback
        )

        if error_match:
            failed_test.error = error_match.group(1).strip()


        return failed_test