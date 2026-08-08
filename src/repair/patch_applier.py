from pathlib import Path
import shutil


class PatchApplier:

    def apply(self, patch):
        file_path = Path(patch["file_path"])

        if not file_path.exists():
            raise FileNotFoundError(
                f"Source file not found: {file_path}"
            )

        line_number = patch["line_number"]
        original = patch["original"]
        replacement = patch["replacement"]

        # ---------------------------------------------
        # Create backup
        # ---------------------------------------------
        backup_path = file_path.with_suffix(
            file_path.suffix + ".bak"
        )

        shutil.copy2(file_path, backup_path)

        lines = file_path.read_text(
            encoding="utf-8"
        ).splitlines()

        if line_number < 1 or line_number > len(lines):
            raise ValueError(
                f"Invalid line number: {line_number}"
            )

        # Verify the expected original line
        if lines[line_number - 1].strip() != original.strip():
            raise ValueError(
                "Original source line does not match patch."
            )

        # ---------------------------------------------
        # Apply replacement
        # ---------------------------------------------
        indentation = len(lines[line_number - 1]) - len(
            lines[line_number - 1].lstrip()
        )

        base_indent = " " * indentation

        replacement_lines = replacement.splitlines()

        formatted_lines = []

        for index, replacement_line in enumerate(
            replacement_lines
        ):
            if index == 0:
                formatted_lines.append(
                    base_indent + replacement_line
                )
            else:
                # Preserve the indentation supplied
                # by the generated replacement.
                formatted_lines.append(
                    base_indent + replacement_line
                )

        new_lines = (
            lines[: line_number - 1]
            + formatted_lines
            + lines[line_number:]
        )

        file_path.write_text(
            "\n".join(new_lines) + "\n",
            encoding="utf-8",
        )

        return {
            "applied": True,
            "file_path": str(file_path),
            "backup_path": str(backup_path),
            "line_number": line_number,
        }

    def rollback(self, result):
        backup_path = Path(result["backup_path"])
        file_path = Path(result["file_path"])

        if not backup_path.exists():
            raise FileNotFoundError(
                f"Backup file not found: {backup_path}"
            )

        shutil.copy2(
            backup_path,
            file_path,
        )

        backup_path.unlink()

        return {
            "rolled_back": True,
            "file_path": str(file_path),
        }