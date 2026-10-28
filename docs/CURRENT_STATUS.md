# Verified Project Status and Planning Protocol

**As of 28 October 2026.** This is the authoritative *current-status index* for the FreeCol Save Editor. Historical phase plans, reviews and changelog entries remain evidence of what was planned or known at their publication time; they are **not** current status without reconciliation here.

## Verified merged baseline

- `main`: `a97ae1aa9362c6a22a4cc1025b1eb9ccd9d87e5d`, tag `v0.6.2.6.4-oc001` (annotated, points at this commit); CI on `main` succeeded.
- Phase 2C: PR #6 merged `64dc15c`, 27 October; non-destructive Qt editing parity. **Not pending C3/C4 reacceptance.**
- Phase 2D-1: PR #7 merged `9bf270b`, 27 October. **Implemented and integrated**, not upcoming. `qt_stage_controls.StageChangeButton`, `qt_equipment_editor.EquipmentEditor`, `qt_readonly.py` editing-instructions banner and source-value Inspector notice, and `test_phase2d_ux.py`, `test_phase2d1_review_regressions.py`. Claude's review of an earlier head recorded caveats; merge and subsequent testing constitute the accepted integration outcome. Do not present 2D-1 as planned.
- Phase 2D-1.5: PR #8 merged `852e1e5`, 27 October. Shared `NumericStageEditor`, indexed equipment rules, performance and eligibility corrections; accepted real-save checks and Windows retests. **Integrated**, not pending.
- OC-001 Special Resources: PR #9 merged `a97ae1a`, 28 October. Warehouse filtering, Liberty Bells/Crosses national progress, optional Java bridge for gross Hammers, staged eligible national liberty, threshold from actual saved difficulty. Windows and FreeCol export/turn/reload accepted; founder threshold **673 in Lady Philippa = 673 in FreeCol**. Follow-up independent Claude review **explicitly deferred** to the next independent review (not independently re-PASSed).
- OC-002 C1/C2 movement-error cascade: **CLOSED BY PROJECT DIRECTOR'S DECISION, NOT ROOT-CAUSE PROVEN.** Probable FreeCol game issue; do not reproduce, investigate or block editor development on this without new evidence and explicit reauthorization. Preserve editor-specific movement validation and existing accepted proportional movement semantics.

## Verified next work: Phase 2D-0, before any new destructive Qt UI

**Not implemented on `main`.** `deletion_engine._element_spans` currently searches for closing tags after a matched opener and cannot safely distinguish self-closing spans; `remove_unit` and `remove_settlement` remain conservative but have no full survivor-preservation/exact-removal guard. No shared `plan_unit_deletion` API is present. The distinct native removal path remains in `edit_backend.py`. These are concrete code findings, not assumed from the plan.

2D-0 must address:
1. Precise XML deletion spans for self-closing, normal and mixed tags, with ambiguous cases refused.
2. Verify actual planned removals and all surviving nodes (including cached duplicates and contexts), reject collateral changes.
3. Enforce *whole staged transaction* last-colony-inhabitant refusal and edit/deletion conflicts.
4. Unify safe native/unit deletion backend, retaining Tk compatibility, and supply read-only unit-deletion impact planner.
5. CI regressions, representative genuine FreeCol save/load/advance/save/reload, Windows acceptance, and **independent safety review** before opening 2D-2.

Then proceed **2D-2** safe unit deletion Qt; **2D-3** native settlement deletion Qt; **2D-4** human and rival European colony deletion on separate reviewed branch, beginning with actual FreeCol dependency matrix. Never reopen cached-missionary unsafe deletion as an assumed prerequisite; preserve conservative refusal.

## Other known unfinished matters — not immediate phase blockers unless separately agreed

- Claude's OC-001 post-correction independent review, bundled into next independent review with explicit review request.
- Phase 2D-1.5 minor review items (accessible per-field Stage Change naming, possible narrow-window clipping/style naming and future rules correctness) remain follow-ups, not evidence that the completed phases are unmerged.
- Reveal Entire Map: research-gated future staged operation.
- Terrain editing milestones, map rendering and release 0.9 cleanup remain on `ROADMAP.md`; not implemented as part of 2D-0.

## Permanent rule: source-of-truth reconciliation before **every** future development phase, plan or status answer

1. Query actual `main` SHA, merged PRs, exact tags, active branches and **CI on the relevant exact commit**. Confirm features by inspecting production code and behavioural regression tests; do not infer from historical roadmap text or a PR title alone.
2. Compare against `ROADMAP.md`, `docs/PHASE2D_IMPLEMENTATION_PLAN.md`, `docs/OUTSTANDING_COMMITMENTS.md`, review reports, acceptance evidence and `CHANGELOG.md`. Classify each item as **implemented / merged / accepted / partially implemented / open / deferred by explicit decision / obsolete**. Treat these as different states.
3. Record any conflict between code, tests, reviews and documents as an explicit discrepancy; *do not silently promote a code presence to Windows acceptance or independent review*.
4. **Before implementing the next item**, reconcile this status index, ROADMAP and outstanding commitments on a focused branch; put the audit evidence and remaining gates in the PR. Before recommending work, confirm that the feature is **not already in the merged baseline**.
5. Update status at **each** acceptance and merge/tag transition; mark old instructions as historical when superseded. Keep independent-review deferrals visible until reviewed or explicitly waived. The responsible coordinator is ChatGPT; the Project Director approves scope, milestones and integrations.
6. Do not merge, tag, delete branches or change accepted behaviour without separate express authorization. A documentation-only audit PR is not authorization to alter application code or advance a checkpoint.

## Audit trail

28 October 2026: checked GitHub merged PRs #6–#9, `main` commit and green CI; inspected `qt_readonly.py`, `qt_stage_controls.py`, `qt_equipment_editor.py`, `deletion_engine.py`, `edit_backend.py`, published review records and regression test filenames. Full re-execution of test suite and additional Windows verification were **not** performed in this documentation audit. No implementation-code changes.
