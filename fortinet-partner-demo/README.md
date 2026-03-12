# Fortinet Partner Demo

Synapse-style demos for Fortinet channel partners: **Policy Translator**, **Alert Triage Engine**, and **Customer Report Narrator**. All three run on a single page, powered by a local SLM (Ollama). No cloud; no real FortiGate or FortiAnalyzer required — everything uses simulated data.

## Plan & use cases

**Goal:** Help Fortinet sellers simplify setup and management of Fortinet devices for small businesses. Solution: a **mini-PC** the partner carries to customer sites; software on the mini-PC supports typical use cases partners struggle with.

**Use cases (implemented):**

- **Policy Translator** — Natural-language security intent → FortiOS CLI + summary (for human review; nothing applied automatically).
- **Alert Triage Engine** — FortiAnalyzer-style logs → prioritized High/Medium/Low report with explanations and recommended actions.
- **Customer Report Narrator** — Mock telemetry → executive-style monthly security narrative for C-level readers.

**What to implement next:** Depends on partner feedback (e.g. more policies, real device discovery, or export formats). See **[USE_CASES.md](USE_CASES.md)** for why these three map to real partner pain points and for **additional use cases** (VPN intent→config, compliance summary, troubleshooting “why can’t X reach Y?”, rule cleanup, branch provisioning, SD-WAN, upgrade planning, quoting/BOM).

## Local AI — data stays on your machine

The UI shows an **Ollama status** indicator and a clear message: *"All processing runs on your machine via Ollama. No data is sent to the cloud."* Every demo panel is labeled **Powered by local LLM**. No telemetry or prompts leave the device.

## Demos (eight)

| Demo | What it does |
|------|----------------|
| **Policy Translator** | Plain-English security intent → FortiOS CLI + summary. For human review only. |
| **Alert Triage Engine** | FortiAnalyzer-style log lines → prioritized triage report (High/Medium/Low) with explanations and actions. |
| **Customer Report Narrator** | Telemetry (blocked threats, VPN, bandwidth) → executive monthly security narrative for C-level. |
| **Quote / BOM** | Customer requirements (users, sites, UTM, HA) → suggested FortiGate model and license bundles with rationale. |
| **Customer Products** | Customer name or environment description → list of Fortinet products deployed (FortiGate, FortiAnalyzer, FortiClient); handy before meetings, renewals, or audits. |
| **VPN Wizard** | Describe VPN requirement (e.g. "Remote access for 30 users, split tunnel") → checklist, FortiOS CLI snippets, and caveats. |
| **Compliance Summary** | Short description of customer setup → one-paragraph compliance summary + controls list for auditors. |
| **Troubleshooter** | Symptom (e.g. "VPN users can't reach file server") + optional logs → likely causes, suggested checks, and one quick win. |

## Host the mockup on GitHub Pages

A **static mockup** (same UI, sample outputs only, no backend) is in the **`docs/`** folder. You can host it on GitHub Pages to share with others:

- **Option A:** Create a new repo, copy `docs/index.html` to the repo root, push, then enable **Pages** from the main branch (root). Your site: `https://USERNAME.github.io/REPO_NAME/`.
- **Option B:** In this repo enable **Settings → Pages → Deploy from branch**, branch **main**, folder **/docs**. Site: `https://USERNAME.github.io/OpenWrt/` (if the repo is named OpenWrt).

See **`docs/README.md`** for step-by-step instructions.

## Run locally (live AI)

1. **Ollama** running with a model, e.g.:
   ```bash
   ollama run phi3:mini
   ```
2. Start the demo server:
   ```bash
   cd fortinet-partner-demo
   python3 server.py
   ```
3. Open **http://localhost:8767** in your browser.

Port is configurable: `FORTINET_DEMO_PORT=8888 python3 server.py`. Model: `OLLAMA_MODEL=llama3.2 python3 server.py`.

## Requirements

- Python 3.6+
- Ollama installed and running (default: `http://localhost:11434`)

No Fortinet hardware or APIs needed; the demos are self-contained for partner briefings.
