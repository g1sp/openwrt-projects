# Home Network Copilot (Demo)

Single-page demo that runs on your MacBook: natural-language questions about your "home network" answered by a **local SLM** (Ollama). No cloud, no real router required.

**Simulated router:** The app injects mock router state (connected devices: MacBook-Pro, Kids-Tablet, Living-Room-TV; last event: DNS block for ads.example.com from Kids-Tablet) into every prompt, and uses a system prompt so the model answers as the "router copilot" only—no generic chatbot replies. Edit `MOCK_DEVICES` and `MOCK_LAST_EVENT` in `server.py` to change the scenario.

## What it does

Only these phrases trigger the **mock router** and get SLM answers. Anything else (e.g. "hello", "what's the weather") returns a fixed "I'm the router copilot, try these commands" message — so you never get generic chatbot replies.

| You say | What runs (mock router) |
|--------|--------------------------|
| **Who's connected?** or **List devices** | List connected devices (MacBook-Pro, Kids-Tablet, Living-Room-TV); SLM summarizes. |
| **Why did you block that?** or **Explain the last block** | Explain last event (DNS block for ads.example.com from Kids-Tablet); SLM gives 2 sentences + action. |
| **Block Kids-Tablet** or **Block 192.168.1.102** | SLM extracts device; app returns "Blocked … (demo)". |
| **Unblock Kids-Tablet** or **Allow Kids-Tablet** | SLM extracts device; app returns "Unblocked … (demo)". |
| **What can you do?** or **Help** | SLM lists router-only capabilities. |

## Requirements

- **Python 3** (stdlib only; no pip install).
- **Ollama** installed and running (`ollama serve`), with at least one model (e.g. `ollama run phi3:mini` or `llama3.2`).

## Run the demo

```bash
# Terminal 1: Ollama is usually already running (if not: ollama serve)
ollama run phi3:mini   # pull/run a model if needed

# Terminal 2: start the copilot server (use python3, not sh)
cd OpenWrt/home-copilot-demo
python3 server.py
```

**Then open in your browser:** **http://localhost:8765** (or the port printed).  
**Do not use http://localhost:11434** — that is Ollama’s API; the copilot UI and buttons are only on port 8765.

If you see **Address already in use**, the server will try the next port (8766, 8767, …). Use the URL it prints. To free port 8765: `lsof -i :8765` then `kill <PID>`.

## Configuration

- **OLLAMA_MODEL** — Model name (default: `phi3:mini`). Set in env or in `server.py`.
- **OLLAMA_HOST** — Ollama API base URL (default: `http://localhost:11434`).

## Project layout

- `server.py` — HTTP server, Ollama client, mock data, prompt logic.
- `index.html` — Single-page UI: input, send, show result.
- `README.md` — This file.
