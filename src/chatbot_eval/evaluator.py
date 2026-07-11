from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from chatbot_eval.multi_turn_evaluator import evaluate_multi_turn
from chatbot_eval.result_builder import error_result
from chatbot_eval.single_turn_evaluator import evaluate_single_turn


SUPPORTED_SCHEMA_VERSION = "1.0"


def load_payload(path: str | Path) -> dict[str, Any]:
    payload_path = Path(path)
    with payload_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError("Evaluation input must be a JSON object.")
    return payload


def evaluate_payload(
    payload: dict[str, Any],
    metric_override: str | None = None,
) -> dict[str, Any]:
    test_id = payload.get("test_id")
    suite_type = payload.get("suite_type")

    schema_version = payload.get("schema_version", SUPPORTED_SCHEMA_VERSION)
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        return error_result(
            test_id=test_id,
            suite_type=suite_type,
            error_type="ValueError",
            message=f"Unsupported schema_version: {schema_version}",
        )

    if suite_type == "single_turn":
        return evaluate_single_turn(payload, metric_override=metric_override)
    if suite_type == "multi_turn":
        return evaluate_multi_turn(payload, metric_override=metric_override)

    return error_result(
        test_id=test_id,
        suite_type=suite_type,
        error_type="ValueError",
        message=f"Unsupported suite_type: {suite_type}",
    )


def evaluate_file(path: str | Path, metric_override: str | None = None) -> dict[str, Any]:
    try:
        payload = load_payload(path)
    except Exception as exc:
        return error_result(
            error_type=exc.__class__.__name__,
            message=str(exc),
        )
    return evaluate_payload(payload, metric_override=metric_override)
