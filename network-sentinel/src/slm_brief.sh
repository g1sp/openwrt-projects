#!/bin/sh
# Network Sentinel — optional SLM brief (Phase B)
# Builds a short prompt from event(s), calls llama.cpp (local or proxy), parses
# "explanation" + "action". Falls back to template explainer on timeout/error.
# SLM: SmolLM2-135M (Q2_K/Q4_K_M) via llama.cpp recommended for 256MB+ routers.

SENTINEL_DIR="${SENTINEL_DIR:-${0%/*}}"
LLAMA_CPP="${LLAMA_CPP:-}"           # e.g. /usr/bin/llama-cli or empty
LLAMA_MODEL="${LLAMA_MODEL:-}"      # e.g. /usr/share/sentinel/smollm2-135m-q4_k_m.gguf
LLAMA_PROXY_URL="${LLAMA_PROXY_URL:-}"  # e.g. http://192.168.1.100:11434/api/generate
TIMEOUT="${SENTINEL_SLM_TIMEOUT:-15}"

export SENTINEL_EVENTS_FILE="${SENTINEL_EVENTS_FILE:-/tmp/sentinel_events.log}"
export SENTINEL_TEMPLATES="$SENTINEL_DIR/templates"

event_line="$1"
[ -z "$event_line" ] && event_line=$(tail -n 1 "$SENTINEL_EVENTS_FILE" 2>/dev/null)
[ -z "$event_line" ] && { echo "No event."; exit 1; }

type=$(echo "$event_line" | cut -f1)
ts=$(echo "$event_line" | cut -f2)
src=$(echo "$event_line" | cut -f3)
dst=$(echo "$event_line" | cut -f4)
port=$(echo "$event_line" | cut -f5)
domain=$(echo "$event_line" | cut -f6)
reason=$(echo "$event_line" | cut -f7)

prompt="You are a home network security assistant. In 2 short sentences explain what this event means, then in one sentence suggest a safe action. Event: type=$type src=$src dst=$dst port=$port domain=$domain. Reply with only: What happened: ... Suggested action: ..."

fallback() {
	tmp=$(mktemp 2>/dev/null) || tmp="/tmp/sentinel_slm.$$"
	echo "$event_line" > "$tmp"
	export SENTINEL_TEMPLATES="${SENTINEL_TEMPLATES:-$SENTINEL_DIR/templates}"
	[ "$SENTINEL_DIR" = /usr/share/sentinel ] && export SENTINEL_TEMPLATES=/usr/share/sentinel/templates
	if [ -x "$SENTINEL_DIR/explainer.sh" ]; then
		"$SENTINEL_DIR/explainer.sh" "$tmp" 1 2>/dev/null
	elif [ -r "$SENTINEL_DIR/explainer.sh" ]; then
		sh "$SENTINEL_DIR/explainer.sh" "$tmp" 1 2>/dev/null
	elif command -v sentinel-explainer >/dev/null 2>&1; then
		sentinel-explainer "$tmp" 1 2>/dev/null
	fi
	rm -f "$tmp"
	exit 0
}

# Local llama.cpp (e.g. llama-cli -m model -p "prompt" --no-display-prompt)
if [ -n "$LLAMA_CPP" ] && [ -n "$LLAMA_MODEL" ] && [ -f "$LLAMA_MODEL" ]; then
	res=$(echo "$prompt" | timeout "$TIMEOUT" "$LLAMA_CPP" -m "$LLAMA_MODEL" -p - --no-display-prompt -n 120 2>/dev/null) || fallback
	echo "---"
	echo "$res" | head -20
	echo "Event: $type @ $ts"
	exit 0
fi

# Proxy (Ollama-style or simple POST with prompt)
if [ -n "$LLAMA_PROXY_URL" ]; then
	body="{\"prompt\":\"$(echo "$prompt" | sed 's/"/\\"/g' | tr '\n' ' ')\",\"max_tokens\":120}"
	res=$(curl -s -m "$TIMEOUT" -X POST -H "Content-Type: application/json" -d "$body" "$LLAMA_PROXY_URL" 2>/dev/null) || fallback
	# Try to extract text (Ollama: .response, generic: .text or first line)
	text=$(echo "$res" | sed -n 's/.*"response":"\([^"]*\)".*/\1/p')
	[ -z "$text" ] && text=$(echo "$res" | sed -n 's/.*"text":"\([^"]*\)".*/\1/p')
	[ -z "$text" ] && text="$res"
	echo "---"
	echo "$text" | head -20
	echo "Event: $type @ $ts"
	exit 0
fi

# No SLM configured — use templates
fallback
