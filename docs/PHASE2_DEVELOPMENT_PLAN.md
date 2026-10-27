# Phase 2 — Qt Editing: Consolidated Development and Acceptance Plan

**Status:** ACCEPTED by user — 25 October 2026 (development plan and scope; individual implementation checkpoints still require testing and sign-off).  
**Prepared:** 25 October 2026  
**Baseline:** Accepted Phase 1, merged and tagged `v0.6.2.6.4-phase1`.  
**Purpose:** Bring the Qt application to safe editing parity with the accepted Tk interface, extend deletion to rival European units and colonies, and independently investigate selected new capabilities. **The development plan is accepted; implementation proceeds under its staged checkpoints and branch safeguards, with no automatic authorisation to merge unaccepted work.**

## Priority definitions

- 🔴 **Must:** Required for Phase 2 core acceptance; failure blocks core sign-off.
- 🟡 **Should:** Strongly preferred for Phase 2; omission requires explicit review and documented deferral.
- 🟢 **Could:** Optional polish; not an acceptance blocker.

The original six prioritised requirements from `UI_MODERNISATION_PLAN.md` are **preserved verbatim in substance** below and marked **O1–O6**. Additional work is separately marked **A1–A9**; its proposed priority is subject to user acceptance.

## Consolidated priority matrix

| ID | Priority | Requirement | Stage | Acceptance evidence |
|---|---|---|---|---|
| O1 | 🔴 Must | Every accepted Tk edit works in Qt via `EditSession` and `produce()`: gold, tax, XP, moves, goods, Sons of Liberty, diplomacy, learnable skills, equipment, and supported deletions — **including the accepted Tk unit deletion, native unit deletion and native settlement deletion (0.5.3, game-tested)**. | 2C–2D | Tk/Qt parity matrix and game-tested output |
| O2 | 🔴 Must | Editable fields look editable and staged changes are visually marked. | 2B–2C | Windows UI checks |
| O3 | 🔴 Must | Edited saves load and remain playable in FreeCol. | 2B–2F | Load → advance turn → save → reload |
| O4 | 🔴 Must _(promoted from Should; A2 and the 2B checkpoint already require undo)_ | Staged-changes panel with per-item undo and pending-change count on Save button. | 2B | UI tests for staging/undo/count |
| O5 | 🟡 Should | Destructive actions are visually separate from routine edits and require confirmation. | 2D | UI and cancellation tests |
| O6 | 🟢 Could | Keyboard workflow: Tab between fields, Enter to stage, Esc to cancel. | 2B–2C | Keyboard UI checks |
| A1 | 🔴 Must | Refactor Qt into view components with model/proxy tables and robust behavioural Qt tests before implementing edits. | 2A | Visual/functional parity; offscreen test suite |
| A2 | 🔴 Must | Stage/validate/undo and export edits exclusively via the existing safe Save As pipeline; original save untouched. | 2B | Hash checks, undo, valid export, overwrite rejection |
| A3 | 🔴 Must | Delete units owned by **any** nation, including the human player, rival European nations, and native nations, subject to safety validation. **Preserve existing safe refusal for cached-missionary cases; fixing that limitation is explicitly deferred until after 1.0 if users request it** (see 2D). | 2D | Cross-owner deletion tests |
| A4 | 🔴 Must | Safely delete **European colonies**, whether owned by the human or a rival European nation; validate references and associated objects, preserve/rehome visiting or stationed units only where valid, refuse unresolved dependencies. **Accepted and merged as a separate step that cannot block the 2A–2C merges** (see Delivery). | 2D | Real-game tests and dependency matrix |
| A5 | 🔴 Must | Preserve all accepted Phase 1 Qt views, artwork, navigation, contextual buttons and accepted Tk editing behaviour. | 2A–2F | Behavioural and Windows regression suite |
| A6 | 🟢 Could, research-gated _(lowest value of A6–A8)_ | Inspect and edit saved random seed only after confirming format, validation, and RNG semantics. | 2E | Changed/unchanged/invalid cases plus game roundtrip |
| A7 | 🟡 Should, research-gated | Stage/revoke Founding Fathers after verifying acquisition/recruitment/ability invariants. | 2E | State/dependency tests plus game roundtrip |
| A8 | 🟡 Should, research-gated | Reveal Entire Map **for one selected European player** while preserving fog of war and every other player's knowledge; begin with read-only exploration coverage. | 2E | See dedicated specification and in-game visibility tests |
| A10 | 🔴 Must | Warn before exit, opening another save, or any action that would discard staged but unexported changes; never lose staged work silently. | 2B | UI tests for each discard path |
| A9 | 🔴 Must | Final acceptance gates: green CI at tested head, real Windows smoke test, original-save integrity, FreeCol game roundtrip, and explicit user sign-off before merge. | 2F | Evidence recorded with commit hash |

