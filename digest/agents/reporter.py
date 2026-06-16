from __future__ import annotations

from dataclasses import dataclass, field

from digest.core.telegram import TelegramClient


@dataclass
class RunReport:
    articles_in: int = 0
    posts_written: int = 0
    published: int = 0
    errors: list[str] = field(default_factory=list)
    site_url: str = ""


class Reporter:
    """Sends a daily summary and error alerts (cause + fix) to Telegram."""

    def __init__(self, telegram: TelegramClient) -> None:
        self.telegram = telegram

    def daily_summary(self, report: RunReport) -> int:
        lines = [
            "<b>AI Digest — daily run</b>",
            f"Articles ingested: {report.articles_in}",
            f"Posts written: {report.posts_written}",
            f"Published: {report.published}",
        ]
        if report.errors:
            lines.append(f"Errors ({len(report.errors)}):")
            lines.extend(f"• {e}" for e in report.errors)
        if report.site_url:
            lines.append(f"Site: {report.site_url}")
        return self.telegram.send_message("\n".join(lines))

    def error_alert(self, *, stage: str, cause: str, fix: str) -> int:
        text = (
            f"❌ <b>{stage} failed</b>\n"
            f"Cause: {cause}\n"
            f"Fix: {fix}"
        )
        return self.telegram.send_message(text)
