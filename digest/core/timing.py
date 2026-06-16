from __future__ import annotations

import logging
import time
from contextlib import contextmanager

logger = logging.getLogger("digest.timing")


@contextmanager
def timed(label: str, sink: dict | None = None):
    """Time a block, log its duration, and optionally record it into `sink`.

        with timed("process", report.timings):
            ...
    """
    start = time.perf_counter()
    logger.info("▶ %s …", label)
    try:
        yield
    finally:
        dur = time.perf_counter() - start
        if sink is not None:
            sink[label] = round(sink.get(label, 0.0) + dur, 2)
        logger.info("✓ %s — %.2fs", label, dur)
