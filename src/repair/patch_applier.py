from pathlib import Path
import shutil


class PatchApplier:
    """Apply a generated patch and provide rollback support."""

    def apply(self, patch):
        file_path = Path(patch["file_path"])

        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file not found: {file_path}"
            )

        line_number = patch["line_number"]

        lines = file_path.read_text(
            encoding="utf-8"
        ).splitlines()

        if line_number < 1 or line_number > len(lines):
            raise ValueError(
                f"Invalid line number: {line_number}"
            )

        original_line = lines[line_number - 1]

        if original_line != patch["original"]:
            raise ValueError(
                "Source line does not match the expected "
                "original line."
            )

        backup_path = file_path.with_suffix(
            file_path.suffix + ".bak"
        )

        shutil.copy2(file_path, backup_path)

        replacement_lines = patch["replacement"].splitlines()

        lines[
            line_number - 1:
            line_number
        ] = replacement_lines

        file_path.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

        return {
            "file_path": str(file_path),
            "backup_path": str(backup_path),
            "applied": True,
        }

    def rollback(self, result):
        file_path = Path(result["file_path"])
        backup_path = Path(result["backup_path"])

        if not backup_path.exists():
            raise FileNotFoundError(
                f"Backup file not found: {backup_path}"
            )

        shutil.copy2(backup_path, file_path)
        backup_path.unlink()

        return True