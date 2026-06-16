# AI Digest — Setup Checklist

The code is complete and unit-tested with mocks. To run it for real you must provide a
few secrets/services. Work top to bottom; each box is a thing only **you** can do.

## 0. Python deps
```bash
cd ~/Desktop/Workspace/ai-digest
uv sync            # installs runtime + dev deps from uv.lock
uv run pytest      # should report all tests passing
```

## 1. Local models — Ollama + Gemma (cheap tier)
- [ ] Ollama running: `ollama serve` (default `http://localhost:11434`).
- [ ] Pull the model: `ollama pull gemma3:4b` (or your variant).
- [ ] Quick check: `curl http://localhost:11434/api/tags` lists the model.

## 2. Claude CLI (smart tier)
- [ ] `claude` is installed and logged in (Max subscription, no API key):
      run `claude -p "say hi in 3 words"` once and confirm it answers.
- [ ] If the binary isn't on PATH, set `CLAUDE_BIN` in `.env` to its full path.
- [ ] Note the flag: the backend calls `claude -p <prompt> --append-system-prompt <sys>`.
      If your `claude` version differs, adjust `digest/core/backends.py:ClaudeBackend`.

## 3. Tavily (web search / discovery)
- [ ] Create a free API key at https://tavily.com (free tier ~1000/mo).
- [ ] Put it in `.env` as `TAVILY_API_KEY=...`.
- [ ] To disable discovery entirely: set `discovery.enabled: false` in
      `digest/config/settings.yaml`.

## 4. Telegram bot (reports + approval)
- [ ] In Telegram, message **@BotFather** → `/newbot` → copy the **bot token**.
- [ ] Get your **chat id**: message your new bot, then open
      `https://api.telegram.org/bot<TOKEN>/getUpdates` and read `result[].message.chat.id`.
- [ ] Put both in `.env`: `TELEGRAM_BOT_TOKEN=...`, `TELEGRAM_CHAT_ID=...`.

## 5. The `.env` file
```bash
cp .env.example .env
```
Fill in:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
CLAUDE_BIN=claude
TAVILY_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
SITE_URL=https://<your-username>.github.io/ai-digest/   # optional, shown in reports
```
(`.env` is git-ignored — never commit it.)

## 6. Behavior config — `digest/config/settings.yaml`
- [ ] `approval_required: true` for the first weeks (review each post via Telegram),
      flip to `false` once you trust it (auto-publish).
- [ ] `languages: [en, vi]`, `translator_mode: draft_then_review` (default).
- [ ] `discovery.keywords:` your topics.
- [ ] **Dry run first:** set `steps.publish: false`, run once, inspect
      `site/content/posts/` locally before enabling real publishing.
- [ ] Tune RSS sources in `digest/config/feeds.yaml`.

## 7. GitHub Pages (hosting)
- [ ] Create a GitHub repo and add it as a remote:
      `git remote add origin git@github.com:<you>/ai-digest.git`
- [ ] Push the branch / merge to `main`.
- [ ] Repo **Settings → Pages → Build and deployment → Source: GitHub Actions**.
- [ ] Set the real `baseURL` in `site/hugo.toml` (or rely on the workflow's
      `--baseURL "${{ steps.pages.outputs.base_url }}/"`, which already overrides it).
- [ ] First push touching `site/**` triggers `.github/workflows/deploy.yml` → live site.

## 8. Schedule it
**Daily run (cron):**
```bash
crontab -e
# 7am daily:
0 7 * * * cd ~/Desktop/Workspace/ai-digest && ~/.local/bin/uv run python -m digest.orchestrator >> digest/state/cron.log 2>&1
```

**Approver service (user systemd)** — needed only while `approval_required: true`:
```bash
mkdir -p ~/.config/systemd/user
cp deploy/ai-digest-approver.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now ai-digest-approver
journalctl --user -u ai-digest-approver -f
```

## 9. First live smoke test
```bash
# with steps.publish=false and approval_required=true:
uv run python -m digest.orchestrator
```
Expect: a Telegram summary message, draft `.md` files under `site/content/posts/`, and
(if approval is on) per-post messages with ✅/✏️/❌ buttons. Press ✅ and confirm the
approver commits + the Pages workflow deploys.

---

### What's NOT done (by design — needs your accounts/secrets)
- Real Tavily key, Telegram bot token+chat id, GitHub remote + Pages enablement.
- A live end-to-end run (requires Ollama up + Claude logged in + the secrets above).
- These are exactly the steps in this checklist; the code paths for all of them are
  implemented and unit-tested with mocks.
