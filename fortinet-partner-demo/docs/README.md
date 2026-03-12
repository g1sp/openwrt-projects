# Host the Fortinet Partner Demo on GitHub Pages

This folder contains a **static mockup** of the Fortinet Partner Demo: same UI and sample outputs, no backend. You can host it on GitHub Pages so your friend can open it in a browser.

## Option A — New repo (recommended for sharing one link)

1. **Create a new repository** on GitHub (e.g. `fortinet-partner-demo`).
   - Go to [github.com/new](https://github.com/new).
   - Name it e.g. `fortinet-partner-demo`, public, no README.

2. **Put only `index.html` in the repo root:**
   ```bash
   mkdir fortinet-partner-demo-pages && cd fortinet-partner-demo-pages
   # Copy the single file (from this docs folder)
   cp /path/to/OpenWrt/fortinet-partner-demo/docs/index.html .
   git init
   git add index.html
   git commit -m "Fortinet Partner Demo mockup for GitHub Pages"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/fortinet-partner-demo.git
   git push -u origin main
   ```

3. **Turn on GitHub Pages:**
   - Repo → **Settings** → **Pages**.
   - Under **Source**, choose **Deploy from a branch**.
   - Branch: **main**, folder: **/ (root)**.
   - Save.

4. **Open the site** (after a minute or two):
   - `https://YOUR_USERNAME.github.io/fortinet-partner-demo/`

Share that URL with your friend.

---

## Option B — Use an existing repo (e.g. OpenWrt) and the `docs/` folder

If this `docs/` folder is already inside a repo (e.g. `OpenWrt`):

1. **Commit and push** the `docs/` folder (including this `index.html`).
2. In the repo go to **Settings** → **Pages**.
3. Under **Source** choose **Deploy from a branch**.
4. Branch: **main** (or your default), folder: **/docs**.
5. Save. The site will be at:
   - `https://YOUR_USERNAME.github.io/REPO_NAME/`
   - The main page is `index.html` from `docs/`.

---

## What your friend sees

- The same eight tabs: Policy, Alert Triage, Report, Quote/BOM, Customer Products, VPN Wizard, Compliance, Troubleshoot.
- Banner: **Demo mockup** — “Live version runs with Ollama on your machine.”
- **Load sample** fills the text areas; **Generate** / **Triage** etc. show **pre-written sample outputs** (no real AI; simulates a short delay).
- Footer note: for live AI, run the Python server locally with Ollama.

No server or Ollama is needed for the GitHub Pages mockup.
