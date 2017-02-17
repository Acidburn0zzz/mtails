require 'uri'

Given /^the only hosts in APT sources are "([^"]*)"$/ do |hosts_str|
  hosts = hosts_str.split(',')
  $vm.file_content("/etc/apt/sources.list /etc/apt/sources.list.d/*").chomp.each_line { |line|
    next if ! line.start_with? "deb"
    source_host = URI(line.split[1]).host
    if !hosts.include?(source_host)
      raise "Bad APT source '#{line}'"
    end
  }
end

Given /^no proposed-updates APT suite is enabled$/ do
  $vm.file_content("/etc/apt/sources.list /etc/apt/sources.list.d/*").chomp.each_line do |line|
    assert(not(line.match("-proposed-updates")),
           "proposed-updates APT source found: #{line}")
  end
end

When /^I configure APT to use non-onion sources$/ do
  script = <<-EOF
  use strict;
  use warnings FATAL => "all";
  s{vwakviie2ienjx6t[.]onion}{ftp.us.debian.org};
  s{sgvtcaew4bxjd7ln[.]onion}{security.debian.org};
  s{sdscoq7snqtznauu[.]onion}{deb.torproject.org};
  s{jenw7xbd6tf7vfhp[.]onion}{deb.tails.boum.org};
EOF
  # VMCommand:s cannot handle newlines, and they're irrelevant in the
  # above perl script any way
  script.delete!("\n")
  $vm.execute_successfully(
    "perl -pi -E '#{script}' /etc/apt/sources.list /etc/apt/sources.list.d/*"
  )
end

When /^I update APT using apt$/ do
  recovery_proc = Proc.new do
    step 'I kill the process "apt"'
    $vm.execute('rm -rf /var/lib/apt/lists/*')
  end
  retry_tor(recovery_proc) do
    Timeout::timeout(15*60) do
      $vm.execute_successfully("echo #{@sudo_password} | " +
                               "sudo -S apt update", :user => LIVE_USER)
    end
  end
end

Then /^I should be able to install a package using apt$/ do
  package = "cowsay"
  recovery_proc = Proc.new do
    step 'I kill the process "apt"'
    $vm.execute("apt purge #{package}")
  end
  retry_tor(recovery_proc) do
    Timeout::timeout(2*60) do
      $vm.execute_successfully("echo #{@sudo_password} | " +
                               "sudo -S apt install #{package}",
                               :user => LIVE_USER)
    end
  end
  step "package \"#{package}\" is installed"
end

When /^I update APT using Synaptic$/ do
  recovery_proc = Proc.new do
    step 'I kill the process "synaptic"'
    step "I start Synaptic"
  end
  retry_tor(recovery_proc) do
    try_for(60, :msg => "Failed to trigger the reload of the package list") {
      # here using the Synaptic keyboard shortcut is more effective on retries.
      @screen.type("r", Sikuli::KeyModifier.CTRL)
      @screen.wait('SynapticReloadPrompt.png', 10)
    }
    try_for(15*60, :msg => "Took too much time to download the APT data") {
      !$vm.has_process?("/usr/lib/apt/methods/tor+http")
    }
    if @screen.exists('SynapticFailure.png')
      raise "Updating APT with Synaptic failed."
    end
    if !$vm.has_process?("synaptic")
      raise "Synaptic process vanished, did it segfault again?"
    end
  end
end

Then /^I should be able to install a package using Synaptic$/ do
  package = "cowsay"
  recovery_proc = Proc.new do
    step 'I kill the process "synaptic"'
    $vm.execute("apt -y purge #{package}")
    step "I start Synaptic"
  end
  retry_tor(recovery_proc) do
    try_for(60) do
      @screen.wait_and_click('SynapticSearchButton.png', 10)
      @screen.wait_and_click('SynapticSearchWindow.png', 10)
    end
    @screen.type(package + Sikuli::Key.ENTER)
    @screen.wait_and_double_click('SynapticCowsaySearchResult.png', 20)
    @screen.wait_and_click('SynapticApplyButton.png', 10)
    @screen.wait('SynapticApplyPrompt.png', 60)
    @screen.type(Sikuli::Key.ENTER)
    @screen.wait('SynapticChangesAppliedPrompt.png', 4*60)
    step "package \"#{package}\" is installed"
  end
end

When /^I start Synaptic$/ do
  step 'I start "Synaptic Package Manager" via the GNOME "System Tools" applications menu'
  deal_with_polkit_prompt('PolicyKitAuthPrompt.png', @sudo_password)
  @screen.wait('SynapticLoaded.png', 30)
end
