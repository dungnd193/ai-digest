---
title: Architecture
summary: How AI Digest works end-to-end — a self-hosted multi-agent content pipeline.
---

AI Digest is a self-hosted **multi-agent pipeline** for a personal machine. You run one
command each morning; it gathers AI/tech news, processes it with a cheap model, writes
and translates blog posts with a strong model, runs a quality gate, and publishes this
bilingual site — optionally gated by a human approval step over Telegram.

![AI Digest architecture](architecture.png)

## Daily operation

`./scripts/daily.sh` is idempotent: it kills stale services, starts Ollama only if the
mode needs it (saving power/heat), runs the pipeline once, and logs each step's timing
to `digest/state/runs/`. Then you review in Telegram (if approval is on) and shut down.

## The reusable core: a Model Router

Every agent asks for a *tier* — `cheap` or `smart` — never a specific provider. The
**Model Router** maps tiers to backends via `model_mode`:

- **claude_only** — both tiers → Claude (fast, no local GPU heat) — *default*
- **both** — cheap → Gemma (Ollama, local), smart → Claude
- **ollama_only** — both tiers → Gemma (fully local)

A second seam, the **Search interface**, wraps the web-search provider (Tavily).

## Per-story pipeline

| Stage | Tier | Role |
|-------|------|------|
| Collect | — | Parse RSS feeds (tolerant per feed) |
| Discover | cheap | Daily web search + relevance filter |
| Ingest | — | Merge sources, dedupe, drop already-seen |
| Process | cheap | Per-article summary + category + tags |
| Cluster | cheap | Group articles about the same story |
| Analyze | smart | Synthesize + prioritize into a digest |
| Write | smart | One post per story, with citations (no fabrication) |
| Translate | cheap→smart | EN→VI, keeping technical terms in English |
| Quality gate | smart | Block fabricated / ungrounded posts |
| Publish | — | Render Markdown, commit, push |

Each story is processed end-to-end and **timed per sub-step** (write · gate · vi),
reported daily over Telegram.

## Publish modes & dedup

`approval_required: false` (default) auto-publishes; `true` sends each post to Telegram
with ✅/✏️/❌ buttons. Re-runs never duplicate: articles are deduped by URL
(`seen.json`) and stories by `date:slug` (`posts.json`); same-day duplicates are merged
by the Clusterer.

## Publishing & CI/CD

The Publisher writes **generator-neutral** Markdown (CommonMark + front-matter, no Hugo
shortcodes) so the generator stays swappable. On push, GitHub Actions builds the Hugo
site (homepage by day, EN/VI i18n, taxonomy) and deploys to GitHub Pages.

## Resilience

Every model-calling agent degrades gracefully on bad output — one broken feed, failed
search, or rejected post never sinks the run. The Quality Gate is the last line of
defense against fabricated claims.
