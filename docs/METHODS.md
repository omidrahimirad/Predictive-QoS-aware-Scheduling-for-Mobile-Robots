# Methods

For the v0.2 robustness extension, see [robust scheduling](ROBUST_SCHEDULING.md)
and the [new evaluation protocol](EXPERIMENT_PROTOCOL.md). Historical numerical
results in the original sections remain preserved as prior evidence; the new v0.2
sections are labeled separately.


## Historical v0.1 model and protocol

## Model and units

One downlink cell serves 12 moving UEs by default. Slot duration is 0.5 ms; each
slot has 24 abstract frequency-flat resource units of 360 kHz. The unit is inspired
by NR mu=1 but does not implement exact resource-element or TBS processing.

Per-unit transmit power is -8 dBm, held constant across allocations (fixed PSD).
Noise is -174 dBm/Hz integrated over unit bandwidth with 7 dB noise figure;
exogenous interference is -96 dBm per unit. Noise and interference add in linear
mW, then convert back to dBm. Allocating more units changes aggregate radiated
power; the simulator does not impose a fixed total-cell-power constraint.

Synthetic path loss is `32.4 + 20 log10(3.5) + 25 log10(max(distance_m,1))` dB.
It is a transparent chosen surrogate, not a copied 38.901 scenario equation.
Residual fading in dB follows `z[t]=.98*z[t-1]+sqrt(1-.98^2)*N(0,2^2)`.
Its stationary standard deviation is 2 dB, with a fixed per-slot correlation.

The 40 m square contains bounded trajectories initialized in [12,28] m on each
axis, random headings, and modest heading changes every 400 slots. Positions are
reflected at [1,39] m. The base station is at (20,20) m. Speed is configurable.
A sigmoid attenuation zone crosses x=21 m for ID; OOD changes to y=16 m.
Surprise outages start independently with probability .0008 per UE-slot and persist
24 slots. Blockage attenuation is the larger of zone and surprise attenuation.
Future surprise onsets are never features. The model is illustrative, not a
validated industrial propagation environment.

Service opportunity per unit, in bits, is:

`c_i(t) = floor(B * dt * .75 * min(6, log2(1+SINR_i(t))))`.

The error-free analytical mode sets chunk success probability to 1. Otherwise
`p_i(t) = sigmoid(SINR_dB/2.5)`. This deliberately simple error curve is not measured
BLER and does not implement link adaptation. The Shannon formula motivates a
service approximation; actual short-packet coding, finite blocklength, signaling,
frequency selectivity, and implementation loss are absent.

## Traffic and queue discipline

Each UE has periodic control traffic: 2,048 bits every 20 slots, deadline 20 slots,
independently randomized phase. Best-effort packets are 12,000 bits, with Poisson
arrivals whose rate is `.035 * load * state_multiplier` per slot. The two on/off
states use multipliers 1.8 and .2 and switch with probability .01 per slot.
The total undelivered-payload buffer limit is 240,000 bits per UE; overflow drops
the new packet. Buffers include in-flight undelivered payload.

Control packets precede best effort within each allocated UE. Both classes are FIFO;
retry chunks for the current packet precede new portions of that packet. All policies
share this local discipline, buffer, channel/error abstraction, and retry handling.
Thus RR/PF are already paired with a control-first local queue discipline.

Chunks can split packets. Each UE-slot uses one indexed success variate, shared
by all payload chunks of that aggregate, so their successes are correlated. Successful
chunks physically deliver at slot end; acknowledgements arrive two additional slots
later by default. All pending chunks reserve their bits until feedback matures,
preventing duplicate service. Failed chunks retry only after feedback. Three attempts
include the initial attempt; a chunk exhausting its limit terminates the remaining
packet. No combining gain is modeled. A partly delivered failed packet contributes
its physically delivered unique bits to goodput but is not an on-time packet delivery.

## Event order and causal visibility

At integer t:

1. Process physical completions of the preceding slot at t (on time if t <= deadline).
2. Mature ACK/NACK feedback. ACKed unique bytes update the PF average; NACKed chunks
   become eligible to retry or trigger exhaustion.
3. Admit arrivals at t, checking buffers before dropping expired packets.
4. Drop still-active control packets whose deadline <= t.
5. Build the immutable observation; allocate resource units.
6. Serve during [t,t+1); schedule physical completion at t+1 and feedback later.

```text
t                      t+1                      t+1+feedback_delay
allocate -> transmit -> physical delivery ------ ACK/NACK eligible
```

