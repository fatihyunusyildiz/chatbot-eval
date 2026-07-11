from __future__ import annotations

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


def create_reference_groundedness_metric(judge_model):
    return GEval(
        name="Reference Groundedness",
        evaluation_steps=[
            "Review the reference context.",
            "Identify factual claims in the actual output.",
            "Check whether each factual claim is supported by the reference context.",
            "Penalize claims that contradict or go beyond the reference context.",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
