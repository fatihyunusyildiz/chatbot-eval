from __future__ import annotations

from metrics.answer_correctness import create_answer_correctness_metric
from metrics.answer_relevancy import create_answer_relevancy_metric
from metrics.instruction_following import create_instruction_following_metric
from metrics.judge_model import get_judge_model
from metrics.negative_rejection import create_negative_rejection_metric
from metrics.reference_groundedness import create_reference_groundedness_metric
from metrics.unsupported_claim import create_unsupported_claim_metric


def build_single_turn_metrics(expected_behavior: str):
    judge_model = get_judge_model()
    common_metrics = [
        create_reference_groundedness_metric(judge_model),
        create_unsupported_claim_metric(judge_model),
        create_instruction_following_metric(judge_model),
        create_answer_relevancy_metric(judge_model),
    ]

    if expected_behavior == "reject_or_unknown":
        return [
            create_negative_rejection_metric(judge_model),
            *common_metrics,
        ]

    return [
        create_answer_correctness_metric(judge_model),
        *common_metrics,
    ]
