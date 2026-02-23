#!/usr/bin/env python3
# Run with:  python3 server.py   (do not use  sh server.py)
"""
Instant Fix — "Why is Zoom freezing?"
Uses mock network telemetry + local Ollama to explain and suggest a fix.
Never suggests rebooting the router; suggests 5 GHz or resetting network settings when appropriate.
"""

import json
import os
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi3:mini")
PORT = int(os.environ.get("INSTANT_FIX_PORT", "8766"))

# Mock telemetry for demo (e.g. Zoom is choppy because laptop is on 2.4 GHz and tablet is heavy on bandwidth)
MOCK_TELEMETRY = {
    "devices": [
        {"hostname": "MacBook-Pro", "ip": "192.168.1.101", "bandwidth_mbps": 2, "band": "2.4GHz", "role": "user device (likely Zoom)"},
        {"hostname": "Kids-Tablet", "ip": "192.168.1.102", "bandwidth_mbps": 45, "band": "5GHz", "role": "heavy usage"},
        {"hostname": "Living-Room-TV", "ip": "192.168.1.103", "bandwidth_mbps": 30, "band": "5GHz", "role": "streaming"},
    ],
    "summary": "MacBook-Pro is on 2.4GHz with low throughput; Kids-Tablet and Living-Room-TV are using most of the bandwidth on 5GHz.",
    "latency_ms": 120,
    "packet_loss_pct": 2,
}


INSTANT_FIX_SYSTEM = """You are a home network troubleshooting assistant. The user is asking why their video call (e.g. Zoom) is freezing or why the internet is slow.

Rules for suggested fixes:
- You MAY suggest: switching the user's device to 5 GHz WiFi, resetting the router's network settings (not power cycle), reducing usage on other devices, moving closer to the router, or checking for interference.
- You must NOT suggest: rebooting the router, power cycling the router, or unplugging the router. If a full reset is needed, say "reset the router's network settings" (from the router admin page), not "reboot the router".

Give (1) a short explanation in 1-2 sentences using the telemetry context, then (2) one or two concrete suggested actions. Be specific (e.g. "Try connecting your laptop to the 5 GHz network" or "Reset the network settings from the router's admin page")."""


def telemetry_blob():
    """Current network state as text for the model."""
    t = MOCK_TELEMETRY
    lines = [
        "Connected devices and current usage:",
        *[f"  - {d['hostname']} ({d['ip']}): {d['bandwidth_mbps']} Mbps, {d['band']}, {d['role']}" for d in t["devices"]],
        f"Summary: {t['summary']}",
        f"Latency: {t['latency_ms']} ms, packet loss: {t['packet_loss_pct']}%",
    ]
    return "\n".join(lines)


def ollama_generate(prompt: str, system: str = "") -> str:
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
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode("utf-8"))
            return (data.get("response") or "").strip()
    except urllib.error.URLError as e:
        return f"[Ollama error: {e}]"
    except Exception as e:
        return f"[Error: {e}]"


def handle_ask(query: str) -> dict:
    q = (query or "").strip()
    if not q:
        return {"ok": False, "error": "Empty query."}

    ctx = telemetry_blob()
    prompt = (
        f"Network telemetry:\n{ctx}\n\n"
        f"User asked: \"{query}\"\n\n"
        "Give (1) a brief explanation of what is likely causing the issue, then (2) one or two suggested actions. "
        "Do not suggest rebooting the router; you may suggest resetting network settings or switching to 5 GHz."
    )
    answer = ollama_generate(prompt, system=INSTANT_FIX_SYSTEM)
    return {
        "ok": True,
        "answer": answer or "Could not generate a response.",
        "telemetry_summary": MOCK_TELEMETRY["summary"],
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
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
            print("Instant Fix (Why is Zoom freezing?):")
            print("  -->  http://localhost:%s  <--" % try_port)
            print("  Ollama: %s" % OLLAMA_HOST)
            server.serve_forever()
        except OSError as e:
            if e.errno != 48:
                raise
            if attempt == 0:
                print("Port %s in use, trying next..." % try_port)
    print("Could not bind to port %s-%s." % (PORT, PORT + 4))


if __name__ == "__main__":
    main()
