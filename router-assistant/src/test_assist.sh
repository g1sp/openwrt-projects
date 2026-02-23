#!/bin/sh
# Quick test: parser + executor with --dry-run (no real UCI/firewall changes).

case "$0" in */*) _d="${0%/*}"; ;; *) _d="."; ;; esac
ASSIST_DIR=$(cd "$_d" 2>/dev/null && pwd) || ASSIST_DIR="$PWD"
export DRY_RUN=1
export CONFIRM_BLOCK=0

echo "=== Parser tests ==="
for phrase in "help" "show clients" "block 192.168.1.50" "block device Kids-Tablet" "enable guest wifi" "restart dns" "status"; do
	printf "  %-30s -> " "$phrase"
	sh "$ASSIST_DIR/parser.sh" "$phrase"
done

echo ""
echo "=== CLI (dry-run) ==="
for phrase in "help" "show clients" "status"; do
	echo "  $ phrase: $phrase"
	ASSIST_DIR="$ASSIST_DIR" sh "$ASSIST_DIR/router-assist" --dry-run "$phrase" 2>&1 | sed 's/^/    /'
done

echo ""
echo "=== Voice API (simulated GET) ==="
case "$0" in */*) _d="${0%/*}"; ;; *) _d="."; ;; esac
AD=$(cd "$_d" 2>/dev/null && pwd) || AD="$PWD"
export REQUEST_METHOD=GET QUERY_STRING="text=show%20clients" ASSIST_DIR="$AD"
api_out=$(sh "$AD/voice-api.cgi" 2>/dev/null)
echo "$api_out" | head -5
echo ""

echo "=== Done ==="
