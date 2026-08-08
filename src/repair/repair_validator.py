from pathlib import Path
import subprocess
import sys


class RepairValidator:

    def validate(self, project_path):
        project_path = Path(project_path)

        if not project_path.exists():
            return {
                "passed": False,
                "return_code": None,
                "stdout": "",
                "stderr": f"Project not found: {project_path}",
            }

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
            )

            return {
                "passed": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as exc:
            return {
                "passed": False,
                "return_code": None,
                "stdout": "",
                "stderr": str(exc),
            }