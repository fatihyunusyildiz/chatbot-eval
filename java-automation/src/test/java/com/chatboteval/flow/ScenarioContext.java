package com.chatboteval.flow;

import com.chatboteval.evaluation.ConversationTurn;
import com.chatboteval.evaluation.DeepEvalRunResult;
import com.chatboteval.evaluation.EvaluationInput;
import com.fasterxml.jackson.databind.JsonNode;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class ScenarioContext {
    private final String suiteType;
    private final JsonNode goldenCase;
    private final Path artifactDirectory;
    private EvaluationInput evaluationInput;
    private DeepEvalRunResult deepEvalRunResult;
    private String lastAssistantOutput;
    private final List<ConversationTurn> smokeTurns = new ArrayList<>();

    public ScenarioContext(String suiteType, JsonNode goldenCase, Path artifactDirectory) {
        this.suiteType = suiteType;
        this.goldenCase = goldenCase;
        this.artifactDirectory = artifactDirectory;
    }

    public String suiteType() {
        return suiteType;
    }

    public JsonNode goldenCase() {
        return goldenCase;
    }

    public Path artifactDirectory() {
        return artifactDirectory;
    }

    public EvaluationInput evaluationInput() {
        return evaluationInput;
    }

    public void setEvaluationInput(EvaluationInput evaluationInput) {
        this.evaluationInput = evaluationInput;
    }

    public DeepEvalRunResult deepEvalRunResult() {
        return deepEvalRunResult;
    }

    public void setDeepEvalRunResult(DeepEvalRunResult deepEvalRunResult) {
        this.deepEvalRunResult = deepEvalRunResult;
    }

    public String lastAssistantOutput() {
        return lastAssistantOutput;
    }

    public void setLastAssistantOutput(String lastAssistantOutput) {
        this.lastAssistantOutput = lastAssistantOutput;
    }

    public List<ConversationTurn> smokeTurns() {
        return smokeTurns;
    }
}
