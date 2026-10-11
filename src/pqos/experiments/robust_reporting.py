"""Rebuild all v2 scientific summaries and figures from saved episode data."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pqos.experiments.robust import comparisons
from pqos.experiments.runner import atomic_csv
from pqos.experiments.statistics import interval

COLORS = {
    "edf": "#59666f",
    "reactive": "#e6a23c",
    "predictive": "#3976b8",
    "robust": "#21866c",
    "robust_no_adaptation": "#8666a8",
}
LABELS = {
    "edf": "EDF",
    "reactive": "Reactive",
    "predictive": "Predictive",
    "robust": "Robust",
    "robust_no_adaptation": "No adaptive fallback",
}


def report_robust(directory: Path) -> Path:
    frame = pd.read_csv(directory / "episode_metrics.csv")
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["status"] != "complete":
        raise ValueError("cannot report incomplete study as completed")
    paired = comparisons(frame)
    atomic_csv(directory / "paired_comparisons.csv", paired)
    metrics = [c for c in frame.columns if c not in {"scenario", "policy", "trace_hash", "seed"}]
    rows = []
    for (scenario, policy), group in frame.groupby(["scenario", "policy"]):
        for metric in metrics:
            values = group[metric].to_numpy(dtype=float)
            mean, low, high = interval(values)
            rows.append(
                {
                    "scenario": scenario,
                    "policy": policy,
                    "metric": metric,
                    "n_episodes": int(np.isfinite(values).sum()),
                    "mean": mean,
                    "ci_low": low,
                    "ci_high": high,
                }
            )
    summary = pd.DataFrame(rows)
    atomic_csv(directory / "summary.csv", summary)
    prediction = pd.read_csv(directory / "prediction_metrics.csv")
    figures = directory / "figures"
    figures.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.dpi": 120,
            "savefig.dpi": 170,
            "svg.hashsalt": "pqos-v2",
        }
    )
    scenarios = sorted(frame.scenario.unique())
    names = [n.replace("-", "\n", 1) for n in scenarios]
    policies = list(COLORS)[:4]

    def save(fig, name):
        fig.tight_layout()
        for suffix in ("png", "svg"):
            fig.savefig(
                figures / f"{name}.{suffix}", bbox_inches="tight", metadata={"Creator": "pqos"}
            )
        plt.close(fig)

    def bars(ax, selected):
        width = 0.8 / len(selected)
        for j, policy in enumerate(selected):
            table = (
                summary[(summary.policy == policy) & (summary.metric == "control_violation")]
                .set_index("scenario")
                .loc[scenarios]
            )
            means = table["mean"].to_numpy() * 100
            bounds = np.array(
                [means - table.ci_low.to_numpy() * 100, table.ci_high.to_numpy() * 100 - means]
            )
            ax.bar(
                np.arange(len(scenarios)) + (j - (len(selected) - 1) / 2) * width,
                means,
                width,
                yerr=np.maximum(bounds, 0),
                color=COLORS[policy],
                label=LABELS[policy],
                capsize=2,
            )
        ax.set_xticks(range(len(scenarios)), names)
        ax.set_ylabel("Control deadline violation (%)")
        ax.legend(ncol=2, fontsize=9)
        ax.grid(axis="y", alpha=0.2)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    bars(ax, policies)
    ax.set_title("Held-out control violations · episode mean and 95% bootstrap CI")
    save(fig, "control_violations")

    fig, axes = plt.subplots(2, 4, figsize=(13, 6.5), sharey=True)
    for name, ax in zip(scenarios, axes.flat):
        for policy in policies:
            group = frame[(frame.scenario == name) & (frame.policy == policy)]
            x, xl, xh = interval(group.be_goodput_mbps.to_numpy())
            y, yl, yh = interval(group.control_violation.to_numpy() * 100)
            ax.errorbar(
                x,
                y,
                xerr=[[max(x - xl, 0)], [max(xh - x, 0)]],
                yerr=[[max(y - yl, 0)], [max(yh - y, 0)]],
                fmt="o",
                color=COLORS[policy],
                label=LABELS[policy],
                capsize=2,
            )
        ax.set_title(name)
        ax.set_xlabel("BE goodput (Mbit/s)")
        ax.grid(alpha=0.2)
    axes[0, 0].set_ylabel("Control violation (%)")
    axes[1, 0].set_ylabel("Control violation (%)")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Reliability–throughput trade-off · lower violations and higher goodput preferred")
    save(fig, "reliability_goodput")

    fig, ax = plt.subplots(figsize=(11, 4.5))
    for j, model in enumerate(["persistence", "learned"]):
        values = [
            interval(
                prediction[
                    (prediction.scenario == n) & (prediction.model == model)
                ].mae_db.to_numpy()
            )
            for n in scenarios
        ]
        m, low, high = np.array(values).T
        ax.bar(
            np.arange(8) + (j - 0.5) * 0.32,
            m,
            0.32,
            yerr=np.maximum(np.array([m - low, high - m]), 0),
            capsize=2,
            label=model.title(),
            color=["#59666f", "#3976b8"][j],
        )
    ax.set_xticks(range(8), names)
    ax.set_ylabel("Future true SINR MAE (dB)")
    ax.set_title(
        f"Forecast error under changing conditions · horizon {int(prediction.horizon.iloc[0])} slots"
    )
    ax.legend()
    save(fig, "prediction_shift")

    timeline = pd.read_csv(directory / "timeline-H-combined.csv")
    slot_seconds = manifest["freeze"]["config"]["scenario"].get("slot_seconds", 0.0005)
    fig, axes = plt.subplots(3, 1, figsize=(11, 6), sharex=True)
    t = timeline.slot * slot_seconds * 1000
    axes[0].plot(t, timeline.sinr_db, color="#3976b8", label="UE 0 true SINR (offline diagnostic)")
    axes[0].set_ylabel("SINR (dB)")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[1].plot(t, timeline.confidence, color="#21866c", label="Global confidence diagnostic")
    axes[1].axhline(
        1 / (1 + manifest["freeze"]["robust_settings"]["threshold"]),
        color="#59666f",
        ls="--",
        label="Switch threshold",
    )
    axes[1].set_ylabel("Confidence")
    axes[1].legend(loc="upper right", fontsize=8)
    axes[2].step(t, timeline.fallback, where="post", color="#e6a23c")
    axes[2].set_ylabel("EDF fallback")
    axes[2].set_xlabel("Episode time (ms)")
    axes[0].set_title(
        "Illustrative held-out H-combined episode · fallback is global, not UE 0 only"
    )
    save(fig, "fallback_timeline")

    fig, ax = plt.subplots(figsize=(12, 4.5))
    bars(ax, ["edf", "reactive", "predictive", "robust", "robust_no_adaptation"])
    ax.set_title("Mechanism ablation · same held-out traces and predictive settings")
    save(fig, "ablation")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for j, baseline in enumerate(["predictive", "edf"]):
        table = (
            paired[(paired.reference == baseline) & (paired.metric == "control_violation")]
            .set_index("scenario")
            .loc[scenarios]
        )
        m = table.difference.to_numpy()
        axes[0].errorbar(
            m,
            np.arange(8) + (j - 0.5) * 0.16,
            xerr=np.maximum(
                np.array([m - table.ci_low.to_numpy(), table.ci_high.to_numpy() - m]), 0
            ),
            fmt="o",
            label=f"Robust − {LABELS[baseline]}",
            capsize=2,
            color=["#21866c", "#59666f"][j],
        )
    axes[0].set_yticks(range(8), scenarios)
    axes[0].axvline(0, color="#777", ls="--")
    axes[0].set_xlabel(
        "Violation difference (percentage points)\nNegative favors Robust · paired 95% CI"
    )
    axes[0].legend(fontsize=8)
    for policy in policies:
        group = frame[frame.policy == policy].groupby("scenario").mean(numeric_only=True)
        axes[1].scatter(
            group.be_goodput_mbps,
            group.control_violation * 100,
            label=LABELS[policy],
            color=COLORS[policy],
        )
    axes[1].set_xlabel("Scenario mean BE goodput (Mbit/s)")
    axes[1].set_ylabel("Scenario mean control violation (%)")
    axes[1].legend(fontsize=8)
    fig.suptitle("Robust scheduling: measured effects and throughput trade-offs")
    save(fig, "main_findings")

    # Descriptive timing, including monitor/gate cost but excluding batch ML inference.
    timing = (
        frame.groupby(["scenario", "policy"])[["scheduler_mean_us", "scheduler_p99_us"]]
        .mean()
        .reset_index()
    )
    atomic_csv(directory / "timing.csv", timing)
    pareto = []
    for name, group in frame.groupby("scenario"):
        means = group.groupby("policy").mean(numeric_only=True)
        for policy, row in means.iterrows():
            dominated = any(
                other.control_violation <= row.control_violation
                and other.be_goodput_mbps >= row.be_goodput_mbps
                and (
                    other.control_violation < row.control_violation
                    or other.be_goodput_mbps > row.be_goodput_mbps
                )
                for p, other in means.iterrows()
                if p != policy and p != "oracle"
            )
            pareto.append(
                {
                    "scenario": name,
                    "policy": policy,
                    "descriptive_pareto_goodput": not dominated,
                    "descriptive_pareto_fairness": not any(
                        other.control_violation <= row.control_violation
                        and other.jain_fairness >= row.jain_fairness
                        and (
                            other.control_violation < row.control_violation
                            or other.jain_fairness > row.jain_fairness
                        )
                        for p, other in means.iterrows()
                        if p != policy and p != "oracle"
                    ),
                }
            )
    atomic_csv(directory / "pareto.csv", pd.DataFrame(pareto))
    lines = [
        "# Robust scheduling v2 — measured study",
        "",
        f"Profile: **{manifest['profile']}**. Completed **{len(frame):,} episode-policy executions**,",
        f"with **{manifest['independent_episodes_per_condition']} independent seeds per condition** and nine policies.",
        "The eight conditions use disjoint seed ranges. Historical test evidence was not reused.",
        "",
        f"Frozen code revision: `{manifest['freeze']['environment']['git_commit']}`.",
        f"Source hash: `{manifest['freeze']['source_hash']}`.",
        f"Selected settings: `{manifest['freeze']['robust_settings']}`.",
        "",
        "## Primary paired differences",
        "",
        "Robust minus reference, pp. Negative favors Robust. Percentile bootstrap resamples matched episodes",
        "10,000 times. Intervals are marginal; many comparisons are not multiplicity-adjusted. No universal superiority claim.",
        "",
        "| Scenario | Versus predictive: pp [95% CI] | Versus EDF: pp [95% CI] | Robust BE Mbit/s | Fallback % slots |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in scenarios:
        values = []
        for ref in ["predictive", "edf"]:
            row = paired[
                (paired.scenario == name)
                & (paired.reference == ref)
                & (paired.metric == "control_violation")
            ].iloc[0]
            values.append(f"{row.difference:.3f} [{row.ci_low:.3f}, {row.ci_high:.3f}]")
        group = frame[(frame.scenario == name) & (frame.policy == "robust")]
        lines.append(
            f"| {name} | {values[0]} | {values[1]} | {group.be_goodput_mbps.mean():.3f} | {group.fallback_frequency.mean() * 100:.1f} |"
        )
    lines += [
        "",
        "## Computational cost",
        "",
        "Mean of episode timings; P99 column is the mean of within-episode P99 values, not a pooled P99.",
        "Scheduler timing includes residual monitoring and gating, excludes precomputed model inference.",
        "Batch inference time is separately recorded per episode in prediction_metrics.csv.",
        "Process workers compete for CPU; these are descriptive Python timings, not real-time RAN measurements.",
        "",
        "| Policy | Mean µs | Mean episode P99 µs | Relative to EDF | Relative to predictive |",
        "|---|---:|---:|---:|---:|",
    ]
    avg = frame.groupby("policy").mean(numeric_only=True)
    for p in policies + ["robust_no_adaptation"]:
        row = avg.loc[p]
        lines.append(
            f"| {LABELS[p]} | {row.scheduler_mean_us:.1f} | {row.scheduler_p99_us:.1f} | {row.scheduler_mean_us / avg.loc['edf'].scheduler_mean_us:.2f}× | {row.scheduler_mean_us / avg.loc['predictive'].scheduler_mean_us:.2f}× |"
        )
    lines += [
        "",
        "## Interpretation and artifact map",
        "",
        "Compare summary.csv for all secondary metrics, paired_comparisons.csv for effect intervals,",
        "prediction_metrics.csv for true-SINR errors and empirical observable q90 coverage,",
        "confidence_errors.csv for error conditional on diagnostic confidence, and pareto.csv for descriptive frontiers.",
        "The static calibration q90 is an empirical residual band, not a conformal guarantee: correlated time series,",
        "feature shift, noisy delayed targets and threshold selection invalidate such a shortcut.",
        "No-adaptation retains mandatory invalid-forecast EDF fallback; it disables only the risk-driven switch.",
        "Persistence and reactive decisions coincide when persistence uses the same expected current service.",
        "Latency is conditional on delivery; failure counts and violation ratios must accompany it.",
        "Synthetic channels, short windows and heuristic scheduling do not establish industrial safety or URLLC.",
        "",
    ]
    for name in [
        "main_findings",
        "control_violations",
        "reliability_goodput",
        "prediction_shift",
        "fallback_timeline",
        "ablation",
    ]:
        lines += [f"![{name.replace('_', ' ')}](figures/{name}.png)", ""]
    (directory / "REPORT.md").write_text("\n".join(lines))
    return directory
