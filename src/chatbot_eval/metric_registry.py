from __future__ import annotations

from collections.abc import Callable

from metrics.answer_correctness import create_answer_correctness_metric
from metrics.answer_relevancy import create_answer_relevancy_metric
from metrics.instruction_following import create_instruction_following_metric
from metrics.judge_model import get_judge_model
from metrics.negative_rejection import create_negative_rejection_metric
from metrics.reference_groundedness import create_reference_groundedness_metric
from metrics.unsupported_claim import create_unsupported_claim_metric
from metrics.multiturn.context_retention import create_context_retention_metric
from metrics.multiturn.conversation_memory import create_conversation_memory_metric
from metrics.multiturn.coreference_resolution import create_coreference_resolution_metric
from metrics.multiturn.correction_handling import create_correction_handling_metric
from metrics.multiturn.instruction_persistence import create_instruction_persistence_metric


MetricFactory = Callable[[object], object]


SINGLE_TURN_FACTORIES: dict[str, MetricFactory] = {
    "answer_correctness": create_answer_correctness_metric,
    "reference_groundedness": create_reference_groundedness_metric,
    "unsupported_claim": create_unsupported_claim_metric,
    "negative_rejection": create_negative_rejection_metric,
    "instruction_following": create_instruction_following_metric,
    "answer_relevancy": create_answer_relevancy_metric,
}

MULTI_TURN_FACTORIES: dict[str, MetricFactory] = {
    "conversation_memory": create_conversation_memory_metric,
    "context_retention": create_context_retention_metric,
    "coreference_resolution": create_coreference_resolution_metric,
    "instruction_persistence": create_instruction_persistence_metric,
    "correction_handling": create_correction_handling_metric,
}


def single_turn_metric_keys_for_behavior(expected_behavior: str) -> list[str]:
    common = [
        "reference_groundedness",
        "unsupported_claim",
        "instruction_following",
        "answer_relevancy",
    ]
    if expected_behavior == "reject_or_unknown":
        return ["negative_rejection", *common]
    return ["answer_correctness", *common]


def multi_turn_metric_keys(metric_focus: str | None = None) -> list[str]:
    if metric_focus:
        if metric_focus not in MULTI_TURN_FACTORIES:
            raise ValueError(f"Unknown multi-turn metric key: {metric_focus}")
        return [metric_focus]
    return list(MULTI_TURN_FACTORIES)


def supported_metrics() -> dict[str, list[str]]:
    return {
        "single_turn": list(SINGLE_TURN_FACTORIES),
        "multi_turn": list(MULTI_TURN_FACTORIES),
    }


def build_single_turn_metric_items(keys: list[str]) -> list[tuple[str, object]]:
    judge_model = get_judge_model()
    return [(key, SINGLE_TURN_FACTORIES[key](judge_model)) for key in keys]


def build_multi_turn_metric_items(keys: list[str]) -> list[tuple[str, object]]:
    judge_model = get_judge_model()
    return [(key, MULTI_TURN_FACTORIES[key](judge_model)) for key in keys]


def metric_suite(metric_key: str) -> str:
    if metric_key in SINGLE_TURN_FACTORIES:
        return "single_turn"
    if metric_key in MULTI_TURN_FACTORIES:
        return "multi_turn"
    raise ValueError(f"Unknown metric key: {metric_key}")
