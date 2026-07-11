from __future__ import annotations

from deepeval.metrics import ConversationalGEval
from deepeval.test_case import MultiTurnParams


def create_context_retention_metric(judge_model):
    return ConversationalGEval(
        name="Context Retention",
        evaluation_steps=[
            "Review the entire conversation history.",
            "Identify important context provided in earlier user turns.",
            "Check whether the assistant uses that prior context correctly in later answers.",
            "Give a high score if the assistant preserves relevant context such as durations, conditions, starting points, preferences, or constraints.",
            "Penalize if the assistant forgets, distorts, contradicts, or adds unclear information that was not supported by the earlier context.",
        ],
        evaluation_params=[MultiTurnParams.CONTENT],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
