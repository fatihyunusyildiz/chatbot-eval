package com.chatboteval.evaluation;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class DeepEvalClient {
    private final DeepEvalConfig config;
    private final ProcessRunner processRunner;
    private final ObjectMapper objectMapper;

    public DeepEvalClient(DeepEvalConfig config) {
        this(config, new DefaultProcessRunner(), JsonSupport.objectMapper());
    }

    public DeepEvalClient(DeepEvalConfig config, ProcessRunner processRunner, ObjectMapper objectMapper) {
        this.config = config;
        this.processRunner = processRunner;
        this.objectMapper = objectMapper;
    }

    public DeepEvalRunResult evaluate(Path evaluationInputJson, String metricOverride, Path artifactDirectory) {
        List<String> command = new ArrayList<>();
        command.add(config.pythonExecutable().toString());
        command.add("-m");
        command.add("chatbot_eval");
        command.add("evaluate");
        command.add(evaluationInputJson.toString());
        if (metricOverride != null && !metricOverride.isBlank()) {
            command.add(metricOverride);
        }

        try {
            ProcessResult processResult = processRunner.run(command, config.workingDirectory(), config.timeout());
            DeepEvalResult result = parseResult(processResult);
            DeepEvalRunResult runResult = new DeepEvalRunResult(
                    result,
                    processResult.exitCode(),
                    processResult.stdout(),
                    processResult.stderr(),
                    processResult.timedOut()
            );
            writeArtifacts(runResult, artifactDirectory);
            return runResult;
        } catch (IOException exception) {
            DeepEvalRunResult runResult = errorRun("IOException", exception.getMessage(), 2, "", "", false);
            writeArtifacts(runResult, artifactDirectory);
            return runResult;
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            DeepEvalRunResult runResult = errorRun("InterruptedException", exception.getMessage(), 2, "", "", false);
            writeArtifacts(runResult, artifactDirectory);
            return runResult;
        }
    }

    private DeepEvalResult parseResult(ProcessResult processResult) {
        if (processResult.timedOut()) {
            return errorResult("TimeoutException", "DeepEval process exceeded timeout.");
        }

        try {
            DeepEvalResult result = objectMapper.readValue(processResult.stdout(), DeepEvalResult.class);
            if (processResult.exitCode() < 0 || processResult.exitCode() > 2) {
                return errorResult(
                        "ContractMismatchException",
                        "Python returned unsupported exit code: " + processResult.exitCode()
                );
            }

            DeepEvalStatus jsonStatus;
            try {
                jsonStatus = result.statusEnum();
            } catch (IllegalArgumentException exception) {
                return errorResult(
                        "ContractMismatchException",
                        "Python returned unsupported JSON status: " + result.status()
                );
            }

            DeepEvalStatus exitStatus = DeepEvalStatus.fromExitCode(processResult.exitCode());
            if (jsonStatus != exitStatus) {
                return errorResult(
                        "ContractMismatchException",
                        "Python exit code " + processResult.exitCode()
                                + " conflicts with JSON status " + result.status()
                );
            }
            return result;
        } catch (JsonProcessingException exception) {
            return errorResult(
                    "JsonProcessingException",
                    "Python stdout was not valid evaluation JSON: " + exception.getMessage()
            );
        }
    }

    private void writeArtifacts(DeepEvalRunResult runResult, Path artifactDirectory) {
        if (artifactDirectory == null) {
            return;
        }
        try {
            Files.createDirectories(artifactDirectory);
            Files.writeString(
                    artifactDirectory.resolve("evaluation_result.json"),
                    objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(runResult.result()),
                    StandardCharsets.UTF_8
            );
            Files.writeString(artifactDirectory.resolve("deepeval_stdout.json"), runResult.stdout(), StandardCharsets.UTF_8);
            Files.writeString(artifactDirectory.resolve("deepeval_stderr.log"), runResult.stderr(), StandardCharsets.UTF_8);
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot write DeepEval artifacts.", exception);
        }
    }

    private DeepEvalRunResult errorRun(
            String type,
            String message,
            int exitCode,
            String stdout,
            String stderr,
            boolean timedOut
    ) {
        return new DeepEvalRunResult(errorResult(type, message), exitCode, stdout, stderr, timedOut);
    }

    private static DeepEvalResult errorResult(String type, String message) {
        return new DeepEvalResult(
                "1.0",
                null,
                null,
                "ERROR",
                List.of(),
                new DeepEvalError(type, message == null ? "" : message)
        );
    }
}
