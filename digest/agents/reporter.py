from __future__ import annotations

from dataclasses import dataclass, field

from digest.core.telegram import TelegramClient


@dataclass
class RunReport:
    date: str = ""                                  # human-readable date of the run
    articles_in: int = 0
    posts_written: int = 0
    published: int = 0
    errors: list[str] = field(default_factory=list)
    site_url: str = ""
    mode: str = ""                                  # model_mode used
    approval: bool = True                           # approval_required
    duration_s: float = 0.0
    timings: dict = field(default_factory=dict)     # stage -> seconds
    published_titles: list[str] = field(default_factory=list)


def _fmt_secs(s: float) -> str:
    s = int(round(s))
    return f"{s // 60}m{s % 60:02d}s" if s >= 60 else f"{s}s"


class Reporter:
    """Sends a richly formatted daily summary and error alerts to Telegram."""

    def __init__(self, telegram: TelegramClient) -> None:
        self.telegram = telegram

    def daily_summary(self, report: RunReport) -> int:
        mode_label = {"claude_only": "Claude", "ollama_only": "Gemma",
                      "both": "Gemma+Claude"}.get(report.mode, report.mode or "?")
        flow = "✋ needs approval" if report.approval else "🤖 auto-publish"
        verb = "Sent for approval" if report.approval else "Published"
        count = report.posts_written if report.approval else report.published

        lines = ["🗞️ <b>AI Digest — Daily Run</b>"]
        if report.date:
            lines.append(f"📅 {report.date}")
        lines.append(f"⚙️ {mode_label} · {flow} · ⏱️ {_fmt_secs(report.duration_s)}")
        lines += [
            "",
            f"📥 Ingested: <b>{report.articles_in}</b>",
            f"📝 Written: <b>{report.posts_written}</b>",
            f"🚀 {verb}: <b>{count}</b>",
        ]
        if report.published_titles:
            lines.append("")
            lines.append("<b>Posts:</b>")
            lines += [f"  • {t}" for t in report.published_titles]
        if report.timings:
            lines.append("")
            lines.append("<b>⏱️ Stage timings:</b>")
            lines += [f"  • {stage}: {_fmt_secs(secs)}" for stage, secs in report.timings.items()]
        if report.errors:
            lines.append("")
            lines.append(f"⚠️ <b>Notes ({len(report.errors)}):</b>")
            lines += [f"  • {e}" for e in report.errors]
        if report.site_url:
            lines += ["", f"🔗 {report.site_url}"]
        return self.telegram.send_message("\n".join(lines))

    def error_alert(self, *, stage: str, cause: str, fix: str) -> int:
        text = (
            f"❌ <b>{stage} failed</b>\n\n"
            f"🔍 <b>Cause:</b> {cause}\n"
            f"🛠️ <b>Fix:</b> {fix}"
        )
        return self.telegram.send_message(text)
