"""Event-driven dispatch guard for terminal gate webhooks.

Gate webhooks arrive late, twice, and out of order. Before any truck is sent:
drop duplicates and stale events, enforce the dwell threshold, then take an
idempotency lock so each chassis is reserved exactly once.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

HOUR = 3600


class Kind(str, Enum):
    AVAILABLE = "available"  # released for pickup at the terminal
    OUTGATE = "outgate"      # container left the terminal


@dataclass(frozen=True)
class GateEvent:
    event_id: str
    container: str
    kind: Kind
    ts: float  # terminal clock (epoch seconds), not arrival time


class Lock:
    """In-memory stand-in for Redis `SET key 1 NX EX ttl`."""

    def __init__(self) -> None:
        self._expires: dict[str, float] = {}

    def acquire(self, key: str, ttl: float, now: float) -> bool:
        if self._expires.get(key, 0.0) > now:
            return False
        self._expires[key] = now + ttl
        return True


@dataclass
class DispatchGuard:
    dwell_threshold_h: float = 72.0  # free time ends at 96h; dispatch with a 24h buffer
    lock: Lock = field(default_factory=Lock)
    seen: set[str] = field(default_factory=set)
    last_ts: dict[str, float] = field(default_factory=dict)

    def evaluate(self, ev: GateEvent, now: float) -> str:
        if ev.event_id in self.seen:
            return "DUPLICATE"
        self.seen.add(ev.event_id)
        if ev.ts < self.last_ts.get(ev.container, float("-inf")):
            return "STALE"  # older than what we already know: never act on it
        self.last_ts[ev.container] = ev.ts
        if ev.kind is Kind.OUTGATE:
            return "CLOSED"
        dwell_h = (now - ev.ts) / HOUR
        if dwell_h < self.dwell_threshold_h:
            return f"HOLD {dwell_h:.0f}h"
        if not self.lock.acquire(f"chassis:{ev.container}", ttl=24 * HOUR, now=now):
            return "LOCKED"  # another event already reserved this chassis
        return f"DISPATCH {dwell_h:.0f}h"
