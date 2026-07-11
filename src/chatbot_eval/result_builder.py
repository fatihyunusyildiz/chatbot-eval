from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "1.0"


def metric_result(
    *,
    key: str,
    name: str,
    status: str,
    score: float | None = None,
    threshold: float | None = None,
    reason: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "key": key,
        "name": name,
        "status": status,
        "score": score,
        "threshold": threshold,
        "reason": reason,
        "error": error,
    }


def evaluation_result(
    *,
    test_id: str | None,
    suite_type: str | None,
    status: str,
    metrics: list[dict[str, Any]] | None = None,
    error: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "test_id": test_id,
        "suite_type": suite_type,
        "status": status,
        "metrics": metrics or [],
        "error": error,
    }


def error_result(
    *,
    test_id: str | None = None,
    suite_type: str | None = None,
    error_type: str,
    message: str,
) -> dict[str, Any]:
    return evaluation_result(
        test_id=test_id,
        suite_type=suite_type,
        status="ERROR",
        metrics=[],
        error={
            "type": error_type,
            "message": message,
        },
    )


def exit_code_for_status(status: str) -> int:
    if status == "PASS":
        return 0
    if status == "FAIL":
        return 1
    return 2
