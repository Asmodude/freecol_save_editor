# OC-001 Special Resources — implementation and acceptance plan

**Origin:** Project Director decision 26 October 2026. **Mandatory C2 follow-up before C3 FreeCol roundtrip.**  
**Source:** accepted Phase 2D-1.5 release `852e1e5` / `v0.6.2.6.4-phase2d1-5`.  
**Branch:** `feature/special-resources-oc001`. **Not accepted.**

## The agreed behaviour

| Resource | Remove from | Required destination |
| --- | --- | --- |
| Bells | Colony Goods, National Goods | Colony Overview; Nation Overview; Continental Congress. National liberty-points editor after mapping the authoritative player attribute and export implications. |
| Crosses | Colony Goods, National Goods | Nation Overview; immigration progress against next threshold, using real source and rules. |
| Hammers | Colony Goods, National Goods | Colony Overview: production per turn, initially read-only. |

These are *production or progress concepts*, not physical warehouse stock. Avoid pretending an element of `storedGoods` is the national liberty total, the immigration tally or production per turn. For nonstandard rulesets, transformation ratios may differ: 1 Bell does not necessarily equal 1 liberty point, and 1 Cross does not necessarily equal 1 immigration point.

## Checkpoints

**SR-1 — Warehouse views (implemented, awaiting CI/Windows):** shared `qt_special_resources.py` identifiers; exclude all three kinds from `goods_catalog`, `colony_sections`, National Goods aggregation and goods/cargo drilldowns; preserve original XML, all physical goods and item identities.

**SR-2 — Authoritative progress and production mapping (open):** inspect real FreeCol `Morten.fsg` and Java model/source to identify the saved player liberty/Father progress, immigration accumulation and immigration threshold (including owner-specific modifiers), colony total production per-turn. Document exact XML paths and derived formulas. Where a value cannot be computed faithfully, label it *unavailable* rather than invent it.

**SR-3 — Qt presentation (open):** show only source-backed fields and valid derived production in colony/national/Continental Congress views.

**SR-4 — National liberty editor (open):** design validation, preflight, staged undo, backend Save As and exported consistency based on exact source mapping. Do not add a clickable editor that only changes display while leaving FreeCol's data untouched.

**SR-5 — Acceptance (open):**  automated tests for ruleset variants, sorting, staged edits, Undo, immutable source, integrity and player scoping; Windows acceptance; independent Claude review; resolve OC-002 movement-error issue; then deferred C3 real FreeCol roundtrip. Explicit approval required before merge/tag/branch cleanup.

## Non-regression and release governance

Maintain all Phase 1–2D-1.5 behaviours. This branch does not implement destructive deletion or modify Tk. PR and green CI are not acceptance or merge authorization. Unfinished SR-2/3/4 prohibit claiming OC-001 complete.
