# Robust predictive scheduling v0.2

Research question: can a causal reliability monitor mitigate forecast mismatch while
preserving useful best-effort throughput? This is an interpretable heuristic, not
an optimal allocator or deadline guarantee. It keeps the existing simulator and
predictive/EDF implementations.

## Measurements and residuals

A forecast issued at slot t predicts true SINR at t+H. The fitted horizon H is selected
on validation. Runtime monitoring uses **observed** SINR, never true future SINR.
With observation delay d, a noisy sample stamped t+H arrives at t+H+d. Only then:

`a_i(t+H+d) = abs(predicted_db_i(t,H) - observed_db_i(t+H+d))` (dB).

Each UE's error EWMA is updated with smoothing beta=.05:
`m_i <- (1-beta)*m_i + beta*a_i`. Unmatured forecasts remain in a bounded pending
map keyed by target timestamp. Duplicate initial measurements do not update errors.
Skipped timestamps discard unmatched forecasts rather than using another target.
Future measurement timestamps and non-monotone decision times are rejected.
Episode reset clears all pending predictions and starts `m_i=b`, where b is the
mean absolute observable residual on separate calibration episodes (minimum .1 dB).

The prediction target remains true SINR in training. Online residuals include
measurement noise and delay and therefore are proxies for reliability, not exact
true-channel error. Noise and delayed recovery can keep the gate conservative.

## Training-feature envelope

For each predictor feature j, training-only .5th and 99.5th percentiles define L_j,U_j.
The current causal feature vector x_i produces dimensionless normalized excess:

`z_i = max_j max(L_j-x_ij, x_ij-U_j, 0) / max(U_j-L_j, 1)`.

The numerical floor is one unit in the respective feature's units. This cheap
coordinate-wise envelope is not a multivariate density test. Motion, position,
measurement history and age are checked, without any true blockage indicator.
It can miss in-envelope distribution shift and trigger on harmless speed changes.

## Gate and allocator

`r(t) = max(max_i m_i(t)/b, max_i z_i(t)/s_z)`; `c(t)=1/(1+r(t))`.

Here s_z=.1 and c is a bounded **diagnostic score**, not a calibrated probability.
With threshold tau chosen on development episodes:

- valid forecast and r <= tau: use the existing predictive allocation exactly;
- r > tau: use the existing EDF allocation exactly;
- missing/nonfinite/short/stale forecast or invalid reliability inputs: use EDF;
- first history-1 slots: no valid learned reliability forecast, so EDF.

The gate is global: a single troubled UE can switch the whole slot. This conservative
choice avoids mixing priority scales; it may lose throughput or overreact. Both
allocators use deadline demands, backlog eligibility and ACK-based PF rate history.
EDF serves nearest eligible control deadlines and uses PF when no control remains.
All allocations still obey nonnegative integer counts and the resource budget.

The **no-adaptation ablation** runs the same monitor but disables only the r>tau
switch; mandatory invalid-forecast EDF fallback remains. It otherwise uses exactly
the original predictive policy. Thus ablation differences isolate the global risk gate,
not a changed predictive score. Persistence and Reactive are decision-equivalent
for constant expected-service forecasts and common weights, as tested across an episode.

## Calibration and tuning

Predictor model/urgency/horizon are selected using validation seeds 12000–12003.
Observable-residual mean b and empirical q90 band use separate seeds 13000–13003.
The envelope uses training seeds 11000–11011 only. Thresholds {1.5,2.5,4} are tested
on development conditions A–H with three episode seeds each. Choose minimum mean
violation subject to aggregate mean BE >= .9 of PF; tie: higher BE, then lower tau.
If no threshold meets the floor, choose highest BE, then lower violation/tau and
record infeasibility. This development floor is neither per-condition nor a runtime
constraint. Final results may violate it.

The empirical ±q90 residual band reports observed-target coverage, separately from
true-SINR MAE/RMSE. It is **not** a conformal interval: time/UE correlation, model
selection, and shift do not justify exchangeability or OOD coverage guarantees.
See Angelopoulos and Bates, [A Gentle Introduction to Conformal Prediction](https://arxiv.org/abs/2107.07511v6),
2022 revision, for why formal interval claims require additional assumptions.
We chose an observable-residual monitor rather than uncalibrated tree disagreement.
The [ExtraTrees documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesRegressor.html)
describes the fitted estimator; dependency versions remain pinned in uv.lock.

## Cost and failure modes

Monitoring stores roughly H+d pending UE vectors and scans the current causal features.
Scheduling uses the unchanged greedy resource allocator. Per-slot Python mean/P99
time includes monitoring/gating but excludes batched ML inference. Inference timing
is separately saved; parallel worker contention makes both descriptive. These are
not deployable RAN processing measurements.

Unexpected outages cannot be anticipated from future innovations. The gate responds
only after observations reveal deterioration. No calibrated interval, safety proof,
or maximum-delay guarantee is claimed. EDF can still win; pure EDF is necessary to
identify whether switching adds any value beyond its conservative comparator.
