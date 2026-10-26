# Phase 2C — Full Non-Destructive Qt Editing Parity

**Status:** PROPOSED — awaiting independent Claude review and user acceptance. No coding authorised by this document alone.
**Prepared:** 26 October 2026
**Repository:** `Asmodude/freecol_save_editor`
**Review branch:** `feature/phase2c-editing-parity` (based on merged Phase 2B `main`)
**Normative source:** [PHASE2_DEVELOPMENT_PLAN.md](PHASE2_DEVELOPMENT_PLAN.md), accepted 25 October 2026. See also [Phase 2B evidence](PHASE2B_ACCEPTANCE_EVIDENCE.md) and `ROADMAP.md`.

## 1. Objective, acceptance boundary and principles

Bring Lady Philippa Y. Side VI, the Qt editor, to **every accepted non-destructive Tk editing capability**, using the already accepted Phase 2B inline-staging/undo/Save As workflow. Phase 2C is not permission to introduce arbitrary editable XML or derived-value manipulation.

**Phase 2C checkpoint from the accepted plan:** "every currently accepted non-destructive Tk edit is matched and verified in Qt." The complete destructive-edit parity (including game-tested Tk deletion) is explicitly **2D**; it is mandatory for final Phase 2 acceptance, not a blocker for the independent 2C checkpoint.

Preserve the accepted three-pane UI: edits where values are displayed in the lower middle contextual Overview/tabs; right-side resizable Staged Changes below Inspector; visual staged-value indicators (original and current); the single identity-safe upper workspace; and automatic selection/inspection whenever the normal workspace displays exactly one visible record, including filtered singletons.

No code implementation, acceptance or merge should occur solely because the proposal is filed. `main` stays protected.

## 2. Must / Should / Could: exact priority inheritance

Priorities derive from the **whole-Phase-2** accepted matrix, *not* new priority assignments invented for 2C.

| ID | Accepted priority | Requirement | 2C interpretation |
|---|---|---|---|
| **O1** | **MUST** | Every accepted Tk edit works in Qt via shared session and producer | Deliver **non-destructive** operations in 2C; destructive operations remain **MUST in 2D** |
| **O2** | **MUST** | Editable controls recognisable, staged values visibly marked | Apply uniformly to all newly editable 2C fields |
| **O3** | **MUST** | Exported saves playable in FreeCol | Representative real-game roundtrips |
| **O4** | **MUST** | Staged Changes, per-item undo, Save As count | Preserve and extend Phase 2B capabilities across new edit types |
| **A2** | **MUST** | Validate/stage/undo/export exclusively using `EditSession` and `produce()`; never overwrite originals | Preserve existing contract; do not implement a second serializer |
| **A5** | **MUST** | Preserve accepted Phase 1/2A/2B Qt and Tk behaviour | Regression tests and Windows checks |
| **A10** | **MUST** | No silent loss of unexported edits | Retain dirty/exported state and discard warnings |
| **O6** | **COULD** | Tab through fields, Enter stage, Escape cancel | Optional polish in 2C; no 2C acceptance blocker |

**Requirements not assigned to 2C:** O5 (**SHOULD**, separate/confirm destructive actions) and A3/A4 (**MUST**, cross-owner unit and European colony deletion) are scheduled for 2D. A7/A8 (**SHOULD**, research-gated Founding Fathers and one-player Reveal Entire Map) and A6 (**COULD**, random seed) are scheduled for 2E. A9 (**MUST**, final overall Phase 2 gate) is 2F, although green CI, Windows, integrity and FreeCol checks apply to the 2C milestone. A1 was completed and accepted in 2A.

**Important exclusions:** The known cached-missionary deletion limitation stays a clear **safe refusal**, with its fix deferred until after 1.0 if users request it. European colony deletion remains mandatory for **overall Phase 2**, but is a separate 2D branch/checkpoint. No new Tk features: Tk is bug-fixes-only while Qt development continues.

## 3. Operation inventory — to be confirmed against actual Tk code

The accepted overarching plan names these capabilities, but **this list must be audited against actual Tk code before being called exhaustive**.

