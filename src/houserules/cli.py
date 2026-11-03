"""HouseRules command line.

    houserules fetch-data           download + verify the CASAS Aruba home
    houserules run                  fetch (if needed) and run the benchmark
    houserules profile              print the measured routine profile

`houserules run` is the one-command quickstart: it writes
results/results.json, results/decision_log.jsonl and RESULTS.md, and
prints the headline metrics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from . import __version__
from .adapters import CasasAdapter, build_routine_profile
from .fetch import DOI, ZENODO_RECORD, aruba_path, default_data_dir, fetch_data
from .invariants import InvariantConfig
from .policies import BASELINE_POLICIES
from .report import render_results_md
from .runner import run_benchmark


def _resolve_data(args) -> Path:
    if getattr(args, "data", None):
        return Path(args.data)
    candidate = aruba_path(default_data_dir())
    if candidate.exists():
        return candidate
    return fetch_data()


def _md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_fetch_data(args) -> int:
    path = fetch_data(Path(args.data_dir) if args.data_dir else None,
                      force=args.force)
    print(f"Aruba home ready at {path}")
    return 0


def cmd_profile(args) -> int:
    path = _resolve_data(args)
    days = CasasAdapter(path).days()
    prof = build_routine_profile(days)
    print(json.dumps(prof.as_dict(), indent=2))
    return 0


def cmd_run(args) -> int:
    path = _resolve_data(args)
    days = CasasAdapter(path).days()
    if args.days:
        days = days[: args.days]
    prof = build_routine_profile(days)
    policies = [cls() for cls in BASELINE_POLICIES]
    results, decisions = run_benchmark(days, policies, InvariantConfig())
    results["benchmark"] = {
        "name": "HouseRules", "version": __version__,
        "artifact": "Before It Acts: A Safety Benchmark for LLM Agents in "
                    "Real Smart Homes (POC, step 1)",
        "policies_are_scripted_baselines": True,
        "live_model_run": False,
    }
    results["dataset"] = {
        "home": "Aruba (single resident)",
        "source": "CASAS Smart Home dataset (aruba, cairo, milan, tulum) - "
                  "free living, motion, door, temperature, activity labels (WSU)",
        "zenodo_record": ZENODO_RECORD, "doi": DOI,
        "license": "CC BY 4.0",
        "file": path.name, "file_md5": _md5(path),
        "days": len(days),
        "routine_profile": prof.as_dict(),
    }
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(results, indent=2))
    with open(out_dir / "decision_log.jsonl", "w") as fh:
        for rec in decisions:
            fh.write(json.dumps(rec) + "\n")
    Path(args.results_md).write_text(render_results_md(results))
    print(f"HouseRules {__version__} — {len(days)} real days of the Aruba home, "
          f"{prof.total_events} sensor events")
    print(f"{'policy':<16} {'episodes':>8} {'task':>7} {'SAFE':>7} "
          f"{'viol/100':>8} {'sev-wtd':>8} {'refuse✓':>8} {'over-ref':>8}")
    for name, p in results["policies"].items():
        def pct(x):
            return "n/a" if x is None else f"{x * 100:.1f}%"
        print(f"{name:<16} {p['episodes']:>8} {pct(p['task_success_rate']):>7} "
              f"{pct(p['safe_success_rate']):>7} "
              f"{p['violations_per_100_episodes']:>8} "
              f"{p['severity_weighted_score']:>8} "
              f"{pct(p['correct_refusal_rate']):>8} "
              f"{pct(p['over_refusal_rate']):>8}")
    print(f"\nWrote {out_dir / 'results.json'}, "
          f"{out_dir / 'decision_log.jsonl'}, {args.results_md}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="houserules", description=__doc__)
    ap.add_argument("--version", action="version", version=__version__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch-data", help="download + verify the Aruba dataset")
    f.add_argument("--data-dir", default=None)
    f.add_argument("--force", action="store_true")
    f.set_defaults(fn=cmd_fetch_data)

    r = sub.add_parser("run", help="run the benchmark end-to-end")
    r.add_argument("--data", default=None, help="path to a CASAS-format home file")
    r.add_argument("--days", type=int, default=None, help="limit to first N days")
    r.add_argument("--out-dir", default="results")
    r.add_argument("--results-md", default="RESULTS.md")
    r.set_defaults(fn=cmd_run)

    p = sub.add_parser("profile", help="print the measured routine profile")
    p.add_argument("--data", default=None)
    p.set_defaults(fn=cmd_profile)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
