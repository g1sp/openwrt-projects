#!/bin/sh
# Router Assistant — executor: run UCI/firewall/init.d per intent.
# Usage: executor.sh INTENT [args...]
# Expects: DRY_RUN=1 to only echo commands; CONFIRM_BLOCK=1 to require confirmation for block.

run() {
	if [ "$DRY_RUN" = 1 ]; then
		echo "[dry-run] $*"
	else
		"$@"
	fi
}

# Resolve hostname to IP via DHCP leases
resolve_host() {
	local name="$1"
	[ -z "$name" ] && return 1
	[ -r /tmp/dhcp.leases ] || return 1
	awk -v n="$name" 'tolower($4) == tolower(n) {print $2; exit}' /tmp/dhcp.leases
}

intent="$1"
shift

case "$intent" in
	HELP)
		echo "Supported: block <IP|name>, unblock <IP|name>, show clients, enable/disable guest wifi, restart dns, status, help"
		;;
	BLOCK)
		target="$1"
		[ -z "$target" ] && { echo "Error: block requires IP or device name."; exit 1; }
		ip="$target"
		# If not an IP, try to resolve from DHCP
		case "$target" in
			*.*.*.*) ;;
			*) ip=$(resolve_host "$target"); [ -z "$ip" ] && ip="$target"; ;;
		esac
		if [ "$CONFIRM_BLOCK" = 1 ] && [ "$DRY_RUN" != 1 ]; then
			printf "Block device %s (IP %s)? [y/N] " "$target" "$ip"
			read -r ans
			case "$ans" in y|Y|yes) ;; *) echo "Cancelled."; exit 0;; esac
		fi
		# OpenWrt: add drop rule in firewall (simplest: use iptables or a block zone)
		# Generic: uci add firewall rule; set drop; commit
		run iptables -I FORWARD -s "$ip" -j DROP 2>/dev/null || run ip6tables -I FORWARD -s "$ip" -j DROP 2>/dev/null
		echo "Blocked $target ($ip)."
		;;
	UNBLOCK)
		target="$1"
		[ -z "$target" ] && { echo "Error: unblock requires IP or device name."; exit 1; }
		ip="$target"
		case "$target" in
			*.*.*.*) ;;
			*) ip=$(resolve_host "$target"); [ -z "$ip" ] && ip="$target"; ;;
		esac
		run iptables -D FORWARD -s "$ip" -j DROP 2>/dev/null
		run ip6tables -D FORWARD -s "$ip" -j DROP 2>/dev/null
		echo "Unblocked $target ($ip)."
		;;
	LIST_CLIENTS)
		if [ "$DRY_RUN" = 1 ]; then
			echo "[dry-run] cat /tmp/dhcp.leases (or ubus call luci-rpc getDHCPLeases)"
		else
			if [ -r /tmp/dhcp.leases ]; then
				echo "Connected devices (DHCP leases):"
				awk '{printf "  %s  %s  %s\n", $2, $4, $3}' /tmp/dhcp.leases 2>/dev/null || cat /tmp/dhcp.leases
			else
				ubus call luci-rpc getDHCPLeases 2>/dev/null || echo "No DHCP lease file found."
			fi
		fi
		;;
	GUEST_WIFI)
		action="$1"
		if [ "$DRY_RUN" = 1 ]; then
			echo "[dry-run] uci set wireless.@wifi-iface[N].disabled=$([ "$action" = on ] && echo 0 || echo 1); uci commit wireless; wifi reload"
		else
			# Find guest interface (common: second wifi-iface or one with 'guest' in SSID)
			idx=$(uci show wireless 2>/dev/null | grep 'wireless\.@wifi-iface\[.*\]\.ssid' | while read -r l; do
				echo "$l" | sed 's/.*\[\([0-9]*\)\].*/\1/'
			done | head -2 | tail -1)
			[ -z "$idx" ] && idx=1
			uci set "wireless.@wifi-iface[$idx].disabled=$([ "$action" = on ] && echo 0 || echo 1)" 2>/dev/null
			uci commit wireless 2>/dev/null
			wifi reload 2>/dev/null
			echo "Guest WiFi $action."
		fi
		;;
	RESTART_DNS)
		if [ "$DRY_RUN" = 1 ]; then
			echo "[dry-run] /etc/init.d/dnsmasq restart"
		else
			run /etc/init.d/dnsmasq restart 2>/dev/null && echo "DNS restarted." || echo "Failed to restart DNS."
		fi
		;;
	STATUS)
		if [ "$DRY_RUN" = 1 ]; then
			echo "[dry-run] uptime; uci get network.lan.ipaddr; cat /tmp/dhcp.leases | wc -l"
		else
			echo "--- Router status ---"
			uptime 2>/dev/null || true
			lan_ip=$(uci get network.lan.ipaddr 2>/dev/null); [ -n "$lan_ip" ] && echo "LAN IP: $lan_ip"
			[ -r /tmp/dhcp.leases ] && echo "DHCP leases: $(wc -l < /tmp/dhcp.leases)"
		fi
		;;
	UNKNOWN)
		echo "Unknown command: $1"
		exit 1
		;;
	*)
		echo "Unknown intent: $intent"
		exit 1
		;;
esac
