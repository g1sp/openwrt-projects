#!/bin/sh
# Network Sentinel — log collector
# Reads logread and dnsmasq log, emits normalized events (TAB-separated):
#   TYPE	TS	SRC	DST	PORT	DOMAIN	REASON
# TS = Unix timestamp. SRC/DST/PORT/DOMAIN/REASON = - when empty.

EVENTS_FILE="${SENTINEL_EVENTS_FILE:-/tmp/sentinel_events.log}"
MAX_EVENTS="${SENTINEL_MAX_EVENTS:-500}"
# Optional: pass -d to run once (daemon off); otherwise tail logread

emit() {
	printf '%s\n' "$1" >> "$EVENTS_FILE"
	# Keep last N lines (simple ring)
	line_count=$(wc -l < "$EVENTS_FILE" 2>/dev/null) || line_count=0
	if [ "$line_count" -gt "$MAX_EVENTS" ] 2>/dev/null; then
		tail -n "$MAX_EVENTS" "$EVENTS_FILE" > "${EVENTS_FILE}.tmp"
		mv "${EVENTS_FILE}.tmp" "$EVENTS_FILE"
	fi
}

ts() { date +%s 2>/dev/null || echo "0"; }

# Parse kernel/firewall lines (OpenWrt: DROP, REJECT in kernel log)
# Example: ... DROP IN=br-lan OUT= SRC=192.168.1.1 DST=224.0.0.1 ...
parse_fw() {
	local line="$1"
	case "$line" in
		*DROP*|*REJECT*)
			local src="" dst="" port=""
			for word in $line; do
				case "$word" in SRC=*) src="${word#SRC=}";; DST=*) dst="${word#DST=}";; DPT=*) port="${word#DPT=}";; SPT=*) port="${port:-${word#SPT=}}";; esac
			done
			[ -n "$src" ] || return
			emit "FW_DROP	$(ts)	${src}	${dst}	${port}	-	$line"
			;;
		esac
}

# Parse dnsmasq lines
# reply ... is 1.2.3.4 / query[A] ... from 192.168.1.1 / blocked ... is 0.0.0.0
parse_dns() {
	local line="$1"
	local src="" domain="" blocked=""
	case "$line" in
		*" blocked "*|*" is 0.0.0.0"*)
			# blocked query
			for word in $line; do
				case "$word" in
					from) blocked="from";;
					*) [ "$blocked" = "from" ] && src="$word" && blocked="";;
				esac
			done
			domain=$(echo "$line" | sed -n 's/.*query\[.*\] \([^ ]*\) .*/\1/p')
			[ -z "$domain" ] && domain=$(echo "$line" | sed -n 's/.* blocked \([^ ]*\) .*/\1/p')
			emit "DNS_BLOCK	$(ts)	${src}	-	-	${domain}	blocked"
			;;
		*"query["*" from "*)
			domain=$(echo "$line" | sed -n 's/.*query\[.*\] \([^ ]*\) .*/\1/p')
			for word in $line; do
				case "$word" in from) blocked="from";; *) [ "$blocked" = "from" ] && src="$word" && blocked="";; esac
			done
			[ -n "$domain" ] && emit "DNS_QUERY	$(ts)	${src}	-	-	${domain}	-"
			;;
		esac
}

# Run once: parse last chunk of logread and append to events file
run_once() {
	logread 2>/dev/null | tail -n 200 | while read -r line; do
		case "$line" in
			*kernel*DROP*|*kernel*REJECT*) parse_fw "$line";;
			*dnsmasq*) parse_dns "$line";;
		esac
	done
}

# Daemon: follow logread (OpenWrt logread -f)
run_follow() {
	logread -f 2>/dev/null | while read -r line; do
		case "$line" in
			*kernel*DROP*|*kernel*REJECT*) parse_fw "$line";;
			*dnsmasq*) parse_dns "$line";;
		esac
	done
}

case "${1:-}" in
	-d|--once) run_once ;;
	*) run_follow ;;
esac
