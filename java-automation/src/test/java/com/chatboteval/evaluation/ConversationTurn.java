package com.chatboteval.evaluation;

public record ConversationTurn(String role, String content) {
    public static ConversationTurn user(String content) {
        return new ConversationTurn("user", content);
    }

    public static ConversationTurn assistant(String content) {
        return new ConversationTurn("assistant", content);
    }
}
