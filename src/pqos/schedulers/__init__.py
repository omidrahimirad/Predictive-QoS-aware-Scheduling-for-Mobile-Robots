"""Allocators operating only on immutable causal observations."""

import math

from pqos.entities import Allocation, Observation


class GreedyScheduler:
    def __init__(
        self,
        kind: str,
        urgency: float = 4.0,
        opportunity: float = 1.0,
        horizon: int = 16,
        max_age: int = 4,
    ):
        if kind not in {"rr", "pf", "edf", "reactive", "predictive", "persistence", "oracle"}:
            raise ValueError(f"unknown scheduler {kind}")
        if urgency < 0 or opportunity < 0 or horizon < 1:
            raise ValueError("invalid scheduler parameters")
        self.kind = kind
        self.urgency = urgency
        self.opportunity = opportunity
        self.horizon = horizon
        self.max_age = max_age
        self.reset()

    def reset(self) -> None:
        self.pointer = 0
        self.fallbacks = 0

    def allocate(self, observation: Observation) -> Allocation:
        o = observation
        n = len(o.service)
        allocated = [0] * n
        forecast = o.forecast
        predictive = self.kind in {"predictive", "persistence", "oracle"}
        valid = (
            forecast is not None
            and len(forecast) == n
            and all(
                len(row) >= self.horizon and all(math.isfinite(v) and v >= 0 for v in row)
                for row in forecast
            )
        )
        if predictive and (not valid or o.forecast_age > self.max_age):
            self.fallbacks += 1
            predictive = False
        expected = [a * b for a, b in zip(o.service, o.success_probability)]
        pf = [r / max(avg, 1.0) for r, avg in zip(expected, o.average_rate)]
        scale = max(max(pf, default=0), 1e-9)
        for _ in range(o.resources):
            eligible = [
                i
                for i in range(n)
                if expected[i] > 0 and allocated[i] * o.service[i] < o.eligible_bits[i]
            ]
            if not eligible:
                break
            if self.kind == "rr":
                winner = min(eligible, key=lambda i: (i - self.pointer) % n)
                self.pointer = (winner + 1) % n
            else:
                scores = []
                for i in eligible:
                    tentative = allocated[i] * expected[i]
                    cumulative = 0.0
                    urgency = 0.0
                    earliest = float("inf")
                    for demand in o.controls[i]:
                        cumulative += demand.bits
                        unmet = max(cumulative - tentative, 0.0)
                        if unmet == 0:
                            continue
                        slack = max(demand.slack, 1)
                        earliest = min(earliest, slack)
                        if predictive and forecast is not None:
                            h = min(slack, self.horizon)
                            future = sum(forecast[i][:h]) + max(slack - h, 0) * expected[i]
                        else:
                            future = slack * expected[i]
                        urgency = max(urgency, unmet / max(future, 1.0))
                    bonus = 0.0
                    if predictive and forecast is not None and urgency > 0:
                        mean_future = sum(forecast[i][: self.horizon]) / self.horizon
                        bonus = max(expected[i] - mean_future, 0) / max(expected[i], 1.0)
                    score = pf[i] / scale
                    if self.kind in {"reactive", "predictive", "persistence", "oracle"}:
                        score += self.urgency * min(urgency, 10) + self.opportunity * bonus
                    if self.kind == "edf" and earliest < float("inf"):
                        score = 1000 + 1 / earliest
                    scores.append((score, -i, i))
                winner = max(scores)[2]
            allocated[winner] += 1
        result = Allocation(tuple(allocated))
        result.validate(o)
        return result
