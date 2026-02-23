#!/usr/bin/env python3
# Run with:  python3 server.py   (do not use  sh server.py)
"""
Home Network Copilot — demo server.
Serves a single-page UI and /api/ask; calls local Ollama for intent and explanations.
Uses mock router data so the demo runs without a real router.
"""

import json
import os
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi3:mini")
PORT = int(os.environ.get("COPILOT_PORT", "8765"))

# Mock router data — the "simulated router" the model sees. Change these to demo different scenarios.
MOCK_DEVICES = [
    {"ip": "192.168.1.101", "hostname": "MacBook-Pro", "mac": "aa:bb:cc:dd:ee:01"},
    {"ip": "192.168.1.102", "hostname": "Kids-Tablet", "mac": "aa:bb:cc:dd:ee:02"},
    {"ip": "192.168.1.103", "hostname": "Living-Room-TV", "mac": "aa:bb:cc:dd:ee:03"},
]
MOCK_LAST_EVENT = {
    "type": "DNS_BLOCK",
    "ts": 1739123456,
    "src": "192.168.1.102",
    "domain": "ads.example.com",
    "reason": "blocked by ad-block",
}

# System prompt: you ARE the router copilot. Never give generic chatbot replies.
ROUTER_SYSTEM = """You are the Home Network Copilot: an assistant that runs on a home router. You have access to:
- The list of devices currently connected to the LAN (hostnames and IPs).
- The last security/firewall event (e.g. a blocked DNS query or dropped connection).

You ONLY help with: listing connected devices, explaining why something was blocked, and blocking or unblocking a device by name or IP. Answer in 1-3 short sentences. Be specific: use actual device names and IPs from the context you are given. Do not offer general life advice, coding help, or unrelated chat. If the user asks something outside router/network scope, say you can only help with network and device management."""


def router_context_blob():
    """Current router state as text, so the model always sees the 'simulated router'."""
    devices = "\n".join(f"  - {d['hostname']} ({d['ip']})" for d in MOCK_DEVICES)
    ev = MOCK_LAST_EVENT
    return (
        f"Current connected devices:\n{devices}\n"
        f"Last security event: {ev['type']} — {ev['domain']} from device {ev['src']} ({ev['reason']})."
    )


def ollama_generate(prompt: str, system: str = "") -> str:
    """Call Ollama /api/generate; return response text."""
    url = f"{OLLAMA_HOST}/api/generate"
    body = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        body["system"] = system
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
            return (data.get("response") or "").strip()
    except urllib.error.URLError as e:
        return f"[Ollama error: {e}]"
    except Exception as e:
        return f"[Error: {e}]"


