# Router Assistant

CLI assistant for OpenWrt that turns short natural-language phrases into UCI/firewall/network actions. No on-device SLM — keyword/regex intent matching. Works on any router (64 MB+).

## Usage

```sh
router-assist "block 192.168.1.50"
router-assist "show clients"
router-assist "enable guest wifi"
router-assist --dry-run "unblock Kids-Tablet"
router-assist   # interactive: type a phrase, press Enter
```

## Intents (v1)

| Intent        | Example phrases |
|---------------|-----------------|
| Block device  | block &lt;IP&gt;, block device &lt;name&gt; |
| Unblock device| unblock &lt;IP&gt;, allow &lt;name&gt; |
| List clients  | show clients, list devices, who is connected |
| Guest WiFi    | enable/disable guest wifi, turn on/off guest network |
| Restart DNS   | restart dns, restart dnsmasq |
| Show status   | status, router status |
| Help          | help, what can you do |

## Options

- `--dry-run` — print the command that would run, do not execute.
- `--yes` — skip confirmation for block/unblock (use with care).

## Install

Copy `src/` to the device or build the OpenWrt package from `package/`. Requires `uci`, shell, and standard OpenWrt tools.

## Voice integration

Same intents over HTTP so any voice pipeline (browser, phone app, smart speaker) can send text to the router.

- **HTTP API:** `voice-api.cgi` — POST or GET `text=<phrase>`; returns JSON `{ "ok", "intent", "result" }`. No confirmation in API mode (use with care).
- **Test page:** `voice.html` — type a phrase or use the microphone (browser speech recognition) and click Send. Point the page at your router (e.g. `http://192.168.1.1/voice.html` and `http://192.168.1.1/cgi-bin/voice-api.cgi` after installing).

**Setup on OpenWrt:** Install the package, then configure uhttpd to run the CGI and serve the HTML (e.g. copy `voice-api.cgi` to `/www/cgi-bin/` and `voice.html` to `/www/`, and set `ASSIST_DIR=/usr/share/router-assistant` in the CGI env). See `package/` for install paths.

**Voice flow:** Device with microphone → STT (browser, app, or cloud) → POST `text=...` to router CGI → router-assist runs → JSON result.
