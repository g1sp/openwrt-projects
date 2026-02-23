#!/bin/sh
# Network Sentinel — template-based explainer (Phase A)
# Reads event line(s), outputs plain-English explanation + suggested action.
# Event line format: TYPE	TS	SRC	DST	PORT	DOMAIN	REASON

EVENTS_FILE="${SENTINEL_EVENTS_FILE:-/tmp/sentinel_events.log}"
if [ -z "$SENTINEL_TEMPLATES" ]; then
	[ "${0%/*}" = /usr/bin ] && SENTINEL_TEMPLATES=/usr/share/sentinel/templates || SENTINEL_TEMPLATES="${0%/*}/templates"
fi
TEMPLATES_FILE="$SENTINEL_TEMPLATES"

substitute() {
	local text="$1" src="$2" dst="$3" port="$4" domain="$5" reason="$6"
	echo "$text" | sed \
		-e "s|%SRC%|${src}|g" \
		-e "s|%DST%|${dst}|g" \
		-e "s|%PORT%|${port}|g" \
		-e "s|%DOMAIN%|${domain}|g" \
		-e "s|%REASON%|${reason}|g"
}

explain_one() {
	local type="$1" ts="$2" src="$3" dst="$4" port="$5" domain="$6" reason="$7"
	local line explanation action
	while IFS= read -r line; do
		[ -z "$line" ] || case "$line" in \#*) continue;; esac
		case "$line" in
			"$type"\|*)
				explanation=$(echo "$line" | cut -d'|' -f2)
				action=$(echo "$line" | cut -d'|' -f3)
				explanation=$(substitute "$explanation" "$src" "$dst" "$port" "$domain" "$reason")
				action=$(substitute "$action" "$src" "$dst" "$port" "$domain" "$reason")
				echo "---"
				echo "What happened: $explanation"
				echo "Suggested action: $action"
				echo "Event: $type @ $ts | src=$src dst=$dst port=$port domain=$domain"
				return 0
				;;
		esac
	done < "$TEMPLATES_FILE" 2>/dev/null
	# Fallback to UNKNOWN
	while IFS= read -r line; do
		case "$line" in UNKNOWN\|*)
			explanation=$(echo "$line" | cut -d'|' -f2)
			action=$(echo "$line" | cut -d'|' -f3)
			explanation=$(substitute "$explanation" "$src" "$dst" "$port" "$domain" "$reason")
			action=$(substitute "$action" "$src" "$dst" "$port" "$domain" "$reason")
			echo "---"
			echo "What happened: $explanation"
			echo "Suggested action: $action"
			echo "Event: $type @ $ts"
			return 0
			;;
		esac
	done < "$TEMPLATES_FILE" 2>/dev/null
	echo "---"
	echo "What happened: Network activity was logged ($type)."
	echo "Suggested action: Review router logs if you see repeated or suspicious patterns."
	echo "Event: $type @ $ts"
}

# Read event line (TAB-separated): TYPE TS SRC DST PORT DOMAIN REASON
process_line() {
	local line="$1"
	[ -z "$line" ] && return 1
	explain_one \
		"$(echo "$line" | cut -f1)" \
		"$(echo "$line" | cut -f2)" \
		"$(echo "$line" | cut -f3)" \
		"$(echo "$line" | cut -f4)" \
		"$(echo "$line" | cut -f5)" \
		"$(echo "$line" | cut -f6)" \
		"$(echo "$line" | cut -f7)"
}

# Usage: explainer.sh [event_file] [last N lines]
# With no args: read EVENTS_FILE, explain last 1 event
main() {
	local file="${1:-$EVENTS_FILE}"
	local n="${2:-1}"
	[ -r "$file" ] || { echo "No events file: $file"; return 1; }
	tail -n "$n" "$file" | while read -r event_line; do
		process_line "$event_line"
	done
}

main "$@"
