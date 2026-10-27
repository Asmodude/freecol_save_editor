# Phase 2D — Approved Implementation and Acceptance Plan

**Status: PLAN ACCEPTED by user — 27 October 2026. IMPLEMENTATION NOT YET ACCEPTED.**
**Source baseline:** `main` @ `64dc15cb46f4174bff4f1dbba37e1c8cf560c68f` (Phase 2C accepted and merged).
**Initial branch:** `feature/phase2d-ux-and-deletion-parity`.
**Independent review:** `docs/PHASE2D_INDEPENDENT_REVIEW.md` (Claude, 27 October 2026; PASS WITH CAVEATS and mandatory deletion safety gate).
**Parent requirements:** `ROADMAP.md`, `docs/PHASE2_DEVELOPMENT_PLAN.md`, `docs/PHASE2C_PARITY_MATRIX.md`.
**Approval scope:** User accepted the independently reviewed implementation sequence and the PySide6-first design principle. Approval authorises development against the plan, **not** passing any checkpoint, merging, tagging, deleting branches or shipping software.

## Architecture: PySide6-first (explicitly user-approved)

All new GUI features, controls and workflow enhancements target **Lady Philippa Y. Side VI (PySide6/Qt)**. Shared XML parsing, validation, edit session, deletion and save/export modules remain independent of both GUI frameworks and serve the long-term Qt architecture.

**Sir Thorwald Kilgannon Inter (Tkinter)** is frozen: essential fixes and compatibility/non-regression only until his planned retirement. Do not implement new functionality in Tk, design new Qt widgets for Tk, or degrade Qt validation to accommodate Tk. Existing accepted Tk operations must still work. Preserve the shared proportional movement semantics accepted in Phase 2C. Remove retired Tk facilities only at an authorised later milestone.

## Execution sequence and gates

### 2D-1 — Approved Qt UX and targeted editor consolidation (first implementation checkpoint)

- Replace **all staging-action icon-only pencil controls** with text **Stage Change**, not undo or other controls. Audit Overview, unit equipment, colony Goods/Workers/Stationed units, native settlement Alarm/Skill and Diplomacy.
- Permanently display directly beneath the main toolbar: **To make edits: Edit data one at a time followed by clicking "Stage Change" next to that edit.**
- Clearly label Inspector Details and Raw XML as **original/source save values, excluding pending staged changes**; explain that a staged Pioneer/100-tools unit can still show the source default role and `roleCount=0` until export.
- Build a *small* shared Qt inline editor kit (field/choice and **one** equipment editor) so presentation, statuses, accessible names, keyboard behaviour, tooltips and staging buttons cannot diverge. Centralise role terminology in `presentation.py` as appropriate. Do not put FreeCol validation rules in widgets.
- Keep original/staged markers, explicit stage-on-click or Enter semantics, stage-time validation, undo and guarded Save As unchanged. Confirm long button labels fit resized windows; do not silently change mouse-wheel equipment controls.
- Replace source-text assertions touched by the refactor with behavioural offscreen UI checks; run broad regression suite and user Windows visual checks.
- No destructive editing UI in this checkpoint.

### 2D-0 — Deletion engine hardening (hard gate before 2D-2 onward)

This safety checkpoint may proceed separately from 2D-1; **no new destructive UI may be exposed until 2D-0 is accepted**.

- Fix `deletion_engine._element_spans` and the native deletion path for self-closing elements, explicit closing tags and mixed forms. Refuse uncertain XML structures.
- Implement an **exact-removal verification guard** on destructive operations: verify the planned target, associated AI/owned-unit/cached records and references are the only removed/changed records. Account for repeated cached IDs and structural context; verify all surviving elements' contents/attributes, not merely sets of unique IDs. Fail closed on unexpected changes, including syntactically valid collateral deletions.
- Forbid removing the **last inhabitant of a European colony**, counting the aggregate staged edit set, including deletions that are individually legal but jointly invalid. Investigate/verify SoL and Tory state where remaining workers change.
- Reconcile `remove_unit(...allow_settlement=...)` with `edit_backend._remove_native_unit` into one tested shared deletion implementation; keep legacy Tk edit-key compatibility and accepted safety refusals.
- Provide `plan_unit_deletion()` (or equivalent UI-independent impact planning API) reporting owner, location, planned removals/dependencies/refusal reasons without mutating XML.
- Regression matrix: self-closing/explicit/mixed tags; deletion of exactly intended nodes; repeated cached IDs; no-op/invalid; nested/cargo/AI references; two-stage last-colonist scenarios; cached-missionary refusal; source immutability and guarded Save As.
- Record demonstrated safe output for representative FreeCol save/load/turn/resave cases. Correct the known potential corruption path before broadening destructive editing.

