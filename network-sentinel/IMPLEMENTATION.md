# Network Sentinel — Implementation summary

## Plan (as implemented)

1. **Log collector** (`collector.sh`) — Parses `logread` for kernel firewall (DROP/REJECT) and dnsmasq (query, blocked). Emits TAB-separated events: `TYPE	TS	SRC	DST	PORT	DOMAIN	REASON`. Appends to a ring file (`/tmp/sentinel_events.log`, last 500 events).
2. **Event buffer** — Same file; collector trims to `SENTINEL_MAX_EVENTS` (default 500).
3. **Template explainer** (`explainer.sh`) — Reads `templates` (format `TYPE|explanation|action` with %SRC% %DST% %PORT% %DOMAIN% %REASON%). Substitutes and prints "What happened:" + "Suggested action:" + "Event: ...".
4. **CLI** (`sentinel-brief`) — `-n N` last N events, `--daily` last 24h, `--refresh` run collector once, `--json` raw event lines. Calls explainer; writes last output to `/tmp/sentinel_brief.txt`.
5. **Optional SLM** (`slm_brief.sh`) — If `LLAMA_CPP` + `LLAMA_MODEL` set: run local llama.cpp with a short prompt. If `LLAMA_PROXY_URL` set: POST prompt to proxy (Ollama-style). Else: fallback to template explainer.
6. **OpenWrt package** — `package/Makefile` and `package/control`; installs binaries under `/usr/bin`, templates under `/usr/share/sentinel/templates`.

## SLM in use (Phase B)

- **Recommended on-device:** **SmolLM2-135M** (Q2_K or Q4_K_M GGUF), run with **llama.cpp** (`llama-cli` or `llama-server`). Suited for 256 MB+ RAM routers or Synapse-style mini-PC.
- **Config:** `LLAMA_CPP=/usr/bin/llama-cli`, `LLAMA_MODEL=/usr/share/sentinel/smollm2-135m-q4_k_m.gguf`.
- **Proxy option:** `LLAMA_PROXY_URL=http://192.168.1.x:11434/api/generate` (or similar) for Ollama or another server; no model on router.

## How to run (development)

```sh
export SENTINEL_DIR=/path/to/OpenWrt/network-sentinel/src
$SENTINEL_DIR/collector.sh --once    # append from logread
$SENTINEL_DIR/sentinel-brief --refresh -n 3
```

## How to run (OpenWrt install)

```sh
sentinel-collector --once
sentinel-brief --refresh
sentinel-slm-brief   # optional; uses templates if no SLM configured
```
