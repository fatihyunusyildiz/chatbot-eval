package com.chatboteval.evaluation;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Properties;

public record DeepEvalConfig(
        Path pythonExecutable,
        Path workingDirectory,
        Duration timeout,
        Path artifactDirectory
) {
    public static DeepEvalConfig loadDefault() {
        Properties properties = new Properties();
        try (InputStream stream = DeepEvalConfig.class
                .getClassLoader()
                .getResourceAsStream("config/deepeval.properties")) {
            if (stream == null) {
                throw new IllegalStateException("config/deepeval.properties not found.");
            }
            properties.load(stream);
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot load DeepEval config.", exception);
        }

        Path repoRoot = Path.of("").toAbsolutePath().normalize();
        Path workingDirectory = resolve(repoRoot, properties.getProperty("python.workingDirectory", "."));
        return new DeepEvalConfig(
                resolve(repoRoot, properties.getProperty("python.executable", ".venv\\Scripts\\python.exe")),
                workingDirectory,
                Duration.ofSeconds(Long.parseLong(properties.getProperty("deepeval.timeoutSeconds", "300"))),
                resolve(repoRoot, properties.getProperty("deepeval.artifactDirectory", "target/deepeval-artifacts"))
        );
    }

    private static Path resolve(Path root, String value) {
        Path path = Path.of(value);
        return path.isAbsolute() ? path.normalize() : root.resolve(path).normalize();
    }
}
