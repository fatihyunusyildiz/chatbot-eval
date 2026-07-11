from __future__ import annotations

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


def create_negative_rejection_metric(judge_model):
    return GEval(
        name="Negative Rejection",
        evaluation_steps=[
            "The expected behavior is to reject, say unknown, or state that the information is unavailable.",
            "Check whether the actual output avoids fabricating an answer.",
            "Give a high score if the assistant clearly says the requested information is not in the provided sources.",
            "Penalize if the assistant invents a specific unsupported answer.",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
