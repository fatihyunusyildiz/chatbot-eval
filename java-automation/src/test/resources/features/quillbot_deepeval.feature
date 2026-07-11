@quillbot_deepeval
Feature: QuillBot AI Chat DeepEval evaluation

  @multi_turn
  Scenario: QB-MT-001 QuillBot remembers the user's name
    Given golden QuillBot multi-turn test case "QB-MT-001" is loaded
    When user completes the conversation in the chatbot UI
    Then metric "conversation_memory" should PASS

  @multi_turn
  Scenario: QB-MT-002 QuillBot follows corrected address information
    Given golden QuillBot multi-turn test case "QB-MT-002" is loaded
    When user completes the conversation in the chatbot UI
    Then metric "correction_handling" should PASS
