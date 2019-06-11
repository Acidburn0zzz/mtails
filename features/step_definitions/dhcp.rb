Then /^the hostname should not have been leaked on the network$/ do
  begin
    hostnames = ["amnesia", $vm.execute("hostname").stdout.chomp]
    packets = PacketFu::PcapFile.new.file_to_array(filename: @sniffer.pcap_file)
    packets.each do |p|
      if PacketFu::IPPacket.can_parse?(p)
        payload = PacketFu::IPPacket.parse(p).payload
      elsif PacketFu::IPv6Packet.can_parse?(p)
        payload = PacketFu::IPv6Packet.parse(p).payload
      else
        next
      end
      hostnames.each do |hostname|
        if payload.match(hostname)
          raise "Hostname leak detected: #{hostname}"
        end
      end
    end
  rescue Exception => e
    save_failure_artifact("Network capture", @sniffer.pcap_file)
    raise e
  end
end
