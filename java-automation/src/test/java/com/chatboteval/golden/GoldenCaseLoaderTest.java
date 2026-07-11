package com.chatboteval.golden;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;

import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

class GoldenCaseLoaderTest {
    @Test
    void loadsSingleTurnGoldenCaseById() {
        JsonNode node = new GoldenCaseLoader(Path.of("").toAbsolutePath().normalize()).singleTurn("TC-001");

        assertThat(node.path("test_id").asText()).isEqualTo("TC-001");
        assertThat(node.path("expected_behavior").asText()).isEqualTo("answer");
    }

    @Test
    void loadsMultiTurnGoldenCaseById() {
        JsonNode node = new GoldenCaseLoader(Path.of("").toAbsolutePath().normalize()).multiTurn("MT-005");

        assertThat(node.path("test_id").asText()).isEqualTo("MT-005");
        assertThat(node.path("metric_focus").asText()).isEqualTo("correction_handling");
    }

    @Test
    void loadsQuillBotSingleTurnGoldenCaseById() {
        JsonNode node = new GoldenCaseLoader(Path.of("").toAbsolutePath().normalize())
                .quillBotSingleTurn("QB-ST-001");

        assertThat(node.path("test_id").asText()).isEqualTo("QB-ST-001");
        assertThat(node.path("metric_focus").asText()).isEqualTo("answer_correctness");
    }

    @Test
    void loadsQuillBotMultiTurnGoldenCaseById() {
        JsonNode node = new GoldenCaseLoader(Path.of("").toAbsolutePath().normalize())
                .quillBotMultiTurn("QB-MT-001");

        assertThat(node.path("test_id").asText()).isEqualTo("QB-MT-001");
        assertThat(node.path("metric_focus").asText()).isEqualTo("conversation_memory");
    }
}