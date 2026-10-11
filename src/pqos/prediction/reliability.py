"""Train-only feature envelope and validation observable-residual calibration."""

import numpy as np

from pqos.config import Scenario
from pqos.prediction.models import HORIZONS, dataset, features
from pqos.traces import Trace


def predict_db(trace: Trace, s: Scenario, bundle: dict, horizon: int) -> np.ndarray:
    spec = bundle[bundle["selected"]]
    x = features(trace, s, spec["position"])
    index = np.flatnonzero(HORIZONS == horizon)
    if len(index) != 1:
        raise ValueError("reliability horizon must be a fitted horizon")
    return (
        spec["estimator"].predict(x.reshape(-1, x.shape[-1]))[:, index[0]].reshape(s.slots, s.n_ues)
    )


def calibrate(train: list[Trace], validation: list[Trace], s: Scenario, bundle: dict) -> dict:
    if {t.seed for t in train} & {t.seed for t in validation}:
        raise ValueError("calibration split overlap")
    spec = bundle[bundle["selected"]]
    x, _, _, _ = dataset(train, s, spec["position"])
    lower, upper = np.quantile(x, [0.005, 0.995], axis=0)
    horizon = bundle["policy"]["horizon"]
    errors = []
    for trace in validation:
        prediction = predict_db(trace, s, bundle, horizon)
        issue = np.arange(s.history - 1, s.warmup + s.duration - horizon - s.observation_delay)
        # At target+h+delay the trace exposes the noisy measurement of target+h.
        errors.append(
            np.abs(prediction[issue] - trace.observed_db[issue + horizon + s.observation_delay])
        )
    error = np.concatenate(errors)
    return {
        "horizon": horizon,
        "residual_scale": max(float(error.mean()), 0.1),
        "observable_error_q90_db": float(np.quantile(error, 0.9)),
        "feature_lower": lower.tolist(),
        "feature_upper": upper.tolist(),
        "calibration_seeds": [t.seed for t in validation],
        "target": "delayed noisy measurement, not hidden future SINR",
    }


def inputs(trace: Trace, s: Scenario, bundle: dict, calibration: dict) -> dict[str, np.ndarray]:
    spec = bundle[bundle["selected"]]
    x = features(trace, s, spec["position"])
    lower = np.array(calibration["feature_lower"])
    upper = np.array(calibration["feature_upper"])
    span = np.maximum(upper - lower, 1.0)
    excess = np.maximum(np.maximum(lower - x, x - upper), 0) / span
    prediction = predict_db(trace, s, bundle, calibration["horizon"])
    prediction[: s.history - 1] = np.nan  # insufficient history => EDF safety fallback
    return {"forecast_db": prediction, "feature_shift": excess.max(axis=2)}
