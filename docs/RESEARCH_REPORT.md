# Predictive QoS-aware Scheduling for Mobile Robots

For the v0.2 robustness extension, see [robust scheduling](ROBUST_SCHEDULING.md)
and the [new evaluation protocol](EXPERIMENT_PROTOCOL.md). Historical numerical
results in the original sections remain preserved as prior evidence; the new v0.2
sections are labeled separately.


## Historical v0.1 research report

## Abstract

This independent Python study tests a causal channel-prediction heuristic for
deadline-constrained downlink scheduling in a synthetic mobile-robot scenario.
The implementation compares seven allocators, uses episode-grouped model selection,
and reports paired bootstrap uncertainty. The full main campaign covers 13 conditions
with 30 independent episodes per condition. Prediction provides selected modest
improvements over a structurally matched reactive method, but it does not consistently
beat EDF. Severe blockage and environmental shift expose material weaknesses.
The contribution is a reproducible model and evaluation pipeline, not a certified
industrial communication system, new theoretical guarantee, or claimed publication.

## Motivation and related work

The HHI 6G role motivating this portfolio emphasizes ML resource allocation, selected
3GPP functions, statistics, and information theory. Historical AI4Mobile work motivates
using QoS forecasts to configure mobile systems proactively. Palaios et al. discuss
practical challenges of vehicular QoS prediction. These are research connections,
not proof that the vacancy belongs to a particular project or that HHI endorses this work.
Primary references and pinned standard clauses appear in STANDARDS_MAPPING.md.

## Research hypothesis

For already queued deadline-constrained packets, a predicted near-future deterioration
may justify service earlier than a reactive allocator would choose. The hypothesis
must be tested against strong deadline and queue-aware policies, not only RR/PF.
The primary endpoint is delivery violation ratio, including non-deadline packet
failures. The main tradeoff is best-effort goodput; fairness and conditional latency
provide complementary views. No prospective result was assumed to be positive.

## System model

A single-cell downlink serves finite control and bursty best-effort queues. Mobile
trajectories, correlated dB channel residuals, attenuation zones, and random outages
create channel variation. The fixed-PSD Shannon surrogate provides per-resource bit
budgets; chunk failures and delayed feedback create retries. The model separates
physical delivery from ACK-based allocator information. METHODS.md defines units,
timing, equations, buffer behavior, conservation, and observation semantics.

This abstraction is relevant to resource-allocation reasoning but omits waveforms,
exact MCS/TBS, full HARQ, bearer protocols, core-network delay, and robot dynamics.
Information-theory exposure here is limited to capacity intuition and its limitations;
the project does not demonstrate advanced finite-blocklength theory or prove reliability.

## Algorithms and learning

RR, PF, and EDF are compared with reactive QoS, persistence forecasts, learned forecasts,
and a diagnostic future-channel reference. All share a control-first local queue discipline.
The hybrid score combines normalized PF with cumulative deadline-demand urgency and
the opportunity to use a presently better channel. It is interpretable and bounded,
but does not solve a global constrained optimization problem.

Ridge and ExtraTrees predict exogenous future SINR, using causal measurement history
and motion features. Model selection and scheduler weights use validation only.
Entire episodes form disjoint splits. A no-position/motion variant, horizon studies,
measurement sensitivity, and surprise-channel tests examine mechanism and robustness.

## Evaluation

The full main factorial experiment uses three loads, two speeds, and two blockage
severities, plus a changed-layout OOD condition. Each condition has 30 independent
episode seeds. All policies share exogenous arrays and indexed service draws.
The episode, not the packet or slot, is the bootstrap unit. Primary paired differences
compare prediction with reactive QoS and EDF. No significance tests or claims of
universal superiority are made. The short measurement window is a bounded benchmark;
there is no claimed warmup/duration convergence or rare-event certification.

## Findings

The exact tables and intervals are in RESULTS.md and the saved full report. Prediction
has a limited effect relative to the reactive score in many mild conditions. In a
moderate-load severe-blockage condition (load 1.5, speed 1 m/s, blockage 28 dB), it
reduces violations versus reactive by about 1.056 pp, but has about 7.243 pp more
violations than EDF. That strong comparator changes the interpretation of the result.

The OOD mean control violation is about 51.340% for prediction and 45.722% for EDF.
The paired difference is 5.618 pp, with 95% CI [3.319,7.701] pp. Prediction's descriptive
BE goodput is higher (6.658 versus 4.918 Mbit/s), illustrating the tradeoff. These
large modeled failure rates also make clear that the project is not an URLLC achievement.

The learned model's forecast skill deteriorates sharply after environment shift.
Better average ID prediction does not ensure better deadline scheduling or reliable
OOD behavior. A perfect future-channel heuristic can also lose, because information
quality does not repair the heuristic's objectives and choices automatically.

The separate full ablation campaign contains 2,160 runs across six conditions and
12 variants, with 30 episodes per condition. All paired predictive-versus-reactive
violation intervals include zero there. The observed sensitivity to horizons and
features does not establish a universal best setting. See RESULTS.md for the variant
table and complete uncertainty artifacts.

## Scientific limitations and next steps

LIMITATIONS.md details the synthetic model, incomplete protocol scope, fixed PSD,
short windows, point forecasts, map memorization, and lack of robot-control validation.
First extensions should be longer-window convergence, calibrated measured channels,
validated link abstraction, and power constraints. Robust model selection across
several training environments is a more useful next step than adding a larger model
without improving the evaluation design. RL, AoI, and communication-control co-design
require separate problem definitions and baselines.

