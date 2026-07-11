from __future__ import annotations

from deepeval.metrics import ConversationalGEval
from deepeval.test_case import MultiTurnParams


def create_coreference_resolution_metric(judge_model):
    return ConversationalGEval(
        name="Coreference Resolution",
        evaluation_steps=[
            "Review the entire conversation history.",
            "Identify user references such as 'o', 'bu', 'bunu', 'az önceki', 'that', or similar expressions.",
            "Check whether the assistant correctly resolves these references using prior turns.",
            "Give a high score if the assistant answers based on the correct prior entity, topic, or concept.",
            "Penalize if the assistant ignores, misinterprets, or asks again for information that is already clear from context.",
        ],
        evaluation_params=[MultiTurnParams.CONTENT],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
