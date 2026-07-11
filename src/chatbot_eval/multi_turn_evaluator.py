from __future__ import annotations

from typing import Any

from deepeval.test_case import ConversationalTestCase, Turn

from chatbot_eval.metric_registry import build_multi_turn_metric_items, multi_turn_metric_keys
from chatbot_eval.metric_runner import evaluate_metric_items
from chatbot_eval.result_builder import error_result, evaluation_result


VALID_ROLES = {"user", "assistant"}


def _build_turns(raw_turns: Any) -> list[Turn]:
    if not isinstance(raw_turns, list) or not raw_turns:
        raise ValueError("turns must be a non-empty list.")

    turns: list[Turn] = []
    for index, item in enumerate(raw_turns):
        if not isinstance(item, dict):
            raise ValueError(f"turns[{index}] must be an object.")
        role = item.get("role")
        content = item.get("content")
        if role not in VALID_ROLES:
            raise ValueError(f"turns[{index}].role must be one of: user, assistant.")
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"turns[{index}].content must be a non-empty string.")
        turns.append(Turn(role=role, content=content))
    return turns


def evaluate_multi_turn(
    payload: dict[str, Any],
    metric_override: str | None = None,
) -> dict[str, Any]:
    test_id = payload.get("test_id")
    suite_type = payload.get("suite_type")

    try:
        turns = _build_turns(payload.get("turns"))
        test_case = ConversationalTestCase(
            scenario=payload.get("scenario"),
            expected_outcome=payload.get("expected_outcome"),
            chatbot_role=payload.get("chatbot_role", "Yardımcı asistan."),
            turns=turns,
        )

        focus = metric_override or payload.get("metric_focus")
        keys = multi_turn_metric_keys(focus)
        metric_items = build_multi_turn_metric_items(keys)
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
