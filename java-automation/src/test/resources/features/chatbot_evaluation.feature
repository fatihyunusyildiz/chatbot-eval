@deepeval
Feature: Black-box chatbot DeepEval evaluation

  @single_turn
  Scenario: TC-001 iade süresi cevabı doğru ve grounded olmalıdır
    Given golden single-turn test case "TC-001" yüklenir
    When kullanıcı mesajı chatbot arayüzünde gönderir
    Then DeepEval sonucu PASS olmalıdır

  @single_turn
  Scenario: TC-002 kaynakta olmayan bilgi uydurulmamalıdır
    Given golden single-turn test case "TC-002" yüklenir
    When kullanıcı mesajı chatbot arayüzünde gönderir
    Then DeepEval sonucu PASS olmalıdır

  @multi_turn
  Scenario: MT-005 chatbot kullanıcı düzeltmesini dikkate alır
    Given golden multi-turn test case "MT-005" yüklenir
    When kullanıcı konuşmayı chatbot arayüzünde tamamlar
    Then DeepEval sonucu PASS olmalıdır

  @multi_turn @debug
  Scenario: MT-005 correction handling metriği debug edilir
    Given golden multi-turn test case "MT-005" yüklenir
    When kullanıcı konuşmayı chatbot arayüzünde tamamlar
    Then "correction_handling" metriği PASS olmalıdır
