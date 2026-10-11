# Standards and research mapping

For the v0.2 robustness extension, see [robust scheduling](ROBUST_SCHEDULING.md)
and the [new evaluation protocol](EXPERIMENT_PROTOCOL.md). Historical numerical
results below remain preserved and are labeled as prior evidence.


Primary-source access date: 11 October 2026. Versions below are pinned references,
not a claim to use the newest revisions. Clauses were checked in the linked ETSI
documents. No copyrighted standard PDFs or MCS tables are redistributed.

| Source/version/clause | Concept | Implementation | Abstraction | Omitted behavior |
|---|---|---|---|---|
| [TS 38.300 v18.2.0](https://www.etsi.org/deliver/etsi_ts/138300_138399/138300/18.02.00_60/ts_138300v180200p.pdf), 6.1 and 6.2.1 | L2 architecture, MAC roles | `entities.py`, `simulator.py` | Application queues feed an abstract allocator | Full bearer/transport/logical-channel protocols |
| [TS 38.321 v18.2.0](https://www.etsi.org/deliver/etsi_ts/138300_138399/138321/18.02.00_60/ts_138321v180200p.pdf), 4.3 and 4.4 | Radio-resource service, measurements, feedback | `Observation`, chunk engine | Delayed noisy measurements and ACK/NACK with retries | MAC PDUs, exact HARQ processes and combining |
| [TS 38.214 v18.4.0](https://www.etsi.org/deliver/etsi_ts/138200_138299/138214/18.04.00_60/ts_138214v180400p.pdf), 5.1.3.1–5.1.3.2 | Modulation/coding and TBS determination | `traces.capacity` | Shannon-derived resource-unit bit budget | Exact MCS/TBS selection and resource-element procedures |
| [TR 38.901 v18.0.0](https://www.etsi.org/deliver/etsi_tr/138900_138999/138901/18.00.00_60/tr_138901v180000p.pdf), 7.4.1 | Scenario-specific path loss and shadowing | `traces.generate` | Chosen log-distance and correlated dB surrogate | Standardized scenario equations, antenna/channel-cluster model |

NR timing motivates the default 0.5 ms slot and 360 kHz PRB-equivalent. These chosen
defaults alone do not implement NR numerology, resource grids, or physical channels.
Scheduling policies are independent experiment algorithms; these standards do not
uniquely prescribe RR/PF/EDF or this proposed predictive score.

RLC handles segmentation/reassembly and mode-dependent reliability; PDCP handles
such functions as sequence handling and security; SDAP maps QoS flows to radio
bearers; RRC handles configuration and connection control. Those protocol stacks
are outside this simulator. No uplink BSR is modeled because queues are at the
downlink transmitter. Application deadlines are not asserted to be standard 5QI budgets.

## Research context

- [HHI AI4Mobile](https://www.hhi.fraunhofer.de/en/departments/wn/projects/ai4mobile.html):
  historical 2020–2023 context for predicting QoS and proactively configuring mobile
  systems, including robotics. It does not establish this project's hiring assignment.
- [HHI Optimization and Learning](https://www.hhi.fraunhofer.de/en/departments/wn/research-groups/optimization-and-learning-for-communications.html):
  motivation for combining model-based algorithms with data-driven methods. This
  implementation does not inherit the group's theoretical guarantees.
- [HHI Industrial Wireless](https://www.hhi.fraunhofer.de/en/departments/wn/technologies-and-solutions/industrial-wireless.html):
  contextual connection to low-latency reliable automation and cross-layer methods.
- [Fraunhofer vacancy 85806](https://jobs.fraunhofer.de/job/Berlin-Wissenschaftlerin-6G-Mobilfunk-10587/1445911533/):
  role motivation for resource allocation, ML at L2/L3, selected 3GPP simulation,
  statistics, and information theory. No endorsement or affiliation is implied.
- [3GPP RAN #113 reports](https://www.3gpp.org/news-events/3gpp-news/ran113-reports),
  14 September 2026: current research context, not a finalized 6G implementation spec.

## Selected bibliography

1. A. Palaios et al., *Machine Learning for QoS Prediction in Vehicular Communication:
   Challenges and Solution Approaches*, 2023, [arXiv:2302.11966](https://arxiv.org/abs/2302.11966).
   Motivation for prediction and its practical challenges; no reproduction of that
   paper's dataset or numerical results is claimed.
2. *AI4Mobile: Use Cases and Challenges of AI-based QoS Prediction for High-Mobility
   Scenarios*, IEEE VTC2021-Spring, 2021,
   [DOI:10.1109/VTC2021-Spring51267.2021.9449059](https://doi.org/10.1109/VTC2021-Spring51267.2021.9449059).
   Use-case context, not evidence that this abstract simulator achieves end-to-end QoS.
3. scikit-learn, [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html):
   train-only fitting and leakage prevention. Dependencies are pinned in `uv.lock`.

The project adds a testable implementation hypothesis and comparison pipeline;
it does not claim that its heuristic is novel in the research literature.

## Robustness research sources

4. A. N. Angelopoulos and S. Bates, *A Gentle Introduction to Conformal Prediction and
   Distribution-Free Uncertainty Quantification*, 2022 revision,
   [arXiv:2107.07511v6](https://arxiv.org/abs/2107.07511v6). The project's correlated
   empirical residual band does not claim these formal guarantees.
5. scikit-learn, [ExtraTreesRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesRegressor.html).
   Point ensemble regression is used; no uncalibrated tree disagreement is labeled an interval.

The vacancy's ML/resource allocation/statistical focus motivated the extension, not an
employer assignment. The [official vacancy](https://jobs.fraunhofer.de/job/Berlin-Wissenschaftlerin-6G-Mobilfunk-10587/1445911533/)
was rechecked on 11 October 2026. 3GPP's [RAN #113 reports](https://www.3gpp.org/news-events/3gpp-news/ran113-reports)
describe 6G study activity; this project implements neither those studies nor a finalized standard.
