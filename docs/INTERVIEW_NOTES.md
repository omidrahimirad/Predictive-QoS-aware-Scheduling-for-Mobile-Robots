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
