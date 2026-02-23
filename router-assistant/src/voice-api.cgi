#!/bin/sh
# Router Assistant — voice/HTTP API (CGI).
# POST text=<phrase> or GET text=<phrase>; returns JSON with intent and result.
# Use with uhttpd or any CGI-capable server. For voice: external STT sends text here.

# Default paths (override via env on OpenWrt)
ASSIST_DIR="${ASSIST_DIR:-/usr/share/router-assistant}"
[ -r "$ASSIST_DIR/parser.sh" ] || ASSIST_DIR="$(cd "${0%/*}" 2>/dev/null && pwd)"
[ -r "$ASSIST_DIR/parser.sh" ] || ASSIST_DIR="."

# Read input: GET -> QUERY_STRING, POST -> stdin (application/x-www-form-urlencoded)
if [ "$REQUEST_METHOD" = "POST" ]; then
	[ -n "$CONTENT_LENGTH" ] && read -r -n "$CONTENT_LENGTH" body 2>/dev/null
	query="$body"
else
	query="$QUERY_STRING"
fi

# Parse text= from query string (+ = space; minimal %XX decode for portability)
text=""
for pair in $(echo "$query" | tr '&' '\n'); do
	case "$pair" in
		text=*) text="${pair#text=}"; break ;;
	esac
done
text=$(echo "$text" | tr '+' ' ')
# Decode %20 to space (common case)
text=$(echo "$text" | sed 's/%20/ /g')

# JSON escape for result string
json_escape() {
	echo "$1" | sed 's/\\/\\\\/g;s/"/\\"/g;s/\t/\\t/g;s/\r//g' | tr '\n' ' '
}

echo "Content-Type: application/json; charset=utf-8"
echo ""

if [ -z "$text" ]; then
	echo "{\"ok\":false,\"error\":\"missing text parameter\",\"hint\":\"POST or GET with text=your phrase\"}"
	exit 0
fi

# Run parser to get intent (no execution yet, so we can return intent in JSON)
parsed=$(export PATH="$PATH"; sh "$ASSIST_DIR/parser.sh" "$text" 2>/dev/null) || {
	echo "{\"ok\":false,\"error\":\"parse failed\",\"text\":\"$(json_escape "$text")\"}"
	exit 0
}
intent=$(echo "$parsed" | cut -f1)
args=$(echo "$parsed" | cut -f2-)

# Execute with --yes (no confirmation in API mode)
export DRY_RUN=0 CONFIRM_BLOCK=0 ASSIST_DIR
result=$(set -- $parsed; i="$1"; shift; sh "$ASSIST_DIR/executor.sh" "$i" "$@" 2>&1)

echo "{\"ok\":true,\"intent\":\"$intent\",\"text\":\"$(json_escape "$text")\",\"result\":\"$(json_escape "$result")\"}"
