"""Causal feature extraction, grouped model fitting, and forecast interpolation."""

import hashlib
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from pqos.config import Scenario
from pqos.traces import Trace, capacity, success_probability

HORIZONS = np.array([1, 2, 4, 8, 16])
FEATURE_SCHEMA = "observed-db-history,current-position,velocity,measurement-age:v1"


def features(trace: Trace, s: Scenario, position: bool = True) -> np.ndarray:
    length, n = trace.sinr_db.shape
    pieces = [trace.observed_db[np.maximum(np.arange(length) - lag, 0)] for lag in range(s.history)]
    values = np.stack(pieces, axis=2)
    age = np.minimum(np.arange(length), s.observation_delay)[:, None, None]
    age = np.broadcast_to(age, (length, n, 1))
    if position:
        values = np.concatenate((values, trace.position, trace.velocity, age), axis=2)
    else:
        values = np.concatenate((values, age), axis=2)
    return values


def dataset(traces: list[Trace], s: Scenario, position: bool = True):
    xs, ys, current, blocked = [], [], [], []
    for trace in traces:
        start, end = s.history - 1, s.warmup + s.duration - int(HORIZONS[-1])
        if end <= start:
            raise ValueError("episode too short for training windows")
        indices = np.arange(start, end)
        xs.append(
            features(trace, s, position)[indices].reshape(
                -1, s.history + 5 if position else s.history + 1
            )
        )
        ys.append(
            np.stack([trace.sinr_db[indices + h] for h in HORIZONS], axis=-1).reshape(
                -1, len(HORIZONS)
            )
        )
        current.append(np.repeat(trace.observed_db[indices].reshape(-1, 1), 5, axis=1))
        blocked.append(
            np.stack([trace.blocked[indices + h] for h in HORIZONS], axis=-1).reshape(-1, 5)
        )
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(current), np.concatenate(blocked)


def fit_predictors(
    train: list[Trace], validation: list[Trace], s: Scenario
) -> tuple[dict, pd.DataFrame]:
    if {t.seed for t in train} & {t.seed for t in validation}:
        raise ValueError("train/validation episode overlap")
    models = {}
    rows = []
    for position in (True, False):
        x, y, _, _ = dataset(train, s, position)
        xv, yv, persistence, blocked = dataset(validation, s, position)
        candidates = {
            "ridge": make_pipeline(StandardScaler(), Ridge(alpha=10)),
            "tree": ExtraTreesRegressor(
                n_estimators=48, max_depth=12, min_samples_leaf=12, n_jobs=1, random_state=7
            ),
        }
        for name, model in candidates.items():
            key = name if position else f"{name}_no_position"
            model.fit(x, y)
            pred = model.predict(xv)
            for k, h in enumerate(HORIZONS):
                error = pred[:, k] - yv[:, k]
                base_mae = np.abs(persistence[:, k] - yv[:, k]).mean()
                rows.append(
                    {
                        "model": key,
                        "split": "validation",
                        "horizon": int(h),
                        "mae_db": np.abs(error).mean(),
                        "rmse_db": np.sqrt((error**2).mean()),
                        "persistence_mae_db": base_mae,
                        "skill": 1 - np.abs(error).mean() / base_mae if base_mae else np.nan,
                        "blocked_mae_db": np.abs(error[blocked[:, k]]).mean()
                        if blocked[:, k].any()
                        else np.nan,
                    }
                )
            models[key] = {
                "estimator": model,
                "position": position,
                "history": s.history,
                "schema": FEATURE_SCHEMA,
            }
    table = pd.DataFrame(rows)
    best = table[table.model.isin(["ridge", "tree"])].groupby("model").mae_db.mean().idxmin()
    models["selected"] = best
    models["training_seeds"] = [t.seed for t in train]
    models["validation_seeds"] = [t.seed for t in validation]
    return models, table


def forecast(trace: Trace, s: Scenario, bundle: dict, name: str | None = None) -> np.ndarray:
    key = name or bundle["selected"]
    spec = bundle[key]
    if spec["history"] != s.history or spec["schema"] != FEATURE_SCHEMA:
        raise ValueError("model feature schema incompatible")
    x = features(trace, s, spec["position"])
    predicted = spec["estimator"].predict(x.reshape(-1, x.shape[-1])).reshape(s.slots, s.n_ues, 5)
    dense = np.empty((s.slots, s.n_ues, 16))
    for t in range(s.slots):
        for i in range(s.n_ues):
            db = np.interp(np.arange(1, 17), HORIZONS, predicted[t, i])
            dense[t, i] = capacity(db, s) * success_probability(db, s.error_free)
    # No complete history yet: persistence fallback rather than extrapolated model input.
    dense[: s.history - 1] = persistence_forecast(trace, s)[: s.history - 1]
    return dense


def persistence_forecast(trace: Trace, s: Scenario) -> np.ndarray:
    expected = capacity(trace.observed_db, s) * success_probability(trace.observed_db, s.error_free)
    return np.repeat(expected[:, :, None], 16, axis=2)


def prediction_metrics(traces: list[Trace], s: Scenario, bundle: dict, split: str) -> pd.DataFrame:
    if split == "test" and (
        {t.seed for t in traces} & set(bundle["training_seeds"] + bundle["validation_seeds"])
    ):
        raise ValueError("held-out episode overlap")
    rows = []
    for key in ("persistence", "ridge", "tree", "ridge_no_position", "tree_no_position"):
        position = key == "persistence" or bundle[key]["position"]
        x, y, base, blocked = dataset(traces, s, position)
        pred = base if key == "persistence" else bundle[key]["estimator"].predict(x)
        for k, horizon in enumerate(HORIZONS):
            error = pred[:, k] - y[:, k]
            denom = np.abs(base[:, k] - y[:, k]).mean()
            rows.append(
                {
                    "model": key,
                    "split": split,
                    "horizon": int(horizon),
                    "samples": len(error),
                    "mae_db": np.abs(error).mean(),
                    "rmse_db": np.sqrt((error**2).mean()),
                    "skill": 1 - np.abs(error).mean() / denom if denom else np.nan,
                    "blocked_mae_db": np.abs(error[blocked[:, k]]).mean()
                    if blocked[:, k].any()
                    else np.nan,
                }
            )
    return pd.DataFrame(rows)


def model_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_bundle(path: Path) -> dict:
    """Only use artifacts generated locally; joblib can execute arbitrary code."""
    return joblib.load(path)
