package com.chatboteval.flow;

import com.chatboteval.config.ChatbotConfig;
import com.chatboteval.evaluation.ArtifactManager;
import com.chatboteval.evaluation.ConversationTurn;
import com.chatboteval.evaluation.DeepEvalClient;
import com.chatboteval.evaluation.DeepEvalConfig;
import com.chatboteval.evaluation.DeepEvalRunResult;
import com.chatboteval.evaluation.EvaluationInput;
import com.chatboteval.evaluation.EvaluationInputWriter;
import com.chatboteval.golden.GoldenCaseLoader;
import com.chatboteval.pages.ChatbotPage;
import com.chatboteval.pages.WebDriverFactory;
import com.fasterxml.jackson.databind.JsonNode;
import org.openqa.selenium.WebDriver;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class ChatbotEvaluationFlow {
    private final ChatbotConfig chatbotConfig;
    private final ArtifactManager artifactManager;
    private final EvaluationInputWriter inputWriter;
    private final GoldenCaseLoader goldenCaseLoader;
    private final DeepEvalClient deepEvalClient;

    private WebDriver driver;
    private ChatbotPage chatbotPage;

    public ChatbotEvaluationFlow() {
        this(Path.of("").toAbsolutePath().normalize(), DeepEvalConfig.loadDefault(), ChatbotConfig.loadDefault());
    }

    public ChatbotEvaluationFlow(Path repoRoot, DeepEvalConfig deepEvalConfig, ChatbotConfig chatbotConfig) {
        this.chatbotConfig = chatbotConfig;
        this.artifactManager = new ArtifactManager(deepEvalConfig.artifactDirectory());
        this.inputWriter = new EvaluationInputWriter();
        this.goldenCaseLoader = new GoldenCaseLoader(repoRoot);
        this.deepEvalClient = new DeepEvalClient(deepEvalConfig);
    }

    public ScenarioContext loadSingleTurnGoldenCase(String testId) {
        return scenario("single_turn", goldenCaseLoader.singleTurn(testId), testId);
    }

    public ScenarioContext loadMultiTurnGoldenCase(String testId) {
        return scenario("multi_turn", goldenCaseLoader.multiTurn(testId), testId);
    }

    public ScenarioContext loadQuillBotSingleTurnGoldenCase(String testId) {
        return scenario("single_turn", goldenCaseLoader.quillBotSingleTurn(testId), testId);
    }

    public ScenarioContext loadQuillBotMultiTurnGoldenCase(String testId) {
        return scenario("multi_turn", goldenCaseLoader.quillBotMultiTurn(testId), testId);
    }

    public ScenarioContext openSmokeScenario() {
        ScenarioContext context = new ScenarioContext(null, null, artifactManager.scenarioDirectory("ui-smoke"));
        openChatbot();
        return context;
    }

    public void runSingleTurnInChatbotUi(ScenarioContext context) {
        requireScenario(context);
        JsonNode goldenCase = context.goldenCase();
        openChatbot();

        String input = goldenCase.path("input").asText();
        String assistantOutput = chatbotPage.sendMessageAndReadAssistantReply(input);
        List<ConversationTurn> turns = List.of(
                ConversationTurn.user(input),
                ConversationTurn.assistant(assistantOutput)
        );

        context.setEvaluationInput(new EvaluationInput(
                "1.0",
                context.suiteType(),
                goldenCase.path("test_id").asText(),
                input,
                assistantOutput,
                goldenCase.path("expected_output").asText(),
                goldenCase.path("reference_context").asText(""),
                goldenCase.path("expected_behavior").asText("answer"),
                null,
                null,
                null,
                null,
                null
        ));
        artifactManager.writeConversation(context.artifactDirectory(), turns);
    }

    public void runMultiTurnInChatbotUi(ScenarioContext context) {
        requireScenario(context);
        JsonNode goldenCase = context.goldenCase();
        openChatbot();

        ChatbotConversationResult conversation = completeConversation(goldenCase.path("user_turns"));
        context.setEvaluationInput(new EvaluationInput(
                "1.0",
                context.suiteType(),
                goldenCase.path("test_id").asText(),
                null,
                null,
                null,
                goldenCase.path("reference_context").asText(""),
                null,
                goldenCase.path("metric_focus").asText(null),
                goldenCase.path("scenario").asText(null),
                goldenCase.path("expected_outcome").asText(null),
                goldenCase.path("chatbot_role").asText(null),
                conversation.turns()
        ));
        artifactManager.writeConversation(context.artifactDirectory(), conversation.turns());
    }

    public void sendSmokeMessage(ScenarioContext context, String userMessage) {
        requireScenario(context);
        String assistantOutput = chatbotPage.sendMessageAndReadAssistantReply(userMessage);
        context.setLastAssistantOutput(assistantOutput);
        context.smokeTurns().add(ConversationTurn.user(userMessage));
        context.smokeTurns().add(ConversationTurn.assistant(assistantOutput));
        artifactManager.writeConversation(context.artifactDirectory(), context.smokeTurns());
    }

    public DeepEvalRunResult evaluate(ScenarioContext context, String metricOverride) {
        requireScenario(context);
        if (context.evaluationInput() == null) {
            throw new IllegalStateException("Evaluation input has not been prepared for this scenario.");
        }

        Path inputJson = inputWriter.write(context.evaluationInput(), context.artifactDirectory());
        DeepEvalRunResult runResult = deepEvalClient.evaluate(inputJson, metricOverride, context.artifactDirectory());
        context.setDeepEvalRunResult(runResult);
        return runResult;
    }

    public void cleanup(ScenarioContext context) {
        if (driver == null) {
            return;
        }

        try {
            if (context != null && context.artifactDirectory() != null) {
                chatbotPage.screenshot(context.artifactDirectory().resolve("browser_screenshot.png"));
            }
        } finally {
            driver.quit();
            driver = null;
            chatbotPage = null;
        }
    }

    private ScenarioContext scenario(String suiteType, JsonNode goldenCase, String testId) {
        return new ScenarioContext(suiteType, goldenCase, artifactManager.scenarioDirectory(testId));
    }

    private ChatbotConversationResult completeConversation(JsonNode userTurns) {
        List<ConversationTurn> turns = new ArrayList<>();
        String lastAssistantOutput = null;
        for (JsonNode userTurn : userTurns) {
            String userMessage = userTurn.asText();
            lastAssistantOutput = chatbotPage.sendMessageAndReadAssistantReply(userMessage);
            turns.add(ConversationTurn.user(userMessage));
            turns.add(ConversationTurn.assistant(lastAssistantOutput));
        }
        return new ChatbotConversationResult(lastAssistantOutput, turns);
    }

    private void openChatbot() {
        if (chatbotConfig.loginRequired()) {
            throw new IllegalStateException(
                    "Login-required chatbot profiles are not configured in this automation."
            );
        }
        if (driver == null) {
            driver = WebDriverFactory.create(chatbotConfig);
            chatbotPage = new ChatbotPage(driver, chatbotConfig);
            chatbotPage.open();
        }
    }

    private static void requireScenario(ScenarioContext context) {
        if (context == null) {
            throw new IllegalStateException("Scenario context has not been initialized.");
        }
    }
}
