from enum import Enum

from pydantic import BaseModel


class FrameStatus(str, Enum):
    """
    str, Enum (not plain Enum) so this serializes cleanly to JSON as a
    plain string via Pydantic, and compares equal to string literals if
    ever needed -- avoids the common Pydantic gotcha where a plain Enum
    field dumps as FrameStatus.NO_APPLICATION_FRAME instead of the
    string "no_application_frame".
    """
    NOT_YET_PARSED = "not_yet_parsed"
    APPLICATION_FRAME_FOUND = "application_frame_found"
    NO_APPLICATION_FRAME = "no_application_frame"   # valid outcome: pure
                                                      # assertion in test
                                                      # body, no application
                                                      # call in the traceback
    PARSE_FAILED = "parse_failed"                     # traceback didn't
                                                        # match expected
                                                        # pytest shape


class FailedTest(BaseModel):
    name: str
    error: str
    traceback: str | None = None
    file_path: str | None = None
    line_number: int | None = None
    function_name: str | None = None
    exception_type: str | None = None
    frame_status: FrameStatus = FrameStatus.NOT_YET_PARSED


class BugReport(BaseModel):
    total_tests: int
    passed: int
    failed: int
    failed_tests: list[FailedTest]