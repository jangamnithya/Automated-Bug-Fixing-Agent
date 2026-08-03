"""
Same interfaces as before:
  - main.py: TestRunner() no-arg constructor, run_tests(project_path).
  - FailedTest(BaseModel): `name`, `error: str` (required, non-optional).

STILL ASSUMES you've added `frame_status: FrameStatus | None = None` to
your FailedTest model. If not, tell me and parser.parse() switches to
returning (FailedTest, FrameStatus) as a tuple instead.

FIX APPLIED: the pasted version had `block_map = {...}` indented one
level deeper than the rest of _build_scoped_failed_tests -- an
IndentationError, confirmed by compiling the isolated fragment before
writing this file. Corrected below; nothing else changed from the prior
version.
"""

import logging
import re
import subprocess
import sys
from typing import List, Optional, Tuple

from src.models.bug_report import BugReport, FailedTest
from src.parser.stack_trace_parser import StackTraceParser, FrameStatus

logger = logging.getLogger(__name__)


_BANNER_PATTERN = re.compile(
    r"^_{5,}\s+(.+?)\s+_{5,}\s*$",
    re.MULTILINE,
)


def _split_into_test_blocks(output: str) -> List[Tuple[str, str]]:
    matches = list(_BANNER_PATTERN.finditer(output))
    if not matches:
        return []
    blocks = []
    for i, match in enumerate(matches):
        test_name = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(output)
        blocks.append((test_name, output[start:end]))
    return blocks


class TestRunner:
    def __init__(self):
        self.parser = StackTraceParser(
            project_source_dirs=["src/"],   # [ASSUMPTION] still unverified
            test_dirs=["tests/"],           # [ASSUMPTION] still unverified
        )

    def run_tests(self, project_path: str) -> BugReport:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", project_path],
            # Using `sys.executable -m pytest` instead of a bare "pytest"
            # avoids depending on pytest being on PATH as a standalone
            # executable -- confirmed necessary: bare "pytest" produced
            # FileNotFoundError [WinError 2] even though `python -m pytest`
            # worked fine in the same terminal. -v is still an assumption
            # about your original invocation, not yet independently verified.
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr

        if result.returncode not in (0, 1):
            raise RuntimeError(
                f"pytest did not run cleanly (exit code {result.returncode}). "
                f"stderr: {result.stderr[:500]}"
            )

        total_match = re.search(r"collected (\d+) item", output)
        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)

        total_tests = int(total_match.group(1)) if total_match else 0
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0

        if passed + failed != total_tests:
            logger.warning(
                "passed (%d) + failed (%d) != total_tests (%d) -- possible "
                "collection error or summary format mismatch.",
                passed, failed, total_tests,
            )

        failed_test_names = [name for name, _ in _split_into_test_blocks(output)]
        failed_tests = self._build_scoped_failed_tests(output, failed_test_names)

        return BugReport(
            total_tests=total_tests,
            passed=passed,
            failed=failed,
            failed_tests=failed_tests,
        )

    def _build_scoped_failed_tests(
        self,
        output: str,
        failed_test_names: List[str],
    ) -> List[FailedTest]:
        blocks = _split_into_test_blocks(output)

        if failed_test_names and not blocks:
            raise RuntimeError(
                "Found failed tests but could not split output into "
                "per-test blocks. Confirm pytest is invoked with -v."
            )

        block_map = {name: block for name, block in blocks}
        failed_tests: List[FailedTest] = []

        for name in failed_test_names:
            block = block_map.get(name)
            if block is None:
                logger.warning(
                    "Could not isolate traceback block for test '%s'.", name
                )
                continue

            failed_test = FailedTest(
                name=name,
                error="",
                traceback=block,
            )
            failed_test = self.parser.parse(failed_test)

            if getattr(failed_test, "frame_status", None) == FrameStatus.PARSE_FAILED:
                logger.warning(
                    "StackTraceParser could not parse traceback for '%s' -- "
                    "'error' remains '' rather than a real message. Check "
                    "frame_status if present, don't rely on error=='' alone.",
                    name,
                )

            failed_tests.append(failed_test)

        return failed_tests