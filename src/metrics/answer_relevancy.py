from __future__ import annotations

from deepeval.metrics import AnswerRelevancyMetric


def create_answer_relevancy_metric(judge_model):
    return AnswerRelevancyMetric(
        threshold=0.80,
        model=judge_model,
    )