**Proposed totals (after review amendments, 25 Oct 2026):** **11 Must, 3 Should, 2 Could** (16 individually tracked requirements). Changes: O4 promoted to Must, A10 added as Must, A6 moved to Could. Of the original six Phase 2 priorities, **4 are now Must, 1 Should, 1 Could**.

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

## Phase 2D approved addendum — 27 October 2026 (supersedes original 2D sequencing)

**User APPROVED the independently reviewed Phase 2D implementation plan and PySide6-first principle.** See `docs/PHASE2D_IMPLEMENTATION_PLAN.md` for the authoritative detailed requirements and `docs/PHASE2D_INDEPENDENT_REVIEW.md` for Claude's findings. This acceptance is **plan only**; no software milestone or merge has been approved.

- **Qt-first:** All new GUI functionality targets PySide6 (Lady Philippa Y. Side VI). Core save/edit/validation/deletion facilities remain UI-independent. Tkinter (Sir Thorwald) is frozen except necessary fixes to preserve accepted functionality; no new Tk features or Qt compromises for Tk.
- **2D-1 first:** UX clarity (Stage Change buttons, always-visible instructions, source-only Inspector/Raw XML) *with* shared Qt inline-editor/equipment components, keyboard/accessibility and focused behavioural testing.
- **2D-0 mandatory hard gate:** Before **2D-2 or any new deletion UI**, fix self-closing XML tag span corruption and add robust exact-removal/survivor integrity verification; prohibit the last colony inhabitant's deletion across the entire staged set; converge native-unit deletion paths and provide an impact planner. 2D-0 may proceed independently alongside 2D-1.
- **Before deletion UI:** unify checked staging and edit-set validation safely, preserving accepted Tk semantics; Qt deletion must always preflight the whole staged set. Build owner-specific impact/confirmation (Cancel default), explicit refusals, consistent staged markers and undo; enforce visually separate destructive controls (O5).
- **2D-2:** deletion for supported human, rival European and native units, fail-closed on unsupported dependencies and locations.
- **2D-3:** safe native settlement deletion parity with existing mixed-owner and cached-missionary refusals.
- **2D-4:** mandatory human and rival European colony deletion on a **separate branch and review/acceptance gate**, preceded by a written, independently reviewed dependency matrix grounded in real saves and FreeCol code.
- **Efficiency:** focused consolidation only, including shared Qt editors and parse reuse before 2D-4; broad architectural clean-up remains in 0.9.0. No regression or weakening of save integrity.
- **Governance:** CI, independent review where appropriate, user Windows/FreeCol tests, explicit acceptance and separate merge/tag/branch-deletion approvals. Cached missionary fix remains deferred past 1.0 on request.

## 2D — Cross-owner deletions and colony dependency safety

**In mandatory scope:**
- Delete units for the human nation, rival European nations and native nations, following the existing relationship-aware deletion engine where supported.
- Delete **European colonies belonging either to the human player or rival European players**. This expands the Qt Phase 2 scope beyond mere Tk parity and requires new dependency-safe behaviour if the Tk editor does not currently support it.
- Determine safe handling of colony buildings, workforce, goods, associated tiles/ownership, references, stationed and visiting units. Never equate safe colony deletion with blindly removing one XML element.
- Stage/unstage deletion, present meaningful impact summary, require user confirmation and fail closed on unknown dependencies.
- Distinguish affected record's owner explicitly in confirmation and review.

- **Port the accepted Tk native unit and native settlement deletion** (O1 parity). This reuses the existing `deletion_engine` planning and confirmation behaviour: dependency check, refusal of unsafe cases, removal of cached copies and linked tiles. It is not new research.

**Accepted non-blocking limitation (user decision, 25 October 2026):** `CHANGELOG.md` records that the deletion engine may refuse to delete missionaries whose unit has cached-tile snapshots. **Do not attempt to fix this in Phase 2.** Preserve the existing safe refusal, explain it clearly in the UI, and document it as a known limitation. Its resolution is deferred **until after version 1.0, and only if users request it**. Cached-missionary deletion must not block any Phase 2 checkpoint or final Phase 2 sign-off.

**European colony deletion (A4): dependencies that must be explicitly researched and handled**, not discovered late:
- **Cached copies:** other players' map knowledge (`cachedTile` and related snapshots) can contain copies of the colony and its tile. Use the native settlement deletion's handling of `cached_copies` as the template.
- **AI state:** AI-controlled players keep separate AI records for units (`aiUnit`, already handled by unit deletion) and, presumably, for colonies. These matter especially for rival colonies.
- **Tiles:** colony-owned and worked tiles (`owner` / `owningSettlement`), colony tile records and tile improvements stay consistent.
- **Units:** workers inside buildings and on colony tiles, as distinct from units merely visiting or stationed on the colony tile. Only rehome units where the target location is valid; otherwise refuse.
- **Game-level consequences:** a player's last colony, capital-like status, and anything that may trigger FreeCol events on load or next turn. Research these; never assume.

