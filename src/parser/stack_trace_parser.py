"""
Fix for Blockers B2-B5, B7 (StackTraceParser) and B6 (single extraction pass).

Replaces the four independent, unanchored re.search calls with a bottom-up
walk over the traceback's actual frame structure. Also replaces the
"return same object with fields possibly None" pattern with an explicit
FrameStatus, so "no application frame exists" is distinguishable from
"parser hasn't run" or "parser failed" -- per B5 and the tri-state
decision from earlier in this review.

Assumes pytest's default verbose traceback format:

    _________________________________ test_add __________________________________

    def test_add():
        result = validate_and_add(2, 3)
    >       assert result == 6
    E       assert 5 == 6

    tests/test_calculator.py:12: AssertionError

    ------------------------------- Captured log --------------------------------
    ...

For a multi-frame case (exception raised inside a helper), pytest shows
each frame in the call chain, most recent last, e.g.:

    def test_add():
        result = validate_and_add(2, 3)

    src/calculator.py:8: in validate_and_add
        return add(a, b)
    src/calculator.py:3: in add
    >       return a / b
    E       ZeroDivisionError: division by zero

    src/calculator.py:3: ZeroDivisionError
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from src.models.bug_report import FailedTest, FrameStatus
# FrameStatus now lives in bug_report.py, as a real Pydantic-validated
# field on FailedTest, not a locally-defined enum bolted onto the
# instance after the fact. Importing it from there (not redefining it
# here) is what makes failed_test.frame_status = FrameStatus.X actually
# go through Pydantic's field validation instead of silently succeeding
# as a plain attribute set that Pydantic never sees.


@dataclass
class _Frame:
    file_path: str
    line_number: int
    context_line: str  # the line of code at that frame, if pytest printed it


class StackTraceParser:
    """
    Configured with the project's source root and the test file(s)/dirs
    to exclude, so it can distinguish "application code" from
    "test code" and "everything else" (stdlib, site-packages).
    """

    # Frame lines look like: path/to/file.py:12: in function_name
    # or, for the final frame:  path/to/file.py:12: ExceptionType
    _FRAME_LINE = re.compile(
        r"^(?P<path>[\w\-./\\]+\.py):(?P<line>\d+):\s*(?:in\s+(?P<func>\w+)|(?P<exc>\w+))?\s*$",
        re.MULTILINE,
    )

    # The line immediately after the E marker holds the real exception.
    # Structurally anchored: must start the line, not appear anywhere in it.
    _EXCEPTION_LINE = re.compile(
        r"^E\s+(?P<exc_type>\w+(?:Error|Exception|Warning))(?:\s*:\s*(?P<msg>.*))?$",
        re.MULTILINE,
    )

    # Fallback for bare `assert x == y` with no explicit exception class printed --
    # pytest still shows "E       assert ..." but there's no ErrorType token.
    _ASSERTION_LINE = re.compile(r"^E\s+assert\b", re.MULTILINE)

    def __init__(
        self,
        project_source_dirs: List[str],
        test_dirs: List[str],
        conftest_filenames: Optional[List[str]] = None,
    ):
        """
        project_source_dirs: e.g. ["src/"] -- frames inside these count as
            "application frames" and are what we're hunting for.
        test_dirs: e.g. ["tests/"] -- frames inside these are excluded,
            same as site-packages/stdlib, even though they're part of
            "your code" in a broader sense. A failure whose only frame
            is inside test_dirs is exactly the NO_APPLICATION_FRAME case.
        conftest_filenames: filenames (not full paths) to treat as
            excluded the same as test files -- default ["conftest.py"].
            This is B3: a fixture frame must not be mistaken for an
            application frame just because it's outside test_dirs.
        """
        self.project_source_dirs = [d.rstrip("/\\") for d in project_source_dirs]
        self.test_dirs = [d.rstrip("/\\") for d in test_dirs]
        self.conftest_filenames = conftest_filenames or ["conftest.py"]

    def parse(self, failed_test: FailedTest) -> FailedTest:
        """
        Single-pass extraction: error, exception_type, and frame-derived
        fields (file_path, line_number, function_name) are all set here,
        together, satisfying B6. failed_test.traceback must already be
        scoped to this one test (TestRunner's job, not this method's --
        if it isn't, this will misbehave the same way the old code did,
        so don't call this on unscoped output).
        """
        traceback = failed_test.traceback

        if not traceback or not traceback.strip():
            failed_test.frame_status = FrameStatus.PARSE_FAILED
            return failed_test

        # --- Exception type + error message: anchored to the E line ---
        exc_match = self._EXCEPTION_LINE.search(traceback)
        if exc_match:
            failed_test.exception_type = exc_match.group("exc_type")
            failed_test.error = (exc_match.group("msg") or "").strip()
        elif self._ASSERTION_LINE.search(traceback):
            # Bare assert with no named exception class -- pytest's own
            # behavior for plain `assert x == y`. Not a parse failure.
            failed_test.exception_type = "AssertionError"
            # Grab the full E-block for the error message (may span
            # multiple E-prefixed lines for a multi-line assert diff).
            failed_test.error = self._extract_multiline_error(traceback)
        else:
            # No E line at all -- traceback doesn't match expected pytest
            # verbose-mode shape. Don't guess; surface it.
            failed_test.frame_status = FrameStatus.PARSE_FAILED
            return failed_test

        # --- Frame walk: find the last application frame, bottom-up ---
        frames = self._extract_frames(traceback)
        application_frame = self._select_application_frame(frames)

        if application_frame is not None:
            failed_test.file_path = application_frame.file_path
            failed_test.line_number = application_frame.line_number
            failed_test.function_name = self._function_name_for(traceback, application_frame)
            failed_test.frame_status = FrameStatus.APPLICATION_FRAME_FOUND
        else:
            # Structurally valid traceback, but every frame is inside
            # test_dirs/conftest -- e.g. a bare assert in the test body
            # with no call into application code. This is B5's explicit
            # tri-state, not a silent None/None/None.
            failed_test.file_path = None
            failed_test.line_number = None
            failed_test.function_name = None
            failed_test.frame_status = FrameStatus.NO_APPLICATION_FRAME

        return failed_test

    def _extract_frames(self, traceback: str) -> List[_Frame]:
        """
        Walks all path:line: (in func|ExcType) lines in the order pytest
        printed them, which is call order (oldest call first, most recent
        last) -- matching a normal Python traceback's convention.
        """
        frames = []
        for m in self._FRAME_LINE.finditer(traceback):
            frames.append(
                _Frame(
                    file_path=m.group("path"),
                    line_number=int(m.group("line")),
                    context_line=m.group(0),
                )
            )
        return frames

    def _select_application_frame(self, frames: List[_Frame]) -> Optional[_Frame]:
        """
        Bottom-up walk (most recent frame first, matching where the
        actual failure occurred): skip frames inside test_dirs and
        conftest files, return the first remaining frame -- that's the
        deepest point in APPLICATION code the failure passed through.

        This directly implements B2/B3/B4: not "first regex match
        anywhere," but "last frame before failure, filtered to
        application source."
        """
        for frame in reversed(frames):
            if self._is_excluded(frame.file_path):
                continue
            if self._is_application_frame(frame.file_path):
                return frame
            # Frame is neither test/conftest nor recognized application
            # source (e.g. site-packages, stdlib) -- skip and keep walking.
        return None

    def _is_excluded(self, file_path: str) -> bool:
        normalized = file_path.replace("\\", "/")
        if any(normalized.startswith(d) for d in self.test_dirs):
            return True
        filename = normalized.rsplit("/", 1)[-1]
        if filename in self.conftest_filenames:
            return True
        return False

    def _is_application_frame(self, file_path: str) -> bool:
        normalized = file_path.replace("\\", "/")
        return any(normalized.startswith(d) for d in self.project_source_dirs)

    def _function_name_for(self, traceback: str, frame: "_Frame") -> Optional[str]:
        """
        Pull the function name directly from the SAME frame line that
        gave us file_path/line_number -- not a separate def-search
        across the whole blob (that was the def\\s+(\\w+) bug, B4).
        """
        pattern = re.compile(
            rf"^{re.escape(frame.file_path)}:{frame.line_number}:\s*in\s+(\w+)\s*$",
            re.MULTILINE,
        )
        m = pattern.search(traceback)
        return m.group(1) if m else None

    def _extract_multiline_error(self, traceback: str) -> str:
        """
        Bare asserts often produce multiple E-prefixed lines (pytest's
        assertion rewriting shows the diff). Collect all consecutive
        E lines starting from the first one, not just the first line.
        """
        lines = traceback.splitlines()
        collected = []
        collecting = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("E "):
                collecting = True
                collected.append(stripped[2:].strip())
            elif collecting:
                break
        return "\n".join(collected)