from __future__ import annotations

from deepeval.metrics import ConversationalGEval
from deepeval.test_case import MultiTurnParams


def _custom_conversation_memory_metric(judge_model):
    return ConversationalGEval(
        name="Conversation Memory",
        evaluation_steps=[
            "Review the full conversation history.",
            "Identify user-provided facts such as names, preferences, locations, or prior statements.",
            "Check whether the assistant remembers and uses those facts correctly in later answers.",
            "Give a high score if the assistant recalls the relevant prior user-provided information.",
            "For Turkish conversations, accept answers such as 'Adınız Fatih', 'İsminiz Fatih', 'Fatih demiştiniz', or 'Adınız Fatih'ti' as correct memory of the user's name.",
            "Do not treat Turkish past-tense wording as a contradiction when the user asks what they said earlier, for example 'Az önce söylediğim ismim neydi?'.",
            "Penalize if the assistant forgets, changes, or asks again for information already provided.",
        ],
        evaluation_params=[MultiTurnParams.CONTENT],
        threshold=0.80,
        model=judge_model,
        async_mode=False,
    )


def create_conversation_memory_metric(judge_model):
    return _custom_conversation_memory_metric(judge_model)
