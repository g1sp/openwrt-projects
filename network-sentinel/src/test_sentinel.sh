#!/bin/sh
# Network Sentinel — small test: inject fake events, run explainer and CLI, show output.

# Resolve directory containing this script (works when run as sh test_sentinel.sh or ./test_sentinel.sh)
case "$0" in
	*/*) _d="${0%/*}"; ;;
	*) _d="."; ;;
esac
SENTINEL_DIR=$(cd "$_d" 2>/dev/null && pwd) || SENTINEL_DIR="$PWD"
EVENTS_FILE="${SENTINEL_EVENTS_FILE:-$SENTINEL_DIR/test_events.log}"
ts=$(date +%s 2>/dev/null) || ts=1739123456

# Backup existing events if any, then create test events
if [ -r "$EVENTS_FILE" ]; then
	mv "$EVENTS_FILE" "${EVENTS_FILE}.bak" 2>/dev/null
fi

# Inject 3 fake events: FW_DROP, DNS_BLOCK, DNS_QUERY
{
	echo "FW_DROP	$ts	192.168.1.50	10.0.0.1	443	-	DROP IN=br-lan"
	echo "DNS_BLOCK	$((ts+1))	192.168.1.50	-	-	ads.example.com	blocked"
	echo "DNS_QUERY	$((ts+2))	192.168.1.100	-	-	google.com	-"
} > "$EVENTS_FILE"

export SENTINEL_EVENTS_FILE="$EVENTS_FILE"
export SENTINEL_TEMPLATES="$SENTINEL_DIR/templates"

echo "=== Test 1: Explain last 1 event (template explainer) ==="
sh "$SENTINEL_DIR/explainer.sh" "$EVENTS_FILE" 1

echo ""
echo "=== Test 2: Explain last 3 events (sentinel-brief -n 3) ==="
SENTINEL_DIR="$SENTINEL_DIR" sh "$SENTINEL_DIR/sentinel-brief" -n 3

echo ""
echo "=== Test 3: SLM fallback (no SLM configured → templates) ==="
SENTINEL_DIR="$SENTINEL_DIR" sh "$SENTINEL_DIR/slm_brief.sh"

# Restore backup if we had one
if [ -r "${EVENTS_FILE}.bak" ]; then
	mv "${EVENTS_FILE}.bak" "$EVENTS_FILE" 2>/dev/null
else
	rm -f "$EVENTS_FILE" 2>/dev/null
fi

echo ""
echo "=== All tests completed ==="
