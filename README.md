# Predictive QoS-aware Scheduling for Mobile Robots

A reproducible **NR-inspired abstract system-level simulator** investigating whether
causal channel prediction helps schedule already queued robot-control packets before
their deadlines. This is an independent portfolio research project, with no
Fraunhofer affiliation, 3GPP conformance claim, or robot-safety guarantee.

The project is motivated by HHI's 6G resource-allocation research role and historical
[AI4Mobile work](https://www.hhi.fraunhofer.de/en/departments/wn/projects/ai4mobile.html).
It combines transparent classical scheduling, CPU-trained predictors, and paired
statistical evaluation. Negative and null results are valid outcomes.

## Quickstart

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). Run from the repository root:

```bash
uv sync --locked --extra dev
uv run pqos generate --config configs/train.yaml
uv run pqos train --config configs/train.yaml
uv run pqos demo --config configs/demo.yaml
uv run pqos evaluate --config configs/evaluation.yaml --profile quick
uv run pqos ablate --config configs/ablation.yaml --profile quick
```

Each command prints its actual output directory. Model training refuses to overwrite
an existing model; use a new `model_dir` in a copied configuration for a fresh training run.
Evaluation resumes matching checkpoints. Run IDs include configuration, model, and
source fingerprints, so changed implementations create different runs.

Regenerate a report using the directory printed by evaluation:

```bash
uv run pqos report --run-dir results/<actual-run-id>
```

For the predeclared larger campaign:

```bash
uv run pqos evaluate --config configs/evaluation.yaml --profile full
uv run pqos ablate --config configs/ablation.yaml --profile full
```

Full evaluation uses 30 independent episodes for each of 12 ID conditions plus one
OOD condition, with seven policies (2,730 episode-policy runs). Quick evaluation
uses four episodes for three ID conditions plus OOD (112 runs). Full execution is
optional for reproduction; its actual execution status is recorded in
[PROJECT_STATUS.md](PROJECT_STATUS.md), never inferred from the presence of a config.

No notebook, GPU, external dataset, or GUI is required. Figures use a headless backend.
On the verification machine, timings and measured runtimes are in run manifests.

## Architecture

```text
Frozen configs + named RNG streams
       -> exogenous mobility / channels / arrivals / observation noise
       -> causal observations -> allocator -> shared chunk/queue engine
Training episodes -> ridge / ExtraTrees -> validation model + policy selection
Held-out episodes -> paired policies -> episode metrics -> bootstrap -> reports
```

| Component | Location | Responsibility |
|---|---|---|
| Config and contracts | `config.py`, `entities.py` | Units, validation, immutable observation |
| Exogenous environment | `traces.py` | Mobility, propagation surrogate, traffic, indexed randomness |
| Simulator | `simulator.py` | Physical delivery, delayed ACKs, retry state, finite queues |
| Policies | `schedulers/` | RR, PF, EDF, reactive, persistence, learned, diagnostic oracle |
| Prediction | `prediction/models.py` | Causal histories, grouped splits, fitting, horizon forecasts |
| Experiments | `experiments/` | Validation selection, paired runs, checkpointing, figures |

Paths in this table are relative to `src/pqos/`. See [METHODS](docs/METHODS.md)
for exact equations and event ordering.

## What is measured

- Primary: control delivery violation ratio, including overflow and retry exhaustion.
- Best-effort and total **unique-payload** goodput during the measurement window.
- Delivered-only control latency p50/p95/p99, with explicit survivor-bias warnings.
- Per-UE goodput/violations, Jain fairness, resource utilization, queue state, retries,
  scheduler computation time, and model errors by horizon.
- Paired differences with 95% episode-bootstrap intervals. Slots and packets are not
  treated as independent statistical repetitions.

Packet arrival defines the measurement cohort; a bounded drain resolves its control
deadlines. Drain traffic does not inflate measurement-window goodput.

## Verified example

The compact [example bundle](examples/verified_run/) contains actual configurations,
manifests, metrics, reports, and figures. See [RESULTS](docs/RESULTS.md) for the measured
findings and [research report](docs/RESEARCH_REPORT.md) for context. The example uses
four independent episodes per condition and is exploratory, not a reliability certification.

## Checks

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy
uv run pytest -q
```

CI performs these checks and a bounded train/evaluate smoke pipeline on Python 3.11
and 3.12. Local validation does not establish that GitHub CI has run.

## Data and output management

`data/`, `models/`, `results/`, and `work/` are ignored. `examples/verified_run/` holds
only compact verified outputs. The original local spec remains outside the checkout
in Documents/Personalprojects, with a provenance copy in `docs/PROJECT_SPEC.md`.

Models are joblib artifacts generated locally. **Do not load model files from
untrusted sources**: pickle-based serialization can execute code.

## Scientific scope

Single-cell downlink; fixed per-resource power spectral density; synthetic
frequency-flat channel; Shannon-based service; synthetic error curve; chunk ARQ
without HARQ combining; no RLC/PDCP/RRC implementation or robot control loop.

Read [LIMITATIONS](docs/LIMITATIONS.md) and [STANDARDS_MAPPING](docs/STANDARDS_MAPPING.md)
before interpreting results. A better prediction metric does not imply a better
scheduler, and zero observed violations do not prove five-nines reliability.

MIT license applies to original project code. Standards and cited research retain
their own rights. Use `CITATION.cff` for software citation; there is no invented DOI.
