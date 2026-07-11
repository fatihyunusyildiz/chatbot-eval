from __future__ import annotations

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


def create_instruction_following_metric(judge_model):
    return GEval(
        name="Instruction Following",
        evaluation_steps=[
            "Inspect the user input for explicit format, style, length, language, or scope instructions.",
            "If no explicit instruction exists, do not penalize the assistant for this metric.",
            "If an instruction exists, check whether the actual output follows it.",
            "Penalize only clear violations of explicit user instructions.",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
        ],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
