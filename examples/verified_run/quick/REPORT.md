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
| id-0 | 0.5 | 1 | 22 | id |
| id-1 | 1.5 | 1 | 22 | id |
| id-2 | 3 | 1 | 22 | id |
| ood-layout-speed | 2.5 | 6 | 28 | ood |

## Primary endpoint

Macro-mean control violation ratio; 95% CI from resampling independent episodes.

| Scenario | Policy | Episodes | Mean % | 95% CI % |
|---|---|---:|---:|---|
| id-0 | edf | 4 | 6.042 | [4.167, 7.500] |
| id-0 | oracle | 4 | 5.990 | [4.167, 7.396] |
| id-0 | persistence | 4 | 6.042 | [4.167, 7.396] |
| id-0 | pf | 4 | 6.562 | [4.115, 8.438] |
| id-0 | predictive | 4 | 5.990 | [4.167, 7.396] |
| id-0 | reactive | 4 | 6.042 | [4.167, 7.396] |
| id-0 | rr | 4 | 7.083 | [4.427, 8.698] |
| id-1 | edf | 4 | 4.635 | [3.229, 6.042] |
| id-1 | oracle | 4 | 4.792 | [3.542, 6.042] |
| id-1 | persistence | 4 | 4.844 | [3.490, 6.042] |
| id-1 | pf | 4 | 6.823 | [3.854, 8.750] |
| id-1 | predictive | 4 | 4.792 | [3.437, 6.146] |
| id-1 | reactive | 4 | 4.844 | [3.490, 6.042] |
| id-1 | rr | 4 | 8.802 | [6.510, 10.729] |
| id-2 | edf | 4 | 7.292 | [5.156, 8.802] |
| id-2 | oracle | 4 | 7.708 | [6.042, 9.271] |
| id-2 | persistence | 4 | 7.135 | [5.417, 8.646] |
| id-2 | pf | 4 | 14.010 | [11.458, 15.937] |
| id-2 | predictive | 4 | 7.083 | [5.260, 8.073] |
| id-2 | reactive | 4 | 7.135 | [5.417, 8.646] |
| id-2 | rr | 4 | 11.406 | [8.281, 13.437] |
| ood-layout-speed | edf | 4 | 69.010 | [58.177, 78.125] |
| ood-layout-speed | oracle | 4 | 73.594 | [64.792, 82.396] |
| ood-layout-speed | persistence | 4 | 72.865 | [62.917, 82.812] |
| ood-layout-speed | pf | 4 | 65.052 | [58.385, 68.646] |
| ood-layout-speed | predictive | 4 | 70.729 | [63.333, 78.125] |
| ood-layout-speed | reactive | 4 | 72.865 | [62.917, 82.812] |
| ood-layout-speed | rr | 4 | 64.427 | [56.302, 69.792] |

## Paired differences

| Scenario | Comparison | Difference pp | 95% CI pp |
|---|---|---:|---|
| id-0 | predictive - reactive | -0.052 | [-0.156, 0.000] |
| id-0 | predictive - edf | -0.052 | [-0.156, 0.000] |
| id-0 | predictive - pf | -0.573 | [-1.094, 0.104] |
| id-0 | predictive - persistence | -0.052 | [-0.156, 0.000] |
| id-0 | predictive - oracle | 0.000 | [0.000, 0.000] |
| id-1 | predictive - reactive | -0.052 | [-0.312, 0.156] |
| id-1 | predictive - edf | 0.156 | [0.000, 0.313] |
| id-1 | predictive - pf | -2.031 | [-3.125, -0.365] |
| id-1 | predictive - persistence | -0.052 | [-0.312, 0.156] |
| id-1 | predictive - oracle | -0.000 | [-0.156, 0.156] |
| id-2 | predictive - reactive | -0.052 | [-0.625, 0.625] |
| id-2 | predictive - edf | -0.208 | [-0.729, 0.208] |
| id-2 | predictive - pf | -6.927 | [-8.021, -5.833] |
| id-2 | predictive - persistence | -0.052 | [-0.625, 0.625] |
| id-2 | predictive - oracle | -0.625 | [-1.250, 0.208] |
| ood-layout-speed | predictive - reactive | -2.135 | [-5.000, 0.781] |
| ood-layout-speed | predictive - edf | 1.719 | [-7.344, 9.375] |
| ood-layout-speed | predictive - pf | 5.677 | [1.250, 9.896] |
| ood-layout-speed | predictive - persistence | -2.135 | [-5.000, 0.781] |
| ood-layout-speed | predictive - oracle | -2.865 | [-4.948, -0.521] |

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
