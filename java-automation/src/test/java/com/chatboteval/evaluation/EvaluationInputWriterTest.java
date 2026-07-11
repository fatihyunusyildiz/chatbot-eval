package com.chatboteval.evaluation;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Path;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class EvaluationInputWriterTest {
    @TempDir
    Path tempDir;

    @Test
    void writesSingleTurnEvaluationInputJson() throws Exception {
        EvaluationInput input = new EvaluationInput(
                "1.0",
                "single_turn",
                "TC-001",
                "İade süresi kaç gündür?",
                "İade süresi teslimattan itibaren 14 gündür.",
                "İade süresi teslimattan itibaren 14 gündür.",
                "Müşteri teslimattan itibaren 14 gün içinde iade talebi oluşturabilir.",
                "answer",
                null,
                null,
                null,
                null,
                null
        );

        Path output = new EvaluationInputWriter().write(input, tempDir);
        JsonNode json = JsonSupport.objectMapper().readTree(output.toFile());

        assertThat(json.path("schema_version").asText()).isEqualTo("1.0");
        assertThat(json.path("suite_type").asText()).isEqualTo("single_turn");
        assertThat(json.path("test_id").asText()).isEqualTo("TC-001");
        assertThat(json.path("actual_output").asText()).contains("14");
    }

    @Test
    void writesMultiTurnEvaluationInputJson() throws Exception {
        EvaluationInput input = new EvaluationInput(
                "1.0",
                "multi_turn",
                "MT-005",
                null,
                null,
                null,
                "",
                null,
                "correction_handling",
                "Kullanıcı adresini düzeltir.",
                "Assistant Ankara bilgisini kullanmalıdır.",
                "Düzeltmeleri dikkate alan asistan.",
                List.of(
                        ConversationTurn.user("Adresim İstanbul."),
                        ConversationTurn.assistant("Adresinizi İstanbul olarak not aldım."),
                        ConversationTurn.user("Düzeltme: adresim Ankara."),
                        ConversationTurn.assistant("Adresiniz Ankara olarak güncellendi."),
                        ConversationTurn.user("Adresim neresi?"),
                        ConversationTurn.assistant("Adresiniz Ankara.")
                )
        );

        Path output = new EvaluationInputWriter().write(input, tempDir);
        JsonNode json = JsonSupport.objectMapper().readTree(output.toFile());

        assertThat(json.path("suite_type").asText()).isEqualTo("multi_turn");
        assertThat(json.path("metric_focus").asText()).isEqualTo("correction_handling");
        assertThat(json.path("turns")).hasSize(6);
    }
}
