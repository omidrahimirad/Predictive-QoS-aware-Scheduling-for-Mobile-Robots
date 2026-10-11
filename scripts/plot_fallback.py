"""Supplementary presentation of the predeclared first deterioration episode.

Does not change numerical source, policy settings, statistical outcomes or frozen hashes.
Usage: uv run python scripts/plot_fallback.py --run-dir <actual-v2-directory>
"""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--run-dir", type=Path, required=True)
root = parser.parse_args().run_dir
frame = pd.read_csv(root / "timeline-E-deterioration.csv")
manifest = json.loads((root / "manifest.json").read_text())
slot_seconds = manifest["freeze"]["config"]["scenario"].get("slot_seconds", 0.0005)
threshold = 1 / (1 + manifest["freeze"]["robust_settings"]["threshold"])
time_ms = frame.slot * slot_seconds * 1000
fig, axes = plt.subplots(3, 1, figsize=(11, 6), sharex=True)
axes[0].plot(time_ms, frame.sinr_db, color="#3976b8")
axes[0].set_ylabel("UE 0 SINR (dB)")
axes[0].set_title("First predeclared deterioration episode · true SINR is offline diagnostic only")
axes[1].plot(time_ms, frame.confidence, color="#21866c", label="Global confidence diagnostic")
axes[1].axhline(threshold, color="#777", ls="--", label="Switch threshold")
axes[1].set_ylim(0, 0.65)
axes[1].set_ylabel("Confidence")
axes[1].legend(loc="upper right", fontsize=9)
axes[2].step(time_ms, frame.fallback, where="post", color="#e6a23c")
axes[2].set_ylim(-0.1, 1.1)
axes[2].set_yticks([0, 1], ["Predictive", "EDF"])
axes[2].set_ylabel("Global mode")
axes[2].set_xlabel("Episode time (ms)")
for ax in axes:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.2)
fig.tight_layout()
plt.rcParams["svg.hashsalt"] = "pqos-v2"
for suffix in ["png", "svg"]:
    fig.savefig(root / "figures" / f"fallback_deterioration.{suffix}", dpi=170, bbox_inches="tight")
plt.close(fig)
