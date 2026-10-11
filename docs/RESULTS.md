# Measured results

For the v0.2 robustness extension, see [robust scheduling](ROBUST_SCHEDULING.md)
and the [new evaluation protocol](EXPERIMENT_PROTOCOL.md). Historical numerical
results below remain preserved and are labeled as prior evidence.


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
