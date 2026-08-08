from pathlib import Path

from src.models.bug_report import BugReport


class CandidateFinder:

    def find_candidates(self, bug_report: BugReport, repository_files):
        candidates = []

        for failed_test in bug_report.failed_tests:

            if failed_test.file_path is None:
                continue

            failed_file = Path(failed_test.file_path).name

            for file_path in repository_files:

                if Path(file_path).name == failed_file:
                    if file_path not in candidates:
                        candidates.append(file_path)

        return candidates