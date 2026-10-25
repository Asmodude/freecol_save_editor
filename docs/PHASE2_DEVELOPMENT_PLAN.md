# Phase 2 — Qt Editing: Consolidated Development and Acceptance Plan

**Status:** PROPOSED — awaiting explicit user approval.  
**Prepared:** 25 October 2026  
**Baseline:** Accepted Phase 1, merged and tagged `v0.6.2.6.4-phase1`.  
**Purpose:** Bring the Qt application to safe editing parity with the accepted Tk interface, extend deletion to rival European units and colonies, and independently investigate selected new capabilities. **This document authorises planning only, not implementation.**

## Priority definitions

- 🔴 **Must:** Required for Phase 2 core acceptance; failure blocks core sign-off.
- 🟡 **Should:** Strongly preferred for Phase 2; omission requires explicit review and documented deferral.
- 🟢 **Could:** Optional polish; not an acceptance blocker.

The original six prioritised requirements from `UI_MODERNISATION_PLAN.md` are **preserved verbatim in substance** below and marked **O1–O6**. Additional work is separately marked **A1–A9**; its proposed priority is subject to user acceptance.

## Consolidated priority matrix

| ID | Priority | Requirement | Stage | Acceptance evidence |
|---|---|---|---|---|
| O1 | 🔴 Must | Every accepted Tk edit works in Qt via `EditSession` and `produce()`: gold, tax, XP, moves, goods, Sons of Liberty, diplomacy, learnable skills, equipment, and supported deletions. | 2C–2D | Tk/Qt parity matrix and game-tested output |
| O2 | 🔴 Must | Editable fields look editable and staged changes are visually marked. | 2B–2C | Windows UI checks |
| O3 | 🔴 Must | Edited saves load and remain playable in FreeCol. | 2B–2F | Load → advance turn → save → reload |
| O4 | 🟡 Should | Staged-changes panel with per-item undo and pending-change count on Save button. | 2B | UI tests for staging/undo/count |
| O5 | 🟡 Should | Destructive actions are visually separate from routine edits and require confirmation. | 2D | UI and cancellation tests |
| O6 | 🟢 Could | Keyboard workflow: Tab between fields, Enter to stage, Esc to cancel. | 2B–2C | Keyboard UI checks |
| A1 | 🔴 Must | Refactor Qt into view components with model/proxy tables and robust behavioural Qt tests before implementing edits. | 2A | Visual/functional parity; offscreen test suite |
| A2 | 🔴 Must | Stage/validate/undo and export edits exclusively via the existing safe Save As pipeline; original save untouched. | 2B | Hash checks, undo, valid export, overwrite rejection |
| A3 | 🔴 Must | Delete units owned by **any** nation, including the human player, rival European nations, and native nations, subject to safety validation. | 2D | Cross-owner deletion tests |
| A4 | 🔴 Must | Safely delete **European colonies**, whether owned by the human or a rival European nation; validate references and associated objects, preserve/rehome visiting or stationed units only where valid, refuse unresolved dependencies. | 2D | Real-game tests and dependency matrix |
| A5 | 🔴 Must | Preserve all accepted Phase 1 Qt views, artwork, navigation, contextual buttons and accepted Tk editing behaviour. | 2A–2F | Behavioural and Windows regression suite |
| A6 | 🟡 Should, research-gated | Inspect and edit saved random seed only after confirming format, validation, and RNG semantics. | 2E | Changed/unchanged/invalid cases plus game roundtrip |
| A7 | 🟡 Should, research-gated | Stage/revoke Founding Fathers after verifying acquisition/recruitment/ability invariants. | 2E | State/dependency tests plus game roundtrip |
| A8 | 🟡 Should, research-gated | Reveal Entire Map **for one selected European player** while preserving fog of war and every other player's knowledge; begin with read-only exploration coverage. | 2E | See dedicated specification and in-game visibility tests |
| A9 | 🔴 Must | Final acceptance gates: green CI at tested head, real Windows smoke test, original-save integrity, FreeCol game roundtrip, and explicit user sign-off before merge. | 2F | Evidence recorded with commit hash |

**Proposed totals:** **9 Must, 5 Should, 1 Could** (15 individually tracked requirements). Of those, **3 Must, 2 Should, 1 Could** are Claude's original six Phase 2 priorities.

> **Priority clarification:** A6–A8 are pre-existing documented Phase 2 additions, not invented in this consolidation. Their exact delivery priority was not assigned in the original six-item classification; 🟡 here is a proposal, not an assertion of prior approval. Should items do not become silently waived: require a recorded user decision to defer.

## 2A — Architecture and behavioural-test foundation

1. Split the current Qt shell into one cohesive view/controller per major section: Players, Units, Colonies, Native Settlements, Diplomacy, Founding Fathers, National Goods and Game Properties.
2. Introduce appropriate `QAbstractTableModel` + `QSortFilterProxyModel` abstractions that preserve stable underlying object identity under sorting and filtering.
3. Centralise navigation by group/scope and keep the window root responsible for composition and routing.
4. Replace brittle literal-source tests with offscreen Qt tests using synthetic saves; retain direct assertions of read-only/non-mutation during this stage.
5. Preserve the current exact accepted display and interactions.

