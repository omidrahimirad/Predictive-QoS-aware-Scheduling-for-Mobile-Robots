"""Reports and headless figures derived solely from saved experiment data."""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pqos.experiments.runner import atomic_csv, atomic_json
from pqos.experiments.statistics import METRICS, paired_comparisons, summaries


def finish(fig, directory: Path, name: str) -> None:
    fig.tight_layout()
    fig.savefig(directory / f"{name}.svg")
    fig.savefig(directory / f"{name}.png", dpi=150)
    plt.close(fig)


def report(directory: Path) -> Path:
    manifest = json.loads((directory / "manifest.json").read_text())
    frame = pd.read_csv(directory / "episode_metrics.csv")
    stats = summaries(frame)
    comparisons = paired_comparisons(frame)
    atomic_csv(directory / "summary_metrics.csv", stats)
    atomic_csv(directory / "paired_comparisons.csv", comparisons)
    figures = directory / "figures"
    figures.mkdir(exist_ok=True)
    episode_count = frame.groupby(["scenario", "policy"]).size()
    caption = f"{manifest['profile']}; n={episode_count.min()}–{episode_count.max()} independent episodes/cell"
    title = caption + "; 95% episode bootstrap CI"
    fig, ax = plt.subplots(figsize=(10, 5))
    control = stats[stats.metric == "control_violation"]
    for policy, group in control.groupby("policy"):
        ax.errorbar(
            group.scenario,
            group["mean"] * 100,
            yerr=np.stack(
                ((group["mean"] - group.ci_low) * 100, (group.ci_high - group["mean"]) * 100)
            ),
            fmt="o-",
            capsize=3,
            label=policy,
        )
    ax.set(ylabel="Control delivery violations (%)", title=title)
    ax.tick_params(axis="x", rotation=30)
    ax.legend(fontsize=8, ncol=3)
    finish(fig, figures, "control_violations")
    id_rows = frame[frame.scenario.str.startswith("id-")]
    conditions = list(id_rows.groupby(["speed", "blockage_db"]))
    if conditions:
        fig, axes = plt.subplots(
            len(conditions), 1, figsize=(9, 4 * len(conditions)), squeeze=False
        )
        for axis, ((speed, severity), subset) in zip(axes[:, 0], conditions):
            for policy, policy_group in subset.groupby("policy"):
                points = []
                from pqos.experiments.statistics import interval

                for load, group in policy_group.groupby("load"):
                    mean, low, high = interval(group.control_violation.to_numpy())
                    points.append((load, mean * 100, (mean - low) * 100, (high - mean) * 100))
                values = np.array(points)
                axis.errorbar(
                    values[:, 0],
                    values[:, 1],
                    yerr=values[:, 2:].T,
                    fmt="o-",
                    capsize=3,
                    label=policy,
                )
            axis.set(
                xlabel="Best-effort offered-load multiplier",
                ylabel="Control violations (%)",
                title=f"Speed {speed:g} m/s; blockage {severity:g} dB; {title}",
            )
            axis.legend(fontsize=8, ncol=3)
        finish(fig, figures, "control_vs_load")
    fig, ax = plt.subplots(figsize=(8, 5))
    for policy, group in frame.groupby("policy"):
        means = group.groupby("scenario")[["be_goodput_mbps", "control_violation"]].mean()
        ax.scatter(means.be_goodput_mbps, means.control_violation * 100, label=policy)
    ax.set(
        xlabel="Best-effort unique goodput (Mbit/s)",
        ylabel="Control violations (%)",
        title=caption + "; scenario means",
    )
    ax.legend(fontsize=8, ncol=2)
    finish(fig, figures, "goodput_tradeoff")
    # Explicitly label delivered-only ECDF and keep different scenarios separate.
    latency = pd.read_csv(directory / "delivered_latency.csv")
    scenario_name = sorted(frame.scenario.unique())[0]
    fig, ax = plt.subplots(figsize=(8, 5))
    for policy, group in latency[latency.scenario == scenario_name].groupby("policy"):
        values = np.sort(group.latency_ms)
        ax.step(values, np.arange(1, len(values) + 1) / len(values), label=policy, where="post")
    ax.set(
        xlabel="Delivered-control latency (ms)",
        ylabel="Conditional empirical CDF",
        title=f"{scenario_name}; {caption}\nDelivered packets only: drops excluded (survivor bias)",
    )
    ax.legend(fontsize=8, ncol=2)
    finish(fig, figures, "latency_ecdf")
    fig, ax = plt.subplots(figsize=(9, 5))
    columns = [c for c in frame if c.startswith("ue_") and c.endswith("goodput_mbps")]
    for policy, group in frame[frame.scenario == scenario_name].groupby("policy"):
        ax.plot(range(len(columns)), group[columns].mean(), "o-", label=policy)
    ax.set(
        xlabel="UE index",
        ylabel="Unique payload goodput (Mbit/s)",
        title=f"{scenario_name}; {caption}; episode means",
    )
    ax.legend(fontsize=8, ncol=3)
    finish(fig, figures, "per_ue_goodput")
    prediction = pd.read_csv(directory / "prediction_metrics.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    for model, group in prediction[prediction.scenario == scenario_name].groupby("model"):
        ax.plot(group.horizon, group.mae_db, "o-", label=model)
    ax.set(
        xlabel="Prediction horizon (slots; 0.5 ms/slot by default)",
        ylabel="SINR MAE (dB)",
        title=f"{scenario_name}; {caption}; pooled forecast samples",
    )
    ax.legend(fontsize=8)
    finish(fig, figures, "forecast_error")
    # Mandatory core ablation comparison is present even in ordinary evaluation.
    fig, ax = plt.subplots(figsize=(9, 5))
    choices = [
        p
        for p in [
            "reactive",
            "persistence",
            "predictive",
            "oracle",
            "no_position",
            "horizon_1",
            "horizon_4",
            "horizon_8",
            "horizon_16",
        ]
        if p in frame.policy.unique()
    ]
    group = control[control.scenario == scenario_name].set_index("policy").reindex(choices)
    ax.bar(choices, group["mean"] * 100)
    ax.errorbar(
        choices,
        group["mean"] * 100,
        yerr=np.stack(
            ((group["mean"] - group.ci_low) * 100, (group.ci_high - group["mean"]) * 100)
        ),
        fmt="none",
        capsize=3,
        color="black",
    )
    ax.set(ylabel="Control violations (%)", title=f"{scenario_name}; {title}")
    ax.tick_params(axis="x", rotation=30)
    finish(fig, figures, "ablation")
    if (directory / "timeline.csv").exists():
        timeline = pd.read_csv(directory / "timeline.csv")
        fig, axes = plt.subplots(4, 1, figsize=(10, 9), sharex=True)
        axes[0].plot(timeline.slot, timeline.x_m, label="UE 0 x-position (m)")
        axes[1].plot(timeline.slot, timeline.true_service, label="True potential bits/unit")
        axes[1].plot(
            timeline.slot, timeline.observed_service, label="Observed bits/unit", alpha=0.6
        )
        axes[1].plot(
            timeline.slot,
            timeline.predicted_service,
            label="16-slot-ahead expected bits/unit",
            alpha=0.6,
        )
        axes[2].plot(timeline.slot, timeline.queue_bits, label="UE 0 queue bits")
        axes[3].step(timeline.slot, timeline.allocated_units, label="UE 0 resource units")
        for axis in axes:
            axis.legend(fontsize=8)
        axes[-1].set_xlabel("Slot index (0.5 ms/slot by default)")
        axes[0].set_title("Single synthetic episode; causal prediction and realized allocations")
        finish(fig, figures, "timeline")
    lines = [
        "# Reproducible experiment report",
        "",
        f"Status: **{manifest['status']}**.",
        f"Profile: **{manifest['profile']}**. {caption}.",
        "",
        "Independent synthetic NR-inspired simulation; no HHI affiliation or standards conformance.",
        "",
        "## Design",
        "",
        "See manifest.json for frozen configurations, splits, model/trace provenance, and runtime.",
        "Primary comparison: predictive minus reactive; EDF is the second reference.",
        "Negative violation differences favor prediction; positive goodput differences favor prediction.",
        "ID and OOD results remain separate. No significance tests were performed.",
        "",
        "## Scenario definitions",
        "",
        "| Scenario | Load | Speed m/s | Blockage dB | Domain |",
        "|---|---:|---:|---:|---|",
    ]
    for name, group in frame.groupby("scenario"):
        r = group.iloc[0]
        lines.append(f"| {name} | {r.load:g} | {r.speed:g} | {r.blockage_db:g} | {r.domain} |")
    lines += [
        "",
        "## Primary endpoint",
        "",
        "Macro-mean control violation ratio; 95% CI from resampling independent episodes.",
        "",
        "| Scenario | Policy | Episodes | Mean % | 95% CI % |",
        "|---|---|---:|---:|---|",
    ]
    for _, r in control.iterrows():
        lines.append(
            f"| {r.scenario} | {r.policy} | {r.n_episodes} | {100 * r['mean']:.3f} | "
            f"[{100 * r.ci_low:.3f}, {100 * r.ci_high:.3f}] |"
        )
    lines += [
        "",
        "## Paired differences",
        "",
        "| Scenario | Comparison | Difference pp | 95% CI pp |",
        "|---|---|---:|---|",
    ]
    for _, r in comparisons[comparisons.metric == "control_violation"].iterrows():
        lines.append(
            f"| {r.scenario} | {r.comparison} | {r.difference:.3f} | "
            f"[{r.ci_low:.3f}, {r.ci_high:.3f}] |"
        )
    lines += [
        "",
        "## Interpretation and limitations",
        "",
        "All policies share exogenous traces and the same control-first local queue discipline.",
        "The perfect-future-channel policy is diagnostic, not a mathematical upper bound.",
        "Delivered-only latency is conditional on delivery. Drops and violations must be read alongside it.",
        "Tail comparisons use episode p99 values; they do not estimate an unconditional population p99.",
        "Bootstrap CIs may be degenerate at zero failures. These runs do not establish five-nines reliability.",
        "Quick-profile intervals are exploratory; finite episode count and synthetic model limit inference.",
        "Point forecasts are not calibrated uncertainty guarantees. Negative and null results are retained.",
        "Machine-dependent timing measurements are not universal real-time performance claims.",
        "",
        "## Artifacts",
        "",
        "See episode_metrics.csv, summary_metrics.csv, paired_comparisons.csv,",
        "prediction_metrics.csv, selected_models.json, and figures/. All plots use actual run data.",
    ]
    (directory / "REPORT.md").write_text("\n".join(lines) + "\n")
    atomic_json(
        directory / "summary.json",
        {
            "status": manifest["status"],
            "profile": manifest["profile"],
            "metrics": METRICS,
            "bootstrap_repetitions": 10000,
            "analysis_seed": 771,
            "statistical_unit": "independent episode",
            "comparisons": comparisons.to_dict("records"),
            "n_episode_policy_runs": len(frame),
        },
    )
    return directory / "REPORT.md"
