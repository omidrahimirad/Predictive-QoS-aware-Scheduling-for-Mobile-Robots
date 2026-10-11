# Reproducible experiment report

Status: **complete**.
Profile: **quick**. quick; n=1–1 independent episodes/cell.

Independent synthetic NR-inspired simulation; no HHI affiliation or standards conformance.

## Design

See manifest.json for frozen configurations, splits, model/trace provenance, and runtime.
Primary comparison: predictive minus reactive; EDF is the second reference.
Negative violation differences favor prediction; positive goodput differences favor prediction.
ID and OOD results remain separate. No significance tests were performed.

## Scenario definitions

| Scenario | Load | Speed m/s | Blockage dB | Domain |
|---|---:|---:|---:|---|
| id-0 | 1.5 | 1 | 22 | id |

## Primary endpoint

Macro-mean control violation ratio; 95% CI from resampling independent episodes.

| Scenario | Policy | Episodes | Mean % | 95% CI % |
|---|---|---:|---:|---|
| id-0 | predictive | 1 | 2.708 | [2.708, 2.708] |

## Paired differences

| Scenario | Comparison | Difference pp | 95% CI pp |
|---|---|---:|---|

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
