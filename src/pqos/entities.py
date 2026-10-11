"""Mutable private packet state and immutable causal scheduler contracts."""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class Packet:
    id: int
    ue: int
    traffic: str
    arrival: int
    size: int
    deadline: int | None
    delivered: int = 0
    acknowledged: int = 0
    reason: str | None = None
    completion: int | None = None


@dataclass
class Chunk:
    packet: int
    bits: int
    attempt: int
    ready: int
    success: bool = False
    physical_at: int | None = None
    physically_delivered: bool = False


@dataclass(frozen=True)
class ControlDemand:
    bits: int
    slack: int


@dataclass(frozen=True)
class UE:
    id: int
    position: tuple[float, float]


@dataclass(frozen=True)
class Flow:
    ue: int
    traffic: str


@dataclass(frozen=True)
class Observation:
    slot: int
    resources: int
    service: tuple[float, ...]
    success_probability: tuple[float, ...]
    eligible_bits: tuple[int, ...]
    controls: tuple[tuple[ControlDemand, ...], ...]
    average_rate: tuple[float, ...]
    forecast: tuple[tuple[float, ...], ...] | None = None
    forecast_age: int = 0
    observed_db: tuple[float, ...] = ()
    measurement_slot: int = -1
    forecast_db: tuple[float, ...] = ()
    feature_shift: tuple[float, ...] = ()


@dataclass(frozen=True)
class Allocation:
    counts: tuple[int, ...]

    def validate(self, observation: Observation) -> None:
        if len(self.counts) != len(observation.service):
            raise ValueError("allocation shape mismatch")
        if any(type(x) is not int or x < 0 for x in self.counts):
            raise ValueError("allocations must be nonnegative integers")
        if sum(self.counts) > observation.resources:
            raise ValueError("resource budget exceeded")
        if any(n and not b for n, b in zip(self.counts, observation.eligible_bits)):
            raise ValueError("allocated ineligible UE")


class Scheduler(Protocol):
    fallbacks: int

    def reset(self) -> None: ...
    def allocate(self, observation: Observation) -> Allocation: ...
