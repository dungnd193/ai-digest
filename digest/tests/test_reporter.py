from unittest.mock import MagicMock

from digest.agents.reporter import Reporter, RunReport


def test_daily_summary_sends_counts():
    tg = MagicMock(); tg.send_message.return_value = 7
    report = RunReport(articles_in=12, posts_written=3, published=3, errors=[], site_url="https://x")
    mid = Reporter(tg).daily_summary(report)
    assert mid == 7
    text = tg.send_message.call_args.args[0]
    assert "12" in text and "3" in text and "https://x" in text


def test_daily_summary_includes_error_count():
    tg = MagicMock()
    report = RunReport(articles_in=5, posts_written=1, published=0, errors=["feed X failed"])
    Reporter(tg).daily_summary(report)
    text = tg.send_message.call_args.args[0]
    assert "feed X failed" in text


def test_error_alert_has_cause_and_fix():
    tg = MagicMock()
    Reporter(tg).error_alert(stage="Writer", cause="claude timeout", fix="check quota")
    text = tg.send_message.call_args.args[0]
    assert "Writer" in text and "claude timeout" in text and "check quota" in text
