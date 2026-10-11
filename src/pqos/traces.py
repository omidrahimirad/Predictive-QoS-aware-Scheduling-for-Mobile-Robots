"""Exogenous traces, unaffected by queue or allocation decisions."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from pqos.config import Scenario, scenario_dict


def stream(seed: int, name: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([seed, name]))


def capacity(sinr_db: np.ndarray, s: Scenario) -> np.ndarray:
    linear = 10.0 ** (np.asarray(sinr_db) / 10.0)
    return np.floor(
        s.bandwidth_hz
        * s.slot_seconds
        * s.overhead_efficiency
        * np.minimum(s.eta_max, np.log2(1.0 + linear))
    )


def success_probability(sinr_db: np.ndarray, error_free: bool = False) -> np.ndarray:
    if error_free:
        return np.ones_like(sinr_db, dtype=float)
    # Synthetic sigmoid, NOT measured link-level BLER or adaptive MCS.
    return 1.0 / (1.0 + np.exp(-np.clip((sinr_db - 0.0) / 2.5, -40, 40)))


@dataclass(frozen=True)
class Trace:
    seed: int
    position: np.ndarray
    velocity: np.ndarray
    sinr_db: np.ndarray
    observed_db: np.ndarray
    service: np.ndarray
    uniforms: np.ndarray
    arrivals: np.ndarray  # [slot, UE, class], class 0 control, 1 best effort counts
    blocked: np.ndarray

    @property
    def digest(self) -> str:
        h = hashlib.sha256()
        for key in (
            "position",
            "velocity",
            "sinr_db",
            "observed_db",
            "service",
            "uniforms",
            "arrivals",
            "blocked",
        ):
            h.update(key.encode())
            h.update(np.ascontiguousarray(getattr(self, key)).tobytes())
        return h.hexdigest()


def generate(s: Scenario, seed: int) -> Trace:
    n, length = s.n_ues, s.slots
    move = stream(seed, 1)
    pos = np.empty((length, n, 2))
    vel = np.empty_like(pos)
    pos[0] = move.uniform(12, 28, (n, 2))
    angle = move.uniform(-np.pi, np.pi, n)
    v = np.column_stack((np.cos(angle), np.sin(angle))) * s.speed
    vel[0] = v
    for t in range(1, length):
        if t % 400 == 0:
            angle += move.normal(0, 0.3, n)
            v = np.column_stack((np.cos(angle), np.sin(angle))) * s.speed
        proposed = pos[t - 1] + v * s.slot_seconds
        for axis in range(2):
            crossing = (proposed[:, axis] < 1) | (proposed[:, axis] > 39)
            v[crossing, axis] *= -1
        pos[t] = np.clip(pos[t - 1] + v * s.slot_seconds, 1, 39)
        vel[t] = v
    rng = stream(seed, 2)
    # Correlated zero-mean dB residual; phi=0.98, stationary std=2 dB.
    residual = np.empty((length, n))
    residual[0] = rng.normal(0, 2, n)
    for t in range(1, length):
        residual[t] = 0.98 * residual[t - 1] + np.sqrt(1 - 0.98**2) * rng.normal(0, 2, n)
    distance = np.maximum(np.linalg.norm(pos - np.array([20, 20]), axis=2), 1)
    pathloss = 32.4 + 20 * np.log10(3.5) + 25 * np.log10(distance)
    # Fixed per-unit power -8 dBm; noise -174 dBm/Hz + 7 dB NF; -96 dBm interferer.
    noise = 10 ** ((-174 + 10 * np.log10(s.bandwidth_hz) + 7) / 10)
    interference = 10 ** (-96 / 10)
    boundary = 21 if s.layout == 0 else 16
    coord = pos[:, :, 0] if s.layout == 0 else pos[:, :, 1]
    zone = 1 / (1 + np.exp(-np.clip((coord - boundary) / 0.7, -40, 40)))
    surprise = np.zeros((length, n), dtype=bool)
    hold = np.zeros(n, dtype=int)
    for t in range(length):
        onset = rng.random(n) < s.surprise_rate
        hold = np.maximum(hold - 1, 0)
        hold[onset] = 24
        surprise[t] = hold > 0
    attenuation = s.blockage_db * np.maximum(zone, surprise.astype(float))
    sinr = -8 - pathloss + residual - attenuation - 10 * np.log10(noise + interference)
    noise_rng = stream(seed, 3)
    source_idx = np.maximum(np.arange(length) - s.observation_delay, 0)
    observed = sinr[source_idx] + noise_rng.normal(0, s.observation_noise_db, (length, n))
    if s.observation_quantization_db > 0:
        observed = (
            np.round(observed / s.observation_quantization_db) * s.observation_quantization_db
        )
    arrivals = np.zeros((length, n, 2), dtype=int)
    traffic = stream(seed, 4)
    phase = traffic.integers(0, s.control_period, n)
    on = traffic.random(n) < 0.5
    for t in range(s.warmup + s.duration):
        arrivals[t, :, 0] = (t % s.control_period == phase).astype(int)
        switch = traffic.random(n) < 0.01
        on = np.logical_xor(on, switch)
        arrivals[t, :, 1] = traffic.poisson(s.be_rate * s.load * np.where(on, 1.8, 0.2))
    uniforms = stream(seed, 5).random((length, n))
    return Trace(
        seed,
        pos,
        vel,
        sinr,
        observed,
        capacity(sinr, s),
        uniforms,
        arrivals,
        np.maximum(zone, surprise.astype(float)) > 0.5,
    )


def save_trace(path: Path, trace: Trace, scenario: Scenario) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {key: getattr(trace, key) for key in trace.__dataclass_fields__ if key != "seed"}
    np.savez_compressed(
        path, **payload, seed=trace.seed, scenario=json.dumps(scenario_dict(scenario))
    )


def load_trace(path: Path) -> tuple[Trace, Scenario]:
    with np.load(path, allow_pickle=False) as z:
        scenario = Scenario(**json.loads(str(z["scenario"])))
        arrays = {key: z[key] for key in Trace.__dataclass_fields__ if key != "seed"}
        return Trace(int(z["seed"]), **arrays), scenario
