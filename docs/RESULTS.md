# Measured results

For the v0.2 robustness extension, see [robust scheduling](ROBUST_SCHEDULING.md)
and the [new evaluation protocol](EXPERIMENT_PROTOCOL.md). Historical numerical
results in the original sections remain preserved as prior evidence; the new v0.2
sections are labeled separately.


## Historical v0.1 evidence

The full main campaign completed **2,730 episode-policy runs**: 12 ID conditions
and one OOD condition, seven allocators, 30 independent episodes per condition.
The same 30 seed families are reused across conditions; 2,730 is a run count,
not 2,730 independent statistical repetitions. Inference is within each condition.

The predictive method is **not a universal winner**. Some paired gains against
reactive QoS are small; EDF has lower control violations in the severe-blockage
conditions and OOD. Best-effort goodput tradeoffs must accompany that comparison.

## Validation selection

Selected predictor: **tree**; urgency weight **2**; horizon **4 slots**.
All choices were made on validation episodes, not test results.
The .9-of-PF BE-goodput floor was feasible on validation; the 1.0 floor was not.
This floor does not guarantee the same constraint on test episodes.

## Full primary comparisons

Difference = predictive minus reference, in percentage points (pp). Negative values
favor prediction. Intervals are 95% percentile bootstrap over 30 matched episodes.
These are effect estimates, not multiplicity-adjusted significance tests.

| Condition | Load | Speed m/s | Blockage dB | Versus reactive: pp [95% CI] | Versus EDF: pp [95% CI] |
|---|---:|---:|---:|---|---|
| id-0 | 0.5 | 1 | 18 | -0.000 [-0.028, 0.028] | -0.014 [-0.069, 0.035] |
| id-1 | 0.5 | 1 | 28 | 0.201 [-0.715, 1.417] | 11.611 [6.097, 17.951] |
| id-2 | 0.5 | 4 | 18 | -0.007 [-0.021, 0.000] | 0.035 [-0.021, 0.111] |
| id-3 | 0.5 | 4 | 28 | -0.618 [-1.458, 0.083] | 11.535 [5.917, 18.028] |
| id-4 | 1.5 | 1 | 18 | -0.035 [-0.090, 0.014] | 0.049 [0.000, 0.097] |
| id-5 | 1.5 | 1 | 28 | -1.056 [-2.083, -0.181] | 7.243 [4.785, 9.833] |
| id-6 | 1.5 | 4 | 18 | -0.069 [-0.125, -0.021] | 0.007 [-0.042, 0.056] |
| id-7 | 1.5 | 4 | 28 | -0.437 [-1.243, 0.438] | 8.243 [5.458, 11.285] |
| id-8 | 3 | 1 | 18 | -0.382 [-0.667, -0.090] | -0.000 [-0.229, 0.215] |
| id-9 | 3 | 1 | 28 | -0.389 [-1.118, 0.347] | 2.701 [1.625, 3.882] |
| id-10 | 3 | 4 | 18 | -0.250 [-0.451, -0.056] | -0.063 [-0.271, 0.139] |
| id-11 | 3 | 4 | 28 | -0.417 [-0.965, 0.160] | 2.625 [1.653, 3.597] |
| ood-layout-speed | 2.5 | 6 | 28 | -1.076 [-2.403, 0.201] | 5.618 [3.319, 7.701] |

## Changed environment

| Policy | Control violation % | BE goodput Mbit/s | Jain fairness |
|---|---:|---:|---:|
| edf | 45.722 | 4.918 | 0.615 |
| oracle | 51.833 | 6.240 | 0.558 |
| persistence | 52.417 | 6.335 | 0.560 |
| pf | 50.889 | 10.829 | 0.548 |
| predictive | 51.340 | 6.658 | 0.555 |
| reactive | 52.417 | 6.335 | 0.560 |
| rr | 47.028 | 9.866 | 0.519 |

