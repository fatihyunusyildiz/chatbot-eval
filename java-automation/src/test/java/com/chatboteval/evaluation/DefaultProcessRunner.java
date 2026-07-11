package com.chatboteval.evaluation;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

public class DefaultProcessRunner implements ProcessRunner {
    @Override
    public ProcessResult run(List<String> command, Path workingDirectory, Duration timeout)
            throws IOException, InterruptedException {
        Process process = new ProcessBuilder(command)
                .directory(workingDirectory.toFile())
                .start();

        ExecutorService executor = Executors.newFixedThreadPool(2);
        try {
            Future<String> stdout = executor.submit(() -> new String(
                    process.getInputStream().readAllBytes(),
                    StandardCharsets.UTF_8
            ));
            Future<String> stderr = executor.submit(() -> new String(
                    process.getErrorStream().readAllBytes(),
                    StandardCharsets.UTF_8
            ));

            boolean finished = process.waitFor(timeout.toMillis(), TimeUnit.MILLISECONDS);
            if (!finished) {
                process.destroyForcibly();
                process.waitFor(5, TimeUnit.SECONDS);
                return new ProcessResult(2, read(stdout), read(stderr), true);
            }

            return new ProcessResult(process.exitValue(), read(stdout), read(stderr), false);
        } finally {
            executor.shutdownNow();
        }
    }

    private static String read(Future<String> future) {
        try {
            return future.get(5, TimeUnit.SECONDS);
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            return "";
        } catch (ExecutionException exception) {
            return "";
        } catch (TimeoutException exception) {
            future.cancel(true);
            return "";
        }
    }
}
