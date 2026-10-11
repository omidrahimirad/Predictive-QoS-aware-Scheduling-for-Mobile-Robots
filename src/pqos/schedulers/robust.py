"""Causal residual monitoring and interpretable binary predictive/EDF gating."""

import math

from pqos.entities import Allocation, Observation
from pqos.schedulers import GreedyScheduler


class RobustPredictiveScheduler:
    """Reliability scores are diagnostics, not calibrated probabilities or guarantees."""

    def __init__(
        self,
        residual_scale: float,
        threshold: float = 2.5,
        shift_scale: float = 0.1,
        smoothing: float = 0.05,
        adaptive: bool = True,
        urgency: float = 2.0,
        horizon: int = 4,
        opportunity: float = 1.0,
    ) -> None:
        if not all(math.isfinite(x) and x > 0 for x in (residual_scale, threshold, shift_scale)):
            raise ValueError("reliability scales must be finite and positive")
        if not 0 < smoothing <= 1:
            raise ValueError("smoothing must be in (0,1]")
        self.residual_scale = residual_scale
        self.threshold = threshold
        self.shift_scale = shift_scale
        self.smoothing = smoothing
        self.adaptive = adaptive
        self.horizon = horizon
        self.predictive = GreedyScheduler(
            "predictive", urgency=urgency, horizon=horizon, opportunity=opportunity
        )
        self.edf = GreedyScheduler("edf")
        self.reset()

    def reset(self) -> None:
        self.predictive.reset()
        self.edf.reset()
        self.fallbacks = 0
        self.pending: dict[int, tuple[float, ...]] = {}
        self.residuals: list[float] = []
        self.last_measurement = -1
        self.last_slot = -1
        self.confidence = 0.0
        self.risk = 0.0
        self.used_fallback = False
        self.residual_updates = 0

    def allocate(self, o: Observation) -> Allocation:
        if o.slot <= self.last_slot:
            raise ValueError("observations must arrive in increasing slot order")
        self.last_slot = o.slot
        if o.measurement_slot > o.slot:
            raise ValueError("future measurement timestamp")
        n = len(o.service)
        if self.residuals and len(self.residuals) != n:
            raise ValueError("UE count changed within episode")
        if not self.residuals:
            self.residuals = [self.residual_scale] * n
        valid = (
            o.forecast is not None
            and len(o.forecast) == n
            and all(
                len(row) >= self.horizon and all(math.isfinite(v) and v >= 0 for v in row)
                for row in o.forecast
            )
            and o.forecast_age <= self.predictive.max_age
            and len(o.forecast_db) == n
            and all(math.isfinite(v) for v in o.forecast_db)
            and len(o.observed_db) == n
            and all(math.isfinite(v) for v in o.observed_db)
            and len(o.feature_shift) == n
            and all(math.isfinite(v) and v >= 0 for v in o.feature_shift)
            and 0 <= o.measurement_slot <= o.slot
        )
        # A target t+h becomes observable only when a measurement stamped t+h arrives.
        # Duplicate startup samples cannot update residuals a second time.
        if o.measurement_slot > self.last_measurement and len(o.observed_db) == n:
            matured = self.pending.pop(o.measurement_slot, None)
            if matured is not None and all(math.isfinite(v) for v in o.observed_db):
                for i, (prediction, measurement) in enumerate(zip(matured, o.observed_db)):
                    error = abs(prediction - measurement)
                    self.residuals[i] = (1 - self.smoothing) * self.residuals[
                        i
                    ] + self.smoothing * error
                self.residual_updates += 1
            self.last_measurement = o.measurement_slot
            self.pending = {t: p for t, p in self.pending.items() if t > o.measurement_slot}
        if valid:
            self.pending[o.slot + self.horizon] = o.forecast_db
        self.risk = max(
            max(self.residuals, default=self.residual_scale) / self.residual_scale,
            max(o.feature_shift, default=0.0) / self.shift_scale,
        )
        self.confidence = 1 / (1 + self.risk) if valid else 0.0
        self.used_fallback = not valid or (self.adaptive and self.risk > self.threshold)
        if self.used_fallback:
            self.fallbacks += 1
            return self.edf.allocate(o)
        return self.predictive.allocate(o)
