@product @old_iso
Feature: Installing Tails to a USB drive
  As a Tails user
  If I have an old versoin of Tails installed on a USB device
  and the USB device has a persistent partition
  I want to upgrade Tails on it
  and keep my persistent partition in the process

  Scenario: Installing an old version of Tails to a pristine USB drive
    Given a computer
    And the computer is set to boot from the old Tails DVD
    And the network is unplugged
    And I start the computer
    When the computer boots Tails
    And I log in to a new session
    And the Tails desktop is ready
    And all notifications have disappeared
    And I create a 4 GiB disk named "old"
    And I plug USB drive "old"
    And I "Clone & Install" Tails to USB drive "old"
    Then the running Tails is installed on USB drive "old"
    But there is no persistence partition on USB drive "old"
    And I unplug USB drive "old"

  Scenario: Creating a persistent partition with the old Tails USB installation
    Given a computer
    And I start Tails from USB drive "old" with network unplugged and I login
    Then Tails is running from USB drive "old"
    And I create a persistent partition
    And I take note of which persistence presets are available
    Then a Tails persistence partition exists on USB drive "old"
    And I shutdown Tails and wait for the computer to power off

  Scenario: Writing files to a read/write-enabled persistent partition with the old Tails USB installation
    Given a computer
    And I start Tails from USB drive "old" with network unplugged and I login with persistence enabled
    Then Tails is running from USB drive "old"
    And all persistence presets are enabled
    And I write some files expected to persist
    And all persistent filesystems have safe access rights
    And all persistence configuration files have safe access rights
    And all persistent directories from the old Tails version have safe access rights
    And I take note of which persistence presets are available
    And I shutdown Tails and wait for the computer to power off
    # XXX: how does guestfs work vs snapshots?
    Then only the expected files are present on the persistence partition on USB drive "old"

  Scenario: Upgrading an old Tails USB installation from a Tails DVD
    Given a computer
    And I clone USB drive "old" to a new USB drive "to_upgrade"
    And I start Tails from DVD with network unplugged and I login
    And I plug USB drive "to_upgrade"
    And I "Clone & Upgrade" Tails to USB drive "to_upgrade"
    Then the running Tails is installed on USB drive "to_upgrade"
    And I unplug USB drive "to_upgrade"

  Scenario: Booting Tails from a USB drive upgraded from DVD with persistence enabled
    Given a computer
    And I start Tails from USB drive "to_upgrade" with network unplugged and I login with persistence enabled
    Then all persistence presets from the old Tails version are enabled
    Then Tails is running from USB drive "to_upgrade"
    And the boot device has safe access rights
    And the expected persistent files created with the old Tails version are present in the filesystem
    And all persistent directories from the old Tails version have safe access rights

  Scenario: Upgrading an old Tails USB installation from another Tails USB drive
    Given a computer
    And I clone USB drive "old" to a new USB drive "to_upgrade"
    And I start Tails from USB drive "current" with network unplugged and I login
    Then Tails is running from USB drive "current"
    And the boot device has safe access rights
    And I plug USB drive "to_upgrade"
    And I "Clone & Upgrade" Tails to USB drive "to_upgrade"
    Then the running Tails is installed on USB drive "to_upgrade"
    And I unplug USB drive "to_upgrade"
    And I unplug USB drive "current"

  Scenario: Booting Tails from a USB drive upgraded from USB with persistence enabled
    Given a computer
    And I start Tails from USB drive "to_upgrade" with network unplugged and I login with persistence enabled
    Then all persistence presets from the old Tails version are enabled
    And Tails is running from USB drive "to_upgrade"
    And the boot device has safe access rights
    And the expected persistent files created with the old Tails version are present in the filesystem
    And all persistent directories from the old Tails version have safe access rights

  Scenario: Upgrading an old Tails USB installation from an ISO image, running on the old version
    Given a computer
    And I clone USB drive "old" to a new USB drive "to_upgrade"
    And I setup a filesystem share containing the Tails ISO
    When I start Tails from USB drive "old" with network unplugged and I login
    And I plug USB drive "to_upgrade"
    And I do a "Upgrade from ISO" on USB drive "to_upgrade"
    Then the ISO's Tails is installed on USB drive "to_upgrade"
    And I unplug USB drive "to_upgrade"

  Scenario: Upgrading an old Tails USB installation from an ISO image, running on the new version
    Given a computer
    And I clone USB drive "old" to a new USB drive "to_upgrade"
    And I setup a filesystem share containing the Tails ISO
    And I start Tails from DVD with network unplugged and I login
    And I plug USB drive "to_upgrade"
    And I do a "Upgrade from ISO" on USB drive "to_upgrade"
    Then the ISO's Tails is installed on USB drive "to_upgrade"
    And I unplug USB drive "to_upgrade"

  Scenario: Booting a USB drive upgraded from ISO with persistence enabled
    Given a computer
    And I start Tails from USB drive "to_upgrade" with network unplugged and I login with persistence enabled
    Then all persistence presets from the old Tails version are enabled
    And Tails is running from USB drive "to_upgrade"
    And the boot device has safe access rights
    And the expected persistent files created with the old Tails version are present in the filesystem
    And all persistent directories from the old Tails version have safe access rights
