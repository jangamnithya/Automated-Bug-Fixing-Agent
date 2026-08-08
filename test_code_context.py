from src.analyzer.code_context import CodeContextExtractor


def test_code_context_extractor():
    extractor = CodeContextExtractor()

    result = extractor.extract(
        "sample_project/calculator.py",
        2,
        context_lines=2,
    )

    assert result["target_line"] == 2
    assert result["file_path"].endswith("calculator.py")

    target = [
        line for line in result["context"]
        if line["is_target"]
    ]

    assert len(target) == 1
    assert target[0]["line_number"] == 2
    assert "a / b" in target[0]["code"]


if __name__ == "__main__":
    test_code_context_extractor()
    print("CODE CONTEXT TEST PASSED")