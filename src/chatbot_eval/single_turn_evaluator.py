from __future__ import annotations

from typing import Any

from deepeval.test_case import LLMTestCase

from chatbot_eval.metric_registry import (
    build_single_turn_metric_items,
    single_turn_metric_keys_for_behavior,
)
from chatbot_eval.metric_runner import evaluate_metric_items
from chatbot_eval.result_builder import error_result, evaluation_result


def evaluate_single_turn(
    payload: dict[str, Any],
    metric_override: str | None = None,
) -> dict[str, Any]:
    test_id = payload.get("test_id")
    suite_type = payload.get("suite_type")

    required_fields = ["input", "actual_output"]
    missing = [field for field in required_fields if not payload.get(field)]
    if missing:
        return error_result(
            test_id=test_id,
            suite_type=suite_type,
            error_type="ValueError",
            message=f"Missing required field(s): {', '.join(missing)}",
        )

    test_case = LLMTestCase(
        input=payload["input"],
        actual_output=payload["actual_output"],
        expected_output=payload.get("expected_output"),
        retrieval_context=[payload.get("reference_context", "")],
    )

    keys = (
        [metric_override]
        if metric_override
        else single_turn_metric_keys_for_behavior(payload.get("expected_behavior", "answer"))
    )

    try:
        metric_items = build_single_turn_metric_items(keys)
        status, metrics, error = evaluate_metric_items(test_case, metric_items)
    except Exception as exc:
        return error_result(
            test_id=test_id,
            suite_type=suite_type,
            error_type=exc.__class__.__name__,
            message=str(exc),
        )

    return evaluation_result(
        test_id=test_id,
        suite_type=suite_type,
        status=status,
        metrics=metrics,
        error=error,
    )
