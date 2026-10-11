# Codex implementation prompt: Predictive QoS-aware Scheduling for Mobile Robots

Provenance: copied from the user-approved local specification; personal absolute paths normalized to ~/Documents for repository portability.

Prepared on 11 October 2026. This file is a specification and executable work brief, not an implemented project or experimental result. Copy the prompt below into Codex when ready to implement.

## Implementation prompt

You are implementing a complete, reproducible Python research project named **Predictive QoS-aware Scheduling for Mobile Robots** in this repository:
https://github.com/omidrahimirad/Predictive-QoS-aware-Scheduling-for-Mobile-Robots

The repository was publicly empty when inspected on 11 October 2026. Recheck its actual state before making changes. Deliver working software, meaningful tests, reproducible experiments, and honest scientific documentation. Do not stop at a skeleton or a proposal.

### 1. Purpose and scientific scope

Build a CPU-friendly, discrete-time, single-cell downlink simulator for mobile robotic UEs sharing limited radio resources. Compare classical schedulers with a causal, prediction-assisted QoS scheduler under periodic deadline-constrained control traffic and competing finite-rate best-effort traffic.

Research question: Does forecasting near-future channel deterioration reduce control-packet deadline violations compared with strong reactive schedulers, and what are the costs in best-effort goodput, fairness, resource use, and computation?

This portfolio project is motivated by Fraunhofer HHI's Berlin vacancy “Wissenschaftler*in 6G Mobilfunk”, reference 85806, inspected on 11 October 2026. The vacancy emphasizes resource allocation, ML at L2/L3, simulators of selected 3GPP functions, statistical analysis, scientific publications, and information theory. The displayed posting date was 9 October 2026 and deadline 24 October 2026. This is an independent portfolio project; do not imply HHI endorsement, affiliation, or that the employer requested this particular implementation. AI4Mobile is historical research context from 2020–2023, not evidence of the hiring team's project assignment.

Describe the software as **an NR-inspired abstract system-level scheduling simulator relevant to 6G research**. It is not a complete NR stack, validated 6G simulator, real robotic testbed, link-level waveform simulator, or safety guarantee. Keep the mandatory contribution narrow and executable. RL, AoI, robot control dynamics, multicell handover, and exact NR transport-block processing belong in documented future work unless the mandatory pipeline is already complete.

### 2. Workspace and Git management

Use the local Documents directory and prefer:
~/Documents/Personalprojects/Predictive-QoS-aware-Scheduling-for-Mobile-Robots/

Resolve the actual home and Documents paths; inspect existing folders and capitalization first. On this user's Mac, Documents is ~/Documents. Preserve the sibling project spec at Documents/Personalprojects/Predictive-QoS-aware-Scheduling-for-Mobile-Robots-SPEC.md. Do not overwrite unrelated projects or create duplicate nested clones. If an existing checkout of the exact repository is already attached to this chat, use it and record its location rather than cloning another copy.

Read applicable AGENTS.md and inspect Git status, remotes, branches, existing files, and available runtimes. Preserve user changes. Clone the exact remote if no suitable checkout exists. An empty remote may have no usable default branch: initialize its first branch safely and record that decision. Use a dedicated implementation branch where practical. Never reset user work, force-push, delete unrelated files, or change another repository's remote.

This prompt authorizes local implementation and local commits. Make coherent commits after relevant checks pass. Leave remote pushing and PR publication for explicit user authorization; do not claim anything was published unless verified. If a PR is subsequently authorized and created, attach it to the chat. Never embed credentials, personal application documents, or local absolute paths in public artifacts. Before committing, review staged content for generated bulk data and secrets.

Keep private scratch work in work/ and regenerable outputs in ignored data/, models/, and results/ directories. Commit source, configurations, tests, reference metadata, and a small verified example-results bundle. Copy this specification into docs/PROJECT_SPEC.md with provenance. Add a sibling PROJECT_STATUS.md inside the local checkout describing exact completed and incomplete work, actual commands, artifact paths, and remote publication status. Do not put outputs in the home-directory root.

### 3. Standards and research grounding

Read the relevant portions of the primary sources below. Pin document versions, record access dates and exact relevant clauses actually checked, and build docs/STANDARDS_MAPPING.md with columns: source/version/clause, concept, implementation location, abstraction, and omitted behavior. Do not invent clause numbers or bibliography details. Link sources rather than redistributing copyrighted standard PDFs.

Verified starting references, not claims that these are the newest versions:

