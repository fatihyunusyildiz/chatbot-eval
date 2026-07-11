package com.chatboteval.pages;

import com.chatboteval.config.ChatbotConfig;
import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public final class WebDriverFactory {
    private WebDriverFactory() {
    }

    public static WebDriver create(ChatbotConfig config) {
        if (!"chrome".equalsIgnoreCase(config.browser())) {
            throw new IllegalArgumentException("Only chrome browser is configured for the first integration phase.");
        }

        WebDriverManager.chromedriver().setup();
        ChromeOptions options = new ChromeOptions();
        if (config.headless()) {
            options.addArguments("--headless=new");
        }
        options.addArguments("--window-size=1440,1000");
        return new ChromeDriver(options);
    }
}
