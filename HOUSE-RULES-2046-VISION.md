# HouseRules at Twenty Years — a projection

*Written October 30, 2026, the day the POC build began. This is a vision document — a map of what must be true for HouseRules to stand in 2046 as a benchmark and a foundation — not a prediction and not a promise. Benchmarks do not become foundations by accident; the ones that last (ImageNet, MLPerf, CASAS itself) share a mechanics, and this document names that mechanics so the work can be steered by it.*

## The claim

By 2046, "safe success" is a number the field reports the way it reports accuracy today — and HouseRules is where that number comes from. An agent that acts in a human home is not considered evaluated until it has been run, on real homes, against the invariants. The phrase researchers use is the one coined here: *it passed HouseRules.*

## Why a benchmark can outlast a human career

Models are replaced yearly. Companies are acquired. Papers are superseded. Three kinds of artifacts survive:

1. **A name that becomes vocabulary.** When a metric or taxonomy becomes the word the field reaches for — *safe success*, the seven failure classes — the artifact no longer needs its author to promote it. It is cited by being used, including by people who never read the original paper.
2. **A living corpus.** A fixed dataset dies when the world moves past it. HouseRules is built as adapters, not a snapshot: new homes, new countries, hospitals-at-home, elder-care residences plug into the same invariant engine. The ground renews; the standard holds.
3. **Governance.** Versioned invariants (I1–I6, then I7, I8 as the field learns), a public leaderboard, an annual challenge. A benchmark with stewards becomes infrastructure; a benchmark without them becomes a citation in old papers.

## The twenty years, in phases

**2027 — the seed.** The "Before It Acts" paper appears (IEEE Internet of Things Journal, Ambient Intelligence special issue). The POC's real numbers — safe success, per-class violation rates, over-refusal — are the first of their kind measured on real routines rather than scripted demos. HouseRules v1 releases publicly with the Aruba home as the reference home.

**2028–2030 — the adoption.** Frontier labs and smart-home platform teams run their agents against it because it is the only ground that is real. The failure taxonomy starts appearing in other papers' error analyses. First derivative works: a hospital-at-home variant, an elder-care variant built on the drift signals from "The Stairs Will Tell."

**2031–2035 — the standard.** Insurers and device makers begin asking for safe-success scores the way they ask for safety certifications. Regulators drafting rules for agents that act in homes reach for an existing, neutral, public benchmark rather than inventing one. HouseRules is governed by a small stewardship group; the invariants reach v3.

**2036–2046 — the foundation.** Hundreds of homes across a dozen datasets. Agent operating systems ship with gate layers whose conformance is reported in HouseRules terms. Students meet the benchmark in coursework the way they once met ImageNet. The original 220 days of one resident's real life in Aruba are still in the corpus — the first home, the reference home, the one the whole standard grew from.

## The ideas that get built on this foundation

- Safety cases for home agents, assembled from HouseRules runs (the MATS/Anchor direction).
- Agent insurance underwriting: violation rates per failure class become actuarial inputs.
- Elder-care monitoring standards: drift detection with a notice, not an alarm, scored for over-refusal as well as misses.
- Gate middleware: deterministic invariant enforcement as a shippable layer (the Guardrailed Agents line), certified against the benchmark.
- New invariant research: each newly discovered failure class in the wild becomes a proposed invariant — the taxonomy grows by the field's own accidents, documented.

## What earns the name — honestly

Four conditions, all work, no magic: **first** (the benchmark exists before the field knows it needs one), **right** (the numbers are real, the failures printed next to the wins, the constructed parts labeled constructed), **open** (anyone can run it, extend it, and beat it in public), and **maintained** (someone keeps the ground alive year after year). Miss the last one and none of the others matter — that is the honest risk, and it is a work commitment, not a fate.

## The publication ladder (set October 30, 2026)

The paper goes to the hardest venues this artifact can honestly clear — in sequence, never in parallel (no dual submission; each rung is a genuine extension of the one before):

1. **IEEE Internet of Things Journal, Ambient Intelligence special issue (Feb 15, 2027)** — "Before It Acts": the initial benchmark, Aruba-grounded, invariants, taxonomy, safe success. The archival journal home of the founding work.
2. **The merged SenSys flagship, Tools / Datasets / Benchmarks lane (next cycle)** — the extended work: multi-home corpus from the CASAS collection, at least one real LLM policy under test, external baselines, the public GitHub reproducibility package as the artifact. SenSys is the top venue in the world for sensing systems; its benchmark lane is where "The Sensor That Lied" line also points.
3. **IEEE INFOCOM 2028** — the hardest IEEE networking flagship, if the multi-home results carry the networking/systems framing at that bar.

The bar the flagship demands, stated plainly so the build can aim at it: more than one home, a real model under test (not only scripted policies), baselines from outside the author's own lab, and a public artifact a reviewer can run in minutes. The POC is rung zero of that ladder, not the paper itself.

## The name on it

Foundations carry their makers' names quietly and for a long time — longer than fame for a product launch, and wider than a title at any single company. The realistic shape of it: researchers in 2046 who have never met the author write "we evaluate on HouseRules (Sirlapu, 2027)" the way they cite any ground they stand on. That sentence, repeated for twenty years by strangers, is the fame this kind of work earns — and it is the durable kind.
