@quillbot_smoke
Feature: QuillBot AI Chat smoke check

  Scenario: QuillBot returns a visible assistant reply
    Given chatbot UI is opened
    When user sends "Sadece OK yaz."
    Then assistant reply should contain "OK"

  Scenario: QuillBot remembers a name across turns
    Given chatbot UI is opened
    When user sends these messages
      | Benim adim Fatih. |
      | Az once soyledigim ismim neydi? |
    Then assistant reply should contain "Fatih"

  Scenario: QuillBot uses the corrected address
    Given chatbot UI is opened
    When user sends these messages
      | Adresim Istanbul. |
      | Duzeltme: adresim Ankara. |
      | Adresim neresi? |
    Then assistant reply should contain "Ankara"
