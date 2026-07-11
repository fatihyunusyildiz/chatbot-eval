package com.chatboteval.steps;

import com.chatboteval.flow.ChatbotEvaluationFlow;
import com.chatboteval.flow.DeepEvalAssertions;
import com.chatboteval.flow.ScenarioContext;
import io.cucumber.datatable.DataTable;
import io.cucumber.java.After;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;

import java.util.Locale;

public class ChatbotEvaluationSteps {
    private final ChatbotEvaluationFlow flow = new ChatbotEvaluationFlow();
    private ScenarioContext scenario;

    @Given("golden single-turn test case {string} yüklenir")
    public void loadSingleTurnGoldenCase(String testId) {
        scenario = flow.loadSingleTurnGoldenCase(testId);
    }

    @Given("golden multi-turn test case {string} yüklenir")
    public void loadMultiTurnGoldenCase(String testId) {
        scenario = flow.loadMultiTurnGoldenCase(testId);
    }

    @Given("golden QuillBot single-turn test case {string} is loaded")
    public void loadQuillBotSingleTurnGoldenCase(String testId) {
        scenario = flow.loadQuillBotSingleTurnGoldenCase(testId);
    }

    @Given("golden QuillBot multi-turn test case {string} is loaded")
    public void loadQuillBotMultiTurnGoldenCase(String testId) {
        scenario = flow.loadQuillBotMultiTurnGoldenCase(testId);
    }

    @When("kullanıcı mesajı chatbot arayüzünde gönderir")
    @When("user sends the single-turn golden input in the chatbot UI")
    public void runSingleTurnInChatbotUi() {
        flow.runSingleTurnInChatbotUi(scenario);
    }

    @When("kullanıcı konuşmayı chatbot arayüzünde tamamlar")
    @When("user completes the conversation in the chatbot UI")
    public void runMultiTurnInChatbotUi() {
        flow.runMultiTurnInChatbotUi(scenario);
    }

    @Then("DeepEval sonucu PASS olmalıdır")
    public void deepEvalResultShouldPass() {
        DeepEvalAssertions.assertPass(flow.evaluate(scenario, null));
    }

    @Then("{string} metriği PASS olmalıdır")
    @Then("metric {string} should PASS")
    public void metricShouldPass(String metricKey) {
        DeepEvalAssertions.assertPass(flow.evaluate(scenario, metricKey));
    }

    @Given("chatbot UI is opened")
    public void chatbotUiIsOpened() {
        scenario = flow.openSmokeScenario();
    }

    @When("user sends {string}")
    public void userSendsMessage(String userMessage) {
        flow.sendSmokeMessage(scenario, userMessage);
    }

    @When("user sends these messages")
    public void userSendsTheseMessages(DataTable dataTable) {
        for (String userMessage : dataTable.asList()) {
            userSendsMessage(userMessage);
        }
    }

    @Then("assistant reply should not be blank")
    public void assistantReplyShouldNotBeBlank() {
        if (scenario.lastAssistantOutput() == null || scenario.lastAssistantOutput().isBlank()) {
            throw new AssertionError("Assistant reply is blank.");
        }
    }

    @Then("assistant reply should contain {string}")
    public void assistantReplyShouldContain(String expectedText) {
        assistantReplyShouldNotBeBlank();
        String actual = scenario.lastAssistantOutput().toLowerCase(Locale.ROOT);
        String expected = expectedText.toLowerCase(Locale.ROOT);
        if (!actual.contains(expected)) {
            throw new AssertionError(
                    "Assistant reply does not contain '" + expectedText + "': " + scenario.lastAssistantOutput()
            );
        }
    }

    @After
    public void cleanup() {
        flow.cleanup(scenario);
    }
}
