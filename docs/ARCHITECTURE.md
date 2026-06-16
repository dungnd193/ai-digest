# AI Digest — Architecture

AI Digest is a self-hosted **multi-agent content pipeline**. Once a day it gathers
AI/tech articles, processes them with a cheap local model (Gemma via Ollama),
synthesizes and writes blog posts with a strong model (Claude via `claude -p`),
translates EN→VI, then publishes a bilingual static site to GitHub Pages — with an
optional human-in-the-loop approval step over Telegram.

![AI Digest architecture](architecture/ai-digest-architecture.png)

> Diagram source: [`architecture/diagram.py`](architecture/diagram.py) ·
> regenerate with `uv run python docs/architecture/diagram.py` ·
> editable GraphViz source: `architecture/ai-digest-architecture.dot`.

## The two reusable seams

Everything hangs off two abstractions, so the rest of the system never hard-codes a
provider:

1. **Model Router** (`digest/core/router.py`) — `router.run(task, tier)` where
   `tier` is `"cheap"` or `"smart"`. Cheap → **Gemma/Ollama** (HTTP); smart →
   **Claude** (`claude -p` subprocess). Swapping or adding a model is a
   construction-time change, invisible to every agent.
2. **Search interface** (`digest/core/search.py`) — `search(query)` wraps Tavily;
   another backend is a drop-in.

## Pipeline stages

| Stage | Module | Tier | Role |
|-------|--------|------|------|
| Collect | `agents/collector.py` | — | Parse RSS feeds (tolerant per feed) |
| Discover | `agents/discovery.py` | cheap | Daily Tavily search + relevance filter |
| Ingest | `agents/ingestor.py` | — | Merge sources, dedupe, drop already-seen |
| Process | `agents/processor.py` | cheap | Per-article summary + category + tags |
| Cluster | `agents/clusterer.py` | cheap | Group articles about the same story |
| Analyze | `agents/analyst.py` | smart | Synthesize + prioritize → `Digest` |
| Write | `agents/writer.py` | smart | One EN blog post per story (+ citations) |
| Translate | `agents/translator.py` | cheap→smart | EN→VI, keep technical terms in English |
| Quality gate | `agents/quality_gate.py` | smart | Flag fabrication (fail-open) |
| Publish | `agents/publisher.py` | — | Render Hugo Markdown, write files, git push |
| Report/Approve | `agents/reporter.py`, `agents/approval.py` | — | Telegram summary + inline-button approval |

`digest/pipeline.py` (`Pipeline`) wires these together; collaborators are injected so
the whole flow is unit-tested with mocks.

## Two entrypoints

- **`digest/orchestrator.py`** — run by **cron** daily. Produces content. In approval
  mode it writes drafts and asks via Telegram; in autopublish mode it commits/pushes.
- **`digest/approver.py`** — a **long-polling systemd service**. Receives Telegram
  button presses (✅ Publish / ✏️ Hold / ❌ Discard) and applies the decision.

`approval_required` in `digest/config/settings.yaml` toggles between the two modes:
`true` while you build trust, `false` once stable (auto-publish).

## Data flow & state

- **Articles** flow as immutable value objects (`core/models.py`,
  `core/digest_types.py`, `core/content_types.py`).
- **Idempotency:** `state/seen.json` (`core/state.py`) records processed article ids
  so reruns never duplicate work.
- **Lifecycle:** `state/posts.json` (`core/post_state.py`) tracks each post:
  `draft → pending_approval → published | held | discarded`.
- Both state files use atomic writes (`os.replace`) so the cron and approver
  processes never read a half-written file.

## Publishing & CI/CD

The Publisher writes **generator-neutral** Markdown (CommonMark + YAML front-matter,
no Hugo shortcodes) into `site/content/posts/` as `<date>-<slug>.<lang>.md`. On push,
`.github/workflows/deploy.yml` builds the Hugo site (homepage grouped by day, EN/VI
i18n, category/tag taxonomy) and deploys to GitHub Pages. Because content is
generator-neutral, the site generator can later be swapped (Astro/Next/…) without
touching the pipeline or the content.

## Resilience

Every model-calling agent **degrades gracefully** on bad output (fallbacks, never
aborts the run). One broken feed, failed search, or rejected post never sinks the
batch. Failures are summarized to Telegram with cause + suggested fix.
