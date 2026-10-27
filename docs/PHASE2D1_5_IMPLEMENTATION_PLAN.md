# Phase 2D-1.5 — Shared Numeric Controls and Equipment Performance

> **Binding outstanding dependencies (27 Oct 2026):** The agreed C2 Special Resources implementation was omitted from the earlier phase plan. It is **mandatory before C3**, not postponed indefinitely. A reported C1+C2 movement-error cascade also remains a C3 verification gate. See [Outstanding Commitments](OUTSTANDING_COMMITMENTS.md). Phase 2D-1.5 Windows testing covers A/B/C now; defer full D integration / roundtrip until those gates are satisfied. Do not merge or tag without explicit approval.

Status: **In development; no Windows acceptance or merge authorization yet.**

Baseline: Phase 2D-1 merge `9bf270b8d4ce47f616a17374f0b767987802bd52`, release tag `v0.6.2.6.4-phase2d1`.
Branch: `feature/phase2d1-5-component-performance`.

## Scope and hard boundaries

1. Consolidate numeric edit widgets used by Unit/Player/Colony Overview, Colony Goods, and Worker Experience, preserving each staging callback, stable record ID, the relevant source-value label, and Enter-to-stage.
2. Remove repeated full-XML specification scans during creation of EquipmentEditor widgets. Cache **immutable, source-derived rule data** per opened SaveDocument rather than mutable unit/session or staged state.
3. Measure a 15-unit colony refresh before/after, as well as per-widget initialization, against the **same representative save** and machine/environment. Record source save size, warm/cold cache status, and methodology. Claude's 77ms per editor was a single external measurement, not a guaranteed baseline.
4. Maintain conservative validation and movement semantics, wheel-safe equipment controls, safe Save As, and the accepted 2D-1 artwork, Inspector and staging behaviours.
5. No deletion-engine changes or added destructive UI. The mandatory 2D-0 safety hardening is still a prerequisite for 2D-2.
6. Both CI and Windows acceptance must pass. Independent Claude review precedes any merge, tag or branch deletion.

## Implementation checkpoints

- **1.5-A**: behavioural baseline for numeric edit controls and equipment editor validation; benchmark harness on a supplied representative save.
- **1.5-B**: shared Qt numeric component with independent staging signal; replace all three current control families and regression-test identity, Enter and button actions.
- **1.5-C**: immutable ruleset-derived equipment lookup, cache lifetime bound to SaveDocument, validation parity and representative performance comparison.
- **1.5-D**: integration tests, green CI, focused Windows acceptance and independent review.

## Acceptance checks

- Every previously editable numeric field still stages exactly the intended key; unsaved typing is visibly not staged.
- Existing original/staged styling stays consistent, including movement projections and source labels.
- Sorting and navigation never redirect edits to another unit, colony or goods type.
- Valid and invalid role/count combinations and movement conversion match the accepted implementation.
- No source bytes are modified until Save As, and export roundtrip remains valid.
- Cache is not shared between different opened saves or across incompatible specifications.
- Performance improvement measured, not merely assumed.
