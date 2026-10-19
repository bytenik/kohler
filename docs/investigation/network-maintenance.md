# Controller network maintenance


The controller's dedicated network Ethernet port is separate from the RJ45 system bus. A direct laptop connection initially received DHCP address `192.168.247.2`, MAC `00:14:6f:0e:33:ad`, from the temporary server in `network/start-dhcp.sh`.

### Update attempt captured on 2026-10-18

Capture: `network/controller-reconnect-01.pcap`, interface `en8`. The connected controller reported MAC `00:14:6f:0e:33:ad` and received `192.168.2.2`; this matches the previously observed identity despite a reported controller replacement. Hardware identity and firmware version remain unconfirmed.

The Ethernet capture was stopped after the update investigation: 45,019 packets captured, zero kernel drops reported. This capture is separate from all AD3 display-bus recordings. Firmware update completion was not established.

Times below are local EDT:

- 14:14:04: DHCP exchange completed. DNS lookup of `0.us.pool.ntp.org` through `8.8.8.8` succeeded, followed by an NTP server reply. Shared internet connectivity was therefore observed for these services.
- 14:14:54: browser requests included `/check_updates.cgi`.
- 14:14:55.411703: controller queried `8.8.8.8` for A record `pr0d3ct-upd.kohler.com` (literal digit zero and digit three).
- 14:14:55.471286: DNS returned NXDOMAIN. A second query received the same result. An independent laptop query to `8.8.8.8` also returned NXDOMAIN.
- 14:14:55.498242: controller sent a TCP SYN from port 5000 to `255.255.255.255:21`. Retransmissions followed at 14:14:58, 14:15:04, 14:15:16, and 14:15:40, with no FTP connection established. Port 21 suggests FTP, but no FTP application exchange was observed.

While the UI claimed an update was running, read-only `/ftp_status.cgi` responses showed `internet_status:"con"`, but zero downloaded bytes, zero files, and zero image sizes. `ftp_download_error` also remained zero. These status flags do not establish update progress. The broadcast destination immediately after DNS failure suggests failed name resolution is being used as an invalid destination address; this is an inference, not a confirmed firmware implementation detail. No firmware download or successful update has been observed.

On 2026-10-18, macOS Internet Sharing was enabled from Wi-Fi to USB 10/100/1G/2.5G LAN (`en8`) for firmware maintenance. Sharing created `bridge100` at `192.168.2.1/24`, with `en8` as its member. The controller subsequently received `192.168.2.2`, and DNS/NTP replies confirmed shared internet connectivity as documented above. Subsequent read-only inspection reports controller software `0.0.3.44`, Interface 1 graphics `0.1.3.32`, Interface 1 OS `0.0.3.0`, and connected Valve 2 software `0.12`. No successful firmware update was observed. Valve payload correlations are recorded in `VALVE_PROTOCOL.md`.
