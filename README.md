# AI Digest

A self-hosted **multi-agent content pipeline**. Daily, it gathers AI/tech articles,
processes them with a cheap local model (**Gemma** via Ollama), synthesizes and writes
blog posts with a strong model (**Claude** via `claude -p`), translates EN→VI, and
publishes a bilingual static site to **GitHub Pages** — with optional human approval
over **Telegram**.

- 📐 **Architecture:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- 🧩 **Design spec:** [`docs/superpowers/specs/`](docs/superpowers/specs/)
- 🗺️ **Implementation plans:** [`docs/superpowers/plans/`](docs/superpowers/plans/)
- 🚀 **Setup / deploy:** [`docs/SETUP.md`](docs/SETUP.md) and [`deploy/README.md`](deploy/README.md)

## Quick start

```bash
# 1. install deps (uv)
uv sync

# 2. configure
cp .env.example .env        # fill in secrets/paths
$EDITOR digest/config/settings.yaml   # behavior (approval_required, languages, ...)
$EDITOR digest/config/feeds.yaml      # RSS sources

# 3. run the tests
uv run pytest

# 4. one daily run (dry-run first: set steps.publish=false in settings.yaml)
uv run python -m digest.orchestrator
```

See [`docs/SETUP.md`](docs/SETUP.md) for the full checklist (Ollama, Claude CLI,
Tavily, Telegram bot, GitHub Pages, cron, systemd).

## Layout

```
digest/      # the pipeline (Python): core/ + agents/ + orchestrator.py + approver.py
site/        # Hugo static site (i18n EN/VI) — content written by the Publisher
deploy/      # systemd unit + cron instructions
docs/        # architecture, specs, plans, setup
.github/     # GitHub Actions: build + deploy site to Pages
```

## Status

All pipeline milestones implemented and unit-tested (mocked, no live services):
**129 tests green**. Core seam is the Model Router (`cheap`→Gemma / `smart`→Claude).
