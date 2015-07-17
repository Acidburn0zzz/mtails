@product @check_tor_leaks
Feature: Time syncing
  As a Tails user
  I want Tor to work properly
  And for that I need a reasonably accurate system clock

  Scenario: Clock with host's time
    Given Tails has booted from DVD without network and logged in
    And Tails is using a simulated Tor network
    When the network is plugged
    And Tor is ready
    Then Tails clock is less than 5 minutes incorrect

  Scenario: Clock is one day in the past
    Given Tails has booted from DVD without network and logged in
    And Tails is using a simulated Tor network
    When I bump the system time with "-1 day"
    And the network is plugged
    And Tor is ready
    Then Tails clock is less than 5 minutes incorrect

  Scenario: Clock is one day in the future
    Given Tails has booted from DVD without network and logged in
    And Tails is using a simulated Tor network
    When I bump the system time with "+1 day"
    And the network is plugged
    And Tor is ready
    Then Tails clock is less than 5 minutes incorrect

  Scenario: Clock way in the future
    Given Tails has booted from DVD without network and logged in
    And Tails is using a simulated Tor network
    When I set the system time to "01 Jan 2020 12:34:56"
    And the network is plugged
    And Tor is ready
    Then Tails clock is less than 5 minutes incorrect

  Scenario: The system time is not synced to the hardware clock
    Given Tails has booted from DVD without network and logged in
    And Tails is using a simulated Tor network
    When I bump the system time with "-15 days"
    And I warm reboot the computer
    And the computer reboots Tails
    Then Tails' hardware clock is close to the host system's time

  Scenario: Anti-test: Changes to the hardware clock are kept when rebooting
    Given Tails has booted from DVD without network and logged in
    And Tails is using a simulated Tor network
    When I bump the hardware clock's time with "-15 days"
    And I warm reboot the computer
    And the computer reboots Tails
    Then the hardware clock is still off by "-15 days"

  Scenario: Boot with a hardware clock set way in the past and make sure that Tails sets the clock to the build date
    Given a computer
    And the network is unplugged
    And the hardware clock is set to "01 Jan 2000 12:34:56"
    And I start the computer
    And the computer boots Tails
    Then the system clock is just past Tails' build date
