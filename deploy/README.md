# Deploy

## Approver service (user systemd)
    mkdir -p ~/.config/systemd/user
    cp deploy/ai-digest-approver.service ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable --now ai-digest-approver
    journalctl --user -u ai-digest-approver -f   # logs

## Daily orchestrator (cron)
    crontab -e
    # 7am daily:
    0 7 * * * cd ~/Desktop/Workspace/ai-digest && ~/.local/bin/uv run python -m digest.orchestrator >> digest/state/cron.log 2>&1
