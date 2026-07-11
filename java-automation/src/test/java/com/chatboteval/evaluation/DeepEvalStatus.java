package com.chatboteval.evaluation;

public enum DeepEvalStatus {
    PASS,
    FAIL,
    ERROR;

    public static DeepEvalStatus fromExitCode(int exitCode) {
        return switch (exitCode) {
            case 0 -> PASS;
            case 1 -> FAIL;
            case 2 -> ERROR;
            default -> ERROR;
        };
    }
}
