from dataclasses import replace

import numpy as np
import pytest

from pqos.config import Scenario, load_config
from pqos.entities import Allocation, ControlDemand, Observation
from pqos.experiments.runner import seed_splits
from pqos.experiments.statistics import interval, paired_comparisons
from pqos.prediction.models import features, fit_predictors, forecast, prediction_metrics
from pqos.schedulers import GreedyScheduler
from pqos.simulator import simulate
from pqos.traces import capacity, generate, load_trace, save_trace, success_probability


def tiny(**changes):
    return Scenario(
        n_ues=1,
        resources=1,
        warmup=0,
        duration=10,
        drain=20,
        control_bits=1000,
        control_period=1000,
        deadline=20,
        be_rate=0,
        error_free=True,
        feedback_delay=0,
        **changes,
    )


def controlled(s, bits=300, arrivals=True, successful=True):
    trace = generate(s, 10)
    arrivals_array = np.zeros_like(trace.arrivals)
    if arrivals:
        arrivals_array[0, 0, 0] = 1
    return replace(
        trace,
        arrivals=arrivals_array,
        service=np.full_like(trace.service, bits),
        observed_db=np.full_like(trace.observed_db, 20),
        uniforms=np.zeros_like(trace.uniforms) if successful else np.ones_like(trace.uniforms),
    )


def obs(resources=1, eligible=(1000, 1000), controls=((), ()), forecast=None):
    return Observation(
        0, resources, (100.0, 100.0), (1.0, 1.0), eligible, controls, (100.0, 100.0), forecast
    )


@pytest.mark.parametrize(
    "key,value",
    [
        ("duration", 0),
        ("resources", -1),
        ("observation_delay", -2),
        ("load", float("nan")),
        ("surprise_rate", 2),
        ("overhead_efficiency", 1.2),
    ],
)
def test_invalid_config(key, value):
    with pytest.raises(ValueError):
        Scenario(**{key: value})


