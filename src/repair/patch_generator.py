from pathlib import Path


class PatchGenerator:

    def generate(self, suggestion):
        file_path = Path(suggestion.file_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file not found: {file_path}"
            )

        lines = file_path.read_text(
            encoding="utf-8"
        ).splitlines()

        line_number = suggestion.line_number

        if line_number < 1 or line_number > len(lines):
            raise ValueError(
                f"Invalid line number: {line_number}"
            )

        original_line = lines[line_number - 1]

        # Preserve indentation from the original source line.
        indentation = original_line[
            : len(original_line) - len(original_line.lstrip())
        ]

        # ZeroDivisionError repair
        if "division" in suggestion.problem.lower():

            if original_line.strip() == "return a / b":

                replacement = (
                    f"{indentation}if b == 0:\n"
                    f"{indentation}    "
                    "raise ValueError('Cannot divide by zero')\n"
                    f"{indentation}return a / b"
                )

            else:
                replacement = original_line

        # Generic fallback
        else:
            replacement = original_line

        return {
            "file_path": str(file_path),
            "line_number": line_number,
            "original": original_line,
            "replacement": replacement,
        }