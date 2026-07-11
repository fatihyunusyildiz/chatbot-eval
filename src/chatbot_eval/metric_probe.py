from __future__ import annotations

from typing import Any

from chatbot_client import call_chatbot
from chatbot_multiturn_client import call_chatbot_multiturn

from chatbot_eval.evaluator import evaluate_payload
from chatbot_eval.golden_case_selector import select_golden_case, select_golden_cases
from chatbot_eval.metric_registry import metric_suite


def _single_turn_probe_payload(metric_key: str, item: dict[str, Any]) -> dict[str, Any]:
    actual_output = call_chatbot(
        item["input"],
        reference_context=item.get("reference_context"),
    )
    return {
        "schema_version": "1.0",
        "suite_type": "single_turn",
        "test_id": item.get("test_id"),
        "input": item["input"],
        "actual_output": actual_output,
        "expected_output": item.get("expected_output"),
        "reference_context": item.get("reference_context", ""),
        "expected_behavior": item.get("expected_behavior", "answer"),
    }


def _multi_turn_probe_payload(metric_key: str, item: dict[str, Any]) -> dict[str, Any]:
    conversation_history: list[dict[str, str]] = []
    turns: list[dict[str, str]] = []

    for user_message in item["user_turns"]:
        turns.append({"role": "user", "content": user_message})
        assistant_message = call_chatbot_multiturn(
            user_message,
            conversation_history=conversation_history,
            reference_context=item.get("reference_context"),
        )
        turns.append({"role": "assistant", "content": assistant_message})
        conversation_history.extend(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ]
        )

    return {
        "schema_version": "1.0",
        "suite_type": "multi_turn",
        "test_id": item.get("test_id"),
        "metric_focus": metric_key,
        "scenario": item.get("scenario"),
        "expected_outcome": item.get("expected_outcome"),
        "chatbot_role": item.get("chatbot_role"),
        "reference_context": item.get("reference_context", ""),
        "turns": turns,
    }


def run_metric_probe(metric_key: str, test_id: str | None = None) -> dict[str, Any]:
    item = select_golden_case(metric_key, test_id=test_id)
    return run_metric_probe_item(metric_key, item)


def run_metric_probe_item(metric_key: str, item: dict[str, Any]) -> dict[str, Any]:
    suite = metric_suite(metric_key)
    payload = (
        _multi_turn_probe_payload(metric_key, item)
        if suite == "multi_turn"
        else _single_turn_probe_payload(metric_key, item)
    )
    return evaluate_payload(payload, metric_override=metric_key)


def iter_metric_probe_results(metric_key: str, test_id: str | None = None):
    for item in select_golden_cases(metric_key, test_id=test_id):
        yield run_metric_probe_item(metric_key, item)
