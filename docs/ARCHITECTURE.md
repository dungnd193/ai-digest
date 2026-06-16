# AI Digest — Architecture

AI Digest is a **self-hosted multi-agent content pipeline** for a personal machine
(not a 24/7 server). You run one command each morning; it gathers AI/tech news,
processes it with a cheap model, writes and translates blog posts with a strong
model, runs a quality gate, and publishes a bilingual static site — optionally
gated by a human approval step over Telegram.

![AI Digest architecture](architecture/ai-digest-architecture.png)

> Diagram source: [`architecture/diagram.py`](architecture/diagram.py) ·
> regenerate: `uv run python docs/architecture/diagram.py` ·
> editable GraphViz: `architecture/ai-digest-architecture.dot`.

## Daily operation

Run `./scripts/daily.sh` (idempotent). It:
1. reads `digest/config/settings.yaml` fresh, syncs deps,
2. kills any stale `ollama` / `approver` / `orchestrator`,
3. starts Ollama **only if `model_mode` needs it** (saves power/heat otherwise),
4. starts the Telegram approver **only if `approval_required: true`**,
5. runs the pipeline once, logging to `digest/state/runs/<timestamp>.log`.

Then review/approve in Telegram (if approval is on) and shut down — nothing needs
to stay running. (A `cron` line can automate the run; see `docs/SETUP.md`.)

## Two reusable seams

Agents never name a provider — they ask for a **tier** (`cheap` / `smart`):

- **Model Router** (`digest/core/router.py`) maps tiers to backends per **`model_mode`**:
  - `claude_only` — both tiers → Claude (`claude -p`); fast, no local GPU heat (default)
  - `both` — cheap → Gemma (Ollama, local), smart → Claude
  - `ollama_only` — both tiers → Gemma; fully local
- **Search interface** (`digest/core/search.py`) wraps the web-search provider (Tavily).

## Per-story pipeline

`digest/pipeline.py` (`Pipeline`) wires the stages; collaborators are injected, so the
whole flow is unit-tested with mocks. Ingestion/processing run in batch; then **each
story is processed end-to-end and timed per sub-step**:

| Stage | Tier | Role |
|-------|------|------|
| Collect (`collector.py`) | — | Parse RSS feeds (tolerant per feed) |
| Discover (`discovery.py`) | cheap | Daily Tavily search + relevance filter |
| Ingest (`ingestor.py`) | — | Merge sources, dedupe, drop already-seen |
| Process (`processor.py`) | cheap | Per-article summary + category + tags |
| Cluster (`clusterer.py`) | cheap | Group articles about the same story |
| Analyze (`analyst.py`) | smart | Synthesize + prioritize into a `Digest` |
| Write (`writer.py`) | smart | One post per story, with citations; no fabrication |
| Translate (`translator.py`) | cheap→smart | EN→VI, keeping technical terms in English |
| Quality gate (`quality_gate.py`) | smart | Block fabricated / ungrounded posts |
| Publish (`publisher.py`) | — | Render Markdown, commit, push |

Two entrypoints: **`orchestrator.py`** (the run) and **`approver.py`** (a long-polling
Telegram service, used only in approval mode).

## Publish modes

`approval_required` (in `settings.yaml`):
- **`false` (default)** — auto-publish: Publisher commits & pushes directly.
- **`true`** — each post is sent to Telegram with ✅ Publish / ✏️ Hold / ❌ Discard
  buttons; the `approver` applies your decision (publish flips the draft and pushes).

## Deduplication

Two layers, so re-running (same day or later) never produces duplicates:
- **By URL** — `state/seen.json` (`core/state.py`): the Ingestor drops any article whose
  id (SHA1 of URL) was processed before; every ingested id is saved at the end of a run.
- **By story** — `state/posts.json` (`core/post_state.py`): a `date:slug` already
  `published`/`discarded` is skipped. (`digest/state/` is git-ignored and never deleted.)

Same-day duplicates from different sources are merged earlier by the Clusterer.

## Ordering & content portability

Posts carry a full timezone-aware datetime, so the site sorts newest-run-first and,
within a run, by importance. The Writer emits **generator-neutral Markdown** (plain
CommonMark + front-matter, no Hugo shortcodes), so the site generator stays swappable.

## Observability

- **Per-run log** `state/runs/<ts>.log` with timestamps. Each model call logs the
  **agent + item + duration + output preview**, e.g.
  `writer:Multi-Agent Systems  tier=smart  4.52s out=157 | Multi-agent systems…`
- **Telegram daily report** (`reporter.py`): date, mode, total time, counts, the post
  list, **per-post timing breakdown** (write · gate · vi), stage totals, and any issues.

## Publishing & CI/CD

Publisher writes `<date>-<slug>.<lang>.md` into `site/content/posts/`. On push, GitHub
Actions builds the Hugo site (homepage grouped by day, EN/VI i18n, category/tag
taxonomy, fingerprinted CSS) and deploys to GitHub Pages.

## Resilience

Every model-calling agent degrades gracefully on bad output (fallbacks, never aborts):
one broken feed, failed search, empty translation draft, or rejected post never sinks
the run. The Quality Gate is the last line of defense against fabricated claims.

## Tech stack

Python 3 + `uv`; `feedparser`, `requests`, `PyYAML`, `python-dotenv`; Claude via the
`claude` CLI; Gemma via Ollama HTTP; Tavily search; Telegram Bot API; Hugo + GitHub
Pages. 150 unit tests (mocked, no live services).