| Area | Accepted non-destructive operations | Priority | Placement proposal |
|---|---|---|---|
| Players | Gold (already in 2B), Tax | MUST (O1/O2) | Lower player Overview |
| Units | Experience, Moves left | MUST | Unit Overview |
| Equipment | Unit role/equipment quantity | MUST | Unit contextual details; coherent composite editor |
| Colonies | Stored goods quantities, Sons of Liberty | MUST | Colony Goods tab / Overview |
| Diplomacy | Supported stance, tension/alarm and other accepted diplomatic values | MUST | Preserve separate Rival Nations and Natives presentations |
| Native settlements | Learnable skill | MUST | Settlement Overview |
| Other accepted Tk edits | Every additional non-destructive operation discovered by audit | MUST | Appropriate existing contextual view |

**Do not infer editability** from a visible statistic, the illustrative mockup, or a derived field. Combat values, prosperity classifications, building counts and calculated production attributes are not automatically editable.

## 4. Concrete implementation work packages

### 2C.1 — Audit and Tk → Qt parity matrix [MUST: O1, A2, A5]

1. Inventory **every accepted, non-destructive Tk editing operation**, inspecting the actual Tk UI, validation, `EditSession`, `edit_backend.produce()`, and ruleset support.
2. Record source XML fields/relationships, ID and key schema, legal types/ranges/choices, dependencies, no-op/undo semantics, and provenance of original values.
3. Map each to its appropriate existing Qt Overview or contextual tab; identify whether a table model/proxy migration or stable identity binding is needed.
4. Document expected readable labels in Staged Changes, including composite keys and owner/counterpart.
5. Build `docs/PHASE2C_PARITY_MATRIX.md` with explicit statuses **Not started / Implemented / Automated PASS / Windows PASS / FreeCol PASS** and evidence references.
6. Record any accepted Tk limitations. Do not silently discard operations because they are inconvenient or extend scope to unaccepted operations.
7. Identify representative examples and fixtures for combined export testing.

**Gate:** reviewed, source-grounded inventory before claiming implementation completeness.

### 2C.2 — Player fields [MUST: O1/O2/A2]

1. Preserve Phase 2B Gold editor, native sentinel and original-value protection.
2. Add inline Tax editing with established numeric bounds and validation.
3. Bind edits to authoritative player IDs, including rival Europeans; do not infer owner from a visual row.
4. Mark Gold/Tax staged in workspace and Overview, with original saved values visible.
5. Refresh staged count, Inspector, pending changes and table after stage/undo.
6. Test Gold+Tax on one player and Tax on another; undo one without affecting others.
7. Verify exported values and untouched records.

### 2C.3 — Unit Experience and Movement [MUST: O1/O2/O3]

1. Add clearly styled inline Experience and Moves Left controls in relevant lower unit detail area.
2. Validate against established XP/range and `movement_cap()` rule logic (including unavailable/unknown ceilings).
3. Use source XML as original and authoritative unit ID as key.
4. Preserve identity across navigation, sort/filter, singletons and inspection of units belonging to different players.
5. Show staged values, original values and per-field undo; do not edit derived/combat fields.
6. Test legal boundaries, illegal values, multiple units, mixed stage/undo and valid FreeCol export.

### 2C.4 — Unit Equipment and Roles [MUST: O1/A2/A5]

1. Audit existing accepted Tk role/equipment behavior, including natural Pioneer flow, and enumerate valid role choices and quantities from game rules.
2. Provide context-sensitive role and quantity controls in the lower contextual unit view.
3. Keep role/quantity a coherent **composite** staged operation using accepted key/validation; never independently apply an inconsistent partial role.
4. Distinguish `unitType`, `role` and `roleCount`; retain equipment conflict rules.
5. Confirm stage, repeated restage, original preservation, per-item undo and readable review.
6. Test accepted role transitions and refusals, and roundtrip in FreeCol.

### 2C.5 — Colony Stored Goods and Sons of Liberty [MUST: O1/O2/O3]

1. Add inline Sons of Liberty editing for the authoritative target specified by accepted Tk behavior.
2. Add inline supported stored-goods quantity edits in colony Goods tab, tied to colony identity and actual goods record/key—not display row.
3. Support accepted zero/absent goods semantics; do not invent new storage rules.
4. Preserve other goods in warehouse; verify that aggregate colony/national summaries refresh correctly.
5. Stage multiple goods and liberty edits, undo individually, keep source-original values and preserve unrelated data.
6. Show human-readable review entries (`Christiansborg — Tools: 150 → 250`).
7. Validate mixed colony export and FreeCol roundtrip.

