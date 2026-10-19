#!/bin/bash
set -eu
if [ "$(id -u)" -ne 0 ]; then
    echo 'Run this script with sudo to bind DHCP port 67 and add the temporary interface address.' >&2
    exit 1
fi
if [ "$(uname -s)" != Darwin ]; then
    echo 'This setup is for macOS.' >&2
    exit 1
fi
if ! /sbin/ifconfig en8 | /usr/bin/grep -q 'ether f4:4d:ad:08:43:6b'; then
    echo 'en8 is no longer the expected USB Ethernet adapter. No changes made.' >&2
    exit 1
fi
if /usr/sbin/lsof -nP -iUDP:67 -t >/dev/null 2>&1; then
    echo 'A DHCP service is already listening on port 67. No changes made.' >&2
    exit 1
fi
if /sbin/ifconfig en8 | /usr/bin/grep -q 'inet 192.168.247.1 '; then
    echo 'The proposed temporary address is already present. No changes made.' >&2
    exit 1
fi
config_path="$(cd "$(dirname "$0")" && pwd)/bootpd.plist"
/usr/bin/plutil -lint "$config_path"
alias_added=0
server_pid=''
cleanup() {
    trap - EXIT INT TERM
    if [ -n "$server_pid" ]; then
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
    if [ "$alias_added" -eq 1 ]; then
        /sbin/ifconfig en8 inet 192.168.247.1 -alias || true
    fi
    echo 'Temporary DHCP stopped; temporary Ethernet address removed.'
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
/sbin/ifconfig en8 inet 192.168.247.1 netmask 255.255.255.0 alias
alias_added=1
echo 'Serving DHCP only on en8. Laptop: 192.168.247.1. Controller lease pool: 192.168.247.2.'
echo 'Keep this terminal running. Press Control-C when configuration is finished.'
/usr/libexec/bootpd -D -d -i en8 -f "$config_path" &
server_pid=$!
wait "$server_pid"
