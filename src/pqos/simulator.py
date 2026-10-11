"""Slot engine with physical delivery separated from delayed acknowledgements."""

import time
from dataclasses import dataclass

import numpy as np

from pqos.config import Scenario
from pqos.entities import Chunk, ControlDemand, Observation, Packet, Scheduler
from pqos.metrics import summarize
from pqos.traces import Trace, capacity, success_probability


@dataclass
class SimulationResult:
    metrics: dict
    packets: list[Packet]
    timeline: list[dict]


def simulate(
    s: Scenario,
    trace: Trace,
    scheduler: Scheduler,
    forecasts: np.ndarray | None = None,
    diagnostic_oracle: bool = False,
    keep_timeline: bool = False,
    reliability_inputs: dict[str, np.ndarray] | None = None,
) -> SimulationResult:
    if trace.service.shape != (s.slots, s.n_ues):
        raise ValueError("trace/scenario shape mismatch")
    scheduler.reset()
    packets: list[Packet] = []
    queues: list[list[int]] = [[] for _ in range(s.n_ues)]
    flights: list[Chunk] = []
    retries: list[Chunk] = []
    average = np.ones(s.n_ues)
    window_bits = np.zeros((s.n_ues, 2))
    timings = []
    timeline = []
    attempts = failures = used = wasted = retry_attempts = 0
    occupancies = []
    hol = []
    observed_service = capacity(trace.observed_db, s)
    probabilities = success_probability(trace.sinr_db, s.error_free)
    observed_probability = success_probability(trace.observed_db, s.error_free)
    physical_completions: dict[int, list[Chunk]] = {}
    feedback: dict[int, list[Chunk]] = {}

    def active(p: Packet) -> bool:
        return p.reason is None

    def available(p: Packet) -> int:
        pending = sum(c.bits for c in flights if c.packet == p.id)
        reserved = sum(c.bits for c in retries if c.packet == p.id)
        return max(p.size - p.acknowledged - pending - reserved, 0)

    def physical(t: int) -> np.ndarray:
        nonlocal wasted
        delivered_slot = np.zeros(s.n_ues)
        for chunk in physical_completions.pop(t, []):
            p = packets[chunk.packet]
            if p.reason is not None:
                wasted += chunk.bits
                continue
            p.delivered += chunk.bits
            chunk.physically_delivered = True
            delivered_slot[p.ue] += chunk.bits
            if s.warmup < t <= s.warmup + s.duration:
                window_bits[p.ue, int(p.traffic == "best_effort")] += chunk.bits
            if p.delivered == p.size:
                p.completion = t
                p.reason = "delivered" if p.deadline is None or t <= p.deadline else "late"
        return delivered_slot

    for t in range(s.slots):
        physical(t)
        acknowledged_slot = np.zeros(s.n_ues)
        for chunk in feedback.pop(t, []):
            flights.remove(chunk)
            p = packets[chunk.packet]
            if chunk.physically_delivered:
                # Successful unique service enters the PF estimate only at ACK maturity.
                p.acknowledged += chunk.bits
                acknowledged_slot[p.ue] += chunk.bits
            if not active(p):
                continue
            if not chunk.success and chunk.attempt >= s.max_attempts:
                p.reason = "retry_exhausted"
            elif not chunk.success:
                retries.append(Chunk(p.id, chunk.bits, chunk.attempt + 1, t))
        # Same bits/slot units as instantaneous service; feedback is delayed causally.
        average = 0.99 * average + 0.01 * acknowledged_slot
        retries = [c for c in retries if active(packets[c.packet])]
        # Admit before expiration, intentionally matching the specified event ordering.
        for i in range(s.n_ues):
            for traffic_class in range(2):
                for _ in range(int(trace.arrivals[t, i, traffic_class])):
                    size = s.control_bits if traffic_class == 0 else s.be_bits
                    backlog = sum(
                        packets[j].size - packets[j].delivered
                        for j in queues[i]
                        if active(packets[j])
                    )
                    packet = Packet(
                        len(packets),
                        i,
                        "control" if traffic_class == 0 else "best_effort",
                        t,
                        size,
                        t + s.deadline if traffic_class == 0 else None,
                    )
                    if backlog + size > s.buffer_bits:
                        packet.reason = "overflow"
                    packets.append(packet)
                    queues[i].append(packet.id)
        for p in packets:
            if active(p) and p.deadline is not None and p.deadline <= t:
                p.reason = "deadline"
        for i in range(s.n_ues):
            queues[i] = [j for j in queues[i] if active(packets[j])]
        retries = [c for c in retries if active(packets[c.packet])]
        eligible = []
        demands = []
        for i in range(s.n_ues):
            ready = sum(c.bits for c in retries if packets[c.packet].ue == i)
            eligible.append(ready + sum(available(packets[j]) for j in queues[i]))
            control_demands = []
            for j in queues[i]:
                p = packets[j]
                if p.deadline is not None:
                    ready_bits = sum(c.bits for c in retries if c.packet == j)
                    bits = available(p) + ready_bits
                    if bits:
                        control_demands.append(ControlDemand(bits, p.deadline - t))
            demands.append(tuple(sorted(control_demands, key=lambda d: d.slack)))
        forecast = None
        if diagnostic_oracle:
            indices = np.minimum(np.arange(t + 1, t + 17), s.slots - 1)
            forecast = (trace.service[indices] * probabilities[indices]).T
        elif forecasts is not None:
            if forecasts.shape != (s.slots, s.n_ues, 16):
                raise ValueError("forecast shape mismatch")
            forecast = forecasts[t]
        reliability = reliability_inputs or {}
        observation = Observation(
            t,
            s.resources,
            tuple(observed_service[t]),
            tuple(observed_probability[t]),
            tuple(eligible),
            tuple(demands),
            tuple(average),
            tuple(tuple(row) for row in forecast) if forecast is not None else None,
            observed_db=tuple(trace.observed_db[t]),
            measurement_slot=max(t - s.observation_delay, 0),
            forecast_db=tuple(reliability["forecast_db"][t]) if reliability else (),
            feature_shift=tuple(reliability["feature_shift"][t]) if reliability else (),
        )
        begin = time.perf_counter()
        allocation = scheduler.allocate(observation)
        timings.append(time.perf_counter() - begin)
        allocation.validate(observation)
        slot_used = 0
        for i, count in enumerate(allocation.counts):
            budget = int(trace.service[t, i]) * count
            if count:
                slot_used += count
            # One shared success variate per UE-slot aggregate; chunks are correlated.
            success = trace.uniforms[t, i] < probabilities[t, i]
            ordered = sorted(
                queues[i], key=lambda j: (packets[j].traffic != "control", packets[j].arrival, j)
            )
            for j in ordered:
                p = packets[j]
                chunks = [c for c in retries if c.packet == j]
                for c in chunks:
                    if budget <= 0:
                        break
                    amount = min(c.bits, budget)
                    c.bits -= amount
                    attempt_chunk = Chunk(
                        j, amount, c.attempt, t + 1 + s.feedback_delay, bool(success), t + 1
                    )
                    flights.append(attempt_chunk)
                    feedback.setdefault(attempt_chunk.ready, []).append(attempt_chunk)
                    if success:
                        physical_completions.setdefault(t + 1, []).append(attempt_chunk)
                    attempts += 1
                    retry_attempts += 1
                    failures += int(not success)
                    budget -= amount
                    if c.bits == 0:
                        retries.remove(c)
                amount = min(available(p), budget)
                if amount > 0:
                    c = Chunk(j, amount, 1, t + 1 + s.feedback_delay, bool(success), t + 1)
                    flights.append(c)
                    feedback.setdefault(c.ready, []).append(c)
                    if success:
                        physical_completions.setdefault(t + 1, []).append(c)
                    attempts += 1
                    retry_attempts += 1
                    failures += int(not success)
                    budget -= amount
        if s.warmup <= t < s.warmup + s.duration:
            used += slot_used
            occupancies.append(sum(p.size - p.delivered for p in packets if active(p)))
            hol.append(max((t - packets[j].arrival for q in queues for j in q), default=0))
        if keep_timeline:
            timeline.append(
                {
                    "slot": t,
                    "confidence": getattr(scheduler, "confidence", float("nan")),
                    "risk": getattr(scheduler, "risk", float("nan")),
                    "fallback": int(getattr(scheduler, "used_fallback", False)),
                    "residual_db": max(getattr(scheduler, "residuals", [float("nan")])),
                    "sinr_db": float(trace.sinr_db[t, 0]),
                    "observed_service": float(observed_service[t, 0]),
                    "predicted_service": float(forecast[0, -1])
                    if forecast is not None
                    else float("nan"),
                    "true_service": float(trace.service[t, 0]),
                    "x_m": float(trace.position[t, 0, 0]),
                    "queue_bits": sum(packets[j].size - packets[j].delivered for j in queues[0]),
                    "allocated_units": allocation.counts[0],
                }
            )
    physical(s.slots)
    for p in packets:
        if p.reason is None:
            p.reason = "censored"
    discarded = sum(p.size - p.delivered for p in packets if p.reason != "censored")
    unresolved = sum(p.size - p.delivered for p in packets if p.reason == "censored")
    generated = sum(p.size for p in packets)
    delivered = sum(p.delivered for p in packets)
    if generated != delivered + discarded + unresolved:
        raise AssertionError("payload conservation failed")
    expired_waste = sum(p.delivered for p in packets if p.reason in {"deadline", "late"})
    extra = {
        "seed": trace.seed,
        "trace_hash": trace.digest,
        "generated_bits": generated,
        "delivered_bits": delivered,
        "discarded_bits": discarded,
        "unresolved_bits": unresolved,
        "resource_utilization": used / (s.duration * s.resources),
        "chunk_attempts": attempts,
        "retry_chunk_attempts": retry_attempts,
        "failed_chunk_attempts": failures,
        "mean_queue_bits": float(np.mean(occupancies)),
        "mean_hol_ms": float(np.mean(hol)) * s.slot_seconds * 1000,
        "expired_delivered_bits": expired_waste,
        "late_feedback_waste_bits": wasted,
        "fallbacks": scheduler.fallbacks,
        "fallback_frequency": scheduler.fallbacks / s.slots,
        "residual_updates": getattr(scheduler, "residual_updates", 0),
    }
    return SimulationResult(summarize(packets, s, window_bits, timings, extra), packets, timeline)