## Reproduction

README.md provides the tested commands, locked environment, and output layout.
The verified bundle contains configurations, raw episode summaries, model-selection
metadata, uncertainty tables, reports, and inspected figures. Model binaries and bulk
traces are regenerated locally rather than committed. No external results, affiliations,
publications, DOI, or execution outcomes are invented.

## v0.2 research report — robustness extension

### Abstract

A causal reliability gate combines delayed observed forecast errors and a training-feature
envelope to select Predictive or EDF allocation. A frozen eight-condition study uses 30
new independent episodes per condition and nine policies, including a no-adaptation
ablation. Robust mitigates forecast-related failures in selected conditions but trades
away BE throughput and does not consistently beat EDF. The contribution is an auditable
implementation and evaluation, not an optimality or reliability guarantee.

### Motivation and research questions

Can uncertainty-aware scheduling improve robustness under model mismatch while keeping
acceptable BE throughput? When should learned forecasts be trusted rather than replaced
by deadline protection? Previously inspected test data motivates the questions, but is
not treated as untouched evidence for the new algorithm.

### System model and algorithms

The historical slot/queue/channel/chunk model is retained. All policies share resources,
traffic, noise, error draws and feedback rules. Existing GreedyScheduler priorities are
unchanged. A binary global gate avoids arbitrary mixing of incomparable scores and uses
exact Predictive or EDF decisions. Pure EDF remains the strong classical comparator;
the diagnostic oracle has future-channel information and is not a deployable bound.

### Uncertainty estimation

A forecast target becomes eligible for error monitoring only when its delayed noisy
measurement arrives. EWMA errors are normalized by a separate calibration mean. Current
features are compared with a train-only percentile envelope. Maximum normalized risk
controls the switch. The bounded confidence score and empirical q90 residual band are
diagnostics, not calibrated probabilities or conformal intervals. ROBUST_SCHEDULING
defines every variable, threshold, causal update and failure mode.

### Experimental methodology

Disjoint training, validation, calibration and development episodes precede a clean-source
freeze. The final source/model/config/calibration hashes were checked before accessing
seeds 900000–900729 in eight disjoint 30-seed ranges. Point model/policy selection uses
validation only; risk threshold selection uses development only. No tuning follows final
inspection. Paired intervals resample independent matched episodes 10,000 times. Multiple
marginal comparisons are not familywise corrected. The no-adaptation ablation is integrated
into the same final campaign; it is not independent additional evidence.

### Results

The final campaign completed 2,160 episode-policy executions; the exploratory profile
completed 144. Under deterioration E, Robust reduces control violations relative to
Predictive by 13.396 pp (95% paired CI [-16.827,-10.083]), while BE decreases from 8.061
to 6.311 Mbit/s. Under severe blockage C, Robust improves over Predictive by 5.826 pp
but is 7.632 pp worse than EDF (CI [5.146,10.486]). Conditions D/G/H use EDF for 100%
of slots. F shows a modest -.257 pp difference against EDF, with a marginal interval
excluding zero; multiplicity and small effect size constrain its interpretation.
All eight conditions, uncertainty tables, secondary metrics and unfavorable outcomes
are in RESULTS and the raw bundle. The .9-of-PF development BE floor was infeasible.

### Discussion

The monitor can repair some poor predictive decisions by abstaining, but pure EDF often
provides most of the benefit. In H, the algorithm exactly becomes EDF and roughly halves
BE goodput relative to Predictive. It is not a new superior scheduler in that condition.
EDF protects immediate deadlines directly; a forecast score can misprioritize future
opportunity or distribute service to BE/fairness objectives. Better average channel MAE
need not improve deadline satisfaction: event timing, queue demand, policy objectives
and rare errors matter. D demonstrates that the shift detector may reject a predictor
whose forecast skill remains positive. G has useful learned SINR error reduction, yet
measurement-age shift still keeps the allocator in EDF. Threshold validation provides
a reproducible choice, not a universal reliability-throughput constraint.

### Limitations

Synthetic channels and errors, one training environment, short windows, fixed PSD and
no robot loop constrain external validity. Eligibility can reflect physical completion
before ACK arrival: the shared engine is not a full transmitter information model.
Confidence is uncalibrated; outage detection is delayed; maximum-over-UE switching can
overreact. Marginal bootstrap intervals, finite samples and conditional latency cannot
establish URLLC, real-world safety, optimality or full 3GPP compliance. Python timings
exclude batch inference and do not establish RAN deployment feasibility.

### Future research

Evaluate measured industrial channels, duration convergence and a fully ACK-limited queue
view in separate campaigns. Test calibrated uncertainty with explicit temporal dependence
assumptions, per-UE abstention and thresholds tuned across more environments. Validate
MCS/BLER/TBS, fixed total-power constraints and communication-control co-design before
hardware deployment. A later outcome-driven iteration needs a fresh final set.

### References and reproducibility

METHODS, ROBUST_SCHEDULING and EXPERIMENT_PROTOCOL specify equations and reproduction.
STANDARDS_MAPPING retains primary 3GPP/ETSI, HHI and ML references, with modeled versus
omitted behavior. Angelopoulos and Bates (2022 revision, arXiv:2107.07511v6) informs the
limits on interval claims; no formal conformal guarantee is implemented here.

[Full v2 report](../examples/robust_scheduling_v2/full/REPORT.md) ·
[Measured results](RESULTS.md) ·
[Freeze manifest](../examples/robust_scheduling_v2/selection/freeze.json)
