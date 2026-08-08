import subprocess
from pathlib import Path


class RepairValidator:
    """Run project tests and determine whether a repair is valid."""

    def validate(self, project_path):
        project_path = Path(project_path)

        if not project_path.exists():
            raise FileNotFoundError(
                f"Project path not found: {project_path}"
            )

        result = subprocess.run(
            ["pytest", "-q"],
            cwd=str(project_path),
            capture_output=True,
            text=True,
        )

        return {
            "passed": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }