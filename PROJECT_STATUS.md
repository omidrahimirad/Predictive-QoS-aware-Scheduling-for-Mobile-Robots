# Project status — 11 October 2026

## Completed locally

- Source checkout: `~/Documents/Personalprojects/Predictive-QoS-aware-Scheduling-for-Mobile-Robots/`.
- Branch: `implementation/predictive-qos`; first implementation commit: `6ca68e5`.
  The final artifact/checkpoint commit is visible in `git log -1`.
- Complete causal single-cell simulator, chunk retries, finite queues, cohort metrics.
- RR, PF, EDF, reactive, persistence, learned-prediction, and diagnostic channel oracle.
- Episode-grouped training/validation, forecast errors, OOD testing, horizon and feature ablations.
- Working `generate`, `train`, `demo`, `evaluate`, `ablate`, and `report` commands.
- Atomic manifests/checkpoints, paired bootstrap statistics, headless SVG/PNG figures.
- Standards mapping, methods, limitations, measured results, research report, interview notes.
- Portable compact verified artifacts under `examples/verified_run/`.

## Verification actually executed

- `uv sync --extra dev` and `uv lock --check`.
- `uv run ruff check src tests`: passed.
- `uv run ruff format --check src tests`: passed.
- `uv run mypy`: passed for configuration/entity/scheduler interfaces (three files).
- `uv run pytest -q`: **45 passed**, Python 3.12.10.
- `uv run --isolated --python 3.11 --extra dev pytest -q`: **45 passed**, Python 3.11.
- Fresh isolated-environment generate/train pipeline using `configs/train.yaml`, with new
  `data/training-v1` and `models/v1` directories; no existing model overwritten.
- Successful standalone demo, quick and full evaluation, quick and full ablation, CLI help,
  and standalone report regeneration. README commands were exercised.
- Every full-run payload conservation and control failure denominator checked; paired trace
  identity and unique episode-policy rows checked in both full campaigns.
- All generated example figures inspected through QA sheets, with main full load figure
  and demo timeline also inspected at readable resolution. Relative artifact links checked.

## Actual campaigns

| Campaign | Directory under results/ | Completed runs | Profile |
|---|---|---:|---|
| Main | evaluation-775c03d2af5a | 2730 | full, 30 episodes/cell |
| Ablations | ablation-deaa2500ccf4 | 2160 | full, 30 episodes/cell |
| Main | evaluation-f1288528243f | 112 | quick, four episodes/cell |
| Ablations | ablation-7dae9bb04849 | 288 | quick, four episodes/cell |
| Demo | demo-635c91e30735 | 1 | illustrative |

Main full runtime: 479.6 s. Full ablation runtime: 340.3 s. Quick main runtime: 49.7 s.
Demo core runtime: 0.65 s. Report plotting time is additional to the manifest's simulation
runtime; concurrent jobs were running. Timings are machine-dependent. Older development
runs, including a failed demo report before repair, remain ignored in results/ and are
not used as final example evidence. Full launch source provenance is preserved.

## Findings

Prediction is not universally better. EDF gives substantially lower control violations
under severe blockage and OOD. Selected gains against reactive QoS are modest and do
not remove model mismatch. OOD channel forecast skill is poor. See docs/RESULTS.md;
no fabricated improvement or URLLC guarantee is claimed.

## Explicitly outside this version

Real industrial-channel calibration, exact NR protocol/PHY, total-power optimization,
robot control-loop validation, formal optimality/reliability proofs, calibrated uncertainty,
RL, AoI, and long-window convergence studies. These are documented future research,
not secretly implemented or claimed outcomes.

## Publication state

**Published to the user-specified GitHub repository on `main` on 11 October 2026,
after explicit user authorization.** The initial remote commit was
`3abfbabb5123d8e55022e5b21fac9dc8b10e841e`; the remote default branch and commit
were verified after pushing. No pull request was created for this initial publication.
GitHub Actions started automatically; consult the [live CI history](https://github.com/omidrahimirad/Predictive-QoS-aware-Scheduling-for-Mobile-Robots/actions)
for the outcome of each published commit. Local verification above remains distinct
from remote CI. The original sibling specification was preserved; public provenance
copies normalize personal absolute paths.

## v0.2 robustness extension — pre-evaluation state

Historical evidence above remains unchanged. The robustness extension adds a causal
observable-residual monitor, training-feature envelope and global Predictive/EDF gate.
New disjoint split ranges and the eight-condition protocol are in
[EXPERIMENT_PROTOCOL](docs/EXPERIMENT_PROTOCOL.md). Development selected threshold
2.5; the .9-of-PF aggregate BE floor was infeasible for all candidates. Final evaluation
has not been executed at this pre-evaluation revision. A clean-source freeze is required.
