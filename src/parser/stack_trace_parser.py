"""
Stack trace parser for pytest failures.

Extracts:
- exception type
- error message
- file path
- line number
- function name
- frame status

The parser walks all traceback frames and selects the deepest
application frame while excluding test and conftest files.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from src.models.bug_report import FailedTest, FrameStatus


@dataclass
class _Frame:
    file_path: str
    line_number: int
    context_line: str


class StackTraceParser:
    """
    Parses pytest traceback output and identifies the relevant
    application frame.
    """

    _FRAME_LINE = re.compile(
        r"^(?P<path>[\w\-./\\]+\.py):"
        r"(?P<line>\d+):\s*"
        r"(?:in\s+(?P<func>\w+)|(?P<exc>\w+))?\s*$",
        re.MULTILINE,
    )

    _EXCEPTION_LINE = re.compile(
        r"^E\s+(?P<exc_type>\w+(?:Error|Exception|Warning))"
        r"(?:\s*:\s*(?P<msg>.*))?$",
        re.MULTILINE,
    )

    _ASSERTION_LINE = re.compile(
        r"^E\s+assert\b",
        re.MULTILINE,
    )

    _DEF_LINE = re.compile(
        r"^\s*def\s+(\w+)\s*\(",
        re.MULTILINE,
    )

    def __init__(
        self,
        project_source_dirs: List[str],
        test_dirs: List[str],
        conftest_filenames: Optional[List[str]] = None,
    ):
        self.project_source_dirs = [
            d.rstrip("/\\") for d in project_source_dirs
        ]

        self.test_dirs = [
            d.rstrip("/\\") for d in test_dirs
        ]

        self.conftest_filenames = (
            conftest_filenames or ["conftest.py"]
        )

    def parse(self, failed_test: FailedTest) -> FailedTest:
        """
        Parse one failed test traceback.
        """

        traceback = failed_test.traceback

        if not traceback or not traceback.strip():
            failed_test.frame_status = FrameStatus.PARSE_FAILED
            return failed_test

        # ---------------------------------------------------------
        # Exception type + error message
        # ---------------------------------------------------------

        exc_match = self._EXCEPTION_LINE.search(traceback)

        if exc_match:
            failed_test.exception_type = exc_match.group(
                "exc_type"
            )

            # IMPORTANT:
            # AssertionError may contain several E-prefixed lines.
            # Therefore we must NOT only take the first message.
            if failed_test.exception_type == "AssertionError":
                failed_test.error = (
                    self._extract_multiline_error(traceback)
                )
            else:
                failed_test.error = (
                    exc_match.group("msg") or ""
                ).strip()

        elif self._ASSERTION_LINE.search(traceback):
            failed_test.exception_type = "AssertionError"

            failed_test.error = (
                self._extract_multiline_error(traceback)
            )

        else:
            failed_test.frame_status = FrameStatus.PARSE_FAILED
            return failed_test

        # ---------------------------------------------------------
        # Extract ALL traceback frames.
        # ---------------------------------------------------------

        frames = self._extract_frames(traceback)

        # ---------------------------------------------------------
        # Select deepest application frame.
        # ---------------------------------------------------------

        application_frame = self._select_application_frame(
            frames
        )

        if application_frame is not None:

            failed_test.file_path = (
                application_frame.file_path
            )

            failed_test.line_number = (
                application_frame.line_number
            )

            failed_test.function_name = (
                self._function_name_for(
                    application_frame,
                    frames,
                    traceback,
                )
            )

            failed_test.frame_status = (
                FrameStatus.APPLICATION_FRAME_FOUND
            )

        else:

            failed_test.file_path = None
            failed_test.line_number = None
            failed_test.function_name = None

            failed_test.frame_status = (
                FrameStatus.NO_APPLICATION_FRAME
            )

        return failed_test

    def _extract_frames(
        self,
        traceback: str,
    ) -> List[_Frame]:
        """
        Extract every traceback frame.

        IMPORTANT:
        There is intentionally NO break here.
        The loop processes every frame.
        """

        frames: List[_Frame] = []

        for match in self._FRAME_LINE.finditer(traceback):

            frames.append(
                _Frame(
                    file_path=match.group("path"),
                    line_number=int(match.group("line")),
                    context_line=match.group(0),
                )
            )

        return frames

    def _select_application_frame(
        self,
        frames: List[_Frame],
    ) -> Optional[_Frame]:
        """
        Search from the deepest traceback frame backwards.

        Test and conftest files are excluded.
        """

        for frame in reversed(frames):

            if self._is_excluded(frame.file_path):
                continue

            if self._is_application_frame(
                frame.file_path
            ):
                return frame

        return None

    def _is_excluded(
        self,
        file_path: str,
    ) -> bool:
        """
        Check whether the frame belongs to tests or conftest.
        """

        normalized = file_path.replace("\\", "/")

        if any(
            normalized.startswith(directory)
            for directory in self.test_dirs
        ):
            return True

        filename = normalized.rsplit("/", 1)[-1]

        if filename in self.conftest_filenames:
            return True

        return False

    def _is_application_frame(
        self,
        file_path: str,
    ) -> bool:
        """
        Check whether a frame belongs to application code.
        """

        normalized = file_path.replace("\\", "/")

        return any(
            normalized.startswith(directory)
            for directory in self.project_source_dirs
        )

    def _function_name_for(
        self,
        frame: _Frame,
        all_frames: List[_Frame],
        traceback: str,
    ) -> Optional[str]:
        """
        Determine the function associated with a traceback frame.
        """

        # ---------------------------------------------------------
        # Attempt 1:
        # Frame contains "in function_name".
        # ---------------------------------------------------------

        match = self._FRAME_LINE.match(
            frame.context_line
        )

        if match and match.group("func"):
            return match.group("func")

        # ---------------------------------------------------------
        # Attempt 2:
        # Look for another frame with the same location.
        # ---------------------------------------------------------

        for other in all_frames:

            if other is frame:
                continue

            if (
                other.file_path == frame.file_path
                and other.line_number
                == frame.line_number
            ):

                other_match = self._FRAME_LINE.match(
                    other.context_line
                )

                if (
                    other_match
                    and other_match.group("func")
                ):
                    return other_match.group("func")

        # ---------------------------------------------------------
        # Attempt 3:
        # Find nearest preceding function definition.
        # ---------------------------------------------------------

        frame_position = traceback.find(
            frame.context_line
        )

        if frame_position == -1:
            return None

        preceding_text = traceback[:frame_position]

        definitions = list(
            self._DEF_LINE.finditer(preceding_text)
        )

        if definitions:
            return definitions[-1].group(1)

        return None

    def _extract_multiline_error(
        self,
        traceback: str,
    ) -> str:
        """
        Extract the COMPLETE pytest assertion error.

        Example:

        E   AssertionError: assert {'a': 1} == {'a': 2}
        E     Differing items:
        E     {'a': 1} != {'a': 2}

        All E-prefixed lines are collected.

        IMPORTANT:
        The loop does not exit after the first E line.
        """

        lines = traceback.splitlines()

        collected: List[str] = []

        collecting = False

        for line in lines:

            stripped = line.strip()

            # -----------------------------------------------------
            # Collect every E-prefixed line.
            # -----------------------------------------------------

            if stripped.startswith("E"):

                content = stripped[1:].strip()

                if content:
                    collecting = True
                    collected.append(content)

            # -----------------------------------------------------
            # Once collection begins, ignore blank lines.
            # -----------------------------------------------------

            elif collecting:

                if not stripped:
                    continue

                # Real non-E content means the E-block ended.
                break

        return "\n".join(collected)