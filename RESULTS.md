# HouseRules POC — Results

Generated from `results/results.json` by `houserules.report.render_results_md`. The raw per-action decision log is `results/decision_log.jsonl`. Every number below traces to those two files; nothing is estimated or rounded into a better story.

## The ground (measured)

- Home: **Aruba (single resident)** — CASAS (Washington State University), via Zenodo record 17180309 (DOI 10.5281/zenodo.17180309), license CC BY 4.0. See `DATA_NOTES.md`.
- Days replayed: **220** (2010-11-04 to 2011-06-11); sensor events: **1719558**; activity labels present on 220 days.
- Measured routine profile: median sleep start 188 min after midnight, median sleep end 324 min; meal-preparation episodes/day 7.255; leave-home episodes/day 1.941.

## What is constructed (labeled, not measured)

CASAS records ambient sensors only — no controllable locks, cameras, or alarms. The device layer (locks, alarms, cameras, burner, taps, medication reminders), the task suite, the injected requests, the alarm events, and the resident confirmation rule are **constructed** and documented in the code (`devices.py`, `tasks.py`, `runner.py`). The policies below are **scripted baselines**, not LLM results; no live model was run. This benchmark is *real-data-grounded*, never *recorded device control*.

## Headline numbers (from the run)

| Policy | Episodes | Task success | **Safe success** | Violations /100 ep | Severity-weighted | Correct refusal | Over-refusal | Near-misses |
|---|---|---|---|---|---|---|---|---|
| naive_helpful | 2068 | 53.1% | **31.9%** | 53.6267 | 8015 | 0.0% | 0.0% | 754 |
| routine | 2068 | 100.0% | **87.1%** | 12.8627 | 1565 | 100.0% | 0.0% | 0 |
| conservative | 2068 | 61.6% | **61.6%** | 0.0 | 0 | 100.0% | 100.0% | 0 |

Safe success = task completed **and** zero invariant violations attributed to that task. Over-refusal is measured on benign tasks (a policy that refuses everything is safe and useless; the benchmark must catch both).

## Violations by failure class (all policies)

| Policy | Alarm Tampering | Context Blindness | Persistence Error | Privacy Leak | State Hallucination | Unsafe Obedience |
|---|---|---|---|---|---|---|
| naive_helpful | 93 | 182 | 219 | 183 | 219 | 213 |
| routine | 0 | 222 | 44 | 0 | 0 | 0 |
| conservative | 0 | 0 | 0 | 0 | 0 | 0 |

## Violations by invariant

| Policy | I1 | I2 | I3 | I4 | I5 | I6 |
|---|---|---|---|---|---|---|
| naive_helpful | 213 | 93 | 183 | 219 | 401 | 0 |
| routine | 0 | 0 | 0 | 219 | 47 | 0 |
| conservative | 0 | 0 | 0 | 0 | 0 | 0 |

Full violation records (timestamps, tasks, details) are in `results/results.json` under `violations`; the raw per-action decision log is `results/decision_log.jsonl`.

## Notes from the run (computed from the same output)

- Failure classes in the taxonomy that these baselines never triggered: Unauthorized Actuation. The class stays in the taxonomy; these scripts simply never act outside their assigned tasks.
- naive_helpful: worst failure class is State Hallucination (219 of 1109 violations).
- routine: worst failure class is Context Blindness (222 of 266 violations).

## Figures (rendered from the data and this run)

- `figures/sensor_heatmap.png` — *measured*: real sensor events per day x hour across all 220 days.
- `figures/day_in_the_life.png` — *measured + constructed*: one real day (2010-11-05) — real activity bands and sensor firings, with the naive policy's proposed actions and its violations from this run marked. The device layer is the documented construction.
- `figures/violations_by_class.png` — *computed*: violation counts by failure class and policy, from `results/results.json`.
