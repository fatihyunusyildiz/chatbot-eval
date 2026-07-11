from __future__ import annotations

import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from chatbot_client import call_chatbot
from dataset import load_single_turn_dataset
from metrics.metric_sets import build_single_turn_metrics


@pytest.mark.parametrize("item", load_single_turn_dataset(), ids=lambda item: item["test_id"])
def test_single_turn(item):
    actual_output = call_chatbot(
        item["input"],
        reference_context=item.get("reference_context"),
    )
    test_case = LLMTestCase(
        input=item["input"],
        actual_output=actual_output,
        expected_output=item["expected_output"],
        retrieval_context=[item.get("reference_context", "")],
    )
    metrics = build_single_turn_metrics(item.get("expected_behavior", "answer"))
    assert_test(test_case, metrics, run_async=False)
