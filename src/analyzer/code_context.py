from pathlib import Path


class CodeContextExtractor:
    """Extract source-code context around a suspicious line."""

    def extract(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 3,
    ) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Source file not found: {file_path}"
            )

        lines = path.read_text(encoding="utf-8").splitlines()

        if line_number < 1 or line_number > len(lines):
            raise ValueError(
                f"Line number {line_number} is outside "
                f"the file range 1-{len(lines)}"
            )

        start = max(1, line_number - context_lines)
        end = min(len(lines), line_number + context_lines)

        context = []

        for number in range(start, end + 1):
            context.append({
                "line_number": number,
                "code": lines[number - 1],
                "is_target": number == line_number,
            })

        return {
            "file_path": str(path),
            "target_line": line_number,
            "context": context,
        }