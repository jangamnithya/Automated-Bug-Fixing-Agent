from pathlib import Path


class PatchGenerator:
    """Generate a simple source-code patch from a repair suggestion."""

    def generate(self, suggestion):
        file_path = Path(suggestion.file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file not found: {file_path}"
            )

        lines = file_path.read_text(encoding="utf-8").splitlines()

        line_number = suggestion.line_number

        if line_number < 1 or line_number > len(lines):
            raise ValueError(
                f"Invalid line number: {line_number}"
            )

        original_line = lines[line_number - 1]

        if "division" in suggestion.problem.lower():
            indent = original_line[: len(original_line) - len(original_line.lstrip())]

            replacement = (
                f"{indent}if b == 0:\n"
                f"{indent}    raise ValueError('Cannot divide by zero')\n"
                f"{indent}{original_line.lstrip()}"
            )

            return {
                "file_path": str(file_path),
                "line_number": line_number,
                "original": original_line,
                "replacement": replacement,
            }

        return {
            "file_path": str(file_path),
            "line_number": line_number,
            "original": original_line,
            "replacement": original_line,
        }