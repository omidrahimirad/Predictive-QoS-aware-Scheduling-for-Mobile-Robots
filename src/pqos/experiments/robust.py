"""Separate v2 development/calibration and frozen, held-out paired campaigns."""

import json
import time
from concurrent.futures import Future, ProcessPoolExecutor
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pqos.config import Scenario, scenario_dict
from pqos.experiments.runner import (
    POLICIES,
    atomic_csv,
    atomic_json,
    digest,
    environment,
    source_hash,
    train,
)
from pqos.experiments.statistics import METRICS, interval
from pqos.prediction.models import forecast, load_bundle, model_hash, persistence_forecast
from pqos.prediction.reliability import calibrate, inputs
from pqos.schedulers import GreedyScheduler
from pqos.schedulers.robust import RobustPredictiveScheduler
from pqos.simulator import SimulationResult, simulate
from pqos.traces import generate

V2_POLICIES = POLICIES + ["robust", "robust_no_adaptation"]


def ranges(spec: list[int]) -> list[int]:
    start, count = spec
    if start < 0 or count < 1:
        raise ValueError("invalid seed range")
    return list(range(start, start + count))


def check_protocol(config: dict, bundle: dict) -> None:
    groups = list(bundle["split_manifest"].values()) + [
        ranges(config["calibration"]),
        [
            seed + k * 100
            for k in range(len(config["scenarios"]))
            for seed in ranges(config["development"])
        ],
    ]
    for profile in config["profiles"].values():
        seeds = []
        for k in range(len(config["scenarios"])):
            seeds += list(
                range(
                    profile["seed_start"] + 100 * k,
                    profile["seed_start"] + 100 * k + profile["episodes"],
                )
            )
        groups.append(seeds)
    all_seeds = [seed for group in groups for seed in group]
    if len(all_seeds) != len(set(all_seeds)):
        raise ValueError("development/calibration/evaluation seed overlap")
    # Published historical ranges, including former full test 3000..3029.
    if any(1000 <= seed < 1012 or 2000 <= seed < 2004 or 3000 <= seed < 3030 for seed in all_seeds):
        raise ValueError("historical seed contamination")


def scheduler_for(policy: str, bundle: dict, calibration: dict, settings: dict):
    if policy.startswith("robust"):
        return RobustPredictiveScheduler(
            residual_scale=calibration["residual_scale"],
            adaptive=policy != "robust_no_adaptation",
            **settings,
            **bundle["policy"],
        )
    return GreedyScheduler(policy, **bundle["policy"])


def develop(config: dict) -> Path:
    started = time.perf_counter()
    model_dir = Path(config["model_dir"])
    if not (model_dir / "bundle.joblib").exists():
        train(config)
    bundle = load_bundle(model_dir / "bundle.joblib")
    check_protocol(config, bundle)
    s = Scenario(**config.get("scenario", {}))
    train_traces = [generate(s, seed) for seed in bundle["training_seeds"]]
    calibration_traces = [generate(s, seed) for seed in ranges(config["calibration"])]
    calibration = calibrate(train_traces, calibration_traces, s, bundle)
    settings = {key: config["robust"][key] for key in ("shift_scale", "smoothing")}
    rows = []
    for k, (name, changes) in enumerate(config["scenarios"].items()):
        scenario = s.changed(**changes)
        for seed in ranges(config["development"]):
            trace = generate(scenario, seed + k * 100)
            learned = forecast(trace, scenario, bundle)
            reliability = inputs(trace, scenario, bundle, calibration)
            for threshold in config["robust"]["thresholds"]:
                metrics = simulate(
                    scenario,
                    trace,
                    scheduler_for(
                        "robust", bundle, calibration, {**settings, "threshold": threshold}
                    ),
                    learned,
                    reliability_inputs=reliability,
                ).metrics
                rows.append({**metrics, "scenario": name, "threshold": threshold})
            reference = simulate(scenario, trace, GreedyScheduler("pf")).metrics
            rows.append({**reference, "scenario": name, "threshold": "pf"})
    table = pd.DataFrame(rows)
    candidates = (
        table[table.threshold != "pf"]
        .groupby("threshold")
        .agg(violation=("control_violation", "mean"), be=("be_goodput_mbps", "mean"))
        .reset_index()
    )
    pf_reference = table[table.threshold == "pf"].be_goodput_mbps.mean()
    candidates["feasible"] = candidates.be >= config["robust"]["be_floor"] * pf_reference
    pool = candidates[candidates.feasible]
    # If the aggregate floor is infeasible, prioritize BE deficit, then violations.
    if pool.empty:
        chosen = candidates.sort_values(
            ["be", "violation", "threshold"], ascending=[False, True, True]
        ).iloc[0]
    else:
        chosen = pool.sort_values(
            ["violation", "be", "threshold"], ascending=[True, False, True]
        ).iloc[0]
    calibration["settings"] = {**settings, "threshold": float(chosen.threshold)}
    calibration["selection_feasible"] = bool(chosen.feasible)
    calibration["development_pf_be_mbps"] = pf_reference
    calibration["config_hash"] = digest(config)
    calibration["environment"] = environment()
    calibration["source_hash"] = source_hash()
    calibration["runtime_seconds"] = time.perf_counter() - started
    atomic_json(model_dir / "reliability.json", calibration)
    atomic_csv(model_dir / "robust_development.csv", table)
    atomic_csv(model_dir / "robust_selection.csv", candidates)
    return model_dir


