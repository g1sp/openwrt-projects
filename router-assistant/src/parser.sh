#!/bin/sh
# Router Assistant — parser: normalize input, match patterns, output intent and args.
# Output: INTENT	arg1	arg2	...   (TAB-separated)

normalize() {
	echo "$1" | tr 'A-Z' 'a-z' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//;s/[[:space:]]+/ /g'
}

# Extract first IPv4 address from string (after "block " or similar)
extract_ip() {
	echo "$1" | sed -n 's/.*[^0-9]\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' | head -1
}

# Rest of phrase after keyword (e.g. "block device Kids-Tablet" -> "Kids-Tablet")
rest_phrase() {
	local line="$1" kw="$2"
	line="${line#"$kw"}"
	echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

line=$(normalize "$1")
[ -z "$line" ] && exit 1

# Help
case "$line" in
	help|commands) echo "HELP"; exit 0 ;;
	"what can you do") echo "HELP"; exit 0 ;;
esac

# Block device: "block 192.168.1.50" or "block device Kids-Tablet"
case "$line" in
	block\ device\ *) echo "BLOCK	$(rest_phrase "$line" "block device")"; exit 0 ;;
	block\ *) ip=$(extract_ip "$line"); [ -n "$ip" ] && echo "BLOCK	$ip" || echo "BLOCK	$(rest_phrase "$line" "block")"; exit 0 ;;
esac

# Unblock / allow
case "$line" in
	unblock\ device\ *) echo "UNBLOCK	$(rest_phrase "$line" "unblock device")"; exit 0 ;;
	unblock\ *) ip=$(extract_ip "$line"); [ -n "$ip" ] && echo "UNBLOCK	$ip" || echo "UNBLOCK	$(rest_phrase "$line" "unblock")"; exit 0 ;;
	allow\ device\ *) echo "UNBLOCK	$(rest_phrase "$line" "allow device")"; exit 0 ;;
	allow\ *) ip=$(extract_ip "$line"); [ -n "$ip" ] && echo "UNBLOCK	$ip" || echo "UNBLOCK	$(rest_phrase "$line" "allow")"; exit 0 ;;
esac

# List clients
case "$line" in
	show\ clients|list\ clients|list\ devices|who\ is\ connected|connected\ devices) echo "LIST_CLIENTS"; exit 0 ;;
esac

# Guest WiFi
case "$line" in
	enable\ guest\ wifi|enable\ guest\ network|turn\ on\ guest|guest\ wifi\ on) echo "GUEST_WIFI	on"; exit 0 ;;
	disable\ guest\ wifi|disable\ guest\ network|turn\ off\ guest|guest\ wifi\ off) echo "GUEST_WIFI	off"; exit 0 ;;
esac

# Restart DNS
case "$line" in
	restart\ dns|restart\ dnsmasq) echo "RESTART_DNS"; exit 0 ;;
esac

# Status
case "$line" in
	status|router\ status|show\ status) echo "STATUS"; exit 0 ;;
esac

# No match
echo "UNKNOWN	$line"
exit 1