**Checkpoint:** no feature loss or visible regression. Do not expose edits until this foundation passes.

## 2B — Safe Qt editing workflow

- Connect eligible editable fields to the existing `EditSession` validation/staging logic; display original and staged values distinctly.
- Provide visible pending-change count, review, per-item undo, unstage all, and warnings before navigating away/opening a different save or exiting with unexported changes.
- Export only through `produce()` and **Save As** to a new path. Never overwrite source or an existing file; verify ZIP/XML and related integrity.
- Test invalid entries, unchanged values, cancellation, multiple edits, undo, and complete roundtrip through FreeCol.
- Prefer a staged-changes panel and keyboard support as marked in the matrix.

**Checkpoint:** at least one simple, independently validated edit stages, undoes and exports safely while original bytes remain unchanged.

## 2C — Existing accepted editing parity

Port all existing accepted Tk operations into the appropriate Qt views: player gold/tax, unit XP/moves/equipment, colony goods/Sons of Liberty, supported diplomatic values, native settlement learnable skills and all other validated Tk operations. Do not introduce arbitrary XML editing as a substitute for ruleset validation.

Maintain an explicit Tk → Qt parity checklist and test realistic combinations of changes in one export.

**Checkpoint:** every currently accepted *non-destructive* Tk edit is matched and verified in Qt.

## 2D — Cross-owner deletions and colony dependency safety

**In mandatory scope:**
- Delete units for the human nation, rival European nations and native nations, following the existing relationship-aware deletion engine where supported.
- Delete **European colonies belonging either to the human player or rival European players**. This expands the Qt Phase 2 scope beyond mere Tk parity and requires new dependency-safe behaviour if the Tk editor does not currently support it.
- Determine safe handling of colony buildings, workforce, goods, associated tiles/ownership, references, stationed and visiting units. Never equate safe colony deletion with blindly removing one XML element.
- Stage/unstage deletion, present meaningful impact summary, require user confirmation and fail closed on unknown dependencies.
- Distinguish affected record's owner explicitly in confirmation and review.

**Outside this mandatory scope:** native settlement deletion remains a distinct research-gated capability, not silently equivalent to European colony deletion.

**Checkpoint:** both rival and player-owned unit and European colony deletion work in verified scenarios; unsafe cases are refused. Cross-owner changes do not corrupt unrelated nations.

**Version alignment:** European colony deletion remains the **0.7.0 functional milestone** from `ROADMAP.md` even if implementation is brought into Qt Phase 2; an architectural phase is **not** a version number.

## 2E — Additional research-gated edits

Work may proceed independently and must never compromise core editing acceptance.

1. **Saved random seed:** find persisted field and valid range; avoid assumptions about deterministic outcomes or unrelated RNG state. Stage, validate, undo and export after verifying semantics.
2. **Founding Fathers:** research acquisition and revocation effects, abilities and recruitment state; do not alter unknown linked fields.
3. **Reveal Entire Map:** begin with authoritative-tile/per-player coverage report; research `cachedTile` and `copied` snapshots; stage only selected player's new exploration knowledge, preserve fog of war, existing caches, hidden native details and other players' knowledge. Do not award exploration rewards or trigger events. See `docs/PHASE2_REVEAL_ENTIRE_MAP.md`.

Each requires its own test evidence and explicit user acceptance before being called delivered. If not safe or feasible, record the blocker and request an explicit deferral decision.

## 2F — Final Phase 2 acceptance

- All Must requirements pass, including A3 and A4 cross-owner deletion.
- Original save's SHA-256 remains unchanged after every test; exported files do not overwrite existing destinations.
- CI runs green on the final tested branch commit, including real offscreen Qt behavioural tests.
- User tests on Windows; FreeCol load → advance turn → save → reload for representative standard, composite and destructive edits.
- Tk-versus-Qt parity matrix complete, with any independently documented limitation visible.
- Previously accepted Phase 1 presentation, navigation, local game artwork and actions preserved.
- Should/Could requirements either verified complete or explicitly deferred, not silently omitted.
- User signs off **before** merging into `main`, tagging, or deleting the Phase 2 branch; those integration actions require separate approval.

## Delivery and scope boundaries

Recommended branch: `feature/phase2-qt-editing`, created **only when implementation is authorised**. Maintain incremental testable checkpoints 2A through 2F, with no premature acceptance status.

Phase 3 retains the integrated Qt map view, map geometry/visual refinement and native RoadPainter-style roads. Existing 0.6 terrain milestones, version 0.7 broader colony management, version 0.8 advanced world editing, and packaging/release stay on their established tracks unless the user separately revises scope.

**Decision requested:** Approve/adjust this matrix (particularly the proposed Should prioritisation for A6–A8 and whether native settlement deletion should be included). This document records a **proposal**, not approved Phase 2 scope.
