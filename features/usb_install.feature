@product
Feature: Installing Tails to a USB drive
  As a Tails user
  I want to install Tails to a suitable USB drive

  Scenario: Try installing Tails to a too small USB drive
    Given Tails has booted from DVD without network and logged in
    And I temporarily create a 2 GiB disk named "too-small-device"
    And I start Tails Installer in "Clone & Install" mode
    But a suitable USB device is not found
    When I plug USB drive "too-small-device"
    Then Tails Installer detects that a device is too small
    And a suitable USB device is not found

  Scenario: Test that Tails installer can detect when a target USB drive is inserted or removed
    Given Tails has booted from DVD without network and logged in
    And I temporarily create a 4 GiB disk named "temp"
    And I start Tails Installer in "Clone & Install" mode
    But a suitable USB device is not found
    When I plug USB drive "temp"
    Then the "temp" USB drive is selected
    When I unplug USB drive "temp"
    Then no USB drive is selected
    And a suitable USB device is not found

  Scenario: Booting Tails from a USB drive without a persistent partition
    Given Tails has booted without network from a USB drive without a persistent partition and stopped at Tails Greeter's login screen
    When I log in to a new session
    Then Tails seems to have booted normally
    And Tails is running from USB drive "current"
    And the persistent Tor Browser directory does not exist
    And there is no persistence partition on USB drive "current"

  Scenario: Booting Tails from a USB drive in UEFI mode
    Given Tails has booted without network from a USB drive without a persistent partition and stopped at Tails Greeter's login screen
    Then I power off the computer
    Given the computer is set to boot in UEFI mode
    When I start Tails from USB drive "current" with network unplugged and I login
    Then the boot device has safe access rights
    And Tails is running from USB drive "current"
    And the boot device has safe access rights
    And Tails has started in UEFI mode

  Scenario: Installing Tails to a USB drive with an MBR partition table but no partitions, and making sure that it boots
    Given a computer
    And I temporarily create a 4 GiB disk named "mbr"
    And I create a msdos label on disk "mbr"
    And I start Tails from DVD with network unplugged and I login
    And I plug USB drive "mbr"
    And I "Clone & Install" Tails to USB drive "mbr"
    Then the running Tails is installed on USB drive "mbr"
    But there is no persistence partition on USB drive "mbr"
    When I shutdown Tails and wait for the computer to power off
    And I start Tails from USB drive "mbr" with network unplugged and I login
    Then Tails is running from USB drive "mbr"
    And the boot device has safe access rights
    And there is no persistence partition on USB drive "mbr"

  Scenario: Cat:ing a Tails isohybrid to a USB drive and booting it, then trying to upgrading it but ending up having to do a fresh installation, which boots
    Given a computer
    And I create a 4 GiB disk named "isohybrid"
    And I cat an ISO of the Tails image to disk "isohybrid"
    And I start Tails from USB drive "isohybrid" with network unplugged and I login
    Then Tails is running from USB drive "isohybrid"
    When I shutdown Tails and wait for the computer to power off
    And I start Tails from DVD with network unplugged and I login
    And I try a "Clone & Upgrade" Tails to USB drive "isohybrid"
    Then I am suggested to do a "Clone & Install"
    When I kill the process "liveusb-creator"
    And I "Clone & Install" Tails to USB drive "isohybrid"
    Then the running Tails is installed on USB drive "isohybrid"
    But there is no persistence partition on USB drive "isohybrid"
    When I shutdown Tails and wait for the computer to power off
    And I start Tails from USB drive "isohybrid" with network unplugged and I login
    Then Tails is running from USB drive "isohybrid"
    And the boot device has safe access rights
    And there is no persistence partition on USB drive "isohybrid"
