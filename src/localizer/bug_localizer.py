from pathlib import Path


class BugLocalizer:

    def rank_candidates(self, failed_test, candidate_files):
        ranked_candidates = []

        for file_path in candidate_files:
            score = 0
            reasons = []

            # 1. File path match
            if failed_test.file_path:
                failed_file = Path(failed_test.file_path).name
                candidate_file = Path(file_path).name

                if failed_file == candidate_file:
                    score += 50
                    reasons.append("traceback file match")

            # 2. Function match
            if failed_test.function_name:
                if self._function_exists(
                    file_path,
                    failed_test.function_name
                ):
                    score += 30
                    reasons.append("function match")

            # 3. Line number available
            if failed_test.line_number is not None:
                score += 20
                reasons.append("line number available")

            ranked_candidates.append({
                "file_path": file_path,
                "score": score,
                "reasons": reasons
            })

        ranked_candidates.sort(
            key=lambda candidate: candidate["score"],
            reverse=True
        )

        return ranked_candidates

    def _function_exists(self, file_path, function_name):
        try:
            source = Path(file_path).read_text(encoding="utf-8")

            return (
                f"def {function_name}(" in source
                or f"async def {function_name}(" in source
            )

        except (OSError, UnicodeDecodeError):
            return False