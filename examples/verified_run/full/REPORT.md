# Reproducible experiment report

Status: **complete**.
Profile: **full**. full; n=30–30 independent episodes/cell.

Independent synthetic NR-inspired simulation; no HHI affiliation or standards conformance.

## Design

See manifest.json for frozen configurations, splits, model/trace provenance, and runtime.
Primary comparison: predictive minus reactive; EDF is the second reference.
Negative violation differences favor prediction; positive goodput differences favor prediction.
ID and OOD results remain separate. No significance tests were performed.

## Scenario definitions

| Scenario | Load | Speed m/s | Blockage dB | Domain |
|---|---:|---:|---:|---|
| id-0 | 0.5 | 1 | 18 | id |
| id-1 | 0.5 | 1 | 28 | id |
| id-10 | 3 | 4 | 18 | id |
| id-11 | 3 | 4 | 28 | id |
| id-2 | 0.5 | 4 | 18 | id |
| id-3 | 0.5 | 4 | 28 | id |
| id-4 | 1.5 | 1 | 18 | id |
| id-5 | 1.5 | 1 | 28 | id |
| id-6 | 1.5 | 4 | 18 | id |
| id-7 | 1.5 | 4 | 28 | id |
| id-8 | 3 | 1 | 18 | id |
| id-9 | 3 | 1 | 28 | id |
| ood-layout-speed | 2.5 | 6 | 28 | ood |

## Primary endpoint

Macro-mean control violation ratio; 95% CI from resampling independent episodes.

