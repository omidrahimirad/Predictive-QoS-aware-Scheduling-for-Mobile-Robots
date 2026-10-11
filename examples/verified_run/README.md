# Verified artifacts

- `full/`: complete 2,730-run main study, 30 episodes per condition.
- `full_ablation/`: complete 2,160-run ablations, 30 episodes per condition.
- `quick/`: 112-run exploratory main study, four episodes per condition.
- `quick_ablation/`: 288-run exploratory ablations, four episodes per condition.
- `demo/`: one synthetic illustrative episode with timeline, not statistical evidence.
- `configs/`: exact configuration inputs for reproduction.
- Root selection CSV/JSON files: training/validation results, not test tuning.

Raw episode summaries are preserved; bulk traces, packet latency arrays, checkpoints,
and opaque joblib models are regenerable and intentionally omitted from this compact
bundle. Reports/figures are copied from actual saved runs. Python source, dependency
lock, and reproduction commands are in the repository. The full main campaign's
report-only source repair is documented in full/PROVENANCE.md.

Run manifests preserve actual Git/source/model state at launch. Some development
runs honestly record an unborn commit or dirty state; that is not rewritten as a
published release. The repository was subsequently published on `main` on
11 October 2026; see [publication status](../../PROJECT_STATUS.md) and the
[live CI history](https://github.com/omidrahimirad/Predictive-QoS-aware-Scheduling-for-Mobile-Robots/actions).
