"""Episode-level confidence intervals; no packet-level independence claim."""

import numpy as np
import pandas as pd

METRICS = ["control_violation", "be_goodput_mbps", "jain_fairness", "latency_p99_ms"]


def interval(values: np.ndarray, seed: int = 771, repetitions: int = 10000):
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, (repetitions, len(values)), replace=True).mean(axis=1)
    return float(values.mean()), *np.percentile(samples, [2.5, 97.5]).tolist()


def summaries(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (scenario, policy), group in frame.groupby(["scenario", "policy"]):
        for metric in METRICS:
            values = group[metric].to_numpy()
            mean, low, high = interval(values)
            rows.append(
                {
                    "scenario": scenario,
                    "policy": policy,
                    "metric": metric,
                    "n_episodes": int(np.isfinite(values).sum()),
                    "mean": mean,
                    "std": np.nanstd(values, ddof=1) if len(values) > 1 else np.nan,
                    "ci_low": low,
                    "ci_high": high,
                }
            )
    return pd.DataFrame(
        rows,
        columns=["scenario", "policy", "metric", "n_episodes", "mean", "std", "ci_low", "ci_high"],
    )


def paired_comparisons(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario, group in frame.groupby("scenario"):
        target = group[group.policy == "predictive"].set_index("seed")
        for reference in ("reactive", "edf", "pf", "persistence", "oracle"):
            baseline = group[group.policy == reference].set_index("seed")
            paired = target.join(baseline, lsuffix="_target", rsuffix="_reference", how="inner")
            if paired.empty:
                continue
            if not (paired.trace_hash_target == paired.trace_hash_reference).all():
                raise ValueError("paired episode trace mismatch")
            for metric in METRICS:
                values = (paired[f"{metric}_target"] - paired[f"{metric}_reference"]).to_numpy()
                mean, low, high = interval(values)
                multiplier = 100 if metric == "control_violation" else 1
                rows.append(
                    {
                        "scenario": scenario,
                        "comparison": f"predictive - {reference}",
                        "metric": metric,
                        "unit": "percentage points" if multiplier == 100 else "native metric units",
                        "n_pairs": int(np.isfinite(values).sum()),
                        "difference": mean * multiplier,
                        "ci_low": low * multiplier,
                        "ci_high": high * multiplier,
                    }
                )
    return pd.DataFrame(
        rows,
        columns=[
            "scenario",
            "comparison",
            "metric",
            "unit",
            "n_pairs",
            "difference",
            "ci_low",
            "ci_high",
        ],
    )
