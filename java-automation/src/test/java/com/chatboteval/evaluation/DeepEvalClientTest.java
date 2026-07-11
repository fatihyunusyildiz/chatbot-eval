package com.chatboteval.evaluation;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class DeepEvalClientTest {
    @TempDir
    Path tempDir;

    @Test
    void parsesPassResultFromPythonStdout() throws Exception {
        DeepEvalClient client = clientReturning(new ProcessResult(
                0,
                """
                        {
                          "schema_version": "1.0",
                          "test_id": "MT-005",
                          "suite_type": "multi_turn",
                          "status": "PASS",
                          "metrics": [],
                          "error": null
                        }
                        """,
                "",
                false
        ));

        DeepEvalRunResult result = client.evaluate(tempDir.resolve("evaluation_input.json"), null, tempDir);

        assertThat(result.exitStatus()).isEqualTo(DeepEvalStatus.PASS);
        assertThat(result.result().statusEnum()).isEqualTo(DeepEvalStatus.PASS);
        assertThat(Files.exists(tempDir.resolve("evaluation_result.json"))).isTrue();
    }

    @Test
    void mapsFailExitCodeAndFailJsonToFail() {
        DeepEvalClient client = clientReturning(new ProcessResult(
                1,
                """
                        {
                          "schema_version": "1.0",
                          "test_id": "MT-005",
                          "suite_type": "multi_turn",
                          "status": "FAIL",
                          "metrics": [],
                          "error": null
                        }
                        """,
                "",
                false
        ));

        DeepEvalRunResult result = client.evaluate(tempDir.resolve("evaluation_input.json"), null, tempDir);

        assertThat(result.exitStatus()).isEqualTo(DeepEvalStatus.FAIL);
        assertThat(result.result().statusEnum()).isEqualTo(DeepEvalStatus.FAIL);
    }

    @Test
    void malformedStdoutBecomesErrorResult() {
        DeepEvalClient client = clientReturning(new ProcessResult(0, "not-json", "", false));

        DeepEvalRunResult result = client.evaluate(tempDir.resolve("evaluation_input.json"), null, tempDir);

        assertThat(result.result().statusEnum()).isEqualTo(DeepEvalStatus.ERROR);
        assertThat(result.result().error().type()).isEqualTo("JsonProcessingException");
    }

    @Test
    void timeoutBecomesErrorResult() {
        DeepEvalClient client = clientReturning(new ProcessResult(2, "", "timeout", true));

        DeepEvalRunResult result = client.evaluate(tempDir.resolve("evaluation_input.json"), null, tempDir);

        assertThat(result.exitStatus()).isEqualTo(DeepEvalStatus.ERROR);
        assertThat(result.result().statusEnum()).isEqualTo(DeepEvalStatus.ERROR);
        assertThat(result.result().error().type()).isEqualTo("TimeoutException");
    }

    @Test
    void mismatchedExitCodeAndJsonStatusBecomesError() {
        DeepEvalClient client = clientReturning(new ProcessResult(
                2,
                """
                        {
                          "schema_version": "1.0",
                          "test_id": "MT-005",
                          "suite_type": "multi_turn",
                          "status": "PASS",
                          "metrics": [],
                          "error": null
                        }
                        """,
                "",
                false
        ));

        DeepEvalRunResult result = client.evaluate(tempDir.resolve("evaluation_input.json"), null, tempDir);

        assertThat(result.result().statusEnum()).isEqualTo(DeepEvalStatus.ERROR);
        assertThat(result.result().error().type()).isEqualTo("ContractMismatchException");
    }

    @Test
    void commandIncludesMetricOverrideWhenProvided() {
        CapturingRunner runner = new CapturingRunner(new ProcessResult(
                0,
                """
                        {
                          "schema_version": "1.0",
                          "test_id": "MT-005",
                          "suite_type": "multi_turn",
                          "status": "PASS",
                          "metrics": [],
                          "error": null
                        }
                        """,
                "",
                false
        ));
        DeepEvalClient client = new DeepEvalClient(config(), runner, JsonSupport.objectMapper());

        client.evaluate(tempDir.resolve("evaluation_input.json"), "correction_handling", tempDir);

        assertThat(runner.command).containsExactly(
                config().pythonExecutable().toString(),
                "-m",
                "chatbot_eval",
                "evaluate",
                tempDir.resolve("evaluation_input.json").toString(),
                "correction_handling"
        );
    }

    private DeepEvalClient clientReturning(ProcessResult processResult) {
        return new DeepEvalClient(config(), new CapturingRunner(processResult), JsonSupport.objectMapper());
    }

    private DeepEvalConfig config() {
        return new DeepEvalConfig(
                Path.of(".venv\\Scripts\\python.exe"),
                Path.of(".").toAbsolutePath().normalize(),
                Duration.ofSeconds(5),
                tempDir
        );
    }

    private static class CapturingRunner implements ProcessRunner {
        private final ProcessResult processResult;
        private List<String> command;

        private CapturingRunner(ProcessResult processResult) {
            this.processResult = processResult;
        }

        @Override
        public ProcessResult run(List<String> command, Path workingDirectory, Duration timeout) {
            this.command = command;
            return processResult;
        }
    }
}
