from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricResult:
    name: str
    status: str
    score: float | None = None
    threshold: float | None = None
    reason: str | None = None
    error: str | None = None


@dataclass
class EvaluationResult:
    test_id: str
    suite: str
    status: str
    metrics: list[MetricResult] = field(default_factory=list)
    error: str | None = None
    input: str | None = None
    actual_output: str | None = None
    user_turns: list[str] | None = None
    assistant_turns: list[str] | None = None
    metric_focus: str | None = None


def metric_name(metric: Any) -> str:
    return str(getattr(metric, "name", metric.__class__.__name__))


def metric_threshold(metric: Any) -> float | None:
    value = getattr(metric, "threshold", None)
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def metric_score(metric: Any) -> float | None:
    value = getattr(metric, "score", None)
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def metric_reason(metric: Any) -> str | None:
    reason = getattr(metric, "reason", None)
    return None if reason is None else str(reason)


def metric_success(metric: Any) -> bool:
    success_attr = getattr(metric, "success", None)
    if isinstance(success_attr, bool):
        return success_attr

    is_successful = getattr(metric, "is_successful", None)
    if callable(is_successful):
        return bool(is_successful())

    score = metric_score(metric)
    threshold = metric_threshold(metric)
    if score is not None and threshold is not None:
        return score >= threshold

    raise ValueError(f"Metric {metric_name(metric)} did not expose a pass/fail state.")


def evaluate_metrics(test_case: Any, metrics: list[Any]) -> tuple[str, list[MetricResult]]:
    results: list[MetricResult] = []
    has_fail = False

    for metric in metrics:
        name = metric_name(metric)
        try:
            metric.measure(test_case)
            is_pass = metric_success(metric)
            has_fail = has_fail or not is_pass
            results.append(
                MetricResult(
                    name=name,
                    status="PASS" if is_pass else "FAIL",
                    score=metric_score(metric),
                    threshold=metric_threshold(metric),
                    reason=metric_reason(metric),
                )
            )
        except AssertionError as exc:
            has_fail = True
            results.append(
                MetricResult(
                    name=name,
                    status="FAIL",
                    score=metric_score(metric),
                    threshold=metric_threshold(metric),
                    reason=metric_reason(metric) or str(exc),
                )
            )
        except Exception as exc:
            return (
                "ERROR",
                [
                    *results,
                    MetricResult(
                        name=name,
                        status="ERROR",
                        score=metric_score(metric),
                        threshold=metric_threshold(metric),
                        reason=metric_reason(metric),
                        error=f"{exc.__class__.__name__}: {exc}",
                    ),
                ],
            )

    return ("FAIL" if has_fail else "PASS", results)
