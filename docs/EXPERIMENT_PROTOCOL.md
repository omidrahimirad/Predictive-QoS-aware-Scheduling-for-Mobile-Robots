# Robust v2 experiment protocol

Predeclared before executing final seed ranges. Historical `examples/verified_run/`
remains unchanged. Its 2,730 main and 2,160 ablation executions are inspected historical
evidence, never untouched evidence for v2.

## Split and selection ledger

| Purpose | Seeds | Use |
|---|---|---|
| Training | 11000–11011 | Fit four old predictor candidates; training envelope |
| Validation | 12000–12003 | Select point model, urgency {2,4}, horizon {4,16} |
| Residual calibration | 13000–13003 | Observable residual mean and empirical q90 |
| Development | 14000–14002 + 100*k | Three episodes for each A–H; select threshold |
| Reserved original-CLI test | 15000 | Dataset compatibility; excluded from v2 inference |
| Quick exploratory | 800000–800001 + 100*k | Two episodes per condition |
| Final held-out | 900000–900029 + 100*k | Thirty independent episodes per condition |

k=0..7 in the ordered config. Conditions use different independent seeds; all nine
policies within a condition reuse the same exogenous trace. Seed checks reject overlap
among all splits/profiles, and published historical 1000/2000/3000 ranges.
The same synthetic family and predeclared scenario descriptions are known during
development; untouched final seeds do not constitute independent real-world validation.

## Eight declared conditions

A moderate load/mild blockage; B load 3 and deadline 12 slots; C blockage 28 dB;
D speed 6 m/s; E frequent unexpected outages with 28 dB attenuation; F changed
attenuation layout; G 8-slot delay and 4 dB noise; H changed layout, speed 6, load 2.5,
32 dB attenuation and more outages. Exact settings are in configs/robust_v2.yaml.
All other simulator constants remain shared. None is selected after final outcomes.

## Freeze and execution

`robust-develop` fits/calibrates/selects on nonfinal data. Commit the validated source,
then `robust-freeze` requires clean Git state and writes model/config/calibration/source
SHA256 values, selected settings and code revision. `robust-evaluate` verifies all hashes
before accessing evaluation traces. A new source or config must use a new study and
fresh final seeds for confirmatory claims. Documentation after results may change,
but the frozen scientific source and numerical settings are retained.

The evaluation includes RR/PF/EDF/Reactive/Persistence/Predictive/diagnostic Oracle,
Robust, and Robust without adaptive fallback: eight conditions x30 seeds x9 policies
=2,160 planned final episode-policy executions. The integrated no-adaptation policy
and paired EDF/Reactive/Predictive comparisons constitute the mechanism ablation on
those same held-out traces. They are not an additional independent 2,160-sample study.
Development threshold sensitivity is exploratory. Pure EDF is the strong comparator.

Metrics/checkpoint files record exact exogenous trace hashes and conservation. Resuming
reuses matching checkpoints; corruption or differing freeze hashes is rejected.
Raw models and bulk traces remain ignored. The compact public v2 bundle holds configs,
selection metadata, freeze, manifests, episode metrics, comparisons, coverage/error
summaries, illustrative timelines, all generated figures and report.

## Estimands and uncertainty

Primary: macro-mean episode control violation, including all failure reasons.
Two central comparisons: Robust minus Predictive and Robust minus EDF within each
condition. Secondary comparisons include Reactive and no-adaptation. A 10,000-draw
paired percentile bootstrap resamples independent matched episodes with analysis seed
771. Effects use pp for violation and native units otherwise. Packet/slot resampling
is prohibited. All estimates and negative findings remain visible.

Eight conditions, four comparators and multiple metrics create many comparisons.
Reported 95% intervals are marginal, without familywise correction, and do not support
selective significance claims. Intervals can degenerate at zero failures. Thirty
short episodes do not establish rare-event reliability or duration convergence.

Secondary data: BE/total goodput, Jain fairness, delivery probability, conditional
p95/p99 latency, occupancy, resource utilization, whole-episode chunk/retry attempts,
true-SINR MAE/RMSE/persistence skill, observable residual q90 coverage, error conditional
on confidence, whole-episode fallback fraction, scheduling mean/P99 and inference time.
Coverage/confidence bins are descriptive correlated sample diagnostics; episode errors
are retained. Figures show macro episode uncertainty where relevant. Pareto frontiers
are descriptive over mean violation versus BE goodput or fairness, excluding oracle
as a deployable contender. Delivered-only latency must be read alongside losses.

## Simulator audit

Event timing, exact deadlines, admission/overflow, partial service, retry exhaustion,
flight reservations, unique-payload goodput, measurement-window/drain semantics,
delayed PF feedback and conservation remain covered by historical tests. v2 adds
observation stamps and diagnostic counters without changing those dynamics.

One retained abstraction deserves explicit attention: the private queue engine removes
physically completed packets before ACK maturity, so allocator eligibility can reflect
completion earlier than transmitter-only ACK knowledge would allow. PF updates wait
for ACKs and the new residual monitor waits for delayed channel measurements. This
queue abstraction is shared by all policies but limits claims of a complete transmitter
information model. A fully ACK-limited queue view is future simulator work, requiring
separate corrected campaigns; historical results are not silently overwritten.

No exact NR PHY/MAC/HARQ/RLC/PDCP/RRC, power optimization, industrial channel calibration,
robot loop or safety validation is implemented. Shannon capacity and sigmoid errors
remain surrogates. Freeze provenance and numerical verification are necessary but
cannot remove these modeling limitations.
