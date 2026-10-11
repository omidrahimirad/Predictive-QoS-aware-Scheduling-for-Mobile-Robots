import json
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from pqos.config import Scenario, load_config
from pqos.entities import ControlDemand, Observation
from pqos.experiments.robust import (
    check_protocol,
    comparisons,
    develop,
    evaluate_robust,
    validate_freeze,
)
from pqos.experiments.runner import atomic_json, digest, model_hash, source_hash
from pqos.prediction.models import fit_predictors, persistence_forecast
from pqos.prediction.reliability import calibrate, inputs
from pqos.schedulers import GreedyScheduler
from pqos.schedulers.robust import RobustPredictiveScheduler
from pqos.simulator import simulate
from pqos.traces import generate, stream


def observation(slot=0, measurement=0, observed=(0.0, 0.0), shift=(0.0, 0.0)):
    return Observation(
        slot,
        1,
        (100.0, 100.0),
        (1.0, 1.0),
        (1000, 1000),
        ((ControlDemand(100, 4),), (ControlDemand(100, 1),)),
        (100.0, 100.0),
        ((1.0,) * 16, (100.0,) * 16),
        observed_db=observed,
        measurement_slot=measurement,
        forecast_db=(0.0, 0.0),
        feature_shift=shift,
    )


def scheduler(**kw):
    return RobustPredictiveScheduler(1.0, **kw)


def test_low_risk_uses_exact_predictive_priority():
    o = observation()
    s = scheduler()
    assert s.allocate(o) == GreedyScheduler("predictive", urgency=2, horizon=4).allocate(o)
    assert s.fallbacks == 0
    assert s.confidence == 0.5


def test_shift_switches_to_exact_edf():
    o = observation(shift=(1.0, 0.0))
    s = scheduler()
    assert s.allocate(o) == GreedyScheduler("edf").allocate(o)
    assert s.fallbacks == 1
    assert s.confidence < 0.1


@pytest.mark.parametrize(
    "field,value",
    [
        ("forecast", None),
        ("forecast", ((float("nan"),) * 16,) * 2),
        ("forecast_db", (float("inf"), 0)),
        ("feature_shift", ()),
        ("feature_shift", (float("nan"), 0)),
        ("observed_db", ()),
        ("forecast_age", 100),
        ("forecast", ((1.0,),) * 2),
    ],
)
def test_invalid_forecast_conservative_fallback(field, value):
    o = replace(observation(), **{field: value})
    s = scheduler()
    assert s.allocate(o) == GreedyScheduler("edf").allocate(o)
    assert s.fallbacks == 1


def test_delayed_residual_update_and_no_duplicate_measurement():
    s = scheduler(smoothing=1.0)
    for t in range(6):
        s.allocate(observation(slot=t, measurement=max(t - 2, 0)))
    assert s.residual_updates == 0
    s.allocate(observation(slot=6, measurement=4, observed=(10.0, 10.0)))
    assert s.residual_updates == 1
    assert s.residuals == [10.0, 10.0]
    assert s.used_fallback
    s.allocate(observation(slot=7, measurement=4, observed=(999.0, 999.0)))
    assert s.residual_updates == 1 and s.residuals == [10.0, 10.0]
    assert len(s.pending) <= s.horizon + 3


def test_no_adaptation_disables_risk_gate_but_keeps_invalid_fallback():
    s = scheduler(adaptive=False)
    assert s.allocate(observation(shift=(10.0, 10.0))) == GreedyScheduler(
        "predictive", urgency=2, horizon=4
    ).allocate(observation())
    assert not s.used_fallback
    s.allocate(replace(observation(slot=1), forecast=None))
    assert s.used_fallback


def test_future_measurement_rejected_before_residual_monitoring():
    s = scheduler()
    s.allocate(observation())
    with pytest.raises(ValueError, match="future measurement"):
        s.allocate(observation(slot=1, measurement=4, observed=(999.0, 999.0)))
    assert s.residual_updates == 0


def test_threshold_boundary_and_reset():
    s = scheduler(threshold=2.5)
    s.allocate(observation(shift=(0.25, 0)))
    assert not s.used_fallback
    s.allocate(observation(slot=1, shift=(0.251, 0)))
    assert s.used_fallback
    s.reset()
    assert not s.pending and s.fallbacks == 0
    s.allocate(observation())


def test_calibration_inputs_prefix_causality_and_shift():
    s = Scenario(duration=70, warmup=10, n_ues=2)
    training = [generate(s, 11000), generate(s, 11001)]
    validation = [generate(s, 12000)]
    bundle, _ = fit_predictors(training, validation, s)
    bundle["policy"] = {"horizon": 4, "urgency": 2, "opportunity": 1}
    calibration = calibrate(training, [generate(s, 13000)], s, bundle)
    trace = generate(s, 800000)
    before = inputs(trace, s, bundle, calibration)
    trace.sinr_db[:] = 10000
    trace.observed_db[40:] += 1000
    trace.position[40:] += 1000
    trace.velocity[40:] += 1000
    after = inputs(trace, s, bundle, calibration)
    for key in before:
        np.testing.assert_equal(before[key][:40], after[key][:40])
    assert after["feature_shift"][40:].max() > 10
    with pytest.raises(ValueError):
        calibrate(training, training, s, bundle)


