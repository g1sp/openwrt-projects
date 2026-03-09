#!/usr/bin/env python3
"""
Fortinet Partner Demo — Synapse-style on-prem SLM demos.
Three apps: Policy Translator, Alert Triage Engine, Customer Report Narrator.
Uses local Ollama; all simulated data. No real FortiGate/FortiAnalyzer.
"""

import json
import os
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi3:mini")
PORT = int(os.environ.get("FORTINET_DEMO_PORT", "8767"))

# --- System prompts ---
POLICY_TRANSLATOR_SYSTEM = """You are a FortiOS policy expert. The user will give a plain-English security or firewall intent. Your job is to output:
1) Valid FortiGate CLI commands (config firewall address, config firewall policy, etc.) that implement that intent.
2) A brief human-readable summary (1-2 sentences) of what the config does.

Output format — use these exact headers:
## CLI
(paste the FortiOS CLI commands here, one per line or block)
## Summary
(1-2 sentences)

Be precise: use real FortiOS syntax. If the intent mentions "Tor exit nodes", use an address object or external blocklist reference. If they say "except from VLAN X", add an exception policy or source restriction. Do not apply changes — only output the commands for human review."""

ALERT_TRIAGE_SYSTEM = """You are a FortiAnalyzer triage assistant. You will receive a list of security event log lines (simulated FortiGate/FortiAnalyzer style). Your job is to:
1) Cluster related events (e.g. same source IP, same signature, same threat type).
2) Assign priority: High (confirmed or likely threat), Medium (investigate), Low (probable false positive or informational).
3) For each cluster: give a one-line plain-English explanation and a recommended next action.

Output format — use clear sections:
## Triage Report
### High priority
- [brief explanation] — Recommended action: ...
### Medium priority
- ...
### Low priority
- ...

Keep the report concise. Focus on what a NOC tech should do next."""

REPORT_NARRATOR_SYSTEM = """You are writing an executive monthly security report for a Fortinet customer. You will receive telemetry metrics (blocked threats, bandwidth, top talkers, VPN usage, etc.). Write a short narrative (2-4 paragraphs) suitable for a C-level or business reader. Emphasize:
- Business outcomes (risk reduced, visibility gained) not technical jargon.
- Key numbers that matter (e.g. "47 threats blocked", "120 VPN sessions").
- One or two recommended next steps if relevant.

Tone: professional, confident, concise. No raw log lines. You may add a one-line opening like "This report summarizes your Fortinet security posture for the period." """

VPN_INTENT_SYSTEM = """You are a FortiGate VPN expert. The user will describe a VPN requirement in plain English (e.g. "Remote access VPN for 25 users with split tunnel" or "Site-to-site VPN between HQ and branch"). Your job is to output:
1) A short checklist of what needs to be configured (user groups, IPsec/SSL portal, firewall policies, etc.).
2) FortiOS CLI snippets (config vpn ssl settings, config user group, config firewall policy, etc.) that implement that intent. Use real FortiOS syntax.
3) One or two caveats or best practices (e.g. "Use a dedicated address pool for VPN" or "Enable 2FA for remote users if available").

Output format — use these exact headers:
## Checklist
(bullet list of steps)
## CLI
(FortiOS CLI blocks)
## Caveats
(1-2 sentences)

Do not apply changes; output is for human review only."""

COMPLIANCE_SUMMARY_SYSTEM = """You are a compliance and audit assistant for Fortinet deployments. The user will provide a short description of their setup (or paste a summary of firewall/VPN/logging config). Your job is to produce a brief "compliance summary" paragraph suitable for an auditor or customer, covering:
- Access control (firewall policies, VPN, admin access).
- Logging and monitoring (where logs go, retention).
- Encryption (VPN, HTTPS).
- Any gaps to mention (e.g. "No centralized logging" or "Recommend enabling 2FA").

Keep it to one short paragraph plus an optional 2-3 bullet "Controls in place" list. Tone: factual, professional. Do not make up specific IPs or hostnames; use placeholders like "central firewall" or "VPN gateway" if needed."""

TROUBLESHOOT_SYSTEM = """You are a FortiGate troubleshooting assistant. The user will describe a symptom (e.g. "User in branch A cannot reach the ERP server in the data center" or "VPN users cannot print"). You will optionally receive a few log lines or config snippets. Your job is to output:
1) **Likely causes** — 2-4 possible reasons (firewall policy, VPN split tunnel, routing, DNS, etc.) in order of likelihood.
2) **Suggested checks** — Concrete steps the engineer should do next (e.g. "Check firewall policy from VPN tunnel to LAN"; "Verify VPN address pool includes ERP subnet"; "Confirm DNS resolution for ERP hostname from VPN").
3) **One quick win** — The single most likely fix or diagnostic to try first.

Use clear section headers. Be concise. Do not run or apply any commands; only suggest. No auto-fix."""

