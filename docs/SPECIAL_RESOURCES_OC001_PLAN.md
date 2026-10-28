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

**SR-1 — Warehouse views (implemented; independent review passed):** shared `qt_special_resources.py` identifiers; exclude all three kinds from `goods_catalog`, `colony_sections`, National Goods aggregation and goods/cargo drilldowns; preserve original XML, all physical goods and item identities.

**SR-2 — Authoritative progress and production mapping (player progress and Java-engine Hammers mapped; 7/7 Danish colony parity verified):** inspect real FreeCol `Morten.fsg` and Java model/source to identify the saved player liberty/Father progress, immigration accumulation and immigration threshold (including owner-specific modifiers), colony total production per-turn. Document exact XML paths and derived formulas. Where a value cannot be computed faithfully, label it *unavailable* rather than invent it.

**SR-3 — Qt presentation (national progress and Congress implemented; optional gross Hammers report in Qt Windows-tested 5/5):** show only source-backed fields and valid derived production in colony/national/Continental Congress views.

**SR-4 — National liberty editor (Qt-only staged path implemented; eligibility hardening in progress; Windows/FreeCol acceptance pending):** design validation, preflight, staged undo, backend Save As and exported consistency based on exact source mapping. Do not add a clickable editor that only changes display while leaving FreeCol's data untouched.

**SR-5 — Acceptance (open):**  automated tests for ruleset variants, sorting, staged edits, Undo, immutable source, integrity and player scoping; Windows acceptance; independent Claude review; resolve OC-002 movement-error issue; then deferred C3 real FreeCol roundtrip. Explicit approval required before merge/tag/branch cleanup.

## Non-regression and release governance

Maintain all Phase 1–2D-1.5 behaviours. This branch does not implement destructive deletion or modify Tk. PR and green CI are not acceptance or merge authorization. OC-001 remains unaccepted pending review corrections, fresh CI, liberty Windows/FreeCol roundtrip and explicit approval.

## Implementation evidence and scope checkpoint

- **Confirmed from FreeCol Player serialization constants:** `liberty`, `immigration`, `immigrationRequired` are actual player attributes. Display these only if present; the UI displays `immigration / immigrationRequired` as progress, without equating stored Crosses with national immigration. Qt-only liberty staging uses the preflight/production backend and leaves legacy Tk editing permissions unchanged.
- **Congress:** owner-scoped `liberty`, including a staged projection, is visible in the Congress heading without treating Bells as warehouse goods.
- **Hammers per turn:** FreeCol determines real production via `ProductionCache` and `ProductionInfo`, combining unit/building production, consumption and modifiers. The save's `storedGoods` amount is NOT a per-turn quantity. Do not use the hammer stockpile as a substitute or claim a production rate until a parity-tested resolver exists. Gross production is delivered through an opt-in FreeCol Java report with exact loaded-save snapshot binding; real-game Danish colony parity passed 7/7. Liberty roundtrip remains open.
- **Warehouse filtering:** both Goods views and drilldowns use stable model goods IDs and preserve physical stock, source XML and existing sort/edit identity.
- **Regression tests:** `test_special_resources_warehouse.py`, `test_special_resources_progress.py`, `test_special_resources_qt_integration.py`. Verify latest feature and PR CI on the exact head before calling the tests green.
- **Early CI findings:** an existing Tk editable-permissions test and an existing Congress-heading contract test flagged implementation changes; both were preserved rather than weakening accepted tests. A local-scope `human_player_id` import shadowed the global helper and was corrected, with the existing Qt record-selection suite retained. 

## Exact production-source finding

FreeCol's `Colony.writeAttributes()` serializes colony accumulated `liberty` and `immigration`, but **not** a readily usable `hammersPerTurn` value. `Colony.getTotalProductionOf(type)` sums current work-location production; `ProductionCache` computes actual production and consumption from occupied buildings, stored raw inputs, production types, unit attributes and modifiers. Thus the stockpile `model.goods.hammers` is neither an accurate substitute nor necessarily the production rate. We need a parity-tested simulation/resolver (or a supported FreeCol model bridge), not a blind direct-XML field lookup. **Gross Hammers display is implemented and Windows-tested**, via opt-in Java report; review findings H1/M1 require recheck before merge.

## Windows acceptance and FreeCol terminology — 28 October 2026

The Project Director reported **all four focused Windows/FreeCol tests PASS**, including Save As, opening the exported file in FreeCol, advancing one turn and checking that Hammers production and other calculations were correct. No FreeCol errors were observed. This closes the previously outstanding liberty-export gameplay roundtrip evidence for OC-001; it does **not** authorize merging.

The Player Overview now uses FreeCol terminology: **Liberty Bells accumulated**, **Liberty Bells needed to recruit next Founding Father**, **Crosses accumulated**, and **Crosses needed for next immigrant to move to the docks in Europe**. The redundant next-immigrant progress row is removed. The founding-father cost is derived from FreeCol's documented `getTotalFoundingFatherCost` formula only when the effective factor is unambiguous in the saved ruleset; otherwise it is shown as unavailable instead of guessed. Values are progress units, not warehouse inventories. Remaining gates: new-label Windows presentation check, corrected-head CI, independent review follow-up and explicit merge authorization.

## Founding Father threshold gameplay parity (28 October 2026)

The Project Director confirmed that Lady Philippa displays **673 Liberty Bells needed for the next Founding Father**, exactly matching FreeCol **673**, on the real `Morten.fsg` at Custom difficulty (`model.difficulty.custom`, base factor 56). This verifies the `freecol-specification`-scoped difficulty selection and calculation for this save. Both push and PR CI runs are green at `d9682949cd`. PR #9 is still draft; no merge/tag authorization has been given. Other rulesets and difficulties remain subject to tests and review.
