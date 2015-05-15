@product
Feature: Tails persistence
  As a Tails user
  I want use Tails persistence feature

  Scenario: Booting Tails from a USB drive with a disabled persistent partition
    Given Tails has booted without network from a USB drive with a persistent partition and stopped at Tails Greeter's login screen
    When I log in to a new session
    Then Tails seems to have booted normally
    And Tails is running from USB drive "current"
    And persistence is disabled
    But a Tails persistence partition exists on USB drive "current"

  Scenario: Booting Tails from a USB drive with an enabled persistent partition
    Given Tails has booted without network from a USB drive with a persistent partition and stopped at Tails Greeter's login screen
    When I enable persistence
    And I log in to a new session
    Then Tails seems to have booted normally
    And Tails is running from USB drive "current"
    And all persistence presets are enabled
    And all persistent directories have safe access rights

  Scenario: Writing files first to a read/write-enabled persistent partition, and then to a read-only-enabled persistent partition
    Given Tails has booted without network from a USB drive with a persistent partition and stopped at Tails Greeter's login screen
    When I enable persistence
    And I log in to a new session
    Then Tails is running from USB drive "current"
    And the boot device has safe access rights
    And all persistence presets are enabled
    And I write some files expected to persist
    And all persistent filesystems have safe access rights
    And all persistence configuration files have safe access rights
    And all persistent directories have safe access rights
    And I take note of which persistence presets are available
    And I shutdown Tails and wait for the computer to power off
    # XXX: how does guestfs work vs snapshots?
    Then only the expected files are present on the persistence partition on USB drive "current"
    Given I start Tails from USB drive "current" with network unplugged and I login with read-only persistence enabled
    Then Tails is running from USB drive "current"
    And the boot device has safe access rights
    And all persistence presets are enabled
    And there is no GNOME bookmark for the persistent Tor Browser directory
    And I write some files not expected to persist
    And I remove some files expected to persist
    And I take note of which persistence presets are available
    And I shutdown Tails and wait for the computer to power off
    # XXX: how does guestfs work vs snapshots?
    Then only the expected files are present on the persistence partition on USB drive "current"

  Scenario: Deleting a Tails persistent partition
    Given Tails has booted without network from a USB drive with a persistent partition and stopped at Tails Greeter's login screen
    And I log in to a new session
    Then Tails is running from USB drive "current"
    And the boot device has safe access rights
    And persistence is disabled
    But a Tails persistence partition exists on USB drive "current"
    And all notifications have disappeared
    When I delete the persistent partition
    Then there is no persistence partition on USB drive "current"

