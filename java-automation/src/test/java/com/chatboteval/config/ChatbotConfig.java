package com.chatboteval.config;

import java.io.IOException;
import java.io.InputStream;
import java.time.Duration;
import java.util.Properties;

public record ChatbotConfig(
        String url,
        String browser,
        boolean headless,
        boolean loginRequired,
        String inputSelector,
        String sendSelector,
        String sendMode,
        String assistantMessageSelector,
        String newChatSelector,
        String dismissSelector,
        String responseIgnoreTexts,
        Duration responseTimeout,
        Duration responseStableDuration
) {
    public static ChatbotConfig loadDefault() {
        String configResource = System.getProperty("chatbot.config", "config/chatbot.properties");
        Properties properties = new Properties();
        try (InputStream stream = ChatbotConfig.class
                .getClassLoader()
                .getResourceAsStream(configResource)) {
            if (stream == null) {
                throw new IllegalStateException(configResource + " not found.");
            }
            properties.load(stream);
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot load chatbot config: " + configResource, exception);
        }

        return new ChatbotConfig(
                properties.getProperty("chatbot.url"),
                properties.getProperty("chatbot.browser", "chrome"),
                Boolean.parseBoolean(properties.getProperty("chatbot.headless", "false")),
                Boolean.parseBoolean(properties.getProperty("chatbot.login.required", "false")),
                properties.getProperty("chatbot.input.selector"),
                properties.getProperty("chatbot.send.selector", ""),
                properties.getProperty("chatbot.send.mode", "button"),
                properties.getProperty("chatbot.assistantMessage.selector"),
                properties.getProperty("chatbot.newChat.selector", ""),
                properties.getProperty("chatbot.dismiss.selector", ""),
                properties.getProperty("chatbot.response.ignoreTexts", ""),
                Duration.ofSeconds(Long.parseLong(properties.getProperty("chatbot.response.timeoutSeconds", "60"))),
                Duration.ofMillis(Long.parseLong(properties.getProperty("chatbot.response.stableMillis", "1500")))
        );
    }
}