### Shared safety infrastructure before deletion UI (complete by 2D-2)

- Establish **one authoritative checked staging path**, preserving Tk compatibility while making Qt preflight mandatory; do not call Tk-only unvalidated `EditSession.stage_*_deletion` methods from Qt.
- Extract shared edit-set validation for `edit_preflight` and `edit_backend.produce` so deletion conflicts, unknown goods and reciprocal stance rules cannot drift. Keep final export validation independent of cached UI state.
- For deletions, validate the **whole staged transaction**; prevent same-record property/edit vs deletion conflicts and colony deletion when its goods, SoL or worker edits are staged.
- Define a shared confirmation surface driven by the impact plan: actual nation/owner, affected units, AI records, cached copies and tiles; **Cancel is default**. Distinguish safe refusal from a broken editor.

### 2D-2 — Unit deletion in Qt, for all owner types

- Expose only supported, validated human/rival European/native unit deletions using checked staging and safe export.
- Visually separate destructive actions from routine edits (**O5**). Confirm before staging, display clear impact/refusal reasons, mark deletions consistently in workspace, Overview, colony lists and Staged Changes. Preserve object until export; undo restores markers.
- Explicitly document/verify fail-closed coverage (Europe, carriers with cargo/passengers, aboard ships, teacher/student, trade route, destinations and other unknown references); ownership eligibility does not imply every location/dependency is supported.
- Automated tests for owner, identity under sorting, staging/undo, cancellation, editing conflicts, cached missionary refusal, source integrity, output integrity; user Windows and FreeCol roundtrip acceptance.

### 2D-3 — Native settlement deletion parity

- Port existing tested native-settlement plan/remove behaviour to Qt, with checked staging, impact, owner display, confirmation, undo and cross-view markers.
- Preserve existing conservative refusals, including mixed-owner unit/missionary relationships and cached-missionary cases. No speculative extension of Tk semantics.
- Verify linked settlement units, ownership/claimed tiles, cached representations, AI references and preservation of unrelated nations; CI, Windows and real FreeCol roundtrip.

### 2D-4 — European colony deletion (mandatory, independent branch and integration gate)

- Before implementation, write and independently review a **dependency matrix based on representative real saves and FreeCol server/source behaviour**. Include workers in buildings/colony tiles; visiting/stationed units on map tiles; colony buildings, goods, exports and improvements; `owningSettlement` and owned/worked tiles; cached snapshots; `aiColony` and AI missions/transport plans; external `destination`/`entryLocation`/`location` references, trade-route stops; messages/history and special targeting; final-colony/capital/defeat, score and Founding Father consequences.
- Only rehome/move units if independently researched and approved; simple removal may delete colony workers while leaving properly situated tile-level visiting/stationed units undisturbed. Refuse unknown dependencies.
- Use a shared parse/deletion context instead of repeated full-save parses per worker where safe; benchmark performance and maintain independent output verification.
- Implement validated staging/undo/impact/confirmation for both **human-owned and rival-European-owned** colonies. Distinct feature branch, CI and independent review. User Windows plus actual FreeCol load → turn advance → resave → reload required.
- No Phase 2 final acceptance without successful European colony deletion for both owner classes.

## Code-efficiency boundaries

Targeted cleaning accompanies the features it enables: shared Qt editors in 2D-1; safe deletion consolidation in 2D-0; staging/edit-set validation before 2D-2; parse reuse before 2D-4. Preserve behaviour with tests. **Do not initiate a separate broad code-efficiency refactor.** Defer remaining large-function splitting, `qt_readonly.py` rename/import hygiene, unaffected source-text test replacement and eventual Tk API retirement to established version 0.9.0 / post-Phase-3 work, as applicable.

## Global acceptance and governance

- Every checkpoint gets automated behavioural and integrity regression tests, green CI on the exact tested branch head, appropriate Claude independent safety review, and explicit user Windows/gameplay acceptance.
- Original `.fsg` bytes never change; Save As must reject existing destinations; XML/ZIP and FreeCol game behaviour must remain valid.
- Cached-missionary deletion fix remains **out of scope until after v1.0, if requested**; preserve safe refusal and explain it.
- No work on the unrelated `MOVE_NO_MOVES`/Lumberjack diagnostic without new evidence or user request.
- Do not add unapproved functionality, broaden destructive semantics by accident, or compromise previously accepted Tk/Qt behaviour.
- **Never merge, tag, delete feature branches or declare any software checkpoint accepted without explicit user authorisation.**

## Decision record — 27 October 2026

Following Claude's written independent review, the user explicitly approved the reviewed plan and the **PySide6-first architecture** principle and requested that this acceptance be recorded in the repository. This document records the **accepted plan**, not implementation or release approval.
