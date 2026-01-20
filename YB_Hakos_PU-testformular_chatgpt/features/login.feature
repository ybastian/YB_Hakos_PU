Feature: Login to webpage

  Scenario: Simple
    Given I open the url "http://localhost:5000"
    Then I expect that the title is "VdS Sternwarte"

  Scenario: login to website
    Given I open the url "http://localhost:5000"
    When I click on the "Anmelden" Link
    And I enter the admin credentials
    Then I am logged in

