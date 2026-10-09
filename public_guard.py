"""Best-effort, process-local limits for a publicly hosted *demo*.

The limit resets on process restart (e.g. free hosting spin-down). It is not a
financial cap or a replacement for rate controls at Qloo/LLM providers.
"""
from __future__ import annotations

import os
import threading
import time
from collections import deque


def _limit(name: str, default: int) -> int:
    try:
        return min(1000, max(1, int(os.environ.get(name, str(default)))))
    except ValueError:
        return default


class DemoBudget:
    """Global, atomic rolling budget shared by all visitor requests in one process."""

    def __init__(self, hourly: int | None = None, daily: int | None = None, concurrent: int = 2,
                 clock=None):
        self.hourly = hourly if hourly is not None else _limit("ATLAS_MAX_HOURLY", 20)
        self.daily = daily if daily is not None else _limit("ATLAS_MAX_DAILY", 60)
        self.concurrent = concurrent
        self.clock = clock or time.monotonic
        self.events = deque()
        self.inflight = 0
        self.lock = threading.Lock()

    def admit(self) -> str | None:
        """Return None on admission, otherwise a safe reason to return as HTTP 429."""
        with self.lock:
            now = self.clock()
            while self.events and now - self.events[0] >= 86400:
                self.events.popleft()
            if self.inflight >= self.concurrent:
                return "busy"
            if len(self.events) >= self.daily:
                return "daily_limit"
            if sum(1 for ts in self.events if now - ts < 3600) >= self.hourly:
                return "hourly_limit"
            self.events.append(now)
            self.inflight += 1
            return None

    def release(self) -> None:
        with self.lock:
            self.inflight = max(0, self.inflight - 1)


PUBLIC_BUDGET = DemoBudget()