def test_unknown_config(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("scenario:\n  resorces: 4\n")
    with pytest.raises(ValueError):
        load_config(path)


def test_capacity_and_probabilities():
    s = Scenario()
    assert capacity(np.array([0.0]), s)[0] == np.floor(
        s.bandwidth_hz * s.slot_seconds * s.overhead_efficiency
    )
    assert success_probability(np.array([0.0]))[0] == 0.5
    assert success_probability(np.array([-99.0]), True)[0] == 1


def test_analytical_partial_service():
    s = tiny()
    result = simulate(s, controlled(s), GreedyScheduler("rr"))
    assert result.packets[0].completion == 4
    assert result.metrics["delivered_bits"] == 1000
    assert result.metrics["latency_p99_ms"] == 2.0


@pytest.mark.parametrize("bits,reason", [(1000, "delivered"), (999, "deadline"), (0, "deadline")])
def test_exact_deadline(bits, reason):
    s = replace(tiny(), deadline=1)
    result = simulate(s, controlled(s, bits), GreedyScheduler("rr"))
    assert result.packets[0].reason == reason
    assert result.metrics["control_violation"] == int(reason != "delivered")


def test_retry_exhaustion_and_no_goodput():
    s = replace(tiny(), error_free=False, feedback_delay=2)
    result = simulate(s, controlled(s, bits=1000, successful=False), GreedyScheduler("rr"))
    assert result.packets[0].reason == "retry_exhausted"
    assert result.metrics["chunk_attempts"] == 3
    assert result.metrics["delivered_bits"] == 0


def test_expiration_no_resurrection():
    s = replace(tiny(), error_free=False, deadline=1, feedback_delay=3)
    result = simulate(s, controlled(s, bits=1000, successful=False), GreedyScheduler("rr"))
    assert result.packets[0].reason == "deadline"
    assert result.metrics["chunk_attempts"] == 1


def test_inflight_does_not_duplicate():
    s = replace(tiny(), feedback_delay=8)
    result = simulate(s, controlled(s, bits=500), GreedyScheduler("rr"))
    assert result.packets[0].completion == 2
    assert result.metrics["chunk_attempts"] == 2
    assert result.metrics["delivered_bits"] == 1000


def test_pf_average_waits_for_feedback():
    s = replace(tiny(), feedback_delay=3)
    seen = []

    class Recorder(GreedyScheduler):
        def allocate(self, observation):
            seen.append(observation.average_rate[0])
            return super().allocate(observation)

    simulate(s, controlled(s, bits=1000), Recorder("pf"))
    assert seen[1] == pytest.approx(0.99**2)
    assert seen[3] == pytest.approx(0.99**4)
    assert seen[4] == pytest.approx(0.99**5 + 10)


def test_empty_metrics():
    s = tiny()
    result = simulate(s, controlled(s, arrivals=False), GreedyScheduler("rr"))
    assert np.isnan(result.metrics["control_violation"])
    assert np.isnan(result.metrics["jain_fairness"])
    assert np.isnan(result.metrics["latency_p99_ms"])


def test_buffer_overflow():
    s = replace(tiny(), buffer_bits=999)
    result = simulate(s, controlled(s), GreedyScheduler("rr"))
    assert result.packets[0].reason == "overflow"
    assert result.metrics["control_overflow"] == 1


def test_future_arrival_not_served():
    s = tiny()
    trace = controlled(s, arrivals=False)
    trace.arrivals[5, 0, 0] = 1
    result = simulate(s, trace, GreedyScheduler("rr"), keep_timeline=True)
    assert all(r["allocated_units"] == 0 for r in result.timeline[:5])
    assert result.packets[0].completion == 9


def test_be_censoring():
    s = tiny()
    trace = controlled(s, bits=0, arrivals=False)
    trace.arrivals[0, 0, 1] = 1
    result = simulate(s, trace, GreedyScheduler("rr"))
    assert result.metrics["be_censored_packets"] == 1
    assert result.metrics["unresolved_bits"] == s.be_bits


def test_measurement_window_excludes_drain_goodput():
    s = replace(tiny(), duration=1)
    result = simulate(s, controlled(s, bits=500), GreedyScheduler("rr"))
    assert result.metrics["delivered_bits"] == 1000
    assert result.metrics["total_goodput_mbps"] == 1.0  # 500 bits / 0.5 ms


@pytest.mark.parametrize(
    "kind", ["rr", "pf", "edf", "reactive", "predictive", "persistence", "oracle"]
)
def test_policy_conservation_and_exogenous_repeatability(kind):
    s = Scenario(n_ues=3, resources=3, duration=80, warmup=10)
    trace = generate(s, 3001)
    original_hash = trace.digest
    first = simulate(s, trace, GreedyScheduler(kind)).metrics
    second = simulate(s, generate(s, 3001), GreedyScheduler(kind)).metrics
    for metric in first:
        if metric.startswith("scheduler_"):
            continue
        assert first[metric] == second[metric] or (
            isinstance(first[metric], float)
            and np.isnan(first[metric])
            and np.isnan(second[metric])
        )
    assert trace.digest == original_hash
    assert (
        first["generated_bits"]
        == first["delivered_bits"] + first["discarded_bits"] + first["unresolved_bits"]
    )


def test_allocation_validation():
    with pytest.raises(ValueError):
        Allocation((2, 0)).validate(obs())
    with pytest.raises(ValueError):
        Allocation((0, 1)).validate(obs(eligible=(100, 0)))
    with pytest.raises(ValueError):
        Allocation((-1, 0)).validate(obs())


def test_round_robin_rotation():
    scheduler = GreedyScheduler("rr")
    assert scheduler.allocate(obs()).counts == (1, 0)
    assert scheduler.allocate(obs()).counts == (0, 1)
    assert GreedyScheduler("rr").allocate(obs(resources=2)).counts == (1, 1)


def test_pf_and_edf_choice():
    observation = replace(obs(), average_rate=(200, 100))
    assert GreedyScheduler("pf").allocate(observation).counts == (0, 1)
    observation = obs(controls=((ControlDemand(100, 2),), (ControlDemand(100, 1),)))
    assert GreedyScheduler("edf").allocate(observation).counts == (0, 1)


def test_reactive_hand_calculation_and_persistence_equivalence():
    # Normalized PF=1 for both. Urgency ratios: 100/(2*100)=.5 and 100/(1*100)=1.
    # With urgency weight 4: total scores 3 and 5, so UE 1 wins.
    observation = obs(
        controls=((ControlDemand(100, 2),), (ControlDemand(100, 1),)),
        forecast=((100.0,) * 16, (100.0,) * 16),
    )
    reactive = GreedyScheduler("reactive").allocate(observation)
    assert reactive.counts == (0, 1)
    assert GreedyScheduler("predictive").allocate(observation) == reactive


def test_prediction_opportunity_choice():
    observation = obs(
        controls=((ControlDemand(100, 4),), (ControlDemand(100, 4),)),
        forecast=((100.0,) * 16, (1.0,) * 16),
    )
    assert GreedyScheduler("reactive").allocate(observation).counts == (1, 0)
    assert GreedyScheduler("predictive").allocate(observation).counts == (0, 1)


@pytest.mark.parametrize(
    "forecast_value,age",
    [(None, 0), (((float("nan"),) * 16,) * 2, 0), (((100.0,) * 16,) * 2, 10), (((1.0,),) * 2, 0)],
)
def test_forecast_fallback(forecast_value, age):
    observation = replace(obs(forecast=forecast_value), forecast_age=age)
    scheduler = GreedyScheduler("predictive")
    assert scheduler.allocate(observation) == GreedyScheduler("reactive").allocate(observation)
    assert scheduler.fallbacks == 1


def test_feature_prefix_causality():
    s = Scenario(duration=80, n_ues=2)
    trace = generate(s, 1000)
    before = features(trace, s)
    # Mutating all future inputs must not change any prefix feature.
    trace.observed_db[50:] += 1000
    trace.position[50:] += 1000
    trace.velocity[50:] += 1000
    trace.sinr_db[:] += 1000  # true SINR is never a feature
    after = features(trace, s)
    np.testing.assert_array_equal(before[:50], after[:50])


def test_future_trace_mutation_cannot_change_earlier_decisions():
    from pqos.prediction.models import persistence_forecast

    s = Scenario(duration=60, warmup=10, n_ues=2, resources=3)
    first = generate(s, 3000)
    second = generate(s, 3000)
    cutoff = 30
    second.sinr_db[cutoff:] = -1000
    second.service[cutoff:] = 0
    second.observed_db[cutoff:] = -1000
    second.arrivals[cutoff:] = 0
    decisions = []

    class Recorder(GreedyScheduler):
        def allocate(self, observation):
            allocation = super().allocate(observation)
            decisions.append(allocation.counts)
            return allocation

    simulate(s, first, Recorder("predictive"), persistence_forecast(first, s))
    prefix = decisions[:cutoff].copy()
    decisions.clear()
    simulate(s, second, Recorder("predictive"), persistence_forecast(second, s))
    assert prefix == decisions[:cutoff]


def test_trace_serialization_and_split_overlap(tmp_path):
    s = Scenario(duration=80, n_ues=2)
    trace = generate(s, 1000)
    file = tmp_path / "trace.npz"
    save_trace(file, trace, s)
    loaded, scenario = load_trace(file)
    assert scenario == s and loaded.digest == trace.digest
    with pytest.raises(ValueError):
        seed_splits({"split": {"train": [1, 2], "validation": [2, 1], "test": [9, 1]}})


def test_prediction_split_guards_and_shapes():
    s = Scenario(duration=80, n_ues=2, warmup=10)
    train = [generate(s, 1000), generate(s, 1001)]
    val = [generate(s, 2000)]
    with pytest.raises(ValueError):
        fit_predictors(train, train, s)
    bundle, table = fit_predictors(train, val, s)
    assert len(table) == 20
    output = forecast(generate(s, 3000), s, bundle)
    assert output.shape == (s.slots, s.n_ues, 16)
    assert np.isfinite(output).all()
    # Scaler's mean exactly equals training-only features, no validation refitting.
    from pqos.prediction.models import dataset

    x, _, _, _ = dataset(train, s)
    np.testing.assert_allclose(bundle["ridge"]["estimator"][0].mean_, x.mean(axis=0))
    with pytest.raises(ValueError):
        prediction_metrics(val, s, bundle, "test")
    with pytest.raises(ValueError):
        forecast(train[0], replace(s, history=4), bundle)


def test_bootstrap_episode_difference():
    mean, low, high = interval(np.array([1, 1, 1]))
    assert (mean, low, high) == (1, 1, 1)
    import pandas as pd

    frame = pd.DataFrame(
        [
            {
                "scenario": "a",
                "policy": p,
                "seed": seed,
                "trace_hash": str(seed),
                "control_violation": value,
                "be_goodput_mbps": 1,
                "jain_fairness": 1,
                "latency_p99_ms": 1,
            }
            for seed in range(3)
            for p, value in [("predictive", 0.1), ("reactive", 0.2)]
        ]
    )
    table = paired_comparisons(frame)
    assert table.iloc[0].difference == pytest.approx(-10)
    frame.loc[0, "trace_hash"] = "bad"
    with pytest.raises(ValueError):
        paired_comparisons(frame)