- Fraunhofer vacancy: https://jobs.fraunhofer.de/job/Berlin-Wissenschaftlerin-6G-Mobilfunk-10587/1445911533/
- HHI AI4Mobile: https://www.hhi.fraunhofer.de/en/departments/wn/projects/ai4mobile.html
- HHI Optimization and Learning: https://www.hhi.fraunhofer.de/en/departments/wn/research-groups/optimization-and-learning-for-communications.html
- HHI Industrial Wireless: https://www.hhi.fraunhofer.de/en/departments/wn/technologies-and-solutions/industrial-wireless.html
- TS 38.300 v18.2.0, NR/NG-RAN overview: https://www.etsi.org/deliver/etsi_ts/138300_138399/138300/18.02.00_60/ts_138300v180200p.pdf
- TS 38.321 v18.2.0, MAC: https://www.etsi.org/deliver/etsi_ts/138300_138399/138321/18.02.00_60/ts_138321v180200p.pdf
- TS 38.214 v18.4.0, physical-layer data procedures: https://www.etsi.org/deliver/etsi_ts/138200_138299/138214/18.04.00_60/ts_138214v180400p.pdf
- TR 38.901 v18.0.0, channel models: https://www.etsi.org/deliver/etsi_tr/138900_138999/138901/18.00.00_60/tr_138901v180000p.pdf
- Palaios et al., “Machine Learning for QoS Prediction in Vehicular Communication: Challenges and Solution Approaches”: https://arxiv.org/abs/2302.11966
- “AI4Mobile: Use Cases and Challenges of AI-based QoS Prediction for High-Mobility Scenarios”: https://doi.org/10.1109/VTC2021-Spring51267.2021.9449059
- Current 3GPP research context: https://www.3gpp.org/news-events/3gpp-news/ran113-reports
- ML leakage guidance: https://scikit-learn.org/stable/common_pitfalls.html

Use MAC resource-allocation and retransmission concepts plus NR timing as inspiration. TS 38.214 is context for link adaptation; a Shannon surrogate is not its MCS/TBS procedure. TR 38.901 is context for propagation; a simple path-loss/fading model is not a complete implementation of that report. Explain RLC, PDCP, SDAP, and RRC roles briefly; do not pretend to implement them. Downlink queue visibility is intentional; uplink buffer-status reporting is out of scope. Do not label an application deadline as an exact standardized 5QI packet-delay budget. Explain that commercial scheduling algorithms are not uniquely prescribed by these standards.

### 4. Package architecture and interfaces

Use Python 3.11+ with a src/ package layout, pyproject.toml, a console CLI called pqos, pytest, Ruff, and type checking on core interfaces. Prefer NumPy, SciPy, pandas, scikit-learn, Matplotlib, PyYAML, and joblib. Keep runtime dependencies small; no GPU or mandatory PyTorch. Pin an actually tested dependency environment with a reproducible lock/requirements mechanism, separating development dependencies.

Suggested structure:

    src/pqos/
      cli.py, config.py, entities.py, randomness.py
      mobility.py, channel.py, traffic.py, traces.py
      simulator.py, observation.py, link.py, metrics.py
      schedulers/base.py, round_robin.py, proportional_fair.py
      schedulers/edf.py, reactive_qos.py, predictive_qos.py, oracle.py
      prediction/features.py, dataset.py, models.py, training.py
      experiments/runner.py, statistics.py, plots.py, reporting.py
    configs/{demo,train,evaluation,ablation}.yaml
    tests/{unit,integration}/
    docs/{PROJECT_SPEC,METHODS,STANDARDS_MAPPING,RESULTS,LIMITATIONS}.md
    examples/verified_run/
    .github/workflows/ci.yml
    README.md, CITATION.cff, Makefile, pyproject.toml, .gitignore

Small reorganizations are fine when justified. Keep simulation, scheduler decisions, prediction, and evaluation separate. Use typed dataclasses or equivalent validated models for Packet, Flow, UE, Observation, Allocation, Scenario, and RunManifest. Implement a common reset()/allocate(observation) scheduler interface with an immutable observation and validated output. Scheduler APIs must not expose future traces or simulator internals. Only a clearly marked diagnostic oracle may access future channels.

### 5. Simulator semantics and radio model

