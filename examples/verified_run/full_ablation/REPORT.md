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
| delay-8 | 1.5 | 1 | 22 | id |
| id-0 | 1.5 | 1 | 22 | id |
| noise-4 | 1.5 | 1 | 22 | id |
| ood-layout-speed | 2.5 | 6 | 28 | ood |
| smooth | 1.5 | 1 | 22 | id |
| surprise | 1.5 | 1 | 22 | id |

## Primary endpoint

Macro-mean control violation ratio; 95% CI from resampling independent episodes.

| Scenario | Policy | Episodes | Mean % | 95% CI % |
|---|---|---:|---:|---|
| delay-8 | edf | 30 | 5.257 | [4.132, 6.549] |
| delay-8 | horizon_1 | 30 | 5.479 | [4.292, 6.799] |
| delay-8 | horizon_16 | 30 | 5.500 | [4.312, 6.833] |
| delay-8 | horizon_4 | 30 | 5.472 | [4.278, 6.799] |
| delay-8 | horizon_8 | 30 | 5.479 | [4.299, 6.785] |
| delay-8 | no_position | 30 | 5.472 | [4.278, 6.799] |
| delay-8 | oracle | 30 | 5.458 | [4.264, 6.806] |
| delay-8 | persistence | 30 | 5.569 | [4.354, 6.944] |
| delay-8 | pf | 30 | 8.465 | [6.500, 10.708] |
| delay-8 | predictive | 30 | 5.472 | [4.278, 6.799] |
| delay-8 | reactive | 30 | 5.569 | [4.354, 6.944] |
| delay-8 | rr | 30 | 9.340 | [7.326, 11.611] |
| id-0 | edf | 30 | 5.201 | [4.028, 6.562] |
| id-0 | horizon_1 | 30 | 5.194 | [4.028, 6.493] |
| id-0 | horizon_16 | 30 | 5.278 | [4.083, 6.625] |
| id-0 | horizon_4 | 30 | 5.257 | [4.048, 6.618] |
| id-0 | horizon_8 | 30 | 5.222 | [4.062, 6.493] |
| id-0 | no_position | 30 | 5.181 | [4.028, 6.458] |
| id-0 | oracle | 30 | 5.201 | [4.069, 6.458] |
| id-0 | persistence | 30 | 5.208 | [4.042, 6.514] |
| id-0 | pf | 30 | 8.271 | [6.361, 10.472] |
| id-0 | predictive | 30 | 5.257 | [4.048, 6.618] |
| id-0 | reactive | 30 | 5.208 | [4.042, 6.514] |
| id-0 | rr | 30 | 9.257 | [7.222, 11.576] |
| noise-4 | edf | 30 | 5.896 | [4.562, 7.424] |
| noise-4 | horizon_1 | 30 | 5.826 | [4.500, 7.292] |
| noise-4 | horizon_16 | 30 | 5.903 | [4.569, 7.424] |
| noise-4 | horizon_4 | 30 | 5.951 | [4.583, 7.465] |
| noise-4 | horizon_8 | 30 | 5.896 | [4.576, 7.347] |
| noise-4 | no_position | 30 | 5.937 | [4.590, 7.424] |
| noise-4 | oracle | 30 | 5.861 | [4.549, 7.326] |
| noise-4 | persistence | 30 | 6.035 | [4.680, 7.556] |
| noise-4 | pf | 30 | 7.507 | [5.764, 9.500] |
| noise-4 | predictive | 30 | 5.951 | [4.583, 7.465] |
| noise-4 | reactive | 30 | 6.035 | [4.680, 7.556] |
| noise-4 | rr | 30 | 9.500 | [7.437, 11.806] |
| ood-layout-speed | edf | 30 | 45.722 | [39.257, 52.389] |
| ood-layout-speed | horizon_1 | 30 | 52.493 | [45.937, 59.091] |
| ood-layout-speed | horizon_16 | 30 | 51.736 | [44.896, 58.611] |
| ood-layout-speed | horizon_4 | 30 | 51.340 | [45.222, 57.528] |
| ood-layout-speed | horizon_8 | 30 | 52.063 | [45.556, 58.542] |
| ood-layout-speed | no_position | 30 | 51.826 | [45.430, 58.320] |
| ood-layout-speed | oracle | 30 | 51.833 | [45.160, 58.521] |
| ood-layout-speed | persistence | 30 | 52.417 | [46.243, 58.688] |
| ood-layout-speed | pf | 30 | 50.889 | [45.951, 55.757] |
| ood-layout-speed | predictive | 30 | 51.340 | [45.222, 57.528] |
| ood-layout-speed | reactive | 30 | 52.417 | [46.243, 58.688] |
| ood-layout-speed | rr | 30 | 47.028 | [41.250, 52.910] |
| smooth | edf | 30 | 5.056 | [3.896, 6.417] |
| smooth | horizon_1 | 30 | 5.139 | [3.937, 6.528] |
| smooth | horizon_16 | 30 | 5.236 | [4.028, 6.597] |
| smooth | horizon_4 | 30 | 5.194 | [3.951, 6.667] |
| smooth | horizon_8 | 30 | 5.174 | [3.972, 6.556] |
| smooth | no_position | 30 | 5.167 | [3.958, 6.562] |
| smooth | oracle | 30 | 5.104 | [3.951, 6.375] |
| smooth | persistence | 30 | 5.167 | [3.979, 6.514] |
| smooth | pf | 30 | 8.042 | [6.174, 10.146] |
| smooth | predictive | 30 | 5.194 | [3.951, 6.667] |
| smooth | reactive | 30 | 5.167 | [3.979, 6.514] |
| smooth | rr | 30 | 9.021 | [6.993, 11.326] |
| surprise | edf | 30 | 5.729 | [4.548, 7.097] |
| surprise | horizon_1 | 30 | 5.736 | [4.521, 7.111] |
| surprise | horizon_16 | 30 | 5.868 | [4.639, 7.243] |
| surprise | horizon_4 | 30 | 5.931 | [4.653, 7.375] |
| surprise | horizon_8 | 30 | 5.792 | [4.549, 7.202] |
| surprise | no_position | 30 | 5.764 | [4.590, 7.056] |
| surprise | oracle | 30 | 5.667 | [4.514, 6.944] |
| surprise | persistence | 30 | 5.819 | [4.611, 7.160] |
| surprise | pf | 30 | 8.986 | [7.236, 10.986] |
| surprise | predictive | 30 | 5.931 | [4.653, 7.375] |
| surprise | reactive | 30 | 5.819 | [4.611, 7.160] |
| surprise | rr | 30 | 10.403 | [8.389, 12.625] |

