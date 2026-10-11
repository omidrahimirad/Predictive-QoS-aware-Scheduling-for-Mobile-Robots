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

## v0.2 completed local research verification

- Final: **2,160** executions, eight conditions, **30 independent episodes per condition**,
  nine policies including the integrated fallback ablation. All completed.
- Exploratory quick: **144** executions, two episodes/condition; development: **96** executions.
- Frozen revision: `db21e0ae3d5bb0db210cb570d3f5eb5014dc543b`; scientific source hash
  `ac16b29780fd1b78a1636edc30dfe568f81bed37d80cd86a737aec99fc9da0e7`. No post-final algorithm tuning.
- `uv run pytest -q`: **67 passed** on Python 3.12.10.
- `uv run --isolated --python 3.11 --extra dev pytest -q`: **67 passed** on Python 3.11.
- Ruff lint/format passed, including the supplementary plot script; mypy passed on six
  modules, including robust scheduler/reliability/orchestration. `uv lock --check` passed.
- CFF validated against schema 1.2.0 with cffconvert; author is Omid Rahimi.
- Historical main/ablation manifests and trace pairing verified; 14 representative
  historical replays match every saved non-timing metric. Historical bundle unchanged.
- Every v2 payload/control/resource ledger, paired trace, unique episode row and policy
  equivalence checked. Paired statistics and reports regenerated identically from raw CSV.
- Six required PNG/SVG figures plus one supplementary deterioration timeline generated.
- Raw evidence in [examples/robust_scheduling_v2](examples/robust_scheduling_v2/).
- Aggregate development BE floor was infeasible. EDF remains better under severe blockage;
  Robust entirely becomes EDF in three shifted conditions. See RESULTS for all outcomes.

Repository description and 11 relevant topics were updated and read back from GitHub.
Publication of v0.2 and remote CI verification follow the user's explicit instruction;
consult the [live CI history](https://github.com/omidrahimirad/Predictive-QoS-aware-Scheduling-for-Mobile-Robots/actions)
for outcomes tied to exact published commits. No full study is run in routine CI.
