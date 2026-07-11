package com.chatboteval.evaluation;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record DeepEvalResult(
        @JsonProperty("schema_version") String schemaVersion,
        @JsonProperty("test_id") String testId,
        @JsonProperty("suite_type") String suiteType,
        String status,
        List<DeepEvalMetricResult> metrics,
        DeepEvalError error
) {
    public DeepEvalStatus statusEnum() {
        return status == null ? DeepEvalStatus.ERROR : DeepEvalStatus.valueOf(status);
    }
}
