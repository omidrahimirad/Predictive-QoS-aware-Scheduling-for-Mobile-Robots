# Defensible interview notes

For the v0.2 robustness extension, see [robust scheduling](ROBUST_SCHEDULING.md)
and the [new evaluation protocol](EXPERIMENT_PROTOCOL.md). Historical numerical
results below remain preserved and are labeled as prior evidence.


**What is the research question?**
I test whether a causal channel forecast helps schedule queued control packets
before their deadlines. I compare it with classical and strong reactive methods.

**Why is this relevant to 6G research?**
It connects resource allocation, ML, protocol abstractions, and statistical evaluation.
The radio model is NR-inspired. I would not call it a complete 6G simulator.

**What did you implement?**
A reproducible Python pipeline: synthetic mobile channels, traffic, queues, delayed
feedback, schedulers, prediction, held-out experiments, and generated reports.
I can show actual tests and results rather than only an architecture diagram.

**What does PF do?**
It divides current expected service by a smoothed acknowledged delivery rate.
This balances channel opportunity and historical service. It does not guarantee deadlines.

**Why compare EDF and reactive QoS?**
EDF is a direct deadline comparator. Reactive QoS uses current channel, backlog,
slack, and fairness. It helps isolate whether prediction adds value over an already
informed policy. All policies share the same control-first packet discipline.

**How is future leakage prevented?**
The predictor uses past measurements and current motion features. Whole episodes
are assigned to different splits. Preprocessing is fitted only on training data.
Only the labeled oracle can access true future channels.

**Why not predict realized throughput?**
Realized throughput depends on scheduler choices. I predict exogenous channel SINR,
then map it into expected service using explicit assumptions.

**What does information theory contribute?**
The Shannon expression gives a useful capacity intuition. Real short-packet service
also depends on coding, blocklength, overhead, errors, and retransmissions. My formula
is a surrogate, not a capacity-achieving NR implementation.

**How did you evaluate it?**
I reused the same exogenous traces for each policy and compared matched episode
differences. Confidence intervals resample independent episodes, not correlated packets.
I kept OOD tests and ablations separate from training and validation.

**Does lower forecast error guarantee better scheduling?**
No. A forecast may have a better average error but miss the rare events that matter
for deadlines. The scheduler may also trade away best-effort goodput or fairness.

**What if the predictive policy loses?**
That is a valid finding. I examine which channels, workloads, and shifts cause it.
I do not change test settings to hide a negative result.

**Can you claim URLLC or robot safety?**
No. These are finite synthetic experiments without a real robot control loop or
calibrated industrial radio model. Zero failures do not establish five-nines reliability.

**Why no RL?**
I prioritized an interpretable hypothesis with strong baselines and reproducible
evaluation. I would add RL only with a separate state/action definition, training
budget, constraints, and fair comparisons. A reward penalty is not a safety proof.

**What would you improve next?**
I would test longer windows, measured channels, calibrated link abstraction, and
total-power constraints, then cross-check with a more detailed network simulator.

Refer to RESULTS and the saved reports for numerical answers. Do not memorize a
performance improvement that is absent from those actual artifacts.

## Robustness extension: defensible interview answers

**Why did the original predictive scheduler lose under severe blockage?**
Its urgency and opportunity score remains a heuristic. It can trade deadline protection
for fairness and BE service, and shifted forecasts can underestimate deterioration.
Even the oracle score is not an optimal allocator. EDF directly protects urgent demand.

**How does uncertainty-aware fallback work?**
I keep a forecast until its target's delayed noisy measurement arrives. I update an
error EWMA, compare current features with a training envelope, and switch the whole
slot to EDF if the normalized risk exceeds a development-selected threshold.
The confidence score is a diagnostic, not a calibrated probability.

**How do you prevent prediction-error leakage?**
I match forecast target timestamps to received measurement timestamps. A forecast of
t+H cannot update the monitor before t+H+observation_delay. The scheduler receives no
true future channel. Prefix mutation and delayed-update tests check this behavior.

**Why a new final set?**
The original test results were already inspected. I used disjoint training, validation,
calibration, development and new final ranges, then froze code/config/model/calibration
hashes before final execution. I would need another final set after outcome-driven tuning.

**Why episode bootstrap?**
Packets and slots within one channel/mobility episode are correlated. I resample matched
independent episodes for policy differences. Many marginal intervals do not establish
universal superiority or control the familywise false-positive rate.

**What does OOD measure here?**
It probes a declared change in synthetic layout, motion, blockage or measurements.
It does not prove generalization to real factories or arbitrary shifts. A coordinate
feature envelope can miss important in-envelope changes and flag harmless ones.

**Does this guarantee deadlines?**
No. It is a switch between two heuristics under finite resources and unpredictable
errors. EDF itself cannot guarantee delivery when channels or offered traffic make
it infeasible. The BE floor was infeasible in development, and is not a runtime bound.

**What is the ML contribution?**
The learned model estimates exogenous future SINR. Classical demand, deadline and PF
logic still chooses resources. The no-adaptation ablation and pure EDF show whether
the reliability mechanism helps beyond the original predictor or simply behaves like EDF.

**What is the biggest weakness?**
The synthetic channel/service family and short episodes limit external validity.
The private engine also withdraws physically completed queues before ACKs arrive,
so it is not a full transmitter-only information model. All policies share that
abstraction, but a deployment study needs an ACK-limited queue view and new campaigns.

**What would you improve before deployment?**
Measured channels, calibrated MCS/BLER/TBS, longer-run queue studies, runtime power and
admission constraints, complete feedback semantics, hardware timing, and a robot loop.
I would validate each assumption before claiming industrial reliability.

**What did the new study actually find?**
Robust reduced violations relative to Predictive under deterioration by 13.396 pp,
but reduced BE from 8.061 to 6.311 Mbit/s. In severe blockage it still lost to EDF
by 7.632 pp. Three shifted conditions used EDF in every slot. A small F-condition
gain over EDF is conditional evidence with a multiple-comparison caveat. I would
not describe the study as universally superior ML scheduling.