def handle_ask(query: str) -> dict:
    """Process natural-language query: call SLM and/or mock logic; return JSON for UI."""
    q = (query or "").strip().lower()
    if not q:
        return {"ok": False, "error": "Empty query."}

    ctx = router_context_blob()

    # 1) "What can you do?" — router-scoped capabilities only
    if "what can you do" in q or q == "help" or q == "capabilities":
        prompt = (
            f"Router state:\n{ctx}\n\nUser asked: What can you do? "
            "Reply in 2 short sentences: only list router capabilities (show devices, explain blocks, block/unblock by name). No generic chat."
        )
        answer = ollama_generate(prompt, system=ROUTER_SYSTEM)
        return {"ok": True, "intent": "help", "answer": answer, "data": None}

    # 2) "Who's connected?" / "List devices" — must match before "block" (so "block" isn't confused with explain)
    list_trigger = (
        "who" in q and "connect" in q
        or "list" in q and ("device" in q or "devices" in q)
        or "show" in q and ("device" in q or "devices" in q or "client" in q)
        or "clients" in q
    )
    if list_trigger:
        prompt = (
            f"Router state:\n{ctx}\n\nUser asked: Who's connected? / List devices. "
            "Reply in 1-2 sentences naming the devices (MacBook-Pro, Kids-Tablet, Living-Room-TV) and that they are on the LAN. Be specific."
        )
        summary = ollama_generate(prompt, system=ROUTER_SYSTEM)
        devices_text = "\n".join(f"- {d['hostname']} ({d['ip']})" for d in MOCK_DEVICES)
        return {
            "ok": True,
            "intent": "list_devices",
            "answer": summary or devices_text,
            "data": {"devices": MOCK_DEVICES},
        }

    # 3) "Block X" — check BEFORE explain, so "Block Kids-Tablet" doesn't hit explain (which also has "block")
    if "unblock" not in q and "allow" not in q and "explain" not in q and "why" not in q and "what happened" not in q and "block" in q:
        prompt = (
            f"Router state:\n{ctx}\n\nUser said: \"{query}\". "
            "Which device should be blocked? Reply with ONLY the device name or IP from the list (e.g. Kids-Tablet or 192.168.1.102). One word or phrase, nothing else."
        )
        target = ollama_generate(prompt, system=ROUTER_SYSTEM).strip().strip('"')
        if not target:
            target = "unknown"
        return {
            "ok": True,
            "intent": "block",
            "answer": f"Blocked device: {target} (demo—no real router).",
            "data": {"target": target},
        }

    # 4) "Unblock X"
    if "unblock" in q or "allow" in q:
        prompt = (
            f"Router state:\n{ctx}\n\nUser said: \"{query}\". "
            "Which device should be unblocked? Reply with ONLY the device name or IP. One word or phrase, nothing else."
        )
        target = ollama_generate(prompt, system=ROUTER_SYSTEM).strip().strip('"')
        if not target:
            target = "unknown"
        return {
            "ok": True,
            "intent": "unblock",
            "answer": f"Unblocked device: {target} (demo—no real router).",
            "data": {"target": target},
        }

    # 5) "Why did you block?" / "Explain the last block" — after block/unblock so we don't steal "Block Kids-Tablet"
    if any(x in q for x in ("why", "explain", "what happened")):
        ev = MOCK_LAST_EVENT
        prompt = (
            f"Router state:\n{ctx}\n\nUser asked: Why did you block that? / Explain. "
            "The last event was a DNS block for ads.example.com from Kids-Tablet (192.168.1.102). "
            "Reply in 2 sentences: (1) What happened: the router blocked an ad/tracking request from Kids-Tablet. (2) Suggested action: none needed, or allow the site in ad-block if it was a false positive."
        )
        answer = ollama_generate(prompt, system=ROUTER_SYSTEM)
        return {
            "ok": True,
            "intent": "explain_event",
            "answer": answer or f"Event: {ev['type']} for {ev['domain']} from {ev['src']}.",
            "data": {"event": ev},
        }

    # 6) Fallback: do NOT call the model for off-topic queries — return fixed router-only message
    # This prevents generic chatbot replies. Only router-related phrases get SLM answers.
    ROUTER_COMMANDS = (
        "I'm the Home Network Copilot. I only respond to router/network questions. "
        "Try one of these:\n\n"
        "• \"Who's connected?\" or \"List devices\" — see connected devices\n"
        "• \"Why did you block that?\" or \"Explain the last block\" — explain the last security event\n"
        "• \"Block Kids-Tablet\" or \"Block 192.168.1.102\" — block a device (demo)\n"
        "• \"Unblock Kids-Tablet\" — unblock a device (demo)\n"
        "• \"What can you do?\" or \"Help\" — list capabilities"
    )
    return {"ok": True, "intent": "router_only", "answer": ROUTER_COMMANDS, "data": None}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "index.html"), "rb") as f:
                self.wfile.write(f.read())
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/api/ask":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(body)
            query = data.get("query", "")
        except Exception:
            query = ""
        result = handle_ask(query)
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
            print("Home Network Copilot demo:")
            print("  -->  http://localhost:%s  <--  (open this in your browser)" % try_port)
            print("  (Port 11434 is Ollama only; this app is on %s)" % try_port)
            print("  Ensure Ollama is running (e.g. ollama run phi3:mini)")
            server.serve_forever()
        except OSError as e:
            if e.errno != 48:  # 48 = address already in use
                raise
            if attempt == 0:
                print("Port %s in use, trying next..." % try_port)
    print("Could not bind to port %s-%s. Stop the process using the port or set COPILOT_PORT." % (PORT, PORT + 4))


if __name__ == "__main__":
    main()
