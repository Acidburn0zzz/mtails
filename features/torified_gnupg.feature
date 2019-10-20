@product @check_tor_leaks
Feature: Keyserver interaction with GnuPG
  As a Tails user
  when I interact with keyservers using various GnuPG tools
  the configured keyserver must be used
  and all Internet traffic should flow only through Tor.

  Background:
    Given I have started Tails from DVD and logged in and the network is connected
    And the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" OpenPGP key is not in the live user's public keyring
    And GnuPG is configured to use a non-Onion keyserver
    And Seahorse is configured to use Chutney's onion keyserver

  Scenario: Fetching OpenPGP keys using GnuPG should work and be done over Tor.
    When I fetch the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" OpenPGP key using the GnuPG CLI
    And the GnuPG fetch is successful
    Then the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" key is in the live user's public keyring
    And GnuPG's dirmngr uses the configured keyserver

  #14770
  @fragile
  Scenario: Fetching OpenPGP keys using Seahorse should work and be done over Tor.
    When I fetch the "30F80A2C" OpenPGP key using Seahorse
    And the Seahorse operation is successful
    Then the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" key is in the live user's public keyring

  #14770
  @fragile
  Scenario: Fetching OpenPGP keys using Seahorse via the OpenPGP Applet should work and be done over Tor.
    When I fetch the "30F80A2C" OpenPGP key using Seahorse via the OpenPGP Applet
    And the Seahorse operation is successful
    Then the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" key is in the live user's public keyring

  #14770
  @fragile
  Scenario: Syncing OpenPGP keys using Seahorse should work and be done over Tor.
    Given I fetch the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" OpenPGP key using the GnuPG CLI
    And the GnuPG fetch is successful
    And the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" key is in the live user's public keyring
    And the key "DF841752B55CD97FDA4879B29E5B04F430F80A2C" has at least 1 subkey
    And I delete the "85C7C1AAA3DFC34623B5516281119B9834AD5681" subkey from the live user's public keyring
    And the key "DF841752B55CD97FDA4879B29E5B04F430F80A2C" has no subkey
    When I start Seahorse
    Then Seahorse has opened
    And I enable key synchronization in Seahorse
    And I synchronize keys in Seahorse
    And the Seahorse operation is successful
    Then the key "DF841752B55CD97FDA4879B29E5B04F430F80A2C" has at least 1 subkey

  #14770
  @fragile
  Scenario: Syncing OpenPGP keys using Seahorse started from the OpenPGP Applet should work and be done over Tor.
    Given I fetch the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" OpenPGP key using the GnuPG CLI
    And the GnuPG fetch is successful
    And the "DF841752B55CD97FDA4879B29E5B04F430F80A2C" key is in the live user's public keyring
    And the key "DF841752B55CD97FDA4879B29E5B04F430F80A2C" has at least 1 subkey
    And I delete the "85C7C1AAA3DFC34623B5516281119B9834AD5681" subkey from the live user's public keyring
    And the key "DF841752B55CD97FDA4879B29E5B04F430F80A2C" has no subkey
    When I start Seahorse via the OpenPGP Applet
    Then Seahorse has opened
    And I enable key synchronization in Seahorse
    And I synchronize keys in Seahorse
    And the Seahorse operation is successful
    Then the key "DF841752B55CD97FDA4879B29E5B04F430F80A2C" has at least 1 subkey
