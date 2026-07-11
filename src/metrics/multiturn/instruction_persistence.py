from __future__ import annotations

from deepeval.metrics import ConversationalGEval
from deepeval.test_case import MultiTurnParams


def create_instruction_persistence_metric(judge_model):
    return ConversationalGEval(
        name="Instruction Persistence",
        evaluation_steps=[
            "Review all user turns in the conversation.",
            "Look specifically for explicit Turkish or English instructions about response style, format, length, or structure.",
            "Examples of explicit instructions include: 'kısa cevap ver', 'madde madde cevap ver', 'bundan sonra kısa ve madde madde cevap ver', 'answer briefly', or 'use bullet points'.",
            "If the user says 'Bundan sonra kısa ve madde madde cevap ver', treat this as an explicit instruction that must persist in later assistant responses.",
            "Check whether later assistant responses follow the requested style or format.",
            "Give a high score if the assistant's later answer is short and uses bullet points after the user requested short bullet-point answers.",
            "Do not penalize the assistant just because the acknowledgement turn is brief or unusual, as long as the later task answer follows the instruction.",
            "Penalize only if the assistant ignores the requested format in later substantive answers.",
        ],
        evaluation_params=[MultiTurnParams.CONTENT],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )
