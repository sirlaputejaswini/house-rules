"""Generate the repo figures from the real data and the real run outputs.

    python tools/make_figures.py [--data data/aruba.txt] [--results results]

Figure 1 (sensor_heatmap.png) is *measured*: counts of real sensor events
from the Aruba stream, per day x hour.
Figure 2 (day_in_the_life.png) mixes both kinds, and its caption says so:
the sensor firings and activity bands are measured from the recording;
the policy actions and violation markers come from the benchmark run over
the *constructed* device layer (results/decision_log.jsonl,
results/results.json).
Figure 3 (violations_by_class.png) is computed from results/results.json —
checker verdicts over the constructed device layer, anchored to the real
stream. Nothing in any figure is stock art or mock data.

Requires the optional `figures` extra: pip install "houserules[figures]".
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from houserules.adapters import CasasAdapter  # noqa: E402

POLICY_FOR_TIMELINE = "naive_helpful"


def figure_heatmap(days, out: Path):
    mat = np.zeros((len(days), 24), dtype=int)
    for i, day in enumerate(days):
        for ev in day.events:
            mat[i, ev.at.hour] += 1
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(mat, aspect="auto", cmap="viridis", origin="upper")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Day of the recording")
    ax.set_title("Aruba home — real sensor events per day x hour (measured)")
    ticks = list(range(0, len(days), 30))
    ax.set_yticks(ticks)
    ax.set_yticklabels([str(days[i].date) for i in ticks])
    ax.set_xticks(range(0, 24, 2))
    fig.colorbar(im, ax=ax, label="sensor events")
    fig.text(0.01, 0.012,
             "Measured: counts of real CASAS Aruba sensor events "
             "(1,719,558 events, 220 days, 2010-11-04 to 2011-06-11).\n"
             "Source: Zenodo record 17180309, CC BY 4.0.",
             fontsize=7, ha="left")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out, dpi=150)
    plt.close(fig)


def figure_day_in_the_life(day, decisions, violations, out: Path):
    date_s = str(day.date)
    day0 = datetime.combine(day.date, datetime.min.time())
    def hr(ts):
        return (ts - day0).total_seconds() / 3600.0
    fig, axes = plt.subplots(3, 1, figsize=(11, 6.5), sharex=True,
                             gridspec_kw={"height_ratios": [1, 2, 1.4]})
    # Panel 1: measured activity bands
    ax = axes[0]
    acts = sorted(day.intervals.items())
    for i, (name, spans) in enumerate(acts):
        for s, e in spans:
            ax.barh(i, hr(e) - hr(s), left=hr(s), height=0.7)
    ax.set_yticks(range(len(acts)))
    ax.set_yticklabels([a for a, _ in acts], fontsize=7)
    ax.set_title(f"A day in the life of the Aruba home — {date_s} (measured activities)")
    # Panel 2: measured sensor firings (motion/door sensors only)
    ax = axes[1]
    sensors = sorted({ev.sensor for ev in day.events if ev.sensor[0] in "MD"})
    sidx = {s: i for i, s in enumerate(sensors)}
    xs, ys = [], []
    for ev in day.events:
        if ev.sensor in sidx:
            xs.append(hr(ev.at))
            ys.append(sidx[ev.sensor])
    ax.scatter(xs, ys, s=1.5, alpha=0.6)
    ax.set_yticks(range(len(sensors)))
    ax.set_yticklabels(sensors, fontsize=6)
    ax.set_ylabel("sensor")
    ax.set_title("Real sensor firings (motion / door sensors)", fontsize=10)
    # Panel 3: policy actions (constructed device layer) + violations
    ax = axes[2]
    dec = [d for d in decisions
           if d["date"] == date_s and d["policy"] == POLICY_FOR_TIMELINE]
    kinds = sorted({d["action"] for d in dec})
    kidx = {k: i for i, k in enumerate(kinds)}
    for d in dec:
        t = hr(datetime.fromisoformat(d["at"]))
        marker = "o" if d["executed"] else "x"
        color = "tab:blue" if d["executed"] else "tab:gray"
        ax.scatter([t], [kidx[d["action"]]], marker=marker, s=28, c=color)
    viol = [v for v in violations
            if v["policy"] == POLICY_FOR_TIMELINE and v["at"][:10] == date_s]
    for v in viol:
        t = hr(datetime.fromisoformat(v["at"]))
        ax.annotate(v["invariant"], (t, len(kinds) - 0.4), color="red",
                    fontsize=9, fontweight="bold", ha="center")
        ax.plot([t, t], [-0.6, len(kinds) - 0.2], color="red", lw=0.8, alpha=0.6)
    ax.set_yticks(range(len(kinds)))
    ax.set_yticklabels(kinds, fontsize=7)
    ax.set_xlabel("Hour of day")
    ax.set_title(f"Policy '{POLICY_FOR_TIMELINE}' — proposed actions (o = executed, "
                 f"x = blocked near-miss); red = invariant violated", fontsize=10)
    fig.text(0.01, 0.012,
             "Measured: activity bands and sensor firings are the real recording.\n"
             "Constructed: the device layer is the benchmark's documented "
             "construction; actions and violations are from the actual run\n"
             "(results/decision_log.jsonl, results/results.json).",
             fontsize=7, ha="left")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out, dpi=150)
    plt.close(fig)


def figure_violations(results, out: Path):
    classes = sorted({c for p in results["policies"].values()
                      for c in p["violations_by_class"]})
    policies = list(results["policies"])
    x = np.arange(len(classes))
    width = 0.8 / max(len(policies), 1)
    fig, ax = plt.subplots(figsize=(11, 5))
    for i, name in enumerate(policies):
        vals = [results["policies"][name]["violations_by_class"].get(c, 0)
                for c in classes]
        ax.bar(x + i * width, vals, width, label=name)
    ax.set_xticks(x + width * (len(policies) - 1) / 2)
    ax.set_xticklabels(classes, rotation=18, ha="right", fontsize=8)
    ax.set_ylabel("violations (220 days, count)")
    ax.set_title("Violations by failure class and policy — from the run output")
    ax.legend()
    fig.text(0.01, 0.012,
             "Computed from results/results.json: deterministic checker verdicts "
             "over the constructed device layer,\non tasks anchored to the real "
             "Aruba stream. Policies are scripted baselines, not LLMs.",
             fontsize=7, ha="left")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out, dpi=150)
    plt.close(fig)


def pick_timeline_day(results, days_by_date):
    """Deterministically pick a rich day: naive violations covering I1+I4+I5."""
    by_day = defaultdict(list)
    for v in results["violations"]:
        if v["policy"] == POLICY_FOR_TIMELINE:
            by_day[v["at"][:10]].append(v["invariant"])
    for d in sorted(by_day):
        if {"I1", "I4", "I5"} <= set(by_day[d]) and len(by_day[d]) >= 4:
            return days_by_date[d]
    raise SystemExit("no suitable timeline day found in the run output")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/aruba.txt")
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="figures")
    args = ap.parse_args()
    days = CasasAdapter(args.data).days()
    results = json.loads((Path(args.results) / "results.json").read_text())
    decisions = [json.loads(line) for line in
                 (Path(args.results) / "decision_log.jsonl").read_text().splitlines()]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    figure_heatmap(days, out_dir / "sensor_heatmap.png")
    days_by_date = {str(d.date): d for d in days}
    day = pick_timeline_day(results, days_by_date)
    figure_day_in_the_life(day, decisions, results["violations"],
                           out_dir / "day_in_the_life.png")
    figure_violations(results, out_dir / "violations_by_class.png")
    print(f"figures written to {out_dir}/ (timeline day: {day.date})")


if __name__ == "__main__":
    main()
