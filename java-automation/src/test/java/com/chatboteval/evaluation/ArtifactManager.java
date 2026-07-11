package com.chatboteval.evaluation;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class ArtifactManager {
    private final Path rootDirectory;
    private final ObjectMapper objectMapper;

    public ArtifactManager(Path rootDirectory) {
        this.rootDirectory = rootDirectory;
        this.objectMapper = JsonSupport.objectMapper();
    }

    public Path scenarioDirectory(String testId) {
        String safeId = testId == null || testId.isBlank() ? "unknown" : testId.replaceAll("[^A-Za-z0-9._-]", "_");
        Path directory = rootDirectory.resolve(safeId);
        try {
            Files.createDirectories(directory);
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot create artifact directory: " + directory, exception);
        }
        return directory;
    }

    public void writeConversation(Path scenarioDirectory, Object conversation) {
        try {
            objectMapper.writerWithDefaultPrettyPrinter()
                    .writeValue(scenarioDirectory.resolve("conversation.json").toFile(), conversation);
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot write conversation artifact.", exception);
        }
    }
}
