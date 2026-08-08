from src.models.repair_suggestion import RepairSuggestion


class RepairGenerator:
    """Generate repair suggestions from fault analysis."""

    def generate(self, fault_analysis: dict) -> RepairSuggestion:
        file_path = fault_analysis["file_path"]
        line_number = fault_analysis["line_number"]
        exception_type = fault_analysis["exception_type"]
        issue = fault_analysis["issue"]
        evidence = fault_analysis.get("evidence", [])

        if exception_type == "ZeroDivisionError":
            suggested_fix = (
                "Check that the divisor is not zero before performing "
                "the division."
            )

            reasoning = [
                "The fault analysis identified a division operation.",
                "ZeroDivisionError indicates that the divisor evaluated to zero.",
                "A zero-value check can prevent the exception.",
            ]

            confidence = 0.95

        elif exception_type == "AssertionError":
            suggested_fix = (
                "Review the comparison condition and correct the "
                "comparison operator or expected value."
            )

            reasoning = [
                "The fault analysis identified a failed assertion.",
                "The suspicious line contains a comparison operation.",
                "The comparison condition should be verified against the expected behavior.",
            ]

            confidence = 0.85

        else:
            suggested_fix = (
                "Review the suspicious line and modify the logic "
                "based on the reported exception."
            )

            reasoning = [
                "The fault analyzer identified a suspicious source location.",
                f"The reported exception is {exception_type}.",
            ]

            confidence = 0.60

        return RepairSuggestion(
            file_path=file_path,
            line_number=line_number,
            problem=issue,
            suggested_fix=suggested_fix,
            confidence=confidence,
            reasoning=reasoning,
        )