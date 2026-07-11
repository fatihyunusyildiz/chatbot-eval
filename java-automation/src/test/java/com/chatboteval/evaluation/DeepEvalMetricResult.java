package com.chatboteval.evaluation;

public record DeepEvalMetricResult(
        String key,
        String name,
        String status,
        Double score,
        Double threshold,
        String reason,
        String error
) {
}
