# Push these projects to your GitHub account

Run these commands in your terminal (from this folder). You'll need `git` and, to create the repo from the CLI, `gh` (GitHub CLI) logged in, or you can create the repo in the browser.

All four projects live in **the same folder/repo**: `network-sentinel`, `router-assistant`, `home-copilot-demo`, `instant-fix`.

---

## Option A: One repo containing all four projects (recommended)

```bash
cd /Users/jeevan/OpenWrt

# If you had a failed git init earlier, remove it first:
rm -rf .git

# Initialize repo and first commit
git init
git add -A
git commit -m "Add network-sentinel, router-assistant, home-copilot-demo, instant-fix"

# Create the repo on GitHub and push (requires: gh auth login)
gh repo create openwrt-projects --public --source=. --remote=origin --push
```

If you don't use `gh`, create a new repo on GitHub (e.g. `openwrt-projects`), then:

```bash
git remote add origin https://github.com/YOUR_USERNAME/openwrt-projects.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Already have the repo? Add new files and push

If you already created `openwrt-projects` and only want to add the copilot project or instant-fix and push:

```bash
cd /Users/jeevan/OpenWrt
git add -A
git status   # check: network-sentinel, router-assistant, home-copilot-demo, instant-fix
git commit -m "Add home-copilot-demo and instant-fix"
git push
```

---

## Option B: Four separate repos

From `/Users/jeevan/OpenWrt`:

```bash
# network-sentinel
cd network-sentinel && git init && git add -A && git commit -m "Initial commit"
gh repo create network-sentinel --public --source=. --remote=origin --push
cd ..

# router-assistant
cd router-assistant && git init && git add -A && git commit -m "Initial commit"
gh repo create router-assistant --public --source=. --remote=origin --push
cd ..

# home-copilot-demo
cd home-copilot-demo && git init && git add -A && git commit -m "Initial commit"
gh repo create home-copilot-demo --public --source=. --remote=origin --push
cd ..

# instant-fix
cd instant-fix && git init && git add -A && git commit -m "Initial commit"
gh repo create instant-fix --public --source=. --remote=origin --push
cd ..
```

If any repo name is already taken on your account, pick another (e.g. `openwrt-network-sentinel`).

---

**Check GitHub CLI login:** `gh auth status`

**Login if needed:** `gh auth login`
