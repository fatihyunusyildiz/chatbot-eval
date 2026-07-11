package com.chatboteval.golden;

import com.chatboteval.evaluation.JsonSupport;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

public class GoldenCaseLoader {
    private final ObjectMapper objectMapper = JsonSupport.objectMapper();
    private final Path dataDirectory;

    public GoldenCaseLoader(Path projectRoot) {
        Path directData = projectRoot.resolve("data");
        this.dataDirectory = directData.toFile().exists()
                ? directData
                : projectRoot.resolve("..").normalize().resolve("data");
    }

    public JsonNode singleTurn(String testId) {
        return find(dataDirectory.resolve("golden_single_turn.json"), testId);
    }

    public JsonNode multiTurn(String testId) {
        return find(dataDirectory.resolve("golden_multi_turn.json"), testId);
    }

    public JsonNode quillBotSingleTurn(String testId) {
        return find(dataDirectory.resolve("golden_quillbot_single_turn.json"), testId);
    }

    public JsonNode quillBotMultiTurn(String testId) {
        return find(dataDirectory.resolve("golden_quillbot_multi_turn.json"), testId);
    }

    private JsonNode find(Path path, String testId) {
        try {
            List<JsonNode> cases = objectMapper.readValue(path.toFile(), new TypeReference<>() {
            });
            return cases.stream()
                    .filter(item -> testId.equals(item.path("test_id").asText()))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException("Golden case not found: " + testId));
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot read golden dataset: " + path, exception);
        }
    }
}