In OOD, prediction has approximately 5.618 pp more violations than EDF
(95% paired CI [3.319, 7.701] pp), while its descriptive mean BE goodput is higher.
Prediction versus reactive is approximately -1.076 pp (CI [-2.403, 0.201] pp).
The latter interval includes zero; it does not establish a consistent gain.

## Forecast quality

| Condition | Horizon slots | Model | SINR MAE dB | Persistence skill |
|---|---:|---|---:|---:|
| id-0 | 4 | persistence | 1.082 | 0.000 |
| id-0 | 4 | tree | 0.980 | 0.094 |
| id-0 | 16 | persistence | 1.656 | 0.000 |
| id-0 | 16 | tree | 1.518 | 0.084 |
| id-1 | 4 | persistence | 1.133 | 0.000 |
| id-1 | 4 | tree | 1.138 | -0.004 |
| id-1 | 16 | persistence | 1.810 | 0.000 |
| id-1 | 16 | tree | 1.784 | 0.014 |
| ood-layout-speed | 4 | persistence | 1.043 | 0.000 |
| ood-layout-speed | 4 | tree | 3.815 | -2.659 |
| ood-layout-speed | 16 | persistence | 1.543 | 0.000 |
| ood-layout-speed | 16 | tree | 10.092 | -5.541 |

Skill = 1 - model MAE / persistence MAE. Positive is better. OOD tree forecasts
are substantially worse than persistence, despite useful ID average prediction.
Forecast accuracy is descriptive and does not by itself establish policy benefit.

## Artifacts and caveats

- [Full main report](../examples/verified_run/full/REPORT.md).
- [Quick report](../examples/verified_run/quick/REPORT.md).
- [Quick ablations](../examples/verified_run/quick_ablation/REPORT.md).
- [Demo timeline](../examples/verified_run/demo/figures/timeline.png).
- Raw episode rows, all failure reasons, tail quantiles, forecast errors, and paired
  differences are preserved alongside the reports. No unsuccessful case was removed.