Use integer slot indices internally. Default slot duration: 0.5 ms, inspired by NR numerology mu=1. Resource units are frequency-flat PRB-equivalents, not exact standardized transport blocks. Proposed starter settings: 12 UEs, 24 resource units per slot, carrier 3.5 GHz, resource-unit bandwidth 360 kHz, configurable overhead fraction and spectral-efficiency ceiling. These are synthetic assumptions, not HHI or standardized requirements. Adjust finite traffic loads after a documented pilot to cover unsaturated, near-capacity, and overloaded conditions; freeze all settings before test evaluation.

Each slot [t,t+1) must have one documented event order: expose matured feedback and delayed measurements; admit arrivals timestamped t; expire packets whose absolute deadline is at or before t; construct causal observations; allocate resources; simulate service over the slot; register completions at t+1; update metrics and internal averages. Delivery at t+1 is on time when completion <= deadline. Document and test exact boundary cases, including delivery exactly at the deadline and arrival during measurement windows.

Implement 2-D mobile robot trajectories with bounded constant-velocity segments, reflections or waypoint changes, and optionally position-linked blockage zones. Generate mobility before scheduling, independently of policy. Include smooth channel evolution and challenging disruptions; random blockage onsets must not become known to the predictor before observable.

Implement a transparent synthetic path-loss model, correlated shadow/fading dynamics with explicit recurrence and parameters, additive noise, and exogenous interference. State units throughout: meters, seconds/ms, Hz, dBm, linear SINR, bits. Do power sums in linear units. For the mandatory model use fixed power spectral density so per-unit SINR is policy independent; label the resulting transmit-power assumption. Do not also claim fixed total cell power. A total-power budget can be a separately validated extension.

Define potential bits per allocated unit as floor(B_unit * slot_seconds * overhead_efficiency * min(eta_max, log2(1+SINR_linear))). Treat it as an idealized service abstraction. Store the true potential channel service for supervision and simulation, but expose only configured delayed/noisy causal measurements to schedulers. Provide optional CQI quantization, observation age, and configurable feedback delays shared across policies. Defaults must be recorded.

Use explicit packets with flow/UE ID, arrival, size, remaining bits, class, deadline, retry count, and terminal reason. Distinguish pending bits from delivered unique payload. Implement a coherent chunk-service model: per-UE per-slot scheduled payload chunks have an explicit success probability, consume resource time even on failure, retain undelivered bits, and are retried after a configurable feedback delay up to a documented retry limit. No combining gain is mandatory. Explain that this is an ARQ-like abstraction inspired by HARQ, not standards-compliant HARQ. Track chunks in flight to prevent duplicate service and double counting. Requeue failed chunks only when feedback matures. Handle expired packets with outstanding chunks deterministically and prevent late feedback from resurrecting them.

Use a documented synthetic SINR-to-error function with tunable parameters; do not present it as a measured BLER curve. Include an error-free switch for analytical checks and sensitivity studies. Packet completion occurs only once all its bits have been successfully delivered. Failed chunks never count as unique goodput. Unused allocation and excess capacity cannot be banked into future slots. Never serve future arrivals.

For policy comparisons precompute exogenous mobility, channel, arrival, and observation-noise traces. Use separate named RNG streams and stable SeedSequence derivation. For service outcomes use a policy-independent indexed random field such as uniform variates keyed by episode, slot, and UE under the shared chunk model. Explain the coupling and that different allocations need not cause identical successful packets. Avoid sequential RNG consumption that makes channel or arrivals change with scheduler behavior. Record hashes of trace arrays and configurations.

### 6. Traffic, queues, and measurement cohorts

Give each UE an independent FIFO control queue and FIFO best-effort queue. A starter control flow is a 256-byte packet every 10 ms, deadline 10 ms, randomized initial phase; offer deadline/period/size variants. Best-effort traffic uses finite arrivals, configurable packet sizes and an on/off or burst model. Buffers are finite with explicit overflow handling. Saturated queues may be a separately labeled stress test, not the only scenario.

Default packet selection within an allocated UE is eligible control first, then best effort, FIFO within class. Share packet selection, retry handling, deadline dropping, and buffer limits across all policies so RR/PF are not weakened artificially. Document that baselines therefore compare UE allocation with a common QoS-aware local queue discipline.

Use a warm-up period, fixed measurement window, and bounded drain period. Define the measurement cohort by packet arrival within the measurement window. Carry warm-up state forward but exclude warm-up arrivals from cohort metrics. During drain stop new arrivals and continue the same policy long enough to resolve cohort control deadlines. Best-effort packets still pending at the drain boundary must be reported as censored. Denominators cannot silently omit dropped, failed, or unresolved packets. Report window-only delivered goodput separately from eventual cohort completion. Do not divide drained bytes by measurement-window duration and call it steady-state throughput.

