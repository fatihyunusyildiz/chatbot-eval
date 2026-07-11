package com.chatboteval.evaluation;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class EvaluationInputWriter {
    private final ObjectMapper objectMapper;

    public EvaluationInputWriter() {
        this(JsonSupport.objectMapper());
    }

    public EvaluationInputWriter(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public Path write(EvaluationInput input, Path artifactDirectory) {
        try {
            Files.createDirectories(artifactDirectory);
            Path output = artifactDirectory.resolve("evaluation_input.json");
            objectMapper.writerWithDefaultPrettyPrinter().writeValue(output.toFile(), input);
            return output;
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot write evaluation_input.json.", exception);
        }
    }
}
