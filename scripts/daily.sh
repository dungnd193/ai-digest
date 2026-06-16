#!/usr/bin/env bash
# AI Digest — one-shot daily runner for a personal machine (not a 24/7 server).
# Boot your PC, run this once. It is idempotent: it kills any stale services and
# starts fresh. Ollama is started only if the configured model_mode needs it
# (saves power/heat otherwise). The Telegram approver is left running in the
# background so you can approve posts through the day; just shut down when done.
#
#   ./scripts/daily.sh
#
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$ROOT"
LOG_DIR="digest/state"
mkdir -p "$LOG_DIR"

say(){ printf '\n\033[1;38;5;208m▶ %s\033[0m\n' "$*"; }
ok(){  printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn(){ printf '  \033[33m!\033[0m %s\n' "$*"; }

# --- read config ---
MODE="$(grep -E '^model_mode:' digest/config/settings.yaml 2>/dev/null | sed 's/#.*//' | cut -d: -f2- | tr -d ' "'\''' )"
MODE="${MODE:-both}"
MODEL="$(grep -E '^OLLAMA_MODEL=' .env 2>/dev/null | cut -d= -f2-)"
MODEL="${MODEL:-gemma4:12b}"
SITE="${SITE_URL:-https://dungnd193.github.io/ai-digest/}"
say "model_mode = $MODE"

# --- 0. deps ---
say "Syncing dependencies (uv)"
uv sync --quiet && ok "deps ready" || { warn "uv sync failed"; exit 1; }

# --- 1. kill stale app processes (idempotent) ---
say "Stopping stale app processes"
pkill -f "digest.approver"     2>/dev/null && ok "killed old approver"     || warn "no approver was running"
pkill -f "digest.orchestrator" 2>/dev/null && ok "killed old orchestrator" || true

# --- 2. Ollama only if the mode needs it ---
if [ "$MODE" = "both" ] || [ "$MODE" = "ollama_only" ]; then
  say "Restarting Ollama (needed for mode=$MODE, model=$MODEL)"
  pkill -f "ollama serve" 2>/dev/null && ok "killed old ollama" || warn "no ollama was running"
  sleep 1
  nohup ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
  for _ in $(seq 1 30); do curl -sf http://localhost:11434/api/tags >/dev/null 2>&1 && break; sleep 1; done
  if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then ok "ollama up"; else warn "ollama did not become ready"; fi
  ollama pull "$MODEL" >/dev/null 2>&1 && ok "model $MODEL ready" || warn "could not pull $MODEL"
else
  say "Ollama not needed (mode=$MODE) — stopping it to save power/heat"
  pkill -f "ollama serve" 2>/dev/null && ok "stopped ollama" || warn "ollama was not running"
fi

# --- 3. start the Telegram approver only if approval is required ---
APPROVAL="$(grep -E '^approval_required:' digest/config/settings.yaml 2>/dev/null | sed 's/#.*//' | cut -d: -f2- | tr -d ' "'\''' )"
if [ "$APPROVAL" = "true" ]; then
  say "Starting Telegram approver (background)"
  setsid bash -c "cd '$ROOT' && PATH=\"\$HOME/.local/bin:\$PATH\" PYTHONPATH='$ROOT' exec uv run python -m digest.approver" \
    > "$LOG_DIR/approver.log" 2>&1 < /dev/null &
  sleep 3
  pgrep -f "digest.approver" >/dev/null && ok "approver running (approve posts in Telegram)" || warn "approver failed to start — see $LOG_DIR/approver.log"
else
  say "Auto-publish mode (approval_required=false) — approver not needed"
fi

# --- 4. run the pipeline once ---
say "Running daily digest (orchestrator)"
uv run python -m digest.orchestrator > "$LOG_DIR/lastrun.log" 2>&1
code=$?
if [ $code -eq 0 ]; then ok "orchestrator finished"; else warn "orchestrator exited with code $code (see $LOG_DIR/lastrun.log)"; fi

say "Done"
echo "  • Review/approve today's posts in Telegram (the approver stays running)."
echo "  • Site: $SITE"
echo "  • Logs: $LOG_DIR/lastrun.log, $LOG_DIR/approver.log"
echo "  • Shut down the PC whenever you're finished — no service needs to stay up."
