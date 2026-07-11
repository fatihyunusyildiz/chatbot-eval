@quillbot_all_metrics
Feature: QuillBot AI Chat all-metrics DeepEval evaluation

  @single_turn @stage2
  Scenario: QB-ST-001 answer correctness
    Given golden QuillBot single-turn test case "QB-ST-001" is loaded
    When user sends the single-turn golden input in the chatbot UI
    Then metric "answer_correctness" should PASS

  @single_turn @stage4
  Scenario: QB-ST-002 reference groundedness
    Given golden QuillBot single-turn test case "QB-ST-002" is loaded
    When user sends the single-turn golden input in the chatbot UI
    Then metric "reference_groundedness" should PASS

  @single_turn @stage4
  Scenario: QB-ST-003 unsupported claim
    Given golden QuillBot single-turn test case "QB-ST-003" is loaded
    When user sends the single-turn golden input in the chatbot UI
    Then metric "unsupported_claim" should PASS

  @single_turn @stage2
  Scenario: QB-ST-004 negative rejection
    Given golden QuillBot single-turn test case "QB-ST-004" is loaded
    When user sends the single-turn golden input in the chatbot UI
    Then metric "negative_rejection" should PASS

  @single_turn @stage4
  Scenario: QB-ST-005 instruction following
    Given golden QuillBot single-turn test case "QB-ST-005" is loaded
    When user sends the single-turn golden input in the chatbot UI
    Then metric "instruction_following" should PASS

  @single_turn @stage4
  Scenario: QB-ST-006 answer relevancy
    Given golden QuillBot single-turn test case "QB-ST-006" is loaded
    When user sends the single-turn golden input in the chatbot UI
    Then metric "answer_relevancy" should PASS

  @multi_turn @stage3
  Scenario: QB-MT-001 conversation memory
    Given golden QuillBot multi-turn test case "QB-MT-001" is loaded
    When user completes the conversation in the chatbot UI
    Then metric "conversation_memory" should PASS

  @multi_turn @stage3
  Scenario: QB-MT-002 correction handling
    Given golden QuillBot multi-turn test case "QB-MT-002" is loaded
    When user completes the conversation in the chatbot UI
    Then metric "correction_handling" should PASS

  @multi_turn @stage4
  Scenario: QB-MT-003 context retention
    Given golden QuillBot multi-turn test case "QB-MT-003" is loaded
    When user completes the conversation in the chatbot UI
    Then metric "context_retention" should PASS

  @multi_turn @stage4
  Scenario: QB-MT-004 coreference resolution
    Given golden QuillBot multi-turn test case "QB-MT-004" is loaded
    When user completes the conversation in the chatbot UI
    Then metric "coreference_resolution" should PASS

  @multi_turn @stage4
  Scenario: QB-MT-005 instruction persistence
    Given golden QuillBot multi-turn test case "QB-MT-005" is loaded
    When user completes the conversation in the chatbot UI
    Then metric "instruction_persistence" should PASS