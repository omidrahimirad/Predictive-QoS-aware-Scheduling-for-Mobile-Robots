"""Manifest-validated resumable experiment orchestration."""

import hashlib
import importlib.metadata
import itertools
import json
import platform
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from pqos.config import Scenario, scenario_dict
from pqos.prediction.models import (
    fit_predictors,
    forecast,
    load_bundle,
    model_hash,
    persistence_forecast,
    prediction_metrics,
)
from pqos.schedulers import GreedyScheduler
from pqos.simulator import simulate
from pqos.traces import generate, load_trace, save_trace

SCHEMA = 1
POLICIES = ["rr", "pf", "edf", "reactive", "persistence", "predictive", "oracle"]


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, (np.integer, np.floating)):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(jsonable(value), indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    temp = path.with_suffix(".csv.tmp")
    frame.reindex(sorted(frame.columns), axis=1).to_csv(temp, index=False)
    temp.replace(path)


def digest(value: dict) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def source_hash() -> str:
    """Invalidate checkpoints when implementation changes, including before first commit."""
    root = Path(__file__).resolve().parents[1]
    h = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        h.update(str(path.relative_to(root)).encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def environment() -> dict:
    def git(*args):
        result = subprocess.run(["git", *args], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else ""

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "dependencies": {
            p: importlib.metadata.version(p)
            for p in ["numpy", "pandas", "scikit-learn", "matplotlib", "scipy"]
        },
        "git_commit": git("rev-parse", "HEAD") or "unborn",
        "git_dirty": bool(git("status", "--porcelain")),
    }


def seed_splits(config: dict) -> dict:
    spec = config.get("split", {"train": [1000, 12], "validation": [2000, 4], "test": [3000, 4]})
    splits = {key: list(range(start, start + count)) for key, (start, count) in spec.items()}
    if set(splits) != {"train", "validation", "test"} or not all(splits.values()):
        raise ValueError("require nonempty train/validation/test episode ranges")
    all_seeds = [seed for seeds in splits.values() for seed in seeds]
    if len(set(all_seeds)) != len(all_seeds):
        raise ValueError("split seeds overlap")
    return splits


def generate_dataset(config: dict) -> Path:
    scenario = Scenario(**config.get("scenario", {}))
    directory = Path(config.get("data_dir", "data/training"))
    splits = seed_splits(config)
    manifest = {"schema": SCHEMA, "scenario": scenario_dict(scenario), "splits": splits}
    path = directory / "manifest.json"
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError("existing dataset configuration differs; choose another data_dir")
    for name, seeds in splits.items():
        for seed in seeds:
            file = directory / name / f"{seed}.npz"
            if file.exists():
                trace, loaded = load_trace(file)
                if loaded != scenario or trace.seed != seed:
                    raise ValueError("existing trace incompatible")
            else:
                save_trace(file, generate(scenario, seed), scenario)
    atomic_json(path, manifest)
    return directory


def train(config: dict) -> Path:
    started = time.perf_counter()
    directory = generate_dataset(config)
    scenario = Scenario(**config.get("scenario", {}))
    splits = seed_splits(config)
    traces = {
        name: [load_trace(directory / name / f"{seed}.npz")[0] for seed in seeds]
        for name, seeds in splits.items()
        if name != "test"
    }
    bundle, errors = fit_predictors(traces["train"], traces["validation"], scenario)
    model_dir = Path(config.get("model_dir", "models/default"))
    model_dir.mkdir(parents=True, exist_ok=True)
    if (model_dir / "bundle.joblib").exists():
        raise ValueError("model exists; use another model_dir instead of overwriting")
    cached_forecasts = [forecast(t, scenario, bundle) for t in traces["validation"]]
    candidates = config.get("selection", {}).get("urgencies", [2.0, 4.0])
    horizons = config.get("selection", {}).get("horizons", [4, 16])
    floors = config.get("selection", {}).get("floors", [0.8, 0.9, 1.0])
    primary_floor = config.get("selection", {}).get("primary_floor", 0.9)
    reference = np.mean(
        [
            simulate(scenario, t, GreedyScheduler("pf")).metrics["be_goodput_mbps"]
            for t in traces["validation"]
        ]
    )
    rows = []
    for urgency, horizon in itertools.product(candidates, horizons):
        result = [
            simulate(
                scenario, t, GreedyScheduler("predictive", urgency=urgency, horizon=horizon), f
            ).metrics
            for t, f in zip(traces["validation"], cached_forecasts)
        ]
        rows.append(
            {
                "urgency": urgency,
                "horizon": horizon,
                "violation": np.mean([m["control_violation"] for m in result]),
                "be_goodput_mbps": np.mean([m["be_goodput_mbps"] for m in result]),
                "pf_be_goodput_mbps": reference,
            }
        )
    table = pd.DataFrame(rows)
    selection = {}
    for floor in sorted(set(floors + [primary_floor])):
        feasible = table[table.be_goodput_mbps >= floor * reference]
        pool = feasible if not feasible.empty else table
        # Predeclared tie: lower violation, then higher BE, then lower urgency/horizon.
        chosen = pool.sort_values(
            ["violation", "be_goodput_mbps", "urgency", "horizon"],
            ascending=[True, False, True, True],
        ).iloc[0]
        selection[str(floor)] = {
            "feasible": not feasible.empty,
            "urgency": float(chosen.urgency),
            "horizon": int(chosen.horizon),
        }
    chosen = selection[str(primary_floor)]
    bundle["policy"] = {
        "urgency": chosen["urgency"],
        "horizon": chosen["horizon"],
        "opportunity": 1.0,
    }
    bundle["scenario"] = scenario_dict(scenario)
    bundle["selection"] = selection
    bundle["split_manifest"] = splits
    joblib.dump(bundle, model_dir / "bundle.joblib")
    atomic_csv(model_dir / "validation_prediction_metrics.csv", errors)
    atomic_csv(model_dir / "validation_selection.csv", table)
    atomic_json(
        model_dir / "selected_models.json",
        {
            "selected": bundle["selected"],
            "policy": bundle["policy"],
            "floor_sensitivity": selection,
            "split_manifest": splits,
            "schema": SCHEMA,
            "model_hash": model_hash(model_dir / "bundle.joblib"),
            "runtime_seconds": time.perf_counter() - started,
            "environment": environment(),
        },
    )
    return model_dir


def evaluate(
    config: dict, profile: str = "quick", ablation: bool = False, demo: bool = False
) -> Path:
    started = time.perf_counter()
    base = Scenario(**config.get("scenario", {}))
    path = Path(config.get("model_dir", "models/default")) / "bundle.joblib"
    bundle = load_bundle(path)
    split = bundle["split_manifest"]
    opts = config.get("profiles", {}).get(profile, {})
    reps = int(opts.get("episodes", 3 if profile == "quick" else 30))
    seed_start = int(opts.get("seed_start", 3000))
    seeds = list(range(seed_start, seed_start + reps))
    if set(seeds) & set(split["train"] + split["validation"]):
        raise ValueError("evaluation seeds overlap fitting episodes")
    grid = opts.get(
        "grid", config.get("grid", {"load": [0.5, 1.5, 3.0], "speed": [1.0], "blockage_db": [22.0]})
    )
    if demo:
        reps, seeds, grid = 1, [seed_start], {"load": [base.load]}
    scenarios = [
        (f"id-{k}", base.changed(**dict(zip(grid, values))))
        for k, values in enumerate(itertools.product(*grid.values()))
    ]
    if not demo:
        scenarios.append(
            ("ood-layout-speed", base.changed(layout=1, speed=6.0, load=2.5, blockage_db=28))
        )
    policies = ["predictive"] if demo else POLICIES.copy()
    if ablation:
        policies += ["no_position", "horizon_1", "horizon_4", "horizon_8", "horizon_16"]
        scenarios += [
            ("delay-8", base.changed(observation_delay=8)),
            ("noise-4", base.changed(observation_noise_db=4)),
            ("smooth", base.changed(surprise_rate=0)),
            ("surprise", base.changed(surprise_rate=0.004)),
        ]
    definition = {
        "schema": SCHEMA,
        "source_hash": source_hash(),
        "config": config,
        "profile": profile,
        "ablation": ablation,
        "demo": demo,
        "model_hash": model_hash(path),
        "seeds": seeds,
        "scenarios": {name: scenario_dict(s) for name, s in scenarios},
        "policies": policies,
    }
    run_id = (
        ("demo" if demo else "ablation" if ablation else "evaluation")
        + "-"
        + digest(definition)[:12]
    )
    directory = Path(config.get("results_dir", "results")) / run_id
    manifest_path = directory / "manifest.json"
    definition["definition_hash"] = digest(definition)
    if manifest_path.exists():
        prior = json.loads(manifest_path.read_text())
        if prior["definition_hash"] != definition["definition_hash"]:
            raise ValueError("run configuration changed")
        manifest = prior
    else:
        manifest = {
            **definition,
            "status": "running",
            "environment": environment(),
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "units": {"latency": "ms", "goodput": "Mbit/s", "time": "slots"},
            "policy": bundle["policy"],
            "selected_predictor": bundle["selected"],
            "split_manifest": split,
        }
        atomic_json(manifest_path, manifest)
    workers = int(opts.get("workers", 4 if profile == "full" else 1))
    if workers < 1:
        raise ValueError("workers must be positive")
    rows = []
    delays = []
    forecast_errors = []
    with ProcessPoolExecutor(max_workers=workers) if workers > 1 else nullcontext(None) as pool:
        for scenario_name, scenario in scenarios:
            traces = [generate(scenario, seed) for seed in seeds]
            forecast_errors.append(
                prediction_metrics(traces, scenario, bundle, "test").assign(scenario=scenario_name)
            )
            for trace in traces:
                learned = forecast(trace, scenario, bundle)
                persistence = persistence_forecast(trace, scenario)
                no_position = (
                    forecast(trace, scenario, bundle, bundle["selected"] + "_no_position")
                    if "no_position" in policies
                    else None
                )
                policy_inputs = {}
                futures = {}
                for policy in policies:
                    kind = policy
                    settings = bundle["policy"].copy()
                    f = persistence if policy == "persistence" else learned
                    if policy == "no_position":
                        kind, f = "predictive", no_position
                    elif policy.startswith("horizon_"):
                        settings["horizon"] = int(policy.split("_")[1])
                        kind = "predictive"
                    scheduler = GreedyScheduler(kind, **settings)
                    kwargs = {
                        "forecasts": f if kind in {"predictive", "persistence"} else None,
                        "diagnostic_oracle": kind == "oracle",
                        "keep_timeline": demo,
                    }
                    policy_inputs[policy] = (scheduler, kwargs)
                    checkpoint = (
                        directory / "episodes" / f"{scenario_name}-{trace.seed}-{policy}.json"
                    )
                    if pool is not None and not checkpoint.exists():
                        futures[policy] = pool.submit(
                            simulate, scenario, trace, scheduler, **kwargs
                        )
                for policy in policies:
                    checkpoint = (
                        directory / "episodes" / f"{scenario_name}-{trace.seed}-{policy}.json"
                    )
                    if checkpoint.exists():
                        payload = json.loads(checkpoint.read_text())
                        if payload["metrics"]["trace_hash"] != trace.digest:
                            raise ValueError("cached trace hash mismatch")
                    else:
                        scheduler, kwargs = policy_inputs[policy]
                        result = (
                            futures[policy].result()
                            if pool is not None
                            else simulate(scenario, trace, scheduler, **kwargs)
                        )
                        metrics = {
                            **result.metrics,
                            "policy": policy,
                            "scenario": scenario_name,
                            "domain": "ood" if scenario_name.startswith("ood") else "id",
                            "load": scenario.load,
                            "speed": scenario.speed,
                            "blockage_db": scenario.blockage_db,
                        }
                        latency = [
                            (p.completion - p.arrival) * scenario.slot_seconds * 1000
                            for p in result.packets
                            if p.traffic == "control"
                            and scenario.warmup <= p.arrival < scenario.warmup + scenario.duration
                            and p.completion is not None
                        ]
                        payload = {"metrics": metrics, "delivered_control_latency_ms": latency}
                        atomic_json(checkpoint, payload)
                        if demo:
                            atomic_csv(directory / "timeline.csv", pd.DataFrame(result.timeline))
                    rows.append(payload["metrics"])
                    delays += [
                        {"scenario": scenario_name, "policy": policy, "latency_ms": d}
                        for d in payload["delivered_control_latency_ms"]
                    ]
    atomic_csv(directory / "episode_metrics.csv", pd.DataFrame(rows))
    atomic_csv(directory / "prediction_metrics.csv", pd.concat(forecast_errors, ignore_index=True))
    atomic_csv(
        directory / "delivered_latency.csv",
        pd.DataFrame(delays, columns=["scenario", "policy", "latency_ms"]),
    )
    atomic_json(
        directory / "selected_models.json",
        json.loads((path.parent / "selected_models.json").read_text()),
    )
    manifest.update(
        status="complete",
        completed_utc=datetime.now(timezone.utc).isoformat(),
        runtime_seconds=time.perf_counter() - started,
        episodes=len(rows),
    )
    atomic_json(manifest_path, manifest)
    from pqos.experiments.reporting import report

    try:
        report(directory)
    except Exception:
        manifest["status"] = "report_failed"
        atomic_json(manifest_path, manifest)
        raise
    return directory
