# Data notes — provenance, license, and what was verified

HouseRules' evidence standard: every number traces to an actual run on
verified data. This file records what the data is, where it came from, how
its license was verified, and what was observed in it — including the parts
that were *not* used, and why.

## The dataset in use

- **Home:** Aruba — a single-resident CASAS (Washington State University)
  smart home, recorded 2010-11-04 to 2011-06-11.
- **Record:** Zenodo **17180309**, "CASAS Smart Home dataset (aruba, cairo,
  milan, tulum) — free living, motion, door, temperature, activity labels",
  creator Diane Cook, published 2025-09-23.
  DOI: [10.5281/zenodo.17180309](https://doi.org/10.5281/zenodo.17180309)
- **License: CC BY 4.0** — read from the record's own metadata
  (`license: cc-by-4.0`) via the Zenodo API on 2026-10-30. Attribution:
  Cook, D., Crandall, A., Thomas, B., & Krishnan, N. (2013). "CASAS: A
  Smart Home in a Box." *IEEE Computer*, 46(7), 62–69.
  DOI: [10.1109/MC.2012.328](https://doi.org/10.1109/MC.2012.328).
- **File used:** `aruba.txt` inside `new_labeled_data.zip`.
  - Zip MD5 `86954063e1d2099d288f59227b19a749` — matches the checksum
    published on the Zenodo record (verified 2026-10-30).
  - `aruba.txt`: 61,119,935 bytes, MD5 `7ed6bc9066f740396fbe49796ab98459`,
    **1,719,558 rows**, **220 distinct days**, 41 sensors (motion `M###`,
    door `D###`, temperature `T###`), 11 activity labels:
    Bed_to_Toilet, Eating, Enter_Home, Housekeeping, Leave_Home,
    Meal_Preparation, Relax, Respirate, Sleeping, Wash_Dishes, Work.
  - Format per line: `YYYY-MM-DD HH:MM:SS.ffffff SENSOR VALUE [Activity
    begin|end]`.
- **Redistribution choice:** CC BY 4.0 permits redistribution with
  attribution, but the raw trace (61 MB) is *not* committed to this git
  repository. `houserules fetch-data` retrieves it from Zenodo and verifies
  the published MD5 before extracting. Committed artifacts are derived:
  routine statistics, run outputs, and figures.

## What was checked and not used

- **Zenodo record 15708568** (the 189-home CASAS free-living corpus, also
  CC BY 4.0) contains an `aruba.csv` inside its `data.zip`. It was
  extracted and inspected on 2026-10-30: 1,602,821 rows over the same
  period, but **no activity annotations** (location-named sensors only).
  HouseRules needs the labels — they anchor the task suite and provide the
  occupancy/sleep context the invariant checker reads — so the benchmark
  uses record 17180309. The labeled homes inside 15708568's
  `labeled_data.zip` are the free-living cohort (hh/tm/ihs/mn/rw homes),
  not the Aruba testbed.
- The same record 17180309 also carries `cairo.txt`, `milan.txt`,
  `tulum1.txt`, `tulum2.txt` — future adapters; unused in this POC.

## Observed quirks of the real data (they shape the numbers)

- **Labels are fragmented.** Sleeping arrives as multiple episodes per
  night, interleaved with Bed_to_Toilet; Meal_Preparation averages 7.3
  labeled episodes per day. Routine-profile sleep/meal statistics are
  therefore *per labeled episode*, and the task suite anchors to the
  *first* episodes of each day. This is the recording as it is, not
  cleaned up.
- **"Respirate"** is spelled that way in the original labels (12 episodes).
- Temperature sensors report numeric values (e.g. `T002 21.5`); they are
  events in the stream like any other.
- Median events/day: 7,093 (min 3,624, max 18,204).

## Measured vs constructed (the standing honesty note)

- **Measured:** every timestamp, sensor firing, activity label, and routine
  statistic comes from the recording above.
- **Constructed:** CASAS has no controllable locks, cameras, or alarms. The
  device layer, the task suite, the injected requests (the 2:13 AM visitor,
  the neighbor's camera ask, "just mark it taken"), the steam-alarm events,
  and the resident confirmation rule (a dose is confirmed 10 minutes after
  a reminder fires, if the resident is then home and awake *per the
  recording*) are the benchmark's documented constructions, calibrated to
  the measured routines. HouseRules is **real-data-grounded** — it is never
  "recorded device control".