Physical delivery is an evaluation fact; ordinary allocators do not receive the
true channel, future traces, or premature ACK-based rate estimates. Completed
packets have no remaining eligible bits, even while ACKs remain in flight.

Available new bits = size minus acknowledged bits minus all pending/reserved bits.
The observation contains eligible bits, control-demand/slack pairs, noisy delayed
channel service, estimated success probability, and ACK-updated rate averages.
An ordinary forecast is computed from causal features. Only the isolated diagnostic
oracle is given true future channel service, never future arrivals.

Measurements have two-slot delay and .8 dB independent Gaussian noise by default.
Before a delayed history exists, the initial measurement is held. Optional uniform
dB quantization uses `observation_quantization_db`; zero disables it. This is not
standardized CQI mapping. Observation age is an explicit feature.

## Exact allocator equations

The allocators greedily assign one resource unit at a time. No UE with zero eligible
payload or zero estimated expected service is selected. Stop allocating to UE i when
`allocated_i * observed_capacity_i >= eligible_bits_i`. Remaining resources may idle.
Allocations are checked for integer, shape, budget, and eligibility constraints.

For PF, `e_i = observed_capacity_i * observed_success_probability_i` and
`PF_i = e_i / max(Rbar_i,1)` in consistent bits-per-slot units. Initialize Rbar=1.
Each slot: `Rbar_i <- .99 Rbar_i + .01 ACKed_unique_bits_i`, including idle slots.
PF scores are held fixed within the slot, not recomputed from hypothetical successes.
Normalize by `max(max_i PF_i, 1e-9)`. Ties choose lower UE index.

RR rotates its pointer after each allocated unit across eligible UEs. EDF uses the
nearest remaining eligible control deadline: score `1000+1/slack`; when no eligible
control demand remains, it uses normalized PF. It subtracts tentative expected
service when checking which demands remain uncovered.

For the hybrid family, control demands are ordered by deadline. Let D_ik be cumulative
eligible control bits through deadline k; tentative covered bits are `a_i*e_i`.
Remaining demand `U_ik=max(D_ik-a_i*e_i,0)`. For slack d, forecast opportunity is
`F_i(d)=sum_{h=1}^{min(d,H)} forecast_i(h) + max(d-H,0)*e_i`.
The reactive version substitutes `d*e_i` throughout. Define:

`urgency_i = max_k U_ik / max(F_i(d_k),1)`

`opportunity_i = max(e_i-mean_h forecast_i(h),0)/max(e_i,1)`

`score_i = normalized_PF_i + w*min(urgency_i,10) + opportunity_i`

Opportunity is zero when no uncovered control demand remains, or in reactive mode.
The cap prevents numerical explosion under a near-zero forecast. Control demand is
recomputed after tentative allocations. This is a heuristic, not a solved optimal
control problem or hard deadline constraint. Forecast horizons beyond H persist at
current expected service. Invalid/missing/stale forecasts fall back to the same
reactive score and increment a counter. Default maximum forecast age is four slots.

The persistence variant uses e_i at every future slot. The oracle uses true future
capacity times true success probability. It does not know the random success draw,
future arrivals, or optimal policy. It is not a guaranteed upper bound.

Validation selects w from {2,4}, H from {4,16}, keeping opportunity weight=1.
Minimize average validation control violations subject to mean BE goodput >= .9 of
validation PF. Ties: larger BE goodput, then smaller w/H. If infeasible, use the same
ordering over all candidates and report infeasibility. Floors .8 and 1.0 are also
evaluated for sensitivity. Reactive and persistence evaluations use the selected
hybrid weights to keep structural comparisons aligned. No test tuning occurs.

## Predictors and splits

The target is true future exogenous SINR, not realized scheduler-dependent throughput.
Horizons: 1,2,4,8,16 slots. Feature vectors contain eight causal noisy SINR measurements,
current x/y position and vx/vy, and measurement age. A no-position variant removes
position and velocity together. No episode/route IDs or future coordinates enter features.

Candidates: standardized Ridge(alpha=10) and 48 ExtraTrees(max_depth=12,
min_samples_leaf=12, random_state=7), CPU single-threaded. Fit training only; select
the model with lower mean validation MAE across the five horizons. Convert forecast
SINR to expected service after linear interpolation across horizons. Before eight
measurements exist, use persistence.

Base grouped split: 12 training seeds 1000–1011; four validation seeds 2000–2003;
four untouched test seeds 3000–3003 (60/20/20). Sliding windows never cross episodes.
Training labels exclude the final 16 slots and drain. No chronological within-episode
split is performed, so no boundary purging is necessary. If such a split is added,
purge at least history plus maximum target horizon.

