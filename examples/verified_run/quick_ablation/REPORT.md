# Reproducible experiment report

Status: **complete**.
Profile: **quick**. quick; n=4–4 independent episodes/cell.

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
| delay-8 | edf | 4 | 4.740 | [3.333, 6.146] |
| delay-8 | horizon_1 | 4 | 4.844 | [3.229, 6.458] |
| delay-8 | horizon_16 | 4 | 4.844 | [3.229, 6.458] |
| delay-8 | horizon_4 | 4 | 4.844 | [3.229, 6.458] |
| delay-8 | horizon_8 | 4 | 4.844 | [3.229, 6.458] |
| delay-8 | no_position | 4 | 4.948 | [3.229, 6.667] |
| delay-8 | oracle | 4 | 4.792 | [3.125, 6.458] |
| delay-8 | persistence | 4 | 5.104 | [3.333, 6.875] |
| delay-8 | pf | 4 | 6.719 | [3.750, 8.490] |
| delay-8 | predictive | 4 | 4.844 | [3.229, 6.458] |
| delay-8 | reactive | 4 | 5.104 | [3.333, 6.875] |
| delay-8 | rr | 4 | 8.906 | [6.615, 10.729] |
| id-0 | edf | 4 | 4.635 | [3.229, 6.042] |
| id-0 | horizon_1 | 4 | 4.844 | [3.490, 6.042] |
| id-0 | horizon_16 | 4 | 4.948 | [3.698, 6.146] |
| id-0 | horizon_4 | 4 | 4.792 | [3.437, 6.146] |
| id-0 | horizon_8 | 4 | 4.844 | [3.542, 6.146] |
| id-0 | no_position | 4 | 4.792 | [3.437, 6.146] |
| id-0 | oracle | 4 | 4.792 | [3.542, 6.042] |
| id-0 | persistence | 4 | 4.844 | [3.490, 6.042] |
| id-0 | pf | 4 | 6.823 | [3.854, 8.750] |
| id-0 | predictive | 4 | 4.792 | [3.437, 6.146] |
| id-0 | reactive | 4 | 4.844 | [3.490, 6.042] |
| id-0 | rr | 4 | 8.802 | [6.510, 10.729] |
| noise-4 | edf | 4 | 5.365 | [3.594, 6.458] |
| noise-4 | horizon_1 | 4 | 5.156 | [3.229, 6.771] |
| noise-4 | horizon_16 | 4 | 5.052 | [3.542, 6.250] |
| noise-4 | horizon_4 | 4 | 5.208 | [3.385, 6.771] |
| noise-4 | horizon_8 | 4 | 5.156 | [3.490, 6.667] |
| noise-4 | no_position | 4 | 5.208 | [3.437, 6.875] |
| noise-4 | oracle | 4 | 5.000 | [3.333, 6.562] |
| noise-4 | persistence | 4 | 5.417 | [3.385, 6.875] |
| noise-4 | pf | 4 | 6.406 | [4.062, 8.594] |
| noise-4 | predictive | 4 | 5.208 | [3.385, 6.771] |
| noise-4 | reactive | 4 | 5.417 | [3.385, 6.875] |
| noise-4 | rr | 4 | 9.115 | [6.927, 10.729] |
| ood-layout-speed | edf | 4 | 69.010 | [58.177, 78.125] |
| ood-layout-speed | horizon_1 | 4 | 73.125 | [62.083, 84.167] |
| ood-layout-speed | horizon_16 | 4 | 76.667 | [64.948, 88.177] |
| ood-layout-speed | horizon_4 | 4 | 70.729 | [63.333, 78.125] |
| ood-layout-speed | horizon_8 | 4 | 71.927 | [62.604, 81.250] |
| ood-layout-speed | no_position | 4 | 72.083 | [63.125, 81.042] |
| ood-layout-speed | oracle | 4 | 73.594 | [64.792, 82.396] |
| ood-layout-speed | persistence | 4 | 72.865 | [62.917, 82.812] |
| ood-layout-speed | pf | 4 | 65.052 | [58.385, 68.646] |
| ood-layout-speed | predictive | 4 | 70.729 | [63.333, 78.125] |
| ood-layout-speed | reactive | 4 | 72.865 | [62.917, 82.812] |
| ood-layout-speed | rr | 4 | 64.427 | [56.302, 69.792] |
| smooth | edf | 4 | 4.479 | [2.917, 6.042] |
| smooth | horizon_1 | 4 | 4.583 | [3.125, 6.042] |
| smooth | horizon_16 | 4 | 4.844 | [3.281, 6.250] |
| smooth | horizon_4 | 4 | 4.687 | [3.229, 6.146] |
| smooth | horizon_8 | 4 | 4.635 | [3.125, 6.146] |
| smooth | no_position | 4 | 4.740 | [3.229, 6.146] |
| smooth | oracle | 4 | 4.635 | [3.229, 6.042] |
| smooth | persistence | 4 | 4.740 | [3.229, 6.146] |
| smooth | pf | 4 | 6.979 | [3.385, 9.115] |
| smooth | predictive | 4 | 4.687 | [3.229, 6.146] |
| smooth | reactive | 4 | 4.740 | [3.229, 6.146] |
| smooth | rr | 4 | 8.646 | [6.042, 10.625] |
| surprise | edf | 4 | 5.312 | [3.854, 6.250] |
| surprise | horizon_1 | 4 | 5.365 | [3.698, 6.562] |
| surprise | horizon_16 | 4 | 5.469 | [3.854, 6.615] |
| surprise | horizon_4 | 4 | 5.625 | [4.167, 6.771] |
| surprise | horizon_8 | 4 | 5.312 | [3.698, 6.510] |
| surprise | no_position | 4 | 5.521 | [3.698, 7.031] |
| surprise | oracle | 4 | 5.417 | [3.542, 6.667] |
| surprise | persistence | 4 | 5.521 | [3.906, 6.615] |
| surprise | pf | 4 | 8.177 | [5.573, 10.000] |
| surprise | predictive | 4 | 5.625 | [4.167, 6.771] |
| surprise | reactive | 4 | 5.521 | [3.906, 6.615] |
| surprise | rr | 4 | 10.312 | [8.125, 11.875] |

