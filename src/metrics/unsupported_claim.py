from __future__ import annotations

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


def create_unsupported_claim_metric(judge_model):
    return GEval(
        name="Unsupported Claim Score",
        evaluation_steps=[
            "Review only the factual claims made in the actual output.",
            "Use the reference context as the source of support.",
            "Penalize unsupported, invented, or contradictory claims.",
            "Do not penalize the answer merely for being short or incomplete.",
            "Give a high score when the answer contains no unsupported claims.",
        ],
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
