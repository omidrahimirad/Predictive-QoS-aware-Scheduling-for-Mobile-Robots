# Scientific limitations

For the v0.2 robustness extension, see [robust scheduling](ROBUST_SCHEDULING.md)
and the [new evaluation protocol](EXPERIMENT_PROTOCOL.md). Historical numerical
results below remain preserved and are labeled as prior evidence.


This software studies a scheduling hypothesis in a synthetic model. It does not
certify industrial wireless reliability or closed-loop robot safety.

- Single-cell downlink with common local queue discipline; no uplink BSR, multicell
  interference coupling, handover, beam management, or admission-control protocol.
- Frequency-flat PRB-equivalents and Shannon-based bit budgets, not exact NR MCS,
  TBS, resource-element overhead, coding, finite-blocklength analysis, or waveforms.
- Fixed per-unit PSD means aggregate cell power increases with allocation. No total
  transmit-power optimization or energy-performance claim is supported.
- Synthetic path loss, dB correlated fading, blockage, and sigmoid error probability;
  no measured industrial calibration, 38.901 conformance, or real-world validation.
- ARQ-like chunk retries without HARQ soft combining or finite-process scheduling.
  Per-UE-slot chunks have correlated success. Feedback delay, buffer bookkeeping,
  and partial-packet accounting are explicit but still abstractions.
- No RLC, PDCP, SDAP, RRC, core network, application processing, or robot control-loop
  simulation. Application packet deadlines are not exact standardized 5QI budgets.
  Queue/radio latency cannot be called end-to-end robot-control latency.
- Causal noisy measurements and point forecasts are not perfect CSI or uncertainty
  guarantees. Forecast fallbacks protect software operation, not safety.
- One training environment and synthetic generator family: position features may
  memorize maps. OOD and no-position experiments test only selected shifts.
- The heuristic has no proof of optimality, stability, or guaranteed deadline
  satisfaction. Its validation goodput floor is not a hard runtime constraint.
  The future-channel oracle is a diagnostic reference, not an optimization bound.
- Four-episode quick studies are exploratory. Delivered-only latency is biased by
  drops; packet/slot samples are correlated. Zero failures do not prove five-nines
  reliability. Bootstrap uncertainty is conditional on the chosen episode family.
- Short 0.4-second measurement windows and fixed warmup limit queue equilibrium and
  rare-event claims. No duration-convergence evidence is claimed. Larger campaigns
  do not repair model mismatch by themselves.
- Scheduler timings depend on machine and implementation. No real-time deployment
  or RAN processing-budget compliance is established.

Useful next work: longer-window convergence, calibrated industrial channel traces,
validated MCS/BLER/TBS, total-power constraints, correlated measurement uncertainty,
calibrated interval prediction, ns-3/5G-LENA cross-checks, and communication-control
co-design. RL and AoI require separate hypotheses, baselines, and semantics before
being added. They are not implemented features of this version.