def freeze(config: dict) -> Path:
    model_dir = Path(config["model_dir"])
    calibration = json.loads((model_dir / "reliability.json").read_text())
    if calibration["config_hash"] != digest(config):
        raise ValueError("configuration differs from completed development")
    env = environment()
    if env["git_dirty"]:
        raise ValueError("freeze requires a clean committed source revision")
    record = {
        "config": config,
        "config_hash": digest(config),
        "source_hash": source_hash(),
        "model_hash": model_hash(model_dir / "bundle.joblib"),
        "calibration_hash": model_hash(model_dir / "reliability.json"),
        "environment": env,
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "policy": load_bundle(model_dir / "bundle.joblib")["policy"],
        "robust_settings": calibration["settings"],
        "statement": "No final seeds executed before this freeze; no tuning after final evaluation.",
    }
    file = model_dir / "freeze.json"
    if file.exists():
        raise ValueError("freeze exists; preserve it and use a new model_dir for a new study")
    atomic_json(file, record)
    return file


def validate_freeze(config: dict) -> dict:
    root = Path(config["model_dir"])
    record = json.loads((root / "freeze.json").read_text())
    actual = {
        "config_hash": digest(config),
        "source_hash": source_hash(),
        "model_hash": model_hash(root / "bundle.joblib"),
        "calibration_hash": model_hash(root / "reliability.json"),
    }
    if any(record[key] != value for key, value in actual.items()):
        raise ValueError("frozen source/config/model/calibration changed; use a new study")
    return record