QUOTE_BOM_SYSTEM = """You are a Fortinet partner sales assistant. The user will describe a customer requirement (number of users, sites, need for VPN, UTM, HA, etc.). Your job is to suggest a Bill of Materials (BOM) with:
1) FortiGate model(s) — e.g. 60F, 61F, 80F — with one-line rationale (user count, throughput, HA).
2) License bundles — FortiCare, FortiGuard/UTP (Unified Threat Protection), optional FortiClient for remote users.
3) Short rationale for each choice (e.g. "50 users and 2 sites fit 60F/61F tier; UTP covers full UTM in one SKU").

Do not include pricing. Output format — use these headers:
## Suggested BOM (add your pricing)
**Firewall** / **Licenses** / **Rationale** or similar. Keep it concise so a partner can paste into a quote tool."""

# --- Sample data for "Load sample" in UI ---
SAMPLE_LOGS = """2025-02-21 10:01:23 device=FortiGate-01 type=ips subtype=signature src=192.168.10.50 dst=203.0.113.10 msg="ET TOR Known Tor Relay"
2025-02-21 10:01:24 device=FortiGate-01 type=utm subtype=webfilter src=192.168.10.51 dst=0.0.0.0 msg="URL blocked: malware.example.com"
2025-02-21 10:02:01 device=FortiGate-01 type=ips subtype=signature src=192.168.10.50 dst=203.0.113.10 msg="ET TOR Known Tor Relay"
2025-02-21 10:05:11 device=FortiGate-01 type=traffic subtype=forward src=10.50.1.100 dst=8.8.8.8 port=443 msg="Allowed"
2025-02-21 10:06:00 device=FortiGate-01 type=utm subtype=webfilter src=192.168.10.51 dst=0.0.0.0 msg="URL blocked: ads.tracker.com"
2025-02-21 10:10:33 device=FortiGate-01 type=ips subtype=signature src=192.168.10.99 dst=198.51.100.5 msg="ET MALWARE C2 Beacon"
2025-02-21 10:11:02 device=FortiGate-01 type=vpn subtype=ssl src=192.168.10.10 msg="SSL-VPN login success"
2025-02-21 10:15:00 device=FortiGate-01 type=utm subtype=webfilter src=192.168.10.51 msg="URL blocked: ads.tracker.com"
"""

SAMPLE_TELEMETRY = {
    "period": "January 2025",
    "blocked_threats": 47,
    "top_source_ip": "192.168.10.50",
    "top_blocked_category": "Malware",
    "vpn_sessions_total": 120,
    "bandwidth_mbps_avg": 85,
    "policy_hits_top_rule": "LAN-to-WAN",
    "web_filter_blocks": 312,
    "ips_alerts": 18,
}

SAMPLE_VPN_INTENT = "Remote access VPN for about 30 users, split tunnel so only corporate traffic goes through the tunnel. No guest or contractor access for now."

SAMPLE_COMPLIANCE_INPUT = "FortiGate 60F at main office, firewall policies for LAN/WAN/DMZ, SSL-VPN for 20 remote users, logs sent to FortiAnalyzer on-prem. Admin access via HTTPS with local users."

SAMPLE_TROUBLESHOOT = "Users connecting over SSL-VPN cannot reach the internal file server at 10.50.1.10. They can reach the internet and the VPN tunnel is up."

SAMPLE_QUOTE = "Customer needs firewall with VPN and full UTM for about 50 users, 2 sites. May want HA in 12 months."


def ollama_generate(prompt: str, system: str = "") -> str:
    """Call Ollama /api/generate; return response text."""
    url = f"{OLLAMA_HOST}/api/generate"
    body = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    if system:
        body["system"] = system
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read().decode("utf-8"))
            return (data.get("response") or "").strip()
    except urllib.error.URLError as e:
        return f"[Ollama error: {e}]"
    except Exception as e:
        return f"[Error: {e}]"


def handle_policy_translate(intent: str) -> dict:
    if not (intent or "").strip():
        return {"ok": False, "error": "Empty intent."}
    prompt = f"User intent:\n{intent.strip()}\n\nOutput the FortiOS CLI and summary as specified."
    out = ollama_generate(prompt, system=POLICY_TRANSLATOR_SYSTEM)
    # Parse ## CLI and ## Summary if present for structured response; else return raw
    cli, summary = "", out
    if "## CLI" in out and "## Summary" in out:
        parts = out.split("## Summary", 1)
        cli_part = parts[0].replace("## CLI", "").strip()
        summary = parts[1].strip() if len(parts) > 1 else ""
        cli = cli_part
    else:
        cli = out
    return {"ok": True, "cli": cli, "summary": summary, "raw": out}


def handle_alert_triage(logs: str) -> dict:
    if not (logs or "").strip():
        return {"ok": False, "error": "No log lines."}
    prompt = f"Security event log lines (one per line):\n\n{logs.strip()}\n\nProduce the triage report."
    report = ollama_generate(prompt, system=ALERT_TRIAGE_SYSTEM)
    return {"ok": True, "report": report}


