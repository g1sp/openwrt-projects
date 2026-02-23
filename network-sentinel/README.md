# Network Sentinel

Plain-English threat briefings from firewall and DNS activity on OpenWrt. Part of the Synapse-style "Guardian Skill" idea: read router signals, explain what happened in 2–3 sentences, suggest a safe action. No automatic firewall changes — explain only.

## SLM (Phase B)

- **On-device (256 MB+ RAM):** **SmolLM2-135M** (Q2_K or Q4_K_M GGUF, ~35–75 MB) via **llama.cpp**. One binary, CPU-only, ARM/ARM64 friendly.
- **Fallback:** Template-based explanations (Phase A) when SLM is not installed or fails.
- **Optional:** Proxy to a home server running Ollama/llama.cpp with Phi-3 or Qwen2.5 for richer text.

## Phases

- **Phase A:** Log collection + event buffer + template-based explanations. Works on any OpenWrt router (64 MB+).
- **Phase B:** Optional SLM path: build a short prompt from event context, call `llama.cpp` (local or proxy), parse explanation + action; fall back to templates on timeout or error.

## Usage

- **CLI:** `sentinel-brief` — show last incident. `sentinel-brief -n 5` — last 5. `sentinel-brief --daily` — summary of last 24h (template-only for now).
- **Output:** Plain text to stdout; optional JSON for LuCI. Briefs written to `/tmp/sentinel_brief.txt` when run via cron.

## Install (OpenWrt)

From OpenWrt build tree: add this package and build, or copy `src/` to the device and run scripts manually. See `package/` for Makefile and control.

## Project layout

- `src/collector.sh` — parse logread + dnsmasq, emit normalized events.
- `src/explainer.sh` — template-based explanation + action (Phase A).
- `src/slm_brief.sh` — optional SLM call (llama.cpp or proxy), fallback to explainer.
- `src/sentinel-brief` — CLI entrypoint.
- `src/templates` — event-type → explanation + action (sourced by explainer).
- `package/` — OpenWrt ipkg Makefile and control.
