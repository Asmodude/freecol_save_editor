# Phase 2B — Safe Qt Editing Workflow: Implementation and Acceptance Plan

**Status:** PROPOSED implementation breakdown — submitted for independent review; not yet accepted as a separate execution plan.  
**Date:** 25 October 2026  
**Repository:** `Asmodude/freecol_save_editor`  
**Branch:** `feature/phase2b-safe-qt-editing`  
**Draft PR:** [#5](https://github.com/Asmodude/freecol_save_editor/pull/5)  
**Baseline:** Accepted, merged Phase 2A, tag `v0.6.2.6.4-phase2a`, merge commit `a52d169f6a2574f13ba3067dbbdbdd7655f1e193`.  
**Primary authority:** [`docs/PHASE2_DEVELOPMENT_PLAN.md`](PHASE2_DEVELOPMENT_PLAN.md), formally accepted by the user 25 October 2026. This proposal interprets and sequences that plan; it does **not** supersede or silently change its requirements.

## 1. Purpose and scope

Transform the accepted PySide6 explorer, Lady Philippa Y. Side VI, from a read-only interface into one capable of safely **staging, validating, reviewing, undoing, and exporting** supported changes to a *new* FreeCol save. The original `.fsg` must remain unchanged. This is a workflow/infrastructure milestone, **not** full Tk editing parity (Phase 2C), destructive editing (2D), or research-gated editing (2E).

**Minimum 2B acceptance checkpoint from the authoritative plan:** At least one simple, independently validated edit can be staged, undone and exported safely, with the original file's bytes unchanged. Real FreeCol load → advance turn → save → reload testing is required.

**Recommended first field (proposal, not preapproved source requirement):** player gold. It uses the established numeric validation and output path, avoiding movement/equipment, relationship and deletion complexity. No arbitrary raw XML editing.

The already accepted Tkinter editor, Sir Thorwald Kilgannon Inter, remains available and is frozen for new functionality (bug fixes only). Preserve all accepted Qt views, navigation, artwork, selection identity, Inspector and search behavior. Phase 2A's *single* model-backed workspace `QTableView` is the baseline; do not restore legacy workspace `QTableWidget` or comparison mode.

## 2. Requirement precedence and priorities

The priority labels below come from the accepted **whole-Phase-2** matrix, which distinguishes original requirements O1–O6 and additions A1–A10. Not every whole-Phase-2 Must must be *implemented in 2B*.

- **MUST (🔴):** Mandatory within the relevant scheduled phase and its acceptance gate.
- **SHOULD (🟡):** Strongly preferred; any omission or deferral needs explicit user review and documentation.
- **COULD (🟢):** Optional polish; omission does not block this checkpoint.

### 2B applicable requirements

| ID | Priority | Accepted requirement | Treatment in 2B |
|---|---|---|---|
| O2 | 🔴 MUST | Editable fields must look editable; staged edits visually marked | Begin with selected supported field; expand in 2C |
| O3 | 🔴 MUST | Edited saves remain playable in FreeCol | Real-game roundtrip for the 2B example |
| O4 | 🔴 MUST (promoted from Should) | Staged-changes panel, per-item undo and pending-change count on **Save button** | Fully required, including working UI integration |
| O6 | 🟢 COULD | Tab between fields, Enter to stage, Esc to cancel | 2B–2C optional enhancement; see package 2B.5 |
| A2 | 🔴 MUST | Stage/validate/undo and export exclusively via existing safe Save As pipeline; no source overwrite | Core of 2B |
| A5 | 🔴 MUST | Preserve all accepted Qt/Tk functionality | Non-regression across 2B |
| A10 | 🔴 MUST | Warn before exiting, opening another save, or any action discarding unexported edits | No silent loss; normal navigation *preserving* session needs no warning |

**Cross-phase prerequisite:** A1 (🔴 MUST) Qt architecture/model-view refactor was completed in accepted Phase 2A.

### Other whole-Phase-2 requirements: intentionally not to be delivered in 2B

| ID | Priority | Scheduled work |
|---|---|---|
| O1 | 🔴 MUST | Complete Tk editing parity, including accepted deletions: 2C–2D |
| O5 | 🟡 SHOULD | Destructive actions visually separated and confirmed: 2D |
| A3 | 🔴 MUST | Cross-owner European/native unit deletion: 2D |
| A4 | 🔴 MUST | Safe European colony deletion, human and rival owners: 2D, separate branch/acceptance |
| A6 | 🟢 COULD, research-gated | Saved random seed: 2E |
| A7 | 🟡 SHOULD, research-gated | Founding Father stage/revoke: 2E |
| A8 | 🟡 SHOULD, research-gated | One-player Reveal Entire Map preserving fog/other players: 2E |
| A9 | 🔴 MUST | Full Phase 2 final acceptance: 2F (its CI, Windows, hash, and game roundtrip disciplines also apply to 2B checkpoints) |

**Known limitation:** Cached-missionary deletion retains safe refusal and an intelligible message. Fixing it is explicitly outside Phase 2 and only reconsidered after 1.0 if requested. It must not block 2B or later Phase 2 signoff. European colony deletion, by contrast, **cannot be deferred from final Phase 2 acceptance**.

## 3. Concrete 2B work packages

The steps below are an **implementation proposal** translating accepted requirements into testable tasks. The package IDs are new organizational labels, not new scope requirements.

### 2B.1 — Field editing and validation [🔴 MUST: O2, A2]

1. Inspect the existing Qt Inspector/Overview, `RecordTableModel`, sorting proxy and editable Tk field contract.
2. Select the smallest existing supported safe operation; **proposed:** player gold, excluding sentinel/non-editable records as governed by existing rules.
3. Provide a visibly editable Qt control in an appropriate existing context; display which value is from the source and which is staged.
4. Resolve edits by authoritative record identity (XML element ID), **never** a visual row index after sort/filter.
5. Parse and validate through `EditSession.validate()` and stage through `EditSession.stage()`; invalid input gives a clear refusal and does not mutate session or XML.
6. No-op changes remove/avoid the corresponding edit. Staged changes survive normal selection/filter/navigation.
7. Refresh affected Overview, workspace row, Inspector and other relevant displays without pretending the persisted XML is already changed.

**Evidence:** valid/invalid/minimum/maximum/no-op cases; identity after sort/filter; XML unchanged before export; visible staged indicator and source value.

### 2B.2 — Pending changes, review and undo [🔴 MUST: O4, A2]

1. Embed a visible **staged-changes panel** into the accepted Qt interface without disturbing its three-pane navigation/workspace/Inspector experience.
2. Show count on the actual Save/Save As button; if no changes, use a clear zero/disabled policy.
3. Display affected record, field, original value and proposed value; identify edits unambiguously. Retain underlying typed edit keys, including composite keys, rather than using display text as identity.
4. Support undo of the selected item and **unstage all**; refresh all affected UI controls and counts.
5. Keep independent edits intact on individual undo; support multiple outstanding edits and editing a staged field a second time.
6. Ensure a staged edit does not alter `SaveDocument.root` or source bytes. Panel is a view/controller over the established `EditSession`, not a competing mutation model.

**Evidence:** pending count, selected undo, all undo, multiple edits, no-op, UI synchronization, source integrity.

### 2B.3 — Session lifecycle / discard protection [🔴 MUST: A10]

1. Track whether there are **unexported staged changes**.
2. Prompt before application/window exit when staged changes would be lost.
3. Prompt before opening another save in the same window when staged changes would be lost.
4. Prompt on any other action that actually discards staged work; **do not** prompt on normal selection/navigation that preserves session.
5. Offer a cancel/retain-work path; implement and test the precise meaning of each presented option.
6. Avoid clearing the old session until a replacement file has loaded successfully; loading failure and canceled dialogs leave current work intact.
7. Define and test session state after successful Save As (including whether edits remain staged or become an acknowledged exported state) before implementing it; never silently discard on export failure.

**Evidence:** exit, successful/failed open, canceled open, replacement, explicit discard, and export-error paths.

### 2B.4 — Safe Save As and archive integrity [🔴 MUST: A2, O3]

1. Integrate a Qt Save As action/button and delegate export through `EditSession.save_as()` → `edit_backend.produce()`.
2. Never write to the source save; reject a target resolving to the source or **any** already existing path, including destination collisions.
3. Preserve unrelated ZIP entries/metadata to the extent guaranteed by the accepted producer, and preserve unrelated FreeCol data.
4. Verify generated ZIP structure and parse `savegame.xml`; apply existing safety/integrity checks; fail closed on validation/format/reference errors.
5. Surface descriptive errors without clearing staged edits; guard against incomplete export artifacts and unintentional overwrites.
6. Verify pre-/post-action source SHA-256 identity and validate intended changed values in the resulting file.
7. Define clear success feedback and subsequent edit/save workflow.

**Evidence:** safe export, ZIP/XML verification, existing-target refusal, same-source refusal, invalid data, unchanged source, preservation checks, real-game roundtrip.

### 2B.5 — Keyboard editing [🟢 COULD: O6, shared with 2C]

1. Tab through editable controls.
2. Enter stages valid input.
3. Escape cancels the uncommitted edit without affecting existing staged changes.
4. Test focus transitions, cancel and rejection behavior.

**Evidence:** focused Qt keyboard tests and Windows smoke checks if implemented. Optional omission does **not** block 2B; leave any incomplete work visibly tracked for 2C.

### 2B.6 — Automated behavioral validation [🔴 MUST: A2, A5 and checkpoint safeguards]

1. Test valid, invalid and boundary values through real `EditSession`/Qt interactions.
2. Test no-op staging, cancellation, repeated edits, independent multiple edits, individual undo and unstage all.
3. Verify sorting/filtering/navigation cannot redirect an edit to the wrong XML record.
4. Test dirty-state prompts, canceled replacement, failed replacement and exit.
5. Test Save As collisions, errors, ZIP/XML integrity, no source mutation and hash checks.
6. Preserve the existing accepted read-only Qt behavior and Tk operations through regression tests.
7. Run the full offscreen/headless suite in required GitHub Actions `headless` check; record **exact** branch-head SHA and run outcome. Replace brittle source-text assertions with behavioral checks where practical without disabling meaningful guards.

**Evidence:** reproducible test cases and final green CI tied to the tested SHA; do not claim green while queued/running.

### 2B.7 — Windows and FreeCol acceptance [🔴 MUST: O3, A2, A5; phase acceptance protocol]

1. Provide a concise Windows checklist for Qt launch, edit visibility, staging, review, undo, dirty warnings, Save As and non-regression.
2. Have the user run it on the final tested branch build, including sorting and contextual navigation.
3. Export a new `.fsg`; open it in FreeCol and verify the edited value.
4. Advance at least one turn, save in FreeCol and reload that save.
5. Verify original file remains unchanged and unrelated game behavior remains intact in the scenario tested.
6. Record Windows/test observations, any limitations, and the exact accepted commit.
7. Request user sign-off **before** integration. No merge, tag or branch deletion without explicit approval.

**Evidence:** Windows result, saved-game roundtrip, final SHA/CI and explicit acceptance.

## 4. Recommended checkpoint sequence

| Checkpoint | Work packages | Deliverable | Gate |
|---|---|---|---|
| **B1 — Staging foundation** | 2B.1–2B.2 | One visibly editable validated field, review, undo, correct pending count | Behavioral tests and CI |
| **B2 — Session/export safety** | 2B.3–2B.4 | Discard protection and safe Save As | Collision/error/hash/ZIP/XML tests and CI |
| **B3 — Verification** | 2B.6–2B.7 | Full headless/Windows and in-game roundtrip evidence | CI green at final tested SHA plus user observations |
| **B4 — Final 2B sign-off** | Final review; optional 2B.5 | Accepted workflow and documented handoff to 2C | Explicit user acceptance; separate authorisation for merge/integration |

These are proposed *engineering checkpoints*, not permission to merge automatically at B1–B3. The authoritative plan explicitly endorses milestone merges after 2A and 2C; a separate 2B merge should therefore be **discussed and explicitly approved**, not assumed.

## 5. Existing code and current branch state

- `save_document.py`: `SaveDocument.load()` reads the original ZIP and parses authoritative objects.
- `edit_session.py`: `EditSession.edits` stores keys with `(original, staged)`; exposes `validate`, `stage`, `unstage`, `clear`, `count` and `save_as`.
- `edit_backend.py`: established `produce()` pipeline.
- `qt_record_table_model.py`, `qt_record_sort_proxy.py`, `qt_record_table_view.py`: identity-safe, currently read-only workspace model/view baseline.
- `qt_readonly.py`: accepted shell; existing read-only labels and editor-disabled behavior must be updated deliberately, not indiscriminately.
- `qt_overview_panel.py`: graphical Overview presentation, currently read-only.

**Work initiated before this detailed planning request:**
- Branch `feature/phase2b-safe-qt-editing` created from accepted `main`.
- Draft PR [#5](https://github.com/Asmodude/freecol_save_editor/pull/5) opened.
- `qt_staged_changes_panel.py` added as a stand-alone session-backed pending-change review/undo widget.
- `test_qt_staged_changes_panel.py` added with initial behavioral tests.
- Last implementation commit at drafting: `f1fc4e5bfc67a8f186b545a315cc47bdf8821d0b`.
- The panel is **not wired into the Qt explorer**, no editable field is exposed and no Save As UI exists yet. The first CI was in progress when initially checked; **do not infer passing status** from this document.

All initial work remains **unaccepted**. This plan document itself is a review submission, not Windows acceptance or engineering completion.

## 6. Safety, design and non-regression constraints

- Never mutate source XML during staging; never overwrite source or another existing save.
- Reuse existing validation and `produce()`; no ad hoc XML writer or arbitrary XML editor.
- Distinguish original values, staged values and exported state in the interface.
- Maintain record identity across proxy sorting/filtering, drill-down and navigation.
- Avoid silent loss of pending edits and avoid misrepresenting them as saved.
- Preserve both UI implementations; Tk bug fixes only during Qt editing migration.
- No accepted UI/feature regression, including flags, sprites, contextual tables, Diplomacy split and read-only sections.
- Fail closed on unexpected XML attributes, unsupported relationships and unsafe operations.
- Each focused engineering increment includes meaningful tests and CI verification. Protected `main` is never directly modified.

## 7. Independent review request for Claude

Please assess the **proposed** Phase 2B breakdown against the **accepted** `docs/PHASE2_DEVELOPMENT_PLAN.md` and actual branch implementation. In particular:

1. Does it faithfully capture **all 2B-applicable Must/Should/Could** requirements while keeping 2C/2D/2E out of scope?
2. Is the recommended player-gold first edit safe and suitable, considering native-player sentinel handling?
3. Can the existing `EditSession` and `produce()` safely support repeated staging, individual undo, dirty-state handling and Save As? Identify implementation gaps.
4. Are there subtle risks in Qt record identity, proxy mapping, Overview/Inspector synchronization or callback lifetimes?
5. Does the new staged-changes panel correctly handle composite keys, repeated edits and meaningful source/staged values? Review the actual code, not just this plan.
6. Are the source hash, ZIP/XML, existing-file protection, atomicity and exported-game validation gates sufficient?
7. Should Save As clear the session or establish an exported baseline, and what is the safest UX contract?
8. Are B1–B4 achievable incremental checkpoints without allowing premature merger/acceptance?
9. Identify any missing mandatory tests, unintended requirements or conflicts with accepted roadmap decisions.
10. Return **PASS / PASS WITH CAVEATS / REVISE**, distinguishing blockers from enhancements. **Do not implement changes as part of the review.**

## 8. Decision record

- The **underlying Phase 2 scope and priority matrix are already accepted** by the user (25 October 2026).
- This **detailed 2B sequencing and UX proposal awaits independent Claude review** and any resulting user decisions.
- Work already in draft PR #5 does not imply approval of all recommendations here.
- No implementation checkpoint is accepted until its tests and required user sign-off have occurred.