| Scenario | Policy | Episodes | Mean % | 95% CI % |
|---|---|---:|---:|---|
| id-0 | edf | 30 | 0.778 | [0.528, 1.056] |
| id-0 | oracle | 30 | 0.771 | [0.521, 1.049] |
| id-0 | persistence | 30 | 0.764 | [0.521, 1.035] |
| id-0 | pf | 30 | 0.847 | [0.576, 1.146] |
| id-0 | predictive | 30 | 0.764 | [0.514, 1.042] |
| id-0 | reactive | 30 | 0.764 | [0.521, 1.035] |
| id-0 | rr | 30 | 0.931 | [0.646, 1.243] |
| id-1 | edf | 30 | 21.694 | [18.125, 25.688] |
| id-1 | oracle | 30 | 33.556 | [24.659, 43.764] |
| id-1 | persistence | 30 | 33.104 | [24.521, 43.022] |
| id-1 | pf | 30 | 21.222 | [18.090, 24.597] |
| id-1 | predictive | 30 | 33.306 | [24.548, 43.507] |
| id-1 | reactive | 30 | 33.104 | [24.521, 43.022] |
| id-1 | rr | 30 | 22.938 | [19.472, 26.632] |
| id-10 | edf | 30 | 1.826 | [1.347, 2.340] |
| id-10 | oracle | 30 | 1.785 | [1.326, 2.292] |
| id-10 | persistence | 30 | 2.014 | [1.479, 2.625] |
| id-10 | pf | 30 | 8.236 | [6.583, 10.021] |
| id-10 | predictive | 30 | 1.764 | [1.257, 2.319] |
| id-10 | reactive | 30 | 2.014 | [1.479, 2.625] |
| id-10 | rr | 30 | 2.667 | [1.861, 3.576] |
| id-11 | edf | 30 | 25.222 | [21.326, 29.577] |
| id-11 | oracle | 30 | 27.424 | [22.965, 32.333] |
| id-11 | persistence | 30 | 28.264 | [23.715, 33.327] |
| id-11 | pf | 30 | 29.431 | [25.417, 33.632] |
| id-11 | predictive | 30 | 27.847 | [23.361, 32.771] |
| id-11 | reactive | 30 | 28.264 | [23.715, 33.327] |
| id-11 | rr | 30 | 26.236 | [22.750, 29.910] |
| id-2 | edf | 30 | 0.917 | [0.597, 1.264] |
| id-2 | oracle | 30 | 0.958 | [0.611, 1.347] |
| id-2 | persistence | 30 | 0.958 | [0.618, 1.347] |
| id-2 | pf | 30 | 0.979 | [0.618, 1.382] |
| id-2 | predictive | 30 | 0.951 | [0.611, 1.340] |
| id-2 | reactive | 30 | 0.958 | [0.618, 1.347] |
| id-2 | rr | 30 | 1.104 | [0.715, 1.535] |
| id-3 | edf | 30 | 21.944 | [18.548, 25.750] |
| id-3 | oracle | 30 | 33.965 | [24.965, 44.354] |
| id-3 | persistence | 30 | 34.097 | [25.423, 44.090] |
| id-3 | pf | 30 | 21.521 | [18.479, 24.827] |
| id-3 | predictive | 30 | 33.479 | [24.757, 43.507] |
| id-3 | reactive | 30 | 34.097 | [25.423, 44.090] |
| id-3 | rr | 30 | 23.389 | [20.069, 26.924] |
| id-4 | edf | 30 | 0.687 | [0.458, 0.944] |
| id-4 | oracle | 30 | 0.743 | [0.500, 1.014] |
| id-4 | persistence | 30 | 0.771 | [0.535, 1.035] |
| id-4 | pf | 30 | 1.465 | [0.875, 2.181] |
| id-4 | predictive | 30 | 0.736 | [0.507, 0.993] |
| id-4 | reactive | 30 | 0.771 | [0.535, 1.035] |
| id-4 | rr | 30 | 1.299 | [0.854, 1.812] |
| id-5 | edf | 30 | 23.444 | [19.187, 28.035] |
| id-5 | oracle | 30 | 30.444 | [24.007, 37.208] |
| id-5 | persistence | 30 | 31.743 | [24.910, 38.972] |
| id-5 | pf | 30 | 23.437 | [19.840, 27.333] |
| id-5 | predictive | 30 | 30.688 | [24.257, 37.500] |
| id-5 | reactive | 30 | 31.743 | [24.910, 38.972] |
| id-5 | rr | 30 | 24.187 | [20.632, 27.986] |
| id-6 | edf | 30 | 0.833 | [0.542, 1.160] |
| id-6 | oracle | 30 | 0.847 | [0.556, 1.167] |
| id-6 | persistence | 30 | 0.910 | [0.590, 1.271] |
| id-6 | pf | 30 | 1.681 | [1.000, 2.500] |
| id-6 | predictive | 30 | 0.840 | [0.556, 1.167] |
| id-6 | reactive | 30 | 0.910 | [0.590, 1.271] |
| id-6 | rr | 30 | 1.514 | [0.937, 2.181] |
| id-7 | edf | 30 | 23.056 | [19.132, 27.466] |
| id-7 | oracle | 30 | 30.583 | [24.333, 37.327] |
| id-7 | persistence | 30 | 31.736 | [25.354, 38.736] |
| id-7 | pf | 30 | 23.542 | [20.083, 27.319] |
| id-7 | predictive | 30 | 31.299 | [25.104, 38.056] |
| id-7 | reactive | 30 | 31.736 | [25.354, 38.736] |
| id-7 | rr | 30 | 24.764 | [21.271, 28.514] |
| id-8 | edf | 30 | 1.576 | [1.146, 2.042] |
| id-8 | oracle | 30 | 1.590 | [1.118, 2.118] |
| id-8 | persistence | 30 | 1.958 | [1.375, 2.611] |
| id-8 | pf | 30 | 8.229 | [6.542, 10.104] |
| id-8 | predictive | 30 | 1.576 | [1.132, 2.083] |
| id-8 | reactive | 30 | 1.958 | [1.375, 2.611] |
| id-8 | rr | 30 | 2.465 | [1.826, 3.201] |
| id-9 | edf | 30 | 24.785 | [20.916, 28.924] |
| id-9 | oracle | 30 | 27.299 | [22.771, 32.194] |
| id-9 | persistence | 30 | 27.875 | [23.312, 32.854] |
| id-9 | pf | 30 | 29.701 | [25.764, 33.833] |
| id-9 | predictive | 30 | 27.486 | [23.125, 32.174] |
| id-9 | reactive | 30 | 27.875 | [23.312, 32.854] |
| id-9 | rr | 30 | 25.757 | [22.243, 29.500] |
| ood-layout-speed | edf | 30 | 45.722 | [39.257, 52.389] |
| ood-layout-speed | oracle | 30 | 51.833 | [45.160, 58.521] |
| ood-layout-speed | persistence | 30 | 52.417 | [46.243, 58.688] |
| ood-layout-speed | pf | 30 | 50.889 | [45.951, 55.757] |
| ood-layout-speed | predictive | 30 | 51.340 | [45.222, 57.528] |
| ood-layout-speed | reactive | 30 | 52.417 | [46.243, 58.688] |
| ood-layout-speed | rr | 30 | 47.028 | [41.250, 52.910] |

## Paired differences