**Native settlement deletion** is in mandatory scope as Tk parity (above). Extending it beyond the accepted Tk behaviour remains separate, research-gated work.

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

**Checkpoint merges (review amendment).** Do not accumulate all of Phase 2 on one long-lived branch.
- **Merge to `main` after 2A** (refactor, no visible change) and **after 2C** (non-destructive parity). Each merge needs green CI on the tested head, a Windows check, and user sign-off.
- Deletion parity (2D: units, native units, native settlements) may merge with 2C or as its own checkpoint.
- **European colony deletion (A4)** gets its own branch and acceptance and cannot block earlier merges.
- 2E research items each merge independently once accepted.

**Tk editor status during Phase 2.** The Tk editor is frozen: bug fixes only. Every new capability (cross-owner and colony deletion, 2E items) is implemented in Qt only, through the shared `EditSession` / `produce()` pipeline. Tk remains available until Phase 3 replaces its Map Editor.

**CI enforcement.** GitHub branch ruleset created for `main` on 25 October 2026, with pull requests, required `headless` GitHub Actions check, up-to-date branches, conversation resolution, and blocked force pushes. A direct documentation write to `main` was actually rejected by the ruleset with a required-PR / `headless` status message, confirming those protections are enforced.

Phase 3 retains the integrated Qt map view, map geometry/visual refinement and native RoadPainter-style roads. Existing 0.6 terrain milestones, version 0.7 broader colony management, version 0.8 advanced world editing, and packaging/release stay on their established tracks unless the user separately revises scope.

## Review amendments — 25 October 2026 (Claude, independent review)

Applied directly in this document:
1. **Native settlement and native unit deletion** are existing, game-tested Tk features (0.5.3), so they are **O1 parity (Must)**, not research-gated.
2. **European colony deletion (A4)** stays Must, but is accepted and merged separately, with its dependencies named explicitly in 2D.
3. **Known cached-missionary deletion caveat:** originally proposed fix-or-carry; subsequently superseded by the user's decision of 25 October 2026 to defer any fix until after 1.0 if requested. Safe refusal remains mandatory; a fix is not a Phase 2 gate.
4. **O4 promoted to Must**; **A10** (no silent loss of staged changes) added as Must; **A6 (random seed)** moved to Could.
5. **Checkpoint merges** after 2A and 2C; **Tk frozen** for new features; **branch protection** on `main`.

**Decision recorded:** The user accepted the amended Phase 2 plan on 25 October 2026, including the scope decisions documented below. Intermediate checkpoints may be accepted and merged independently; this does not imply final Phase 2 completion.

## Scope decision — 25 October 2026 (user)

- **European colony deletion remains a mandatory Phase 2 completion and sign-off requirement**, for both the human nation and rival European nations. It cannot be deferred to claim full Phase 2 acceptance.
- **Cached-missionary deletion is explicitly non-blocking and out of scope for Phase 2.** Keep safe refusal and clear explanation. Reconsider a fix only after 1.0 if users request it; do not spend Phase 2 implementation effort on a fix.
- These decisions supersede any earlier wording that suggests the cached-missionary bug should be fixed in Phase 2.

## Final plan acceptance — 25 October 2026 (user)

The user formally **ACCEPTED this Phase 2 development plan**, including these final clarifications:

1. **Cached-missionary deletion is not a Phase 2 blocker.** Deferring the fix is intentional: the existing deletion engine refuses uncertain operations rather than risking save corruption. That safe refusal remains mandatory, with a clear, understandable explanation in the UI so users do not mistake a safe rejection for a broken editor. Reconsider the fix only after version 1.0 if users request it.
2. **European colony deletion is mandatory before final Phase 2 sign-off**, for both the user's own European nation and rival European nations, with fully validated save outcomes. This is compatible with checkpoint merges: stages 2A and 2C can be separately accepted and merged as completed, but **neither early merge constitutes final Phase 2 acceptance**. The phase cannot receive final sign-off until European colony deletion works.
3. **Protect `main` with repository branch rules.** The user created the ruleset with required pull requests and the `headless` CI check, among other protections. On 25 October, direct editing of `main` was rejected by GitHub rules, as intended.

**Acceptance scope:** Approval is for the plan and its prioritisation, **not** acceptance of software not yet delivered. Each development checkpoint continues to require its documented tests and user approval.
