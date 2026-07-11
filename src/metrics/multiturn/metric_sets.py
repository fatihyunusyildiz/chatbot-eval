from __future__ import annotations

from metrics.judge_model import get_judge_model
from metrics.multiturn.context_retention import create_context_retention_metric
from metrics.multiturn.conversation_memory import create_conversation_memory_metric
from metrics.multiturn.coreference_resolution import create_coreference_resolution_metric
from metrics.multiturn.correction_handling import create_correction_handling_metric
from metrics.multiturn.instruction_persistence import create_instruction_persistence_metric


METRIC_FACTORIES = {
    "conversation_memory": create_conversation_memory_metric,
    "context_retention": create_context_retention_metric,
    "coreference_resolution": create_coreference_resolution_metric,
    "instruction_persistence": create_instruction_persistence_metric,
    "correction_handling": create_correction_handling_metric,
}


def build_multiturn_metrics(metric_focus: str | None = None):
    judge_model = get_judge_model()

    if metric_focus:
        try:
            return [METRIC_FACTORIES[metric_focus](judge_model)]
        except KeyError as exc:
            known = ", ".join(sorted(METRIC_FACTORIES))
            raise ValueError(f"Unknown metric_focus '{metric_focus}'. Known values: {known}") from exc

    return [factory(judge_model) for factory in METRIC_FACTORIES.values()]