Delivered-only latency remains conditional on delivery. The queue/radio surrogate
does not measure end-to-end robotic control or support safety/reliability certification.
No real-world dataset, formal optimality proof, or duration-convergence study is claimed.
Main campaign runtime was approximately 479.6 seconds on the recorded machine,
using four workers. Other jobs were running; scheduler timings are descriptive,
not isolated universal benchmarks. These experiments were verified locally before
remote publication. The repository was subsequently published on `main` on
11 October 2026; remote CI status is available in the
[live CI history](https://github.com/omidrahimirad/Predictive-QoS-aware-Scheduling-for-Mobile-Robots/actions).

See [full campaign provenance](../examples/verified_run/full/PROVENANCE.md) for the
report-only empty-table repair made after that campaign was launched.

## Full ablations

The full ablation campaign completed **2,160 episode-policy runs**: six conditions,
12 variants, and 30 independent episodes per condition. Runtime was approximately
340.3 seconds on the recorded machine with four workers.

| Condition | Reactive violation % | Learned violation % | No-position/motion violation % | Horizon 1 violation % | Horizon 16 violation % |
|---|---:|---:|---:|---:|---:|
| delay-8 | 5.569 | 5.472 | 5.472 | 5.479 | 5.500 |
| id-0 | 5.208 | 5.257 | 5.181 | 5.194 | 5.278 |
| noise-4 | 6.035 | 5.951 | 5.937 | 5.826 | 5.903 |
| ood-layout-speed | 52.417 | 51.340 | 51.826 | 52.493 | 51.736 |
| smooth | 5.167 | 5.194 | 5.167 | 5.139 | 5.236 |
| surprise | 5.819 | 5.931 | 5.764 | 5.736 | 5.868 |

These descriptive variant means do not support a universal optimal horizon or a
claim that the learned predictor is consistently necessary. All six paired intervals
for predictive-minus-reactive violations in the full ablations include zero.
No-position/motion, observation delay/noise, smooth channels, and surprise blockage
are retained; none was discarded after inspecting results. Per-variant uncertainty
is in summary_metrics.csv and the [full ablation report](../examples/verified_run/full_ablation/REPORT.md).

## Robustness extension — new final evidence

The v0.2 final campaign completed **2,160 episode-policy executions** across eight
predeclared conditions, nine policies and **30 independent episodes per condition**.
Each condition uses disjoint new seeds; matched policies share the same exogenous trace.
The no-adaptation mechanism ablation is included in these 2,160 runs, not an additional sample.
A separate two-episode exploratory profile completed 144 runs. Development evaluated 96
episode-policy executions (three thresholds and PF across 24 independent scenario episodes).

Point model: ExtraTrees; predictive urgency 2, horizon 4; robust threshold 2.5,
EWMA smoothing .05, feature shift scale .1. Calibration mean observable residual is
1.154 dB and empirical q90 is 2.227 dB. The aggregate development BE floor was infeasible:
selected Robust 10.810 versus PF 13.234 Mbit/s, approximately 81.7% of PF.

Frozen code: `db21e0ae3d5bb0db210cb570d3f5eb5014dc543b`. Configuration, source,
model and calibration fingerprints were frozen before final seeds were executed.
No algorithm or threshold was changed after inspecting final outcomes.

| Condition | Predictive violation % | Robust violation % | EDF violation % | Robust − Predictive pp [95% CI] | Robust − EDF pp [95% CI] |
|---|---:|---:|---:|---|---|
| A-normal | 0.785 | 0.812 | 0.771 | 0.028 [-0.007, 0.069] | 0.042 [-0.007, 0.090] |
| B-pressure | 2.729 | 2.542 | 2.521 | -0.187 [-0.493, 0.090] | 0.021 [-0.236, 0.299] |
| C-blockage | 43.583 | 37.757 | 30.125 | -5.826 [-8.292, -3.625] | 7.632 [5.146, 10.486] |
| D-mobility | 1.056 | 1.028 | 1.028 | -0.028 [-0.132, 0.056] | 0.000 [0.000, 0.000] |
| E-deterioration | 43.819 | 30.424 | 30.201 | -13.396 [-16.827, -10.083] | 0.222 [-0.819, 1.132] |
| F-layout-shift | 10.715 | 8.951 | 9.208 | -1.764 [-2.451, -1.111] | -0.257 [-0.486, -0.049] |
| G-measurements | 7.049 | 6.944 | 6.944 | -0.104 [-0.292, 0.076] | 0.000 [0.000, 0.000] |
| H-combined | 72.389 | 61.146 | 61.146 | -11.243 [-14.320, -8.215] | 0.000 [0.000, 0.000] |

Differences resample matched independent episodes 10,000 times. Intervals are marginal,
not corrected for the many comparisons. They are not universal superiority or safety proofs.

### Reliability, throughput and fairness

| Condition | Predictive BE | Robust BE | EDF BE | Robust Jain fairness | Fallback % slots |
|---|---:|---:|---:|---:|---:|
| A-normal | 14.545 | 14.540 | 14.536 | 0.933 | 23.5 |
| B-pressure | 24.445 | 24.414 | 24.417 | 0.882 | 26.6 |
| C-blockage | 7.812 | 7.154 | 6.205 | 0.698 | 35.5 |
| D-mobility | 15.013 | 15.007 | 15.007 | 0.934 | 100.0 |
| E-deterioration | 8.061 | 6.311 | 6.010 | 0.773 | 95.3 |
| F-layout-shift | 10.630 | 10.490 | 10.498 | 0.828 | 98.0 |
| G-measurements | 12.528 | 12.502 | 12.502 | 0.878 | 100.0 |
| H-combined | 4.877 | 2.087 | 2.087 | 0.521 | 100.0 |

BE units are Mbit/s. Severe blockage C: Robust improves against Predictive but remains
7.632 pp worse than EDF while delivering 7.154 versus EDF 6.205 Mbit/s BE.
Deterioration E: Robust reduces violations by 13.396 pp versus Predictive while reducing
BE from 8.061 to 6.311 Mbit/s. It remains close to EDF in violation (difference .222 pp,
CI including zero), with slightly higher mean BE. In H, a reduction of 11.243 pp
versus Predictive accompanies BE falling from 4.877 to 2.087 Mbit/s.
This is a large throughput trade-off, not a free improvement.

D/G/H use EDF in every slot and exactly match its scientific metrics. Their gains over
Predictive demonstrate abstention, not a better allocator than EDF. F has a small
-.257 pp Robust-minus-EDF difference with marginal CI [-.486,-.049]; interpret it
cautiously given multiplicity and the negligible throughput/fairness differences.
A/B show no clear interval-supported gain over Predictive. All conditions remain reported.

### Forecast and calibration diagnostics

| Condition | Learned MAE dB | Persistence MAE dB | Learned skill | Observable q90 coverage % |
|---|---:|---:|---:|---:|
| A-normal | 0.980 | 1.075 | 0.089 | 88.7 |
| B-pressure | 0.977 | 1.091 | 0.106 | 89.1 |
| C-blockage | 1.128 | 1.116 | -0.010 | 86.1 |
| D-mobility | 0.967 | 1.078 | 0.103 | 89.0 |
| E-deterioration | 2.567 | 2.205 | -0.161 | 75.3 |
| F-layout-shift | 2.867 | 1.039 | -1.775 | 58.5 |
| G-measurements | 1.997 | 3.567 | 0.441 | 36.8 |
| H-combined | 5.211 | 1.403 | -2.766 | 44.2 |

MAE/RMSE use true future SINR offline; observable coverage uses the eventual delayed
noisy sample. Forecast diagnostics include the post-history warmup prefix and exclude
drain. Nominal q90 coverage is empirical, not a conformal guarantee. Observed coverage
falls sharply in F/G/H. D still has useful learned forecast skill but falls back 100%:
the feature envelope flags speed shift even when prediction remains useful. This
illustrates conservative false alarms. Confidence-group error rows are preserved
as descriptive diagnostics, without treating correlated slot samples as independent.

### Ablation and timing

The no-adaptation policy disables risk-driven switching and retains invalid-forecast
EDF protection. Its performance is close to original Predictive, isolating the gate
rather than a changed predictive score. See all paired ablation intervals in the
[comparison table](../examples/robust_scheduling_v2/full/paired_comparisons.csv).
Persistence and Reactive match all non-timing metrics in all 240 final trace pairs.

Descriptive mean scheduler timing: Robust 203.1 µs; EDF 157.1 µs; Predictive 255.4 µs.
Robust is 1.29× EDF and .80× Predictive; cheaper EDF mode explains the latter.
Mean within-episode P99: Robust 369.2 µs, EDF 257.1 µs, Predictive 485.6 µs.
Batch inference is excluded and separately recorded. Worker contention and Python
overheads preclude real-time RAN claims. The recorded campaign orchestration time
was 392.7 seconds before report rendering. All data and regenerated
statistics were checked for consistency; no final run failed.

### Artifacts and limits

[New full report](../examples/robust_scheduling_v2/full/REPORT.md),
[new raw episode metrics](../examples/robust_scheduling_v2/full/episode_metrics.csv),
[summary figure](../examples/robust_scheduling_v2/full/figures/main_findings.png), and
[deterioration fallback illustration](../examples/robust_scheduling_v2/full/figures/fallback_deterioration.png).
The supplement uses the first predeclared E episode, not an episode chosen for favorable results.
It is reproduced by scripts/plot_fallback.py without changing frozen scientific settings.

Historical evidence remains unchanged. Synthetic channels, physical-completion queue
eligibility, short episodes, conditional latency and uncalibrated confidence remain
limitations. No industrial reliability, 3GPP conformance, novelty or robot safety claim follows.