def comparisons(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.duplicated(["scenario", "policy", "seed"]).any():
        raise ValueError("duplicate episode-policy row")
    rows = []
    for name, group in frame.groupby("scenario"):
        for baseline in ("predictive", "edf", "reactive", "robust_no_adaptation"):
            target = group[group.policy == "robust"].set_index("seed")
            reference = group[group.policy == baseline].set_index("seed")
            if set(target.index) != set(reference.index):
                raise ValueError("unmatched episode sets")
            pair = target.join(reference, lsuffix="_t", rsuffix="_r")
            if not (pair.trace_hash_t == pair.trace_hash_r).all():
                raise ValueError("paired trace mismatch")
            for metric in METRICS:
                differences = (pair[f"{metric}_t"] - pair[f"{metric}_r"]).to_numpy()
                mean, low, high = interval(differences)
                unit = 100 if metric == "control_violation" else 1
                rows.append(
                    {
                        "scenario": name,
                        "reference": baseline,
                        "metric": metric,
                        "n_pairs": int(np.isfinite(differences).sum()),
                        "difference": mean * unit,
                        "ci_low": low * unit,
                        "ci_high": high * unit,
                    }
                )
    return pd.DataFrame(rows)


def evaluate_robust(config: dict, profile: str = "quick") -> Path:
    start = time.perf_counter()
    frozen = validate_freeze(config)
    root = Path(config["model_dir"])
    bundle = load_bundle(root / "bundle.joblib")
    calibration = json.loads((root / "reliability.json").read_text())
    check_protocol(config, bundle)
    opts = config["profiles"][profile]
    definition = {"freeze": frozen, "profile": profile, "policies": V2_POLICIES}
    directory = Path(config["results_dir"]) / (profile + "-" + digest(definition)[:12])
    manifest_path = directory / "manifest.json"
    manifest: dict[str, Any] = {
        **definition,
        "status": "running",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "execution_environment": environment(),
    }
    atomic_json(manifest_path, manifest)
    rows, predictions, conditional = [], [], []
    base = Scenario(**config.get("scenario", {}))
    workers = int(opts["workers"])
    context = ProcessPoolExecutor(max_workers=workers) if workers > 1 else nullcontext(None)
    with context as pool:
        for k, (name, changes) in enumerate(config["scenarios"].items()):
            s = base.changed(**changes)
            seeds = range(
                opts["seed_start"] + k * 100, opts["seed_start"] + k * 100 + opts["episodes"]
            )
            for seed in seeds:
                trace = generate(s, seed)
                begin = time.perf_counter()
                learned = forecast(trace, s, bundle)
                reliability = inputs(trace, s, bundle, calibration)
                inference_us = (time.perf_counter() - begin) / s.slots * 1e6
                persistence = persistence_forecast(trace, s)
                h = calibration["horizon"]
                issue = np.arange(s.history - 1, s.warmup + s.duration - h - s.observation_delay)
                pred = reliability["forecast_db"][issue]
                truth = trace.sinr_db[issue + h]
                observed = trace.observed_db[issue + h + s.observation_delay]
                for model, values in [("learned", pred), ("persistence", trace.observed_db[issue])]:
                    error = values - truth
                    base_mae = np.abs(trace.observed_db[issue] - truth).mean()
                    predictions.append(
                        {
                            "scenario": name,
                            "seed": seed,
                            "model": model,
                            "horizon": h,
                            "mae_db": float(np.abs(error).mean()),
                            "rmse_db": float(np.sqrt((error**2).mean())),
                            "skill": float(1 - np.abs(error).mean() / base_mae),
                            "observable_q90_coverage": float(
                                (
                                    np.abs(values - observed)
                                    <= calibration["observable_error_q90_db"]
                                ).mean()
                            ),
                            "inference_mean_us": inference_us if model == "learned" else 0.0,
                        }
                    )
                futures: dict[str, Future[SimulationResult] | SimulationResult] = {}
                for policy in V2_POLICIES:
                    checkpoint = directory / "episodes" / f"{name}-{seed}-{policy}.json"
                    if checkpoint.exists():
                        continue
                    kwargs: dict[str, Any] = {
                        "forecasts": persistence if policy == "persistence" else learned,
                        "diagnostic_oracle": policy == "oracle",
                        "keep_timeline": policy == "robust",
                        "reliability_inputs": reliability if policy.startswith("robust") else None,
                    }
                    scheduler = scheduler_for(policy, bundle, calibration, calibration["settings"])
                    futures[policy] = (
                        pool.submit(simulate, s, trace, scheduler, **kwargs)
                        if pool
                        else simulate(s, trace, scheduler, **kwargs)
                    )
                for policy in V2_POLICIES:
                    checkpoint = directory / "episodes" / f"{name}-{seed}-{policy}.json"
                    if checkpoint.exists():
                        payload = json.loads(checkpoint.read_text())
                    else:
                        pending = futures[policy]
                        result = pending.result() if isinstance(pending, Future) else pending
                        payload = {
                            "metrics": {**result.metrics, "policy": policy, "scenario": name},
                            "timeline": result.timeline,
                        }
                        atomic_json(checkpoint, payload)
                    if payload["metrics"]["trace_hash"] != trace.digest:
                        raise ValueError("checkpoint trace mismatch")
                    rows.append(payload["metrics"])
                    if policy == "robust":
                        timeline = pd.DataFrame(payload["timeline"])
                        if seed == opts["seed_start"] + k * 100:
                            atomic_csv(directory / f"timeline-{name}.csv", timeline)
                        confidence = timeline.confidence.to_numpy()[issue]
                        for label, mask in [
                            ("low", confidence < 0.25),
                            ("higher", confidence >= 0.25),
                        ]:
                            error = np.abs(pred - truth)[mask]
                            conditional.append(
                                {
                                    "scenario": name,
                                    "seed": seed,
                                    "confidence_group": label,
                                    "samples": int(error.size),
                                    "mae_db": float(error.mean()) if error.size else np.nan,
                                }
                            )
    frame = pd.DataFrame(rows)
    expected = len(config["scenarios"]) * opts["episodes"] * len(V2_POLICIES)
    if len(frame) != expected or frame.duplicated(["scenario", "seed", "policy"]).any():
        raise ValueError("incomplete campaign")
    if not (
        frame.generated_bits == frame.delivered_bits + frame.discarded_bits + frame.unresolved_bits
    ).all():
        raise ValueError("payload conservation")
    if not frame.resource_utilization.between(0, 1).all():
        raise ValueError("resource conservation")
    if not (frame.groupby(["scenario", "seed"]).trace_hash.nunique() == 1).all():
        raise ValueError("unpaired traces")
    atomic_csv(directory / "episode_metrics.csv", frame)
    atomic_csv(directory / "paired_comparisons.csv", comparisons(frame))
    atomic_csv(directory / "prediction_metrics.csv", pd.DataFrame(predictions))
    atomic_csv(directory / "confidence_errors.csv", pd.DataFrame(conditional))
    atomic_json(
        directory / "scenarios.json",
        {n: scenario_dict(base.changed(**c)) for n, c in config["scenarios"].items()},
    )
    manifest.update(
        status="complete",
        episode_policy_runs=len(rows),
        independent_episodes_per_condition=opts["episodes"],
        runtime_seconds=time.perf_counter() - start,
        completed_utc=datetime.now(timezone.utc).isoformat(),
    )
    atomic_json(manifest_path, manifest)
    from pqos.experiments.robust_reporting import report_robust

    try:
        report_robust(directory)
    except Exception:
        manifest["status"] = "report_failed"
        atomic_json(manifest_path, manifest)
        raise
    return directory