### 7. Baselines and predictive policy

Implement and document these allocators under identical observations and radio conditions:

1. Round Robin: deterministic rotating allocation across eligible UEs; test rotation and allocation balance.
2. Proportional Fair: marginal score r_i(t)/(Rbar_i(t)+epsilon), with a documented EWMA time constant and per-UE average updates every slot, including zero service. Define r as the observed expected unique-payload service per unit and Rbar as delivered unique-payload rate, both in consistent units. State initialization, idle-user behavior, tie-breaking, and whether scoring updates within a slot.
3. EDF: prioritize the nearest eligible control deadline, break ties deterministically, then use PF for remaining best-effort capacity. Document per-unit recomputation and exhaustion handling.
4. Reactive QoS: combine current channel service estimate, control backlog, remaining deadline slack, and PF fairness without any forecast. It should be a strong comparator and share the predictive algorithm's structure as closely as possible.
5. Predictive QoS: the proposed hybrid method, described below.
6. Persistence-prediction variant: same predictive policy, future channels held at the latest observation. This isolates whether learned forecasts actually add value.
7. Future-channel oracle: same policy using true future potential channel service, strictly diagnostic. Label it a perfect-channel-information reference, not a guaranteed upper bound or deployable algorithm. It must not know future packet arrivals.

Implement an interpretable rolling-horizon heuristic rather than claiming a globally optimal solution. For queued control packets, estimate remaining service demand and predicted expected service opportunity over their remaining deadlines. A concrete policy family is per-resource-unit greedy allocation using a normalized PF term plus (a) urgency from queued bits relative to forecast service before deadlines and (b) an opportunity term when current service is better than near-future service. Recompute marginal demand after tentative allocations to avoid repeatedly rewarding already covered packets. Use the forecast horizon available and document how longer deadlines are extrapolated with persistence.

Write the exact equations, normalization scales, treatment of multiple packets/deadlines, success-probability approximation, weight ranges, tie-breaking, and infeasible demand behavior before final evaluation. Unit tests must match those equations. Do not silently implement a materially different score under the same name. Tune weights and horizon only on validation episodes using a predeclared objective: minimize control violation ratio subject to a configurable best-effort-goodput floor relative to PF, e.g. 90%; if no candidate is feasible, report infeasibility and choose a documented validation fallback. The floor is a model-selection rule, not a per-run guarantee. Report the validation selection table and sensitivity to the floor. Provide EDF or reactive fallback on missing, nonfinite, incompatible, or stale predictions; record fallback counts.

Future forecasts may motivate earlier service of already queued packets. They cannot reserve fictitious delivered bytes, serve unborn packets, or guarantee robot safety. No theoretical optimality or stability claim without proof.

### 8. Forecasting and leakage prevention

Forecast exogenous potential log-service or SINR at horizons of 1, 2, 4, 8, and 16 slots; align the scheduler's lookahead to these forecasts using a documented interpolation. Prefer channel/service forecasting over predicting realized throughput, because realized throughput depends on scheduler choices.

Compare persistence, a simple linear/ridge autoregressive predictor, and a small CPU-trained tree/boosting regressor. Use causal histories of measurements, measurement age, current/past position and velocity, and time differences. Do not use future coordinates, future blockage labels, true future SINR, episode identity, or route identifiers as predictive features. Queue state belongs in scheduling; avoid introducing it into the exogenous channel predictor. Train channel predictors from traces independent of policy.

Use entire independent episodes/trajectories as split groups, proposed 60/20/20 train/validation/test with explicit disjoint seed ranges. Never randomly split overlapping sliding-window rows. When demonstrating within-episode chronological evaluation, purge at least history length plus maximum forecast horizon around split boundaries. Fit all preprocessing, clipping thresholds, learned normalization, feature selection, and models only on training data. Use validation for hyperparameters, policy weights, forecast horizon selection, and optional uncertainty calibration. Freeze them before test. Save split manifests and assert no overlap.

Report MAE and RMSE by horizon plus persistence skill, including low-service/blockage-conditioned error. Any interval forecast requires measured coverage and width on held-out data; do not call a percentile conservative without checking calibration. Keep point forecasts mandatory; uncertainty-aware variants are optional after the core pipeline works. Mark unseen-environment tests as out-of-distribution, using different route layouts/blockage regimes and speeds/loads without refitting. Include a position-feature ablation to expose route/map memorization. Explain that training and testing on one synthetic generator proves only generalization within that modeled family.

