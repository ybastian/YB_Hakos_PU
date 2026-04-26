Feature: Login with in-memory test database

  @db
  Scenario: Successful login with fixture user
    Given the following users are registered:
      | name     | email            | password  |
      | testuser | test@example.com | TestPass1 |
    When I post login with email "test@example.com" and password "TestPass1"
    Then I am redirected to home
    And the response contains "Abmelden"

  @db
  Scenario: Login fails with wrong password
    Given the following users are registered:
      | name     | email            | password  |
      | testuser | test@example.com | TestPass1 |
    When I post login with email "test@example.com" and password "WrongPass9"
    Then the response contains "Login nicht erfolgreich"