## Paired differences

| Scenario | Comparison | Difference pp | 95% CI pp |
|---|---|---:|---|
| delay-8 | predictive - reactive | -0.097 | [-0.208, 0.007] |
| delay-8 | predictive - edf | 0.215 | [-0.014, 0.465] |
| delay-8 | predictive - pf | -2.993 | [-4.028, -2.076] |
| delay-8 | predictive - persistence | -0.097 | [-0.208, 0.007] |
| delay-8 | predictive - oracle | 0.014 | [-0.069, 0.104] |
| id-0 | predictive - reactive | 0.049 | [-0.042, 0.153] |
| id-0 | predictive - edf | 0.056 | [-0.111, 0.215] |
| id-0 | predictive - pf | -3.014 | [-4.076, -2.042] |
| id-0 | predictive - persistence | 0.049 | [-0.042, 0.153] |
| id-0 | predictive - oracle | 0.056 | [-0.083, 0.215] |
| noise-4 | predictive - reactive | -0.083 | [-0.208, 0.049] |
| noise-4 | predictive - edf | 0.056 | [-0.174, 0.299] |
| noise-4 | predictive - pf | -1.556 | [-2.194, -0.951] |
| noise-4 | predictive - persistence | -0.083 | [-0.208, 0.049] |
| noise-4 | predictive - oracle | 0.090 | [-0.063, 0.278] |
| ood-layout-speed | predictive - reactive | -1.076 | [-2.403, 0.201] |
| ood-layout-speed | predictive - edf | 5.618 | [3.319, 7.701] |
| ood-layout-speed | predictive - pf | 0.451 | [-1.708, 2.639] |
| ood-layout-speed | predictive - persistence | -1.076 | [-2.403, 0.201] |
| ood-layout-speed | predictive - oracle | -0.493 | [-1.778, 0.729] |
| smooth | predictive - reactive | 0.028 | [-0.139, 0.257] |
| smooth | predictive - edf | 0.139 | [-0.042, 0.333] |
| smooth | predictive - pf | -2.847 | [-3.799, -1.944] |
| smooth | predictive - persistence | 0.028 | [-0.139, 0.257] |
| smooth | predictive - oracle | 0.090 | [-0.097, 0.361] |
| surprise | predictive - reactive | 0.111 | [-0.076, 0.319] |
| surprise | predictive - edf | 0.201 | [0.014, 0.389] |
| surprise | predictive - pf | -3.056 | [-3.931, -2.264] |
| surprise | predictive - persistence | 0.111 | [-0.076, 0.319] |
| surprise | predictive - oracle | 0.264 | [0.063, 0.507] |

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
