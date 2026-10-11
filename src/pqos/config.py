"""Validated configurations; all time settings are integer slots."""

from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Scenario:
    n_ues: int = 12
    resources: int = 24
    slot_seconds: float = 0.0005
    bandwidth_hz: float = 360000.0
    overhead_efficiency: float = 0.75
    eta_max: float = 6.0
    warmup: int = 100
    duration: int = 800
    drain: int = 40
    control_bits: int = 2048
    control_period: int = 20
    deadline: int = 20
    be_bits: int = 12000
    be_rate: float = 0.035
    load: float = 1.0
    speed: float = 1.0
    blockage_db: float = 15.0
    layout: int = 0
    surprise_rate: float = 0.0008
    observation_delay: int = 2
    observation_noise_db: float = 0.8
    observation_quantization_db: float = 0.0
    feedback_delay: int = 2
    max_attempts: int = 3
    buffer_bits: int = 240000
    error_free: bool = False
    history: int = 8

    def __post_init__(self) -> None:
        positive = (
            "n_ues",
            "resources",
            "duration",
            "control_bits",
            "control_period",
            "deadline",
            "be_bits",
            "max_attempts",
            "buffer_bits",
            "history",
        )
        nonnegative = ("warmup", "drain", "observation_delay", "feedback_delay", "layout")
        for name in positive:
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name in nonnegative:
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.drain < self.deadline:
            raise ValueError("drain must resolve all cohort control deadlines")
        if not 0 < self.overhead_efficiency <= 1:
            raise ValueError("overhead_efficiency must be in (0,1]")
        import math

        for name in (
            "slot_seconds",
            "bandwidth_hz",
            "eta_max",
            "be_rate",
            "load",
            "speed",
            "blockage_db",
            "surprise_rate",
            "observation_noise_db",
            "observation_quantization_db",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"invalid {name}")
        if min(self.slot_seconds, self.bandwidth_hz, self.eta_max) <= 0:
            raise ValueError("radio dimensions must be positive")
        if self.surprise_rate > 1:
            raise ValueError("surprise_rate must be <= 1")

    @property
    def slots(self) -> int:
        return self.warmup + self.duration + self.drain

    def changed(self, **kwargs: Any) -> "Scenario":
        return replace(self, **kwargs)


def load_config(path: str | Path) -> dict:
    with Path(path).open() as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("configuration must be a mapping")
    allowed = {f.name for f in fields(Scenario)}
    unknown = set(config.get("scenario", {})) - allowed
    if unknown:
        raise ValueError(f"unknown scenario keys: {sorted(unknown)}")
    Scenario(**config.get("scenario", {}))
    return config


def scenario_dict(scenario: Scenario) -> dict:
    return asdict(scenario)
