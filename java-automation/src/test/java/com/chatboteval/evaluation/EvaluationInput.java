package com.chatboteval.evaluation;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record EvaluationInput(
        @JsonProperty("schema_version") String schemaVersion,
        @JsonProperty("suite_type") String suiteType,
        @JsonProperty("test_id") String testId,
        String input,
        @JsonProperty("actual_output") String actualOutput,
        @JsonProperty("expected_output") String expectedOutput,
        @JsonProperty("reference_context") String referenceContext,
        @JsonProperty("expected_behavior") String expectedBehavior,
        @JsonProperty("metric_focus") String metricFocus,
        String scenario,
        @JsonProperty("expected_outcome") String expectedOutcome,
        @JsonProperty("chatbot_role") String chatbotRole,
        List<ConversationTurn> turns
) {
}