def handle_report_narrate(telemetry: dict) -> dict:
    if not telemetry:
        telemetry = SAMPLE_TELEMETRY
    blob = json.dumps(telemetry, indent=2)
    prompt = f"Telemetry for the report:\n\n{blob}\n\nWrite the executive narrative report."
    narrative = ollama_generate(prompt, system=REPORT_NARRATOR_SYSTEM)
    return {"ok": True, "narrative": narrative}


def ollama_status() -> dict:
    """Check if Ollama is reachable and return model info."""
    try:
        url = f"{OLLAMA_HOST}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
            models = data.get("models") or []
            names = [m.get("name", "") for m in models if m.get("name")]
            return {"ok": True, "models": names[:5], "default": OLLAMA_MODEL}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def handle_vpn_intent(intent: str) -> dict:
    if not (intent or "").strip():
        return {"ok": False, "error": "Empty intent."}
    prompt = f"User VPN requirement:\n{intent.strip()}\n\nOutput checklist, CLI, and caveats as specified."
    out = ollama_generate(prompt, system=VPN_INTENT_SYSTEM)
    return {"ok": True, "output": out}


def handle_compliance_summary(description: str) -> dict:
    if not (description or "").strip():
        return {"ok": False, "error": "Empty description."}
    prompt = f"Customer setup description:\n\n{description.strip()}\n\nProduce the compliance summary paragraph and controls list."
    out = ollama_generate(prompt, system=COMPLIANCE_SUMMARY_SYSTEM)
    return {"ok": True, "output": out}


def handle_troubleshoot(symptom: str, logs_or_config: str = "") -> dict:
    if not (symptom or "").strip():
        return {"ok": False, "error": "Describe the symptom."}
    prompt = f"Symptom:\n{symptom.strip()}\n\n"
    if (logs_or_config or "").strip():
        prompt += f"Optional context (logs or config):\n{logs_or_config.strip()}\n\n"
    prompt += "Output likely causes, suggested checks, and one quick win."
    out = ollama_generate(prompt, system=TROUBLESHOOT_SYSTEM)
    return {"ok": True, "output": out}


def handle_quote_bom(requirements: str) -> dict:
    if not (requirements or "").strip():
        return {"ok": False, "error": "Describe the customer requirement."}
    prompt = f"Customer requirement:\n{requirements.strip()}\n\nSuggest BOM and rationale as specified."
    out = ollama_generate(prompt, system=QUOTE_BOM_SYSTEM)
    return {"ok": True, "output": out}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "index.html"), "rb") as f:
                self.wfile.write(f.read())
            return
        if self.path == "/api/sample-logs":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(SAMPLE_LOGS.encode("utf-8"))
            return
        if self.path == "/api/sample-telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(SAMPLE_TELEMETRY).encode("utf-8"))
            return
        if self.path == "/api/status":
            status = ollama_status()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(status).encode("utf-8"))
            return
        if self.path == "/api/sample-vpn-intent":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"intent": SAMPLE_VPN_INTENT}).encode("utf-8"))
            return
        if self.path == "/api/sample-compliance":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"description": SAMPLE_COMPLIANCE_INPUT}).encode("utf-8"))
            return
        if self.path == "/api/sample-troubleshoot":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"symptom": SAMPLE_TROUBLESHOOT}).encode("utf-8"))
            return
        if self.path == "/api/sample-quote":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"requirements": SAMPLE_QUOTE}).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        result = None
        if self.path == "/api/policy-translate":
            result = handle_policy_translate(data.get("intent", ""))
        elif self.path == "/api/alert-triage":
            result = handle_alert_triage(data.get("logs", ""))
        elif self.path == "/api/report-narrate":
            result = handle_report_narrate(data.get("telemetry"))
        elif self.path == "/api/vpn-intent":
            result = handle_vpn_intent(data.get("intent", ""))
        elif self.path == "/api/compliance-summary":
            result = handle_compliance_summary(data.get("description", ""))
        elif self.path == "/api/troubleshoot":
            result = handle_troubleshoot(data.get("symptom", ""), data.get("logs_or_config", ""))
        elif self.path == "/api/quote-bom":
            result = handle_quote_bom(data.get("requirements", ""))

        if result is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

    def log_message(self, format, *args):
        print("[%s] %s" % (self.log_date_time_string(), format % args))


def main():
    for attempt in range(5):
        try_port = PORT + attempt
        try:
            server = HTTPServer(("", try_port), Handler)
            print("Fortinet Partner Demo:")
            print("  -->  http://localhost:%s  <--" % try_port)
            print("  Policy Translator | Alert Triage | Report Narrator")
            print("  Requires Ollama (e.g. ollama run phi3:mini)")
            server.serve_forever()
        except OSError as e:
            if e.errno != 48:
                raise
            if attempt == 0:
                print("Port %s in use, trying next..." % try_port)
    print("Could not bind to port %s-%s." % (PORT, PORT + 4))


if __name__ == "__main__":
    main()
