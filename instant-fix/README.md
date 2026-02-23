# Instant Fix — "Why is Zoom freezing?"

User asks in plain language (e.g. "Why is Zoom freezing?" or "Why is the internet slow?"). The app uses network telemetry (mock or real) and a local SLM (Ollama) to return a short explanation and a **suggested fix**. Suggested fixes may include: try 5 GHz WiFi, reset network settings on the router, reduce load from other devices. **The assistant will not suggest rebooting the router** — resetting network settings is the preferred remedy when a full reset is needed.

## Run (MacBook)

```bash
# Ollama running (e.g. ollama run phi3:mini)
cd OpenWrt/instant-fix
python3 server.py
# Open http://localhost:8766 (or the port printed)
```

## Config

- `OLLAMA_HOST`, `OLLAMA_MODEL` — same as home-copilot-demo.
- `INSTANT_FIX_PORT` — default 8766 (so it doesn’t clash with copilot on 8765).

## Project layout

- `server.py` — HTTP server, mock telemetry, Ollama prompt (no reboot; suggest 5 GHz, reset network settings).
- `index.html` — Single-page UI: ask a question, see explanation + suggested action.