## Paired differences

| Scenario | Comparison | Difference pp | 95% CI pp |
|---|---|---:|---|
| delay-8 | predictive - reactive | -0.260 | [-0.521, -0.052] |
| delay-8 | predictive - edf | 0.104 | [-0.260, 0.365] |
| delay-8 | predictive - pf | -1.875 | [-3.333, -0.312] |
| delay-8 | predictive - persistence | -0.260 | [-0.521, -0.052] |
| delay-8 | predictive - oracle | 0.052 | [0.000, 0.156] |
| id-0 | predictive - reactive | -0.052 | [-0.312, 0.156] |
| id-0 | predictive - edf | 0.156 | [0.000, 0.313] |
| id-0 | predictive - pf | -2.031 | [-3.125, -0.365] |
| id-0 | predictive - persistence | -0.052 | [-0.312, 0.156] |
| id-0 | predictive - oracle | -0.000 | [-0.156, 0.156] |
| noise-4 | predictive - reactive | -0.208 | [-0.469, 0.000] |
| noise-4 | predictive - edf | -0.156 | [-0.625, 0.365] |
| noise-4 | predictive - pf | -1.198 | [-2.240, -0.312] |
| noise-4 | predictive - persistence | -0.208 | [-0.469, 0.000] |
| noise-4 | predictive - oracle | 0.208 | [0.000, 0.417] |
| ood-layout-speed | predictive - reactive | -2.135 | [-5.000, 0.781] |
| ood-layout-speed | predictive - edf | 1.719 | [-7.344, 9.375] |
| ood-layout-speed | predictive - pf | 5.677 | [1.250, 9.896] |
| ood-layout-speed | predictive - persistence | -2.135 | [-5.000, 0.781] |
| ood-layout-speed | predictive - oracle | -2.865 | [-4.948, -0.521] |
| smooth | predictive - reactive | -0.052 | [-0.156, 0.000] |
| smooth | predictive - edf | 0.208 | [0.000, 0.469] |
| smooth | predictive - pf | -2.292 | [-3.750, -0.313] |
| smooth | predictive - persistence | -0.052 | [-0.156, 0.000] |
| smooth | predictive - oracle | 0.052 | [-0.104, 0.208] |
| surprise | predictive - reactive | 0.104 | [-0.104, 0.313] |
| surprise | predictive - edf | 0.312 | [0.104, 0.521] |
| surprise | predictive - pf | -2.552 | [-3.854, -1.250] |
| surprise | predictive - persistence | 0.104 | [-0.104, 0.313] |
| surprise | predictive - oracle | 0.208 | [-0.104, 0.625] |

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
