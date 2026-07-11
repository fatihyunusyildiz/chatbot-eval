package com.chatboteval.flow;

import com.chatboteval.evaluation.DeepEvalRunResult;
import com.chatboteval.evaluation.DeepEvalStatus;

public final class DeepEvalAssertions {
    private DeepEvalAssertions() {
    }

    public static void assertPass(DeepEvalRunResult runResult) {
        DeepEvalStatus status = runResult.result().statusEnum();
        if (status == DeepEvalStatus.PASS) {
            return;
        }

        if (status == DeepEvalStatus.FAIL) {
            throw new AssertionError("DeepEval FAIL: " + runResult.result());
        }

        throw new RuntimeException("DeepEval ERROR: " + runResult.result());
    }
}
