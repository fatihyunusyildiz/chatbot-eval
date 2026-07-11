package com.chatboteval.flow;

import com.chatboteval.evaluation.ConversationTurn;

import java.util.List;

public record ChatbotConversationResult(
        String lastAssistantOutput,
        List<ConversationTurn> turns
) {
}
