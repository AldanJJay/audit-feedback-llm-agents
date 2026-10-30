#!/usr/bin/env python3
"""Deterministically render the design and citation--sensitivity figures.

Run from the repository root with:
    .venv/bin/python paper/latex/generate_figures.py

No requests or raw-ledger analysis are performed. Component estimates and
seed points use the exploratory analysis on exactly the registered CSD support;
CSD estimates and percentile bootstrap intervals use the frozen confirmation.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as PlotPath
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper/latex/figures"
CONFIRM = ROOT / "data/v2/analysis/confirm/results.json"
EXPLORATORY = ROOT / "data/v2/analysis/exploratory/results.json"
MODELS = (
    ("deepseek-v4-flash", "DeepSeek"),
    ("anthropic/claude-haiku-5.5", "Haiku"),
    ("openai/gpt-6-luna", "Luna"),
)
CONTRASTS = ("H3_sci_label", "H4_sci_placebo")
COLORS = ("#0072B2", "#D55E00")


def number(value):
    return f"{value:.4f}".replace("-", "\N{MINUS SIGN}")


def design(r):
    # Coordinates are inches. At .92 manuscript linewidth this figure prints
    # near its native width, keeping every label above 7 pt.
    fig = plt.figure(figsize=(5.65, 4.45))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set(xlim=(0, 5.65), ylim=(0, 4.45))
    ax.axis("off")

    def box(x, y, w, h, text, shade="0.96"):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05",
            fc=shade, ec="0.25", lw=0.8))
        ax.text(x+w/2, y+h/2, text, ha="center", va="center",
                fontsize=7.8, linespacing=1.15, color="black")

    def arrow(*points):
        path = PlotPath(points, [PlotPath.MOVETO] +
                        [PlotPath.LINETO] * (len(points)-1))
        ax.add_patch(FancyArrowPatch(
            path=path, arrowstyle="-|>", mutation_scale=8,
            color="0.25", lw=0.8))

    counts = [len({x["seed"] for x in r["manifest"] if x["model"] == m}) for m, _ in MODELS]
    box(.22, 3.65, 5.2, .68,
        "Assign shared exogenous seeds × five audit packages\n"
        "naive · punitive · label · evidence · false-label\n"
        f"Paired seeds: DeepSeek {counts[0]}; Haiku {counts[1]}; Luna {counts[2]}\n"
        "Six agents; 40 ticks; precompute audit and feature-probe masks",
        "0.90")
    box(.22, 2.85, 5.2, .55,
        "Base decision: action, size and cited features\n"
        "Prompt: rules, persona, portfolio, completed history,\n"
        "latest feedback and current features")
    arrow((2.82, 3.65), (2.82, 3.40))

    box(.22, 1.20, 1.55, 1.35,
        "Trade and update\n"
        "Valid base: order\n"
        "Invalid base: no order\n"
        "Realize market return\n"
        "Evaluate audit; store\n"
        "feedback for next prompt\n"
        "Valid bases:\n"
        "fidelity and citation")
    box(2.00, 1.85, 1.60, .70,
        "Feature probes\n"
        "50% mask; valid base\n"
        "News, then momentum\n"
        "Reverse feature sign\n"
        "Probes never trade")
    box(3.82, 1.85, 1.60, .70,
        "Sampled null re-ask\n"
        "Feature-selected subset\n"
        "Byte-identical prompt\n"
        "Never trades; diagnostics\n"
        "+ secondary sensitivity")
    arrow((.995, 2.85), (.995, 2.55))
    arrow((2.80, 2.85), (2.80, 2.55))
    arrow((4.62, 2.85), (4.62, 2.55))
    # Feedback returns to the next base prompt, outside the analysis path.
    arrow((.22, 1.90), (.055, 1.90), (.055, 3.125), (.22, 3.125))

    box(2.00, .95, 3.42, .60,
        "Valid base + both valid probes: sensitivity and CSD\n"
        "Precision also needs cited probe features\n"
        "Recall also needs action-changing probe features\n"
        "Missing nulls retain raw primary eligibility")
    arrow((2.80, 1.85), (2.80, 1.55))
    lo, hi = r["metadata"]["windows"]["primary"]
    box(.22, .10, 5.2, .57,
        f"Primary window ticks {lo}–{hi}: match eligible coordinates across arms\n"
        "Seed means → equal-seed contrasts\n"
        "Four-test Holm within model; raw sign-flip outcomes", "0.90")
    arrow((.995, 1.20), (.995, .67))
    arrow((3.71, .95), (3.71, .67))
    fig.savefig(OUT / "fig1_design.pdf", facecolor="white",
                metadata={"CreationDate": None, "ModDate": None,
                          "Title": "Experimental design", "Creator": "generate_figures.py"})
    plt.close(fig)



def main():
    confirm = json.loads(CONFIRM.read_text())
    exploratory = json.loads(EXPLORATORY.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42}):
        design(confirm)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 8,
        "axes.titlesize": 10, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "axes.spines.top": False, "axes.spines.right": False,
    })
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 3.3), sharey=True)
    fig.subplots_adjust(left=.082, right=.995, bottom=.26, top=.82, wspace=.13)
    for ax, (model, title) in zip(axes, MODELS):
        ax.set_title(title, pad=5)
        for group, contrast in enumerate(CONTRASTS):
            components = exploratory["models"][model]["C_SCI_components_same_support"][contrast]
            registered = confirm["models"][model]["primary_contrasts"][contrast]
            cd = components["citation_delta"]
            sd = components["dependence_delta"]
            assert cd["n_common_decisions"] == sd["n_common_decisions"]
            assert np.isclose(cd["mean_delta"] - sd["mean_delta"], registered["mean_delta"])
            assert [x["seed"] for x in cd["seed_pairs"]] == [x["seed"] for x in sd["seed_pairs"]]
            for i, (metric, color) in enumerate(zip((cd, sd), COLORS)):
                x = group + (-.17 if i == 0 else .17)
                vals = np.array([p["delta"] for p in metric["seed_pairs"]])
                # Rank-based offsets are fixed, preserve all points and need no RNG.
                offsets = np.linspace(-.065, .065, len(vals))
                order = np.argsort(np.argsort(vals, kind="stable"), kind="stable")
                ax.scatter(x + offsets[order], vals, s=9, facecolors=color,
                           edgecolors="white", linewidths=.3, alpha=.65, zorder=3)
                lo_component, hi_component = metric["bootstrap_ci_95"]
                ax.errorbar(x, metric["mean_delta"],
                            yerr=[[metric["mean_delta"]-lo_component],
                                  [hi_component-metric["mean_delta"]]],
                            fmt="none", color=color, capsize=2, elinewidth=.85, zorder=4)
                ax.plot([x-.10, x+.10], [metric["mean_delta"]]*2,
                        color=color, lw=2.5, zorder=4)
            mean = registered["mean_delta"]
            lo, hi = registered["bootstrap_ci_95"]
            ax.errorbar(group, mean, yerr=[[mean-lo], [hi-mean]], fmt="D",
                        color="black", ms=4, capsize=3, elinewidth=1, zorder=5)
            ax.text(group, -.255,
                    f"CSD {number(mean)}\n[{number(lo)}, {number(hi)}]",
                    ha="center", va="top", fontsize=6.4, linespacing=1.35,
                    transform=ax.get_xaxis_transform(), clip_on=False)
        ax.axhline(0, color=".45", lw=.7, zorder=1)
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color=".9", lw=.6)
        ax.set_xlim(-.5, 1.5)
        ax.set_ylim(-.20, .43)
        ax.set_yticks(np.arange(-.2, .41, .1))
        ax.set_xticks([0, 1], ["P3 (H3): label\ncurrent driver", "P4 (H4): false-label\nopposite driver"])
        ax.tick_params(axis="x", length=0, pad=4)
    axes[0].set_ylabel("Equal-seed change relative to naive")
    fig.legend(handles=[
        Line2D([0], [0], color=COLORS[0], marker="o", lw=2,
               markersize=3, label="Citation: seeds, mean, 95% CI"),
        Line2D([0], [0], color=COLORS[1], marker="o", lw=2,
               markersize=3, label="Sign-flip sensitivity: seeds, mean, 95% CI"),
        Line2D([0], [0], color="black", marker="D", lw=1,
               markersize=3, label="CSD and 95% CI"),
    ], loc="upper center", ncol=3, frameon=False, fontsize=6.5,
       columnspacing=1.0, handlelength=1.6, bbox_to_anchor=(.53, .995))
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / "fig3_csd_decomposition"
    fig.savefig(stem.with_suffix(".pdf"),
                metadata={"CreationDate": None, "ModDate": None,
                          "Title": "Citation--sensitivity decomposition",
                          "Creator": "generate_figures.py"})
    plt.close(fig)


if __name__ == "__main__":
    main()