### 9. Experiment design and statistical analysis

Create deterministic demo, quick, and full profiles. A suggested full design is 3 load levels x 2 speed ranges x 2 blockage severities, with at least 30 independent test episodes per cell and scheduler. Choose episode duration and warm-up from pilots and document actual packet counts and stability checks. Estimate runtime first; support resumable execution and manifest-validated reuse. A quick profile may use fewer repetitions, but mark it exploratory. Do not silently relabel a partial campaign as full.

Predeclare the primary endpoint: per-episode control delivery violation ratio = 1 - on-time control deliveries / control arrivals in the cohort. Include overflow, retry exhaustion, deadline expiration, and late completion consistently as failures. Report mutually exclusive failure reasons; distinguish this total ratio from deadline-expiration-only ratio. A cohort with zero arrivals has an undefined ratio, not zero.

Secondary endpoints: control delivery probability, delivered-control latency p50/p95/p99, deadline-miss ratio per UE, best-effort and total unique-payload goodput, queue occupancy and head-of-line age, retransmission/resource utilization, wasted service on ultimately expired packets, Jain fairness of per-UE goodput, and scheduler computation time. Report deadline failure alongside latency because delivered-only latency has survivor bias. Jain's index is undefined when all goodputs are zero. AoI is optional and requires its own formal sampling and stale-update semantics.

Treat independent episodes as the statistical units, not packets or slots. Compare policies using matched episodes and paired differences. Report means, dispersion, and 95% bootstrap confidence intervals resampling entire episode pairs with a fixed analysis seed, e.g. 10,000 resamples. Report absolute percentage-point difference in violation ratio; relative reduction is undefined at a zero baseline. Preserve per-episode rows; separate macro-average episode ratios from pooled packet-weighted ratios. Avoid claiming thousands of packets are independent repetitions.

Show per-scenario results and clearly labeled aggregates, not only a favorable average. Use paired confidence intervals for scheduler differences and identify a primary comparison with Reactive QoS plus a comparison to EDF. If using many significance tests, label exploratory tests and apply a stated multiplicity correction. Hypothesis testing is optional; effect sizes and uncertainty are mandatory.

Do not claim five-nines reliability from a small synthetic sample or zero observed violations. If all runs have zero failures, show sample size and explain the bootstrap interval's degeneracy; any binomial rule-of-three estimate is only valid under an explicit independence assumption that correlated packet errors may violate. Tail quantiles need sample counts and uncertainty: bootstrap episodes for p99 comparisons and flag sparse delivery populations. Do not set arbitrary missing quantiles to zero.

Required ablations: forecast disabled/reactive, persistence vs learned forecasts, no position features, several horizons, perfect future-channel reference, and observation-delay/model-error sensitivity. Evaluate ID and OOD separately. Include both smooth predictable channels and surprise blockage to test when prediction is useful or misleading. A null or negative result is valid and must remain visible.

### 10. CLI, reproducibility, and artifacts

Provide actual working commands for setup, trace generation, training, demo, evaluation, ablation, and report generation. Suggested CLI:

    pqos generate --config configs/train.yaml
    pqos train --config configs/train.yaml
    pqos demo --config configs/demo.yaml
    pqos evaluate --config configs/evaluation.yaml --profile quick
    pqos evaluate --config configs/evaluation.yaml --profile full
    pqos ablate --config configs/ablation.yaml
    pqos report --run-dir results/<actual-run-id>

Adapt options consistently, document help, and verify every command shown in README. A demo must complete on a laptop in roughly a minute where feasible; record measured runtime and machine context instead of inventing it. Include a noninteractive headless plotting path and notebook-free reproduction. An optional notebook may explain results but must not contain unique computation logic.

Each run saves a manifest with resolved configuration, units, seed/split IDs, trace hash, model hash, feature schema, dependency versions, Git commit and dirty status, timestamps, profile, experiment status, and measured runtime. Write outputs atomically and avoid destructive overwrite. Store compact episode_metrics.csv, prediction_metrics.csv, paired_comparisons.csv, selected_models.json, summary.json, a Markdown report, and SVG/PNG figures. Keep optional packet logs disabled by default for large runs.

Required figures: control violations versus offered load with uncertainty, best-effort-goodput tradeoff, latency ECDF with survivor-bias caption, per-UE fairness, forecast error by horizon, ablation results, and one accurately annotated timeline showing movement/channel state, observed/predicted service, queues, and allocations. Use actual generated data; figures must include scenario, metric units, repetitions, and uncertainty definition. ECDFs never imply dropped packets had low latency.