### 2C.6 — Diplomacy [MUST: O1/O2/A2/A5]

1. Audit the **exact** supported Tk diplomacy values, including stance and any accepted tension/alarm semantics; avoid assuming unsupported choices.
2. Preserve distinct **Rival Nations** and **Natives** diplomacy tables.
3. Bind each editor to authoritative owning player and counterpart, preserving directionality; never infer from sorted visual row.
4. Use suitable value-type controls (choice selector versus numeric) and existing validation.
5. Stage via accepted composite keys, display both participants in readable review, support undo/repeated stage.
6. Test both European and native scenarios, reverse-direction protection, and game export.

### 2C.7 — Native Settlement Learnable Skill [MUST: O1/O2/O3]

1. Show current learnable skill in native settlement lower Overview; provide a visibly editable dropdown of legitimate professions.
2. Reuse existing ruleset choices and validation.
3. Bind to authoritative settlement ID, preserve owning native nation and other settlement attributes.
4. Display readable original/new skill labels in Overview and Staged Changes, retaining internal identifiers underneath.
5. Test navigation/selection identity, restage, undo, invalid choices and FreeCol roundtrip.
6. Exclude native settlement deletion until 2D.

### 2C.8 — Keyboard workflow [COULD: O6]

1. Support intuitive Tab traversal among supported editable fields.
2. Enter stages current valid value.
3. Escape cancels only an **uncommitted** UI edit, retaining any previously staged value.
4. Test dropdowns, numeric/composite controls, error focus and record navigation.
5. Track deferred portions explicitly without blocking 2C acceptance.

## 5. Shared implementation contract [MUST wherever applicable]

- **UI positioning:** lower central Overview/contextual tabs are the normal editable surface. The upper table is a navigation/summary display; the Inspector remains informational, with Staged Changes below it. No separate generic editing form or extra bottom-of-window dock.
- **Visual distinction:** editable controls visibly different even before editing; staged fields clearly different afterwards; original/source value visible; workspace table indicators and review list in sync. Undo removes staged styling.
- **Authoritative identity:** capture key, record ID and original from opened source record; do not obtain original from staged text; edits cannot migrate onto another selected record.
- **Single validation/producer:** domain rules remain authoritative; no direct XML mutation, ad hoc ZIP output or arbitrary edit.
- **State:** preserve Phase 2B export snapshots, no-op semantics, dirty warnings, per-item undo and confirmed Unstage All.
- **Non-regression:** maintain Phase 1/2A/2B UI, artwork, flags, search, diplomacy separation, contextual buttons, sorted identity, automatic singleton selection and Tk support.
- **Reusable controls:** recommend reusable numeric and choice/composite Qt editor primitives for consistent visual/state behavior, while leaving distinct FreeCol game rules in domain-specific validators. This is an **engineering recommendation**, not a mandate to force dissimilar operations into one abstraction.
- **Existing detail widgets:** assess whether retained `QTableWidget` details can enforce identity and safe editing, or whether selected tables require model/proxy migration. No blanket conversion required by 2C itself.

## 6. Consolidated engineering checkpoints

| Checkpoint | Content | Required gate |
|---|---|---|
| **C1 — Audit and numeric editors** | 2C.1 inventory; Tax, Experience, Moves, Sons of Liberty; reusable numeric UI | Behavioural validation, origin/identity, stage/undo and CI green |
| **C2 — Structured/composite editors** | Equipment, Goods, Diplomacy, Learnable Skill and any other accepted non-destructive Tk operation | Composite validation, realistic mixed edits, safe refusal and CI green |
| **C3 — Integrated verification** | Complete UI synchronization, optional O6, full parity matrix, combined export, Windows checklist and FreeCol tests | Green CI on exact tested code; Windows and representative in-game roundtrips; original hash unchanged |
| **C4 — Review and milestone acceptance** | Independent review, corrections, CHANGELOG/ROADMAP and evidence | User acceptance, **separate explicit merge approval**, protected PR merge/tag |

Development may require many small commits/CI checks, but should minimize **user-facing acceptance handoffs**. No intermediate checkpoint implies automatic merge.

## 7. Mandatory acceptance evidence

