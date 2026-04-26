Feature: Vollständiger Workflow - Antrag erstellen, genehmigen, Poweruser meldet sich

  @db
  Scenario: Joe erstellt und schickt Antrag ab, Approver genehmigt, Poweruser meldet möglich
    Given the following users are registered:
      | name      | email             | password    | group           |
      | joe       | joe@test.com      | JoePass1!   | user_group      |
      | approverA | approver@test.com | ApprPass1!  | approver_group  |
      | powerA    | power@test.com    | PowerPass1! | poweruser_group |
    And the following observatories exist:
      | name              | site         |
      | Testobservatorium | Teststandort |
    When I login as "joe@test.com" with password "JoePass1!"
    And I create the following Antraege:
      | requester_name | date       | type | remark        |
      | Joe Tester     | 2026-12-01 | B    | Workflow Test |
    And I submit the last created Antrag
    And I logout
    When I login as "approver@test.com" with password "ApprPass1!"
    Then the approver page shows the Antrag as "Abgeschickt"
    When the approver approves the last Antrag
    And I logout
    When I login as "power@test.com" with password "PowerPass1!"
    Then the poweruser page shows the Antrag
    When the poweruser saves availability "möglich" for the last Antrag
    Then the PoweruserMeldung for the last Antrag has availability 1
