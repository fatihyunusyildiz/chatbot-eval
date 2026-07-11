from __future__ import annotations

from typing import Any

from deepeval_runner import (
    metric_name,
    metric_reason,
    metric_score,
    metric_success,
    metric_threshold,
)

from chatbot_eval.result_builder import metric_result


def evaluate_metric_items(
    test_case: Any,
    metric_items: list[tuple[str, Any]],
) -> tuple[str, list[dict[str, Any]], dict[str, str] | None]:
    results: list[dict[str, Any]] = []
    has_fail = False

    for key, metric in metric_items:
        try:
            metric.measure(test_case)
            passed = metric_success(metric)
            has_fail = has_fail or not passed
            results.append(
                metric_result(
                    key=key,
                    name=metric_name(metric),
                    status="PASS" if passed else "FAIL",
                    score=metric_score(metric),
                    threshold=metric_threshold(metric),
                    reason=metric_reason(metric),
                )
            )
        except AssertionError as exc:
            has_fail = True
            results.append(
                metric_result(
                    key=key,
                    name=metric_name(metric),
                    status="FAIL",
                    score=metric_score(metric),
                    threshold=metric_threshold(metric),
                    reason=metric_reason(metric) or str(exc),
                )
            )
        except Exception as exc:
            return (
                "ERROR",
                results,
                {
                    "type": exc.__class__.__name__,
                    "message": str(exc),
                },
            )

    return ("FAIL" if has_fail else "PASS", results, None)