| Scenario | Comparison | Difference pp | 95% CI pp |
|---|---|---:|---|
| id-0 | predictive - reactive | -0.000 | [-0.028, 0.028] |
| id-0 | predictive - edf | -0.014 | [-0.069, 0.035] |
| id-0 | predictive - pf | -0.083 | [-0.194, 0.014] |
| id-0 | predictive - persistence | -0.000 | [-0.028, 0.028] |
| id-0 | predictive - oracle | -0.007 | [-0.042, 0.021] |
| id-1 | predictive - reactive | 0.201 | [-0.715, 1.417] |
| id-1 | predictive - edf | 11.611 | [6.097, 17.951] |
| id-1 | predictive - pf | 12.083 | [6.083, 19.090] |
| id-1 | predictive - persistence | 0.201 | [-0.715, 1.417] |
| id-1 | predictive - oracle | -0.250 | [-1.201, 0.674] |
| id-10 | predictive - reactive | -0.250 | [-0.451, -0.056] |
| id-10 | predictive - edf | -0.063 | [-0.271, 0.139] |
| id-10 | predictive - pf | -6.472 | [-7.826, -5.194] |
| id-10 | predictive - persistence | -0.250 | [-0.451, -0.056] |
| id-10 | predictive - oracle | -0.021 | [-0.201, 0.174] |
| id-11 | predictive - reactive | -0.417 | [-0.965, 0.160] |
| id-11 | predictive - edf | 2.625 | [1.653, 3.597] |
| id-11 | predictive - pf | -1.583 | [-3.299, 0.139] |
| id-11 | predictive - persistence | -0.417 | [-0.965, 0.160] |
| id-11 | predictive - oracle | 0.424 | [-0.264, 1.201] |
| id-2 | predictive - reactive | -0.007 | [-0.021, 0.000] |
| id-2 | predictive - edf | 0.035 | [-0.021, 0.111] |
| id-2 | predictive - pf | -0.028 | [-0.111, 0.049] |
| id-2 | predictive - persistence | -0.007 | [-0.021, 0.000] |
| id-2 | predictive - oracle | -0.007 | [-0.042, 0.028] |
| id-3 | predictive - reactive | -0.618 | [-1.458, 0.083] |
| id-3 | predictive - edf | 11.535 | [5.917, 18.028] |
| id-3 | predictive - pf | 11.958 | [5.854, 18.903] |
| id-3 | predictive - persistence | -0.618 | [-1.458, 0.083] |
| id-3 | predictive - oracle | -0.486 | [-1.292, 0.271] |
| id-4 | predictive - reactive | -0.035 | [-0.090, 0.014] |
| id-4 | predictive - edf | 0.049 | [0.000, 0.097] |
| id-4 | predictive - pf | -0.729 | [-1.299, -0.271] |
| id-4 | predictive - persistence | -0.035 | [-0.090, 0.014] |
| id-4 | predictive - oracle | -0.007 | [-0.062, 0.035] |
| id-5 | predictive - reactive | -1.056 | [-2.083, -0.181] |
| id-5 | predictive - edf | 7.243 | [4.785, 9.833] |
| id-5 | predictive - pf | 7.250 | [3.764, 11.056] |
| id-5 | predictive - persistence | -1.056 | [-2.083, -0.181] |
| id-5 | predictive - oracle | 0.243 | [-0.854, 1.319] |
| id-6 | predictive - reactive | -0.069 | [-0.125, -0.021] |
| id-6 | predictive - edf | 0.007 | [-0.042, 0.056] |
| id-6 | predictive - pf | -0.840 | [-1.389, -0.396] |
| id-6 | predictive - persistence | -0.069 | [-0.125, -0.021] |
| id-6 | predictive - oracle | -0.007 | [-0.035, 0.021] |
| id-7 | predictive - reactive | -0.437 | [-1.243, 0.438] |
| id-7 | predictive - edf | 8.243 | [5.458, 11.285] |
| id-7 | predictive - pf | 7.757 | [4.291, 11.611] |
| id-7 | predictive - persistence | -0.437 | [-1.243, 0.438] |
| id-7 | predictive - oracle | 0.715 | [-0.104, 1.694] |
| id-8 | predictive - reactive | -0.382 | [-0.667, -0.090] |
| id-8 | predictive - edf | -0.000 | [-0.229, 0.215] |
| id-8 | predictive - pf | -6.653 | [-8.181, -5.243] |
| id-8 | predictive - persistence | -0.382 | [-0.667, -0.090] |
| id-8 | predictive - oracle | -0.014 | [-0.181, 0.160] |
| id-9 | predictive - reactive | -0.389 | [-1.118, 0.347] |
| id-9 | predictive - edf | 2.701 | [1.625, 3.882] |
| id-9 | predictive - pf | -2.215 | [-3.875, -0.576] |
| id-9 | predictive - persistence | -0.389 | [-1.118, 0.347] |
| id-9 | predictive - oracle | 0.187 | [-0.549, 0.917] |
| ood-layout-speed | predictive - reactive | -1.076 | [-2.403, 0.201] |
| ood-layout-speed | predictive - edf | 5.618 | [3.319, 7.701] |
| ood-layout-speed | predictive - pf | 0.451 | [-1.708, 2.639] |
| ood-layout-speed | predictive - persistence | -1.076 | [-2.403, 0.201] |
| ood-layout-speed | predictive - oracle | -0.493 | [-1.778, 0.729] |

## Interpretation and limitations

All policies share exogenous traces and the same control-first local queue discipline.
The perfect-future-channel policy is diagnostic, not a mathematical upper bound.
Delivered-only latency is conditional on delivery. Drops and violations must be read alongside it.
Tail comparisons use episode p99 values; they do not estimate an unconditional population p99.
Bootstrap CIs may be degenerate at zero failures. These runs do not establish five-nines reliability.
Quick-profile intervals are exploratory; finite episode count and synthetic model limit inference.
Point forecasts are not calibrated uncertainty guarantees. Negative and null results are retained.
Machine-dependent timing measurements are not universal real-time performance claims.

## Artifacts

See episode_metrics.csv, summary_metrics.csv, paired_comparisons.csv,
prediction_metrics.csv, selected_models.json, and figures/. All plots use actual run data.
