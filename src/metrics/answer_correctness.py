from __future__ import annotations

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


def create_answer_correctness_metric(judge_model):
    return GEval(
        name="Answer Correctness",
        evaluation_steps=[
            "Compare the actual output with the expected answer.",
            "Check whether the answer preserves all critical facts, conditions, quantities, and timing.",
            "Do not accept overly short answers if they omit a critical condition from the expected answer.",
            "Give a high score only when the actual output is semantically correct and complete.",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
