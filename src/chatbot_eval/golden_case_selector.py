from __future__ import annotations

from typing import Any

from dataset import load_multi_turn_dataset, load_single_turn_dataset

from chatbot_eval.metric_registry import metric_suite, single_turn_metric_keys_for_behavior


def _supports_metric(item: dict[str, Any], metric_key: str, suite: str) -> bool:
    if suite == "multi_turn":
        return item.get("metric_focus") == metric_key
    return metric_key in single_turn_metric_keys_for_behavior(
        item.get("expected_behavior", "answer")
    )


def select_golden_cases(metric_key: str, test_id: str | None = None) -> list[dict[str, Any]]:
    suite = metric_suite(metric_key)
    dataset = load_multi_turn_dataset() if suite == "multi_turn" else load_single_turn_dataset()

    if test_id:
        for item in dataset:
            if item.get("test_id") != test_id:
                continue
            if not _supports_metric(item, metric_key, suite):
                raise ValueError(
                    f"Golden test case {test_id} is not compatible with metric: {metric_key}"
                )
            return [item]
        raise ValueError(f"Golden test case not found: {test_id}")

    candidates = [item for item in dataset if _supports_metric(item, metric_key, suite)]
    if not candidates:
        raise ValueError(f"No golden case found for metric: {metric_key}")
    return candidates


def select_golden_case(metric_key: str, test_id: str | None = None) -> dict[str, Any]:
    return select_golden_cases(metric_key, test_id=test_id)[0]
