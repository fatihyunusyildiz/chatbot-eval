package com.chatboteval.pages;

import com.chatboteval.config.ChatbotConfig;
import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicReference;

public class ChatbotPage {
    private final WebDriver driver;
    private final ChatbotConfig config;

    public ChatbotPage(WebDriver driver, ChatbotConfig config) {
        this.driver = driver;
        this.config = config;
    }

    public void open() {
        driver.get(config.url());
        if (hasText(config.dismissSelector())) {
            clickIfPresent(By.cssSelector(config.dismissSelector()), Duration.ofSeconds(5));
        }
        if (hasText(config.newChatSelector())) {
            clickIfPresent(By.cssSelector(config.newChatSelector()), Duration.ofSeconds(5));
        }
    }

    public String sendMessageAndReadAssistantReply(String userMessage) {
        By input = By.cssSelector(config.inputSelector());
        By assistantMessages = By.cssSelector(config.assistantMessageSelector());

        List<String> previousTexts = visibleTexts(driver.findElements(assistantMessages));
        WebDriverWait wait = new WebDriverWait(driver, config.responseTimeout());
        WebElement inputElement = wait.until(ExpectedConditions.elementToBeClickable(input));
        clearInput(inputElement);
        inputElement.sendKeys(userMessage);
        submitMessage(wait, inputElement);

        return waitForStableAssistantText(wait, assistantMessages, previousTexts, userMessage);
    }

    public void screenshot(Path output) {
        if (!(driver instanceof TakesScreenshot screenshotDriver)) {
            return;
        }
        try {
            Files.createDirectories(output.getParent());
            Files.write(output, screenshotDriver.getScreenshotAs(OutputType.BYTES));
        } catch (Exception exception) {
            throw new IllegalStateException("Cannot write browser screenshot.", exception);
        }
    }

    private void clickIfPresent(By locator, Duration timeout) {
        try {
            new WebDriverWait(driver, timeout).until(ExpectedConditions.elementToBeClickable(locator)).click();
        } catch (Exception ignored) {
            // Optional new-chat button is absent on some chatbot UIs.
        }
    }

    private void submitMessage(WebDriverWait wait, WebElement inputElement) {
        if ("enter".equalsIgnoreCase(config.sendMode()) || !hasText(config.sendSelector())) {
            inputElement.sendKeys(Keys.ENTER);
            return;
        }

        wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector(config.sendSelector()))).click();
    }

    private String waitForStableAssistantText(
            WebDriverWait wait,
            By assistantMessages,
            List<String> previousTexts,
            String userMessage
    ) {
        AtomicReference<String> lastText = new AtomicReference<>("");
        AtomicReference<Instant> lastChange = new AtomicReference<>(Instant.now());

        return wait.until(driver -> {
            List<String> currentTexts = visibleTexts(driver.findElements(assistantMessages));
            if (currentTexts.isEmpty()) {
                return null;
            }

            String currentText = currentTexts.stream()
                    .filter(text -> !previousTexts.contains(text))
                    .filter(text -> !text.contains(userMessage))
                    .filter(this::isAllowedResponseText)
                    .reduce((first, second) -> second)
                    .orElse(null);
            if (currentText == null || currentText.isBlank()) {
                return null;
            }

            if (!currentText.equals(lastText.get())) {
                lastText.set(currentText);
                lastChange.set(Instant.now());
                return null;
            }

            Duration stableFor = Duration.between(lastChange.get(), Instant.now());
            return stableFor.compareTo(config.responseStableDuration()) >= 0 ? currentText : null;
        });
    }

    private static List<String> visibleTexts(List<WebElement> elements) {
        List<String> texts = new ArrayList<>();
        for (WebElement element : elements) {
            try {
                String text = element.getText().trim();
                if (!text.isBlank()) {
                    texts.add(text);
                }
            } catch (StaleElementReferenceException ignored) {
                // Streaming chatbot UIs frequently replace message nodes mid-poll.
            }
        }
        return texts;
    }

    private boolean isAllowedResponseText(String text) {
        String normalizedText = text.toLowerCase(Locale.ROOT);
        return Arrays.stream(config.responseIgnoreTexts().split("\\|"))
                .map(String::trim)
                .filter(ignore -> !ignore.isBlank())
                .map(ignore -> ignore.toLowerCase(Locale.ROOT))
                .noneMatch(normalizedText::contains);
    }

    private static void clearInput(WebElement inputElement) {
        String value = inputElement.getDomProperty("value");
        String text = inputElement.getText();
        if ((value == null || value.isBlank()) && (text == null || text.isBlank())) {
            return;
        }

        try {
            inputElement.clear();
            return;
        } catch (Exception ignored) {
            // Contenteditable chatbot inputs usually do not support clear().
        }

        inputElement.click();
        inputElement.sendKeys(Keys.chord(Keys.CONTROL, "a"));
        inputElement.sendKeys(Keys.BACK_SPACE);
    }

    private static boolean hasText(String value) {
        return value != null && !value.isBlank();
    }
}
