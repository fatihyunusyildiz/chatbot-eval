package com.chatboteval.evaluation;

public record ProcessResult(
        int exitCode,
        String stdout,
        String stderr,
        boolean timedOut
) {
}
