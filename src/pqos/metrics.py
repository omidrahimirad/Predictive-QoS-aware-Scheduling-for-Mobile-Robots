"""Cohort-based delivery metrics and episode summaries."""

import numpy as np

from pqos.config import Scenario
from pqos.entities import Packet


def summarize(
    packets: list[Packet],
    s: Scenario,
    window_bits: np.ndarray,
    scheduler_seconds: list[float],
    extra: dict,
) -> dict:
    cohort = [p for p in packets if s.warmup <= p.arrival < s.warmup + s.duration]
    control = [p for p in cohort if p.traffic == "control"]
    be = [p for p in cohort if p.traffic == "best_effort"]
    ontime = [p for p in control if p.completion is not None and p.completion <= p.deadline]
    delays = [
        (p.completion - p.arrival) * s.slot_seconds * 1000
        for p in control
        if p.completion is not None
    ]
    fairness_bits = window_bits.sum(axis=1)
    total = fairness_bits.sum()
    seconds = s.duration * s.slot_seconds
    reasons = {
        name: sum(p.reason == name for p in control)
        for name in ("deadline", "overflow", "retry_exhausted", "late", "censored")
    }
    result = {
        "control_arrivals": len(control),
        "control_ontime": len(ontime),
        "control_violation": 1 - len(ontime) / len(control) if control else float("nan"),
        "control_delivery_probability": sum(p.completion is not None for p in control)
        / len(control)
        if control
        else float("nan"),
        "deadline_expiration_ratio": reasons["deadline"] / len(control)
        if control
        else float("nan"),
        "control_delivered_samples": len(delays),
        "be_censored_packets": sum(p.reason == "censored" for p in be),
        "be_cohort_completed": sum(p.completion is not None for p in be),
        "be_goodput_mbps": window_bits[:, 1].sum() / seconds / 1e6,
        "total_goodput_mbps": total / seconds / 1e6,
        "jain_fairness": total**2 / (s.n_ues * np.square(fairness_bits).sum())
        if total > 0
        else float("nan"),
        "scheduler_mean_us": np.mean(scheduler_seconds) * 1e6,
        "scheduler_p99_us": np.percentile(scheduler_seconds, 99) * 1e6,
        **{f"control_{key}": value for key, value in reasons.items()},
        **extra,
    }
    for q in (50, 95, 99):
        result[f"latency_p{q}_ms"] = float(np.percentile(delays, q)) if delays else float("nan")
    for i in range(s.n_ues):
        c = [p for p in control if p.ue == i]
        result[f"ue_{i}_violation"] = (
            1 - sum(p in ontime for p in c) / len(c) if c else float("nan")
        )
        result[f"ue_{i}_goodput_mbps"] = fairness_bits[i] / seconds / 1e6
    return result
