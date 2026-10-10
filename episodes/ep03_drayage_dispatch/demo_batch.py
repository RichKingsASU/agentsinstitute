"""Replay a gate webhook batch through DispatchGuard, then assert the invariants."""
import time
from collections import Counter

from dispatch_guard import HOUR, DispatchGuard, GateEvent, Kind

NOW = 1_000 * HOUR
BATCH = [
    GateEvent("e1", "MSKU1234567", Kind.AVAILABLE, NOW - 80 * HOUR),
    GateEvent("e1", "MSKU1234567", Kind.AVAILABLE, NOW - 80 * HOUR),  # webhook retry
    GateEvent("e2", "MSKU1234567", Kind.AVAILABLE, NOW - 80 * HOUR),  # same fact via EDI feed
    GateEvent("e3", "TGHU7654321", Kind.AVAILABLE, NOW - 20 * HOUR),
    GateEvent("e4", "CMAU5550001", Kind.OUTGATE, NOW - 2 * HOUR),     # arrives first...
    GateEvent("e5", "CMAU5550001", Kind.AVAILABLE, NOW - 90 * HOUR),  # ...older event arrives late
    GateEvent("e6", "OOLU8880002", Kind.AVAILABLE, NOW - 75 * HOUR),
]

guard = DispatchGuard()
results = []
for ev in BATCH:
    decision = guard.evaluate(ev, NOW)
    results.append((ev.container, decision.split()[0]))
    print(f"{ev.event_id}  {ev.container}  {ev.kind.value:<9}  -> {decision}")
    time.sleep(0.9)

dispatched = Counter(c for c, d in results if d == "DISPATCH")
assert dispatched == {"MSKU1234567": 1, "OOLU8880002": 1}, dispatched  # one chassis each, no doubles
assert ("CMAU5550001", "STALE") in results                             # late event never sent a truck
print(f"PASS  {len(BATCH)} events  {sum(dispatched.values())} dispatches  0 double reservations  1 stale dropped")

bench, n = DispatchGuard(), 100_000
t0 = time.perf_counter()
for i in range(n):
    bench.evaluate(GateEvent(f"b{i}", f"C{i % 5_000}", Kind.AVAILABLE, NOW - 80 * HOUR), NOW)
rate = n / (time.perf_counter() - t0)
assert rate > 50_000, f"{rate:,.0f} events/s"
print(f"PASS  benchmark {rate:,.0f} events/s (> 50,000)")
