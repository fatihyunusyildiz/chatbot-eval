from __future__ import annotations

import pytest
from deepeval import assert_test
from deepeval.test_case import ConversationalTestCase, Turn

from chatbot_multiturn_client import call_chatbot_multiturn
from dataset import load_multi_turn_dataset
from metrics.multiturn.metric_sets import build_multiturn_metrics


def run_multiturn_conversation(item):
    conversation_history: list[dict[str, str]] = []
    deepeval_turns: list[Turn] = []

    for user_message in item["user_turns"]:
        deepeval_turns.append(Turn(role="user", content=user_message))
        assistant_message = call_chatbot_multiturn(
            user_message,
            conversation_history=conversation_history,
            reference_context=item.get("reference_context"),
        )
        deepeval_turns.append(Turn(role="assistant", content=assistant_message))
        conversation_history.extend(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_message},
            ]
        )

    return deepeval_turns


@pytest.mark.parametrize("item", load_multi_turn_dataset(), ids=lambda item: item["test_id"])
def test_multi_turn(item):
    turns = run_multiturn_conversation(item)
    test_case = ConversationalTestCase(
        scenario=item.get("scenario"),
        expected_outcome=item.get("expected_outcome"),
        chatbot_role=item.get("chatbot_role", "Yardımcı asistan."),
        turns=turns,
    )
    metrics = build_multiturn_metrics(metric_focus=item.get("metric_focus"))
    assert_test(test_case, metrics, run_async=False)