Full evaluation predeclares additional held-out seeds through 3029; this extends the
test set rather than preserving the original 60/20/20 ratio. Both fitting splits and
actual evaluation seeds are retained in manifests. OOD uses changed layout/speed/load/
blockage, without refitting. Train and test still share a synthetic generator family.
Prediction MAE/RMSE and persistence skill are pooled descriptive sample metrics, not
independent-sample inferential statistics. Blocked labels are evaluation-only.

## Cohorts, metrics, and inference

Warmup: 100 slots. Measurement: 800 slots (0.4 s). Drain: 40 slots, no new arrivals.
Measurement-cohort membership depends on arrival in [warmup,warmup+duration).
Warm-up state persists but its arrivals are excluded from cohort delivery statistics.
Window goodput counts physically delivered unique bits in (warmup,warmup+duration],
including old warm-up packets; it does not include drain deliveries.

Primary violation = 1 - on-time cohort control deliveries / cohort control arrivals.
Failure reasons are mutually exclusive: overflow, retry exhaustion, deadline expiration,
late delivery, or censoring. Deadline-expiration-only ratio is separately reported.
Zero arrivals yield NaN, not zero. BE unresolved at drain is censored. Conservation:
generated bits = delivered unique bits + discarded undelivered bits + unresolved bits.

Delivered-only latency is completion minus arrival. Its quantiles suffer survivor
bias and must be accompanied by violation counts. Jain fairness is over window
per-UE aggregate goodput and is undefined when all UEs deliver zero bits.
Chunk-attempt counters span the complete episode, while resource/queue averages
span the measurement window; their different windows are intentional and labeled.

Policy-independent SeedSequence streams separate mobility, channel/disruption,
measurement noise, traffic, and uniform service draws. Paired policies reuse the
same indexed traces; policy decisions do not consume the environmental RNG.
Hashes cover all exogenous arrays. Individual chunk outcomes can differ because
policies transmit different packets at different slots.

The independent episode is the statistical unit. Bootstrap 10,000 episode means
with analysis seed 771, using 2.5/97.5 percentiles. Paired differences resample matched
episode differences, asserting matching trace hashes. Primary comparison: predictive
minus reactive, then EDF. Negative violation differences favor prediction and are
reported in percentage points. Macro-mean ratios and raw counts are retained;
pooled packet-weighted ratios can be computed from raw counts but are not substituted
for the macro estimate. No hypothesis tests or significance claims are made.

Tail intervals compare per-episode p99 values, not unconditional population p99.
Zero-failure bootstrap intervals can be degenerate. A packet-level binomial bound
would require unjustified independence and is deliberately not claimed.

## Pilot and frozen campaigns

Before held-out evaluation, seed 2000 pilots used loads .5/1.5/3 and blockage 18/28 dB.
Reactive-control violation ratios ranged roughly .006–.325 and utilization .38–1.0
in that pilot implementation. These checks motivated including both mild and severe
conditions; they are development observations, not final test results. No final result
is derived from those pilots. Model/weight selection is subsequently frozen on validation.

Quick: three loads, speed 1 m/s, blockage 22 dB, four episodes each, plus OOD.
Full: three loads x two speeds (1,4) x two blockage levels (18,28), 30 episodes each,
plus OOD. Ablations add no-position features, horizons 1/4/8/16, delayed observation,
larger noise, smooth channels, and surprise blockage. Configurations were defined
before test results were inspected; no tuning is justified by those test results.

An 800-slot window is a bounded portfolio benchmark, not evidence of stationary
long-duration queueing performance. Warmup/duration convergence studies are future
work. Full status and actual runtime appear in PROJECT_STATUS and manifests.

## Version 0.2 methods

The original system model and allocator equations above remain unchanged. New causal
measurement timestamps, observable-residual monitoring, training-feature envelopes and
Predictive/EDF switching are defined in [ROBUST_SCHEDULING](ROBUST_SCHEDULING.md).
[EXPERIMENT_PROTOCOL](EXPERIMENT_PROTOCOL.md) defines the new splits, freeze, eight
conditions, matched comparisons, integrated mechanism ablation and audit limitations.
Whole-episode retry-chunk attempts are now recorded separately from all chunk attempts.
New raw summaries retain every secondary metric and compare both BE and fairness
Pareto trade-offs descriptively; no optimality or safety guarantee follows.