def test_robust_future_trace_mutation_decisions_and_repeatability():
    s = Scenario(duration=50, warmup=10, n_ues=2, resources=3)
    traces = [generate(s, 800000), generate(s, 800000)]
    traces[1].observed_db[30:] -= 100
    traces[1].sinr_db[30:] -= 100
    traces[1].service[30:] = 0
    decisions = []
    for trace in traces:
        f = persistence_forecast(trace, s)
        r = {
            "forecast_db": trace.observed_db.copy(),
            "feature_shift": np.zeros_like(trace.observed_db),
        }
        result = simulate(s, trace, scheduler(), f, keep_timeline=True, reliability_inputs=r)
        decisions.append([row["allocated_units"] for row in result.timeline[:30]])
        m = result.metrics
        assert (
            m["generated_bits"] == m["delivered_bits"] + m["discarded_bits"] + m["unresolved_bits"]
        )
    assert decisions[0] == decisions[1]


def test_persistence_reactive_equivalence_entire_episode():
    s = Scenario(duration=70, warmup=10, n_ues=3, resources=4)
    t = generate(s, 810000)
    a = simulate(s, t, GreedyScheduler("reactive"), keep_timeline=True)
    b = simulate(
        s, t, GreedyScheduler("persistence"), persistence_forecast(t, s), keep_timeline=True
    )
    assert [r["allocated_units"] for r in a.timeline] == [r["allocated_units"] for r in b.timeline]
    for key in a.metrics:
        if not key.startswith("scheduler_"):
            assert a.metrics[key] == b.metrics[key] or (
                isinstance(a.metrics[key], float)
                and np.isnan(a.metrics[key])
                and np.isnan(b.metrics[key])
            )


def test_rng_streams_isolated():
    a = stream(900000, 4).random(5)
    stream(900000, 2).random(1000)
    np.testing.assert_array_equal(a, stream(900000, 4).random(5))


def test_v2_paired_statistics_reject_duplicates_and_unmatched():
    rows = [
        {
            "scenario": "A",
            "seed": seed,
            "policy": policy,
            "trace_hash": str(seed),
            "control_violation": 0.1 if policy == "robust" else 0.2,
            "be_goodput_mbps": 1,
            "jain_fairness": 1,
            "latency_p99_ms": 1,
        }
        for seed in range(3)
        for policy in ["robust", "edf", "predictive", "reactive", "robust_no_adaptation"]
    ]
    f = pd.DataFrame(rows)
    result = comparisons(f)
    np.testing.assert_allclose(result[result.metric == "control_violation"].difference, -10)
    assert (result.n_pairs == 3).all()
    with pytest.raises(ValueError, match="duplicate"):
        comparisons(pd.concat([f, f.iloc[:1]]))
    with pytest.raises(ValueError, match="unmatched"):
        comparisons(f.iloc[1:])
    f.loc[0, "trace_hash"] = "bad"
    with pytest.raises(ValueError, match="trace"):
        comparisons(f)


def test_protocol_disjoint_final_seeds():
    config = load_config("configs/robust_v2.yaml")
    bundle = {
        "split_manifest": {
            name: list(range(start, start + count))
            for name, (start, count) in config["split"].items()
        }
    }
    check_protocol(config, bundle)
    config["profiles"]["full"]["seed_start"] = 14000
    with pytest.raises(ValueError, match="overlap"):
        check_protocol(config, bundle)


def test_v2_develop_evaluate_report_resume_and_freeze(tmp_path):
    config = load_config("configs/robust_v2.yaml")
    config.update(
        data_dir=str(tmp_path / "data"),
        model_dir=str(tmp_path / "models"),
        results_dir=str(tmp_path / "results"),
    )
    config["scenario"].update(n_ues=2, resources=2, duration=40, warmup=8)
    config["split"] = {"train": [11000, 2], "validation": [12000, 1], "test": [15000, 1]}
    config["calibration"] = [13000, 1]
    config["development"] = [14000, 1]
    config["selection"].update(urgencies=[2.0], horizons=[4])
    config["robust"]["thresholds"] = [2.5]
    config["profiles"]["quick"].update(episodes=1, workers=1)
    root = develop(config)
    # Integration fixture creates a valid source/model/config freeze; production CLI
    # separately requires committed clean Git state (tested below).
    atomic_json(
        root / "freeze.json",
        {
            "config": config,
            "config_hash": digest(config),
            "source_hash": source_hash(),
            "model_hash": model_hash(root / "bundle.joblib"),
            "calibration_hash": model_hash(root / "reliability.json"),
            "environment": {"git_commit": "test-fixture"},
            "robust_settings": json.loads((root / "reliability.json").read_text())["settings"],
        },
    )
    directory = evaluate_robust(config)
    m = json.loads((directory / "manifest.json").read_text())
    assert m["status"] == "complete" and m["episode_policy_runs"] == 72
    before = (directory / "episode_metrics.csv").read_bytes()
    assert evaluate_robust(config) == directory
    assert before == (directory / "episode_metrics.csv").read_bytes()
    assert len(list((directory / "figures").glob("*.png"))) == 6
    assert len(list((directory / "figures").glob("*.svg"))) == 6
    assert (directory / "REPORT.md").exists()
    config["robust"]["smoothing"] += 0.01
    with pytest.raises(ValueError, match="frozen"):
        validate_freeze(config)


def test_freeze_rejects_dirty_repository(tmp_path, monkeypatch):
    from pqos.experiments.robust import freeze

    config = {"model_dir": str(tmp_path)}
    atomic_json(tmp_path / "reliability.json", {"config_hash": digest(config)})
    monkeypatch.setattr("pqos.experiments.robust.environment", lambda: {"git_dirty": True})
    with pytest.raises(ValueError, match="clean"):
        freeze(config)
