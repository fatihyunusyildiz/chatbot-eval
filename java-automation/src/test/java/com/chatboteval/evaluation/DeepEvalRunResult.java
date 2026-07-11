package com.chatboteval.evaluation;

public record DeepEvalRunResult(
        DeepEvalResult result,
        int exitCode,
        String stdout,
        String stderr,
        boolean timedOut
) {
    public DeepEvalStatus exitStatus() {
        return DeepEvalStatus.fromExitCode(exitCode);
    }
}
