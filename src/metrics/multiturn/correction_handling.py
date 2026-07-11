from __future__ import annotations

from deepeval.metrics import ConversationalGEval
from deepeval.test_case import MultiTurnParams


def create_correction_handling_metric(judge_model):
    return ConversationalGEval(
        name="Correction Handling",
        evaluation_steps=[
            "Review the conversation and identify whether the user corrected earlier information.",
            "Check whether the assistant uses the corrected/latest information rather than the outdated information.",
            "Give a high score if the assistant clearly follows the latest user correction.",
            "Penalize if the assistant repeats or relies on information that the user corrected.",
            "Penalize if the assistant treats both old and corrected information as equally valid.",
        ],
        evaluation_params=[MultiTurnParams.CONTENT],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