- Completed code-grounded Tk→Qt **non-destructive parity matrix**, with no accepted non-destructive field silently omitted.
- For every category: valid, invalid, boundary, no-op, restage, cancel and undo cases as applicable.
- Correct authoritative identity after sort/filter/navigation/automatic singleton selection; no stale widget/editor can commit to a different record.
- Every new staged field visually marked in workspace and lower Overview/contextual view; original value legible.
- Mixed edit export across record types; verify exactly intended XML edits, unrelated values and archive members unaffected.
- Source `.fsg` SHA-256 unchanged; source/existing destination overwrite refusals.
- Exported files open in FreeCol; advance turn → save → reload for representative numeric, composite, diplomatic and combined scenarios.
- Full regression suite, required `headless` GitHub Actions status green on **exact final code SHA**; Windows acceptance on corresponding build.
- Explicitly document any limitation, with Should/Could deferrals separately decided (no silent waivers).
- User sign-off on Phase 2C and **separate explicit authorization** to merge/tag/delete branch.

## 8. Exclusions / forward alignment

**2D (mandatory destructive parity & extension):** human/rival/native unit deletion, accepted Tk native unit and settlement deletion, dependency-safe European colony deletion for both human and rivals; destructive confirmation (O5 SHOULD), cached-missionary safe refusal. European colony deletion gets independent branch and cannot be waived from final Phase 2 sign-off.

**2E (research-gated):** Founding Father stage/revoke (A7 SHOULD), selected-player Reveal Entire Map with preserved fog and other knowledge (A8 SHOULD), saved random seed (A6 COULD).

**2F:** Full Phase 2 sign-off, after remaining Must operations.

**Phase 3:** Qt map integration and terrain/map work under accepted roadmap.

## 9. Documentation and process

Planned documentation:
- This file: `docs/PHASE2C_IMPLEMENTATION_PLAN.md` — **proposal**, to be reviewed before implementation.
- `docs/PHASE2C_PARITY_MATRIX.md` — created as output of code audit (C1).
- `docs/PHASE2C_WINDOWS_CHECKLIST.md` — prepared for C3 testing.
- `docs/PHASE2C_ACCEPTANCE_EVIDENCE.md` — C4 tested commit, findings and sign-off.
- `CHANGELOG.md` and `ROADMAP.md` — update before merging.

All implementation occurs in `feature/phase2c-editing-parity` from accepted Phase 2B `main`, with draft PR and enforced required CI. No direct pushes to `main`, no automatic merge.

## 10. Independent review request for Claude — REVIEW ONLY

Read the accepted `docs/PHASE2_DEVELOPMENT_PLAN.md`, the actual Tk editing handlers, `EditSession`, `edit_backend.produce()`, Qt components and this plan. **Do not implement changes during the review.**

1. Is the 2C Must/Should/Could mapping faithful, without importing 2D/2E features or deferring required non-destructive parity?
2. Does the actual accepted Tk implementation contain operations **missing** from section 3? Supply their keys, rules and target Qt views.
3. Confirm actual schema/validation for player tax, XP/moves, role/equipment, colony Goods/Sons of Liberty, diplomacy and learnable skill; identify conceptual mistakes or unsupported examples.
4. Identify whether the proposed C1 grouping is practical or some field groups should move between checkpoints based on shared infrastructure.
5. Determine whether any existing `QTableWidget` details/diplomacy views must be migrated to preserve identity safely.
6. Assess reusable UI controls versus game-specific validators, including focus, signal lifetimes, deferred Qt widget deletion and repeated re-render.
7. Assess source-original preservation, exported/dirty snapshot, composite key undo and multi-field synchronization.
8. Review tests and evidence needed for combined mixed exports and real FreeCol roundtrips.
9. Identify omissions, regressions, scope creep, or missing mandatory acceptance gates.
10. Return **PASS / PASS WITH CAVEATS / REVISE**, separating Must-level blockers from recommended improvements and optional polish.

**Review does not equal acceptance.** User approves any amended detailed 2C plan before implementation starts; CI, Windows and FreeCol gates remain separate.

## 11. Decision record

- Whole Phase 2 plan accepted 25 October 2026.
- Phase 2B merged, tagged and branch deleted by user before this proposal.
- This proposed Phase 2C breakdown is **not yet independently reviewed or user accepted**.
- The branch and this document exist for independent review only. No implementation or PR merge authorized.
