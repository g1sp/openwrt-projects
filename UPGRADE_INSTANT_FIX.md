# Add instant-fix to g1sp/openwrt-projects

Your local `origin` is set to `https://github.com/g1sp/openwrt-projects.git`. Run these in order:

```bash
cd /Users/jeevan/OpenWrt

# 1. See what will be added (instant-fix + README updates)
git status

# 2. Stage everything (instant-fix folder + any changed files)
git add -A

# 3. Commit
git commit -m "Add instant-fix (Why is Zoom freezing?) and update README for four projects"

# 4. If the repo already has commits you don’t have locally, pull first
git pull origin main --rebase

# 5. Push to GitHub
git push -u origin main
```

If step 4 says "branch 'main' doesn't exist" on remote, try `git push -u origin main` anyway (you might be creating `main`). If you get "failed to push some refs", run `git pull origin main --rebase` again, fix any conflicts, then `git push origin main`.
