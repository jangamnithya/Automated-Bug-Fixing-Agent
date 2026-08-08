import pytest

from src.models.bug_report import FailedTest, FrameStatus
from src.parser.stack_trace_parser import StackTraceParser


def make_parser():
    return StackTraceParser(
        project_source_dirs=["src"],
        test_dirs=["tests"],
    )


def test_application_frame_found():
    traceback = """
________________________________ test_add ________________________________

def test_add():
    result = validate_and_add(2, 3)

src/calculator.py:8: in validate_and_add
    return add(a, b)

def add(a, b):
>   return a / b
E   ZeroDivisionError: division by zero

src/calculator.py:3: ZeroDivisionError
"""

    failed = FailedTest(
        name="test_add",
        error="",
        traceback=traceback,
    )

    parser = make_parser()
    result = parser.parse(failed)

    assert result.frame_status == FrameStatus.APPLICATION_FRAME_FOUND
    assert result.file_path == "src/calculator.py"
    assert result.line_number == 3
    assert result.exception_type == "ZeroDivisionError"
    assert result.function_name == "add"
    assert result.error == "division by zero"


def test_no_application_frame():
    traceback = """
________________________________ test_add ________________________________

def test_add():
>   assert 2 + 2 == 5
E   assert 4 == 5

tests/test_calculator.py:10: AssertionError
"""

    failed = FailedTest(
        name="test_add",
        error="",
        traceback=traceback,
    )

    parser = make_parser()
    result = parser.parse(failed)

    assert result.frame_status == FrameStatus.NO_APPLICATION_FRAME
    assert result.file_path is None
    assert result.line_number is None
    assert result.function_name is None
    assert result.exception_type == "AssertionError"


def test_parse_failed_for_invalid_traceback():
    failed = FailedTest(
        name="test_add",
        error="",
        traceback="this is not a pytest traceback",
    )

    parser = make_parser()
    result = parser.parse(failed)

    assert result.frame_status == FrameStatus.PARSE_FAILED


def test_empty_traceback():
    failed = FailedTest(
        name="test_add",
        error="",
        traceback="",
    )

    parser = make_parser()
    result = parser.parse(failed)

    assert result.frame_status == FrameStatus.PARSE_FAILED


def test_multiline_assertion_message():
    traceback = """
________________________________ test_add ________________________________

def test_add():
>   assert {"a":1} == {"a":2}
E   AssertionError: assert {'a': 1} == {'a': 2}
E     Differing items:
E     {'a': 1} != {'a': 2}

tests/test_calc.py:5: AssertionError
"""

    failed = FailedTest(
        name="test_add",
        error="",
        traceback=traceback,
    )

    parser = make_parser()
    result = parser.parse(failed)

    assert result.exception_type == "AssertionError"
    assert "Differing items" in result.error


def test_conftest_is_excluded():
    traceback = """
________________________________ test_add ________________________________

conftest.py:15: in sample_fixture
    raise RuntimeError()

E   RuntimeError: fixture failed

conftest.py:15: RuntimeError
"""

    failed = FailedTest(
        name="test_add",
        error="",
        traceback=traceback,
    )

    parser = make_parser()
    result = parser.parse(failed)

    assert result.frame_status == FrameStatus.NO_APPLICATION_FRAME