Commit a small complete example run with its own configuration, manifests, metrics, report, and figures. Mark its size/profile prominently. Do not commit huge raw traces, environments, caches, or opaque bulk model files. Document exact regeneration. Store model artifacts locally with metadata; never load an untrusted joblib/pickle model.

### 11. Testing and CI

Implement meaningful analytical and invariant tests before claiming results:

- Empty queues, one UE, zero service, very high service, all-error and error-free cases.
- Resource-budget constraints, eligibility, deterministic ties, no negative queue lengths, no duplicate PRB assignments.
- Conservation: generated payload = delivered unique payload + terminally discarded undelivered payload + unresolved/in-flight payload, with a matching packet-state ledger. Track delivered portions of later-dropped packets separately.
- Deadline exact-boundary behavior; partial completion; late feedback; retry limits; no resurrected/duplicate packets; no service before arrival.
- Constant-channel one-UE service matches analytically expected slots, including floor/overhead and chunk rules.
- RR balances eligible users; PF behavior under equal conditions; EDF follows deadlines; predictive score agrees with hand-calculated tiny examples.
- Predictive and reactive/persistence variants coincide in controlled cases where the forecast adds no information and weights are aligned.
- Paired schedulers see identical exogenous traces; policy-specific queue evolution does not alter arrivals or channel RNG.
- Future information is absent from ordinary observations; sentinel future-trace mutations cannot affect an earlier decision. The oracle is isolated.
- Split disjointness, window-label boundaries, train-only preprocessing, and held-out model selection.
- Metrics for zero arrivals, zero delivery, censoring, all-zero fairness, and mutually exclusive failure counts.
- Deterministic repeatability on the same tested environment; document tolerances for portability.
- Full tiny end-to-end generate -> train -> evaluate -> report run from a clean temporary directory, plus resume/schema compatibility checks.

CI should install the tested environment, run lint, type checks, tests, and a bounded smoke pipeline on supported Python versions. Heavy full experiments do not belong in each CI run. Do not claim CI passed remotely unless observed; local checks and remote checks are different evidence.

### 12. Documentation and delivery criteria

README must explain the research question, architecture, exact setup/quickstart, demonstrated outputs, metric meanings, and limitations. METHODS must contain assumptions, timing diagram, equations, units, causal observation contract, queue/service semantics, baseline pseudocode, predictor target/features, split protocol, validation selection, and statistical procedure. RESULTS must be generated from actual runs with explicit profile/completion status, unfavorable cases, and uncertainty. Include verified bibliography metadata and CITATION.cff without invented DOI/publication/affiliation. Document license selection; do not copy third-party source or standard tables without appropriate terms. No fabricated author credentials or employer branding.

LIMITATIONS must explicitly cover single-cell downlink, abstract frequency-flat PHY, synthetic channel/error models, fixed-PSD power assumption, ARQ-like rather than full HARQ, absent RLC/PDCP/RRC/core-network delays, no real control loop, no real-world validation, imperfect measurements, map memorization risk, finite samples, and no formal optimality/reliability guarantee. Explain the Shannon-capacity intuition and why finite-blocklength effects, coding, protocol overhead, and interference complicate real service. Do not infer real end-to-end robot-control performance from radio queue delay.

Provide a short research-style report with motivation, related work, model, methods, experiments, results, limitations, and next steps. Also provide docs/INTERVIEW_NOTES.md with concise defensible answers about the research question, PF/EDF, information theory assumptions, causal prediction, leakage, paired statistics, tradeoffs, and failure cases. Present skill alignment as project evidence, not invented employment experience.

Implement in stages: validated simulator and classical baselines; training pipeline; predictive method; paired evaluation and ablations; documentation and verified artifacts. Keep progress updates concise. Do not end after planning if meaningful implementation can continue. Prefer completing the bounded core over adding RL or a dashboard. If a full campaign exceeds available execution time, complete the software and quick campaign, retain resumable commands, and plainly mark full results as not run or incomplete.

Before finishing, reproduce the documented quick pipeline from a clean environment/output directory, inspect generated figures and reports, and verify all artifact links. Report what was implemented, exact checks run and outcomes, real experiment results with uncertainty, incomplete work, local paths, Git branch/commit, and remote publication status. Never invent numerical superiority, test outcomes, runtime, theoretical guarantees, or executed external actions. Success means a working, inspectable research pipeline, even if prediction does not outperform the strongest baseline.
