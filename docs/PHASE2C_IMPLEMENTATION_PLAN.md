# Phase 2C — Full Non-Destructive Qt Editing Parity

**Status:** ACCEPTED by user — 26 October 2026, incorporating Claude's independent PASS WITH CAVEATS review. Plan acceptance does not constitute implementation or merge acceptance.
**Prepared:** 26 October 2026
**Repository:** `Asmodude/freecol_save_editor`
**Development branch:** `feature/phase2c-editing-parity` (based on merged Phase 2B `main`)
**Normative source:** [PHASE2_DEVELOPMENT_PLAN.md](PHASE2_DEVELOPMENT_PLAN.md), accepted 25 October 2026. See also [Phase 2B evidence](PHASE2B_ACCEPTANCE_EVIDENCE.md) and `ROADMAP.md`.

## 1. Objective, acceptance boundary and principles

Bring Lady Philippa Y. Side VI, the Qt editor, to **every accepted non-destructive Tk editing capability**, using the already accepted Phase 2B inline-staging/undo/Save As workflow. Phase 2C is not permission to introduce arbitrary editable XML or derived-value manipulation.

**Phase 2C checkpoint from the accepted plan:** "every currently accepted non-destructive Tk edit is matched and verified in Qt." The complete destructive-edit parity (including game-tested Tk deletion) is explicitly **2D**; it is mandatory for final Phase 2 acceptance, not a blocker for the independent 2C checkpoint.

Preserve the accepted three-pane UI: edits where values are displayed in the lower middle contextual Overview/tabs; right-side resizable Staged Changes below Inspector; visual staged-value indicators (original and current); the single identity-safe upper workspace; and automatic selection/inspection whenever the normal workspace displays exactly one visible record, including filtered singletons.

Implementation of C1 is authorised by this accepted plan; acceptance of checkpoints and merge remain separate. `main` stays protected.

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
3. Absent stored goods start at zero; create positive stock only if the colony has a storedGoods parent and the type exists in the save. Do not invent warehouse-capacity rules.
4. Preserve other goods in warehouse; verify that aggregate colony/national summaries refresh correctly.
5. Stage multiple goods and liberty edits, undo individually, keep source-original values and preserve unrelated data.
6. Show human-readable review entries (`Christiansborg — Tools: 150 → 250`).
7. Validate mixed colony export and FreeCol roundtrip.

### 2C.6 — Diplomacy [MUST: O1/O2/A2/A5]

1. Audit the **exact** supported Tk diplomacy values, including stance and any accepted tension/alarm semantics; avoid assuming unsupported choices.
2. Preserve distinct **Rival Nations** and **Natives** diplomacy tables.
3. Bind each editor to authoritative owning player and counterpart, not displayed text or sorted position. Stance changes are symmetric (write both reciprocal records); tension and alarm are directional.
4. Use suitable value-type controls (choice selector versus numeric) and existing validation.
5. Stage via accepted composite keys, display both participants in readable review, support undo/repeated stage.
6. Test both European and native scenarios, reverse-direction protection, and game export.

### 2C.7 — Native Settlement Learnable Skill [MUST: O1/O2/O3]

1. Show current learnable skill in native settlement lower Overview; provide a visibly editable dropdown of legitimate professions.
2. Use SaveDocument.professions — skills currently taught by settlements in the opened save — not a ruleset-wide list.
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
| **C1 — Audit and numeric editors** | 2C.1 inventory; backend preflight; Tax, Experience, Moves (including equipment-aware movement cap); reusable numeric UI | Behavioural validation, origin/identity, stage/undo and CI green |
| **C2 — Structured/composite editors** | Equipment, Goods, Sons of Liberty, Diplomacy, Learnable Skill and any other accepted non-destructive Tk operation | Composite validation, realistic mixed edits, safe refusal and CI green |
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

**Review amendments and detailed plan ACCEPTED 26 October 2026.** CI, Windows, FreeCol and merge gates remain separate.

## 11. Decision record

- Whole Phase 2 plan accepted 25 October 2026.
- Phase 2B merged, tagged and branch deleted by user before this proposal.
- Claude reviewed the plan in docs/PHASE2C_PLAN_REVIEW.md (PASS WITH CAVEATS); user approved all amendments on 26 October 2026.
- This amended plan is ACCEPTED for implementation. No checkpoint implementation or merge is accepted yet.

## 12. Claude review amendments — mandatory accepted engineering contract

Source: [PHASE2C_PLAN_REVIEW.md](PHASE2C_PLAN_REVIEW.md), independent code-grounded review (PASS WITH CAVEATS). This section takes precedence over less-specific guidance in the original proposal. The user approved these amendments on 26 October 2026.

### 12.1 Stage-time backend preflight [MUST: A2, A10, O3]

1. Dry-run the actual backend operation using edit_backend.change_field() on an in-memory XML clone derived from SaveDocument.xml_bytes. Never mutate loaded authoritative XML or write an export during preflight.
2. For related staged edits, preflight the complete proposed staged set in the same ordering and semantics as produce(); the backend may refuse combinations even when standalone field validation passes.
3. On any refusal, show the backend message immediately and leave EditSession unchanged. This applies to both stage and undo operations that could invalidate another edit. produce() remains the final export authority.
4. Disable unsupported editors up front, with explanations: missing experience attribute, unknown movement cap, empty/nonstandard-SoL colony, missing relationship, missing storedGoods parent or unsupported skill.
5. Test each refusal category, verifying no session mutation and no export-only surprise.

### 12.2 Full authoritative edit identity and widget lifecycle [MUST: A2, O2]

1. Carry the complete edit key (record ID, field, goods type or counterpart as appropriate) in Qt.UserRole/model metadata or captured immutable editor state; never derive it from readable labels or sorted row positions.
2. Capture key and source original when an editor is created; stage only on Enter or explicit Stage, never focus loss. Rebuild from EditSession after stage, undo or navigation.
3. Detach obsolete editor widgets before deferred Qt deletion, and flush deferred deletions in behavioral tests before searching for widgets.
4. Staged indicators must remain visible even when the upper workspace row is selected: use durable FontRole or ForegroundRole in addition to background tint. Verify both selected and unselected cases and undo restoration.
5. Retained QTableWidget Goods and Diplomacy tables may remain if authoritative item keys, staging markers and behavioral tests establish safety; migration to RecordTableModel is recommended where that is simpler, not mandatory.

### 12.3 Equipment and movement dependency [MUST: A2]

1. The unit's staged equipment role controls legal movesLeft via movement_cap(). produce() applies equipment before moves.
2. Validate moves against the staged role, not just the opened-save role. Revalidate any staged moves whenever equipment is staged, restaged or undone.
3. Refuse any change/undo that leaves an unexportable combination, requiring movement to be adjusted first as necessary.
4. Test dragoon movement cap 12 versus soldier cap 3, both directions and both undo orders.

### 12.4 Confirmed Tk/backend edit contracts [MUST: O1, A2]

| Field | Authoritative key | Confirmed rules |
|---|---|---|
| Gold | (player_id, 'gold') | 0–2,147,483,647; native sentinel -2147483648 non-editable; delivered in 2B |
| Tax | (player_id, 'tax') | 0–100; numeric source tax required |
| Experience | (unit_id, 'experience') | 0–200; numeric source attribute required; editing via unit Overview reached through full unit record suffices for worker XP parity |
| Moves left | (unit_id, 'movesLeft') | 0–movement_cap(root, unit), respecting staged role and unknown-cap refusal |
| Equipment | (unit_id, 'equipment') | Original tuple (role or model.role.default, roleCount or 1); roles default/soldier/dragoon/scout/pioneer; validate_equipment checks maximum-count, canBeEquipped, abilities and naval/native refusals; refuse deletion conflicts |
| Colony goods | (colony_id, 'model.goods.<type>') | 0–2,147,483,647; goods type exists in save; absent stock original 0; create if new >0 and storedGoods element present; no new warehouse-capacity rule |
| Sons of Liberty | (colony_id, 'sonsOfLibertyTarget') | 0–100; population >0; current SoL must equal min(100, liberty*100 // (population*200)); otherwise refuse |
| Stance | (player_id, 'stance|<other>') | peace, war, cease_fire, alliance; existing equal reciprocal required; one edit writes both directions; never stage both directions simultaneously |
| Tension | (player_id, 'tension|<other>') | 0–2,147,483,647; existing relation; directional |
| Settlement alarm | (settlement_id, 'alarm|<colonial player>') | 0–2,147,483,647; existing relation; directional; cannot add missing relation |
| Learnable skill | (settlement_id, 'learnableSkill') | Only skills in SaveDocument.professions, i.e. those taught by authoritative settlements in this save |

Equipment UI: Hardy Pioneer with default role should preselect Pioneer appropriately; roleCount 1–5 for Pioneer corresponds to 20/40/60/80/100 tools. No colony warehouse goods are consumed by equipment changes.

Known Tk discrepancy: Tk may let a user stage an absent alarm entry from zero, but produce() refuses the export. Qt must show absent relationships as non-editable and explain why; document this limitation in the parity matrix rather than copying the broken behavior.

### 12.5 Stance symmetry and honest derived-value display [MUST: O2, A2]

1. Each Diplomacy navigation row carries owner, counterpart and relationship kind. Stance stages must visibly update both Danish→Swedish and Swedish→Danish views; reverse-side staging while the first direction is pending is refused.
2. Staged Changes must explicitly say that stance affects both nations, for example 'Danish ⇄ Swedish: peace → war (both directions)'. Tension and alarm remain independent/directional.
3. SoL export recalculates six attributes: liberty, sonsOfLiberty, oldSonsOfLiberty, tories, oldTories and productionBonus. The UI shows the staged target as proposed and explains downstream recalculation on export; optionally show explicitly labelled projections using pure colony_sol_values(). Do not suggest dependent fields are already modified in XML.
4. National Goods summaries must either reflect staged goods or be clearly labelled as source values; choose one and test it.

### 12.6 C1/C2 sequencing amendment

**C1:** full parity audit, reusable numeric control, stage-time backend preflight, player Tax, unit Experience and Moves, equipment-aware movement cap foundation and selected-row visible staging markers.

**C2:** equipment, colony goods **and Sons of Liberty**, Diplomacy stance/tension/alarm, settlement learnable skill. Moving SoL to C2 is mandatory because its population, formula and six-field update rules exceed basic numeric validation.

### 12.7 Strengthened tests and acceptance [MUST]

1. One combined export includes at least one of every accepted type: gold, tax, XP, moves, equipment, existing goods, newly created goods, SoL, stance, tension, alarm and learnable skill. Reload via SaveDocument.load(); inspect all intended attributes, all six SoL fields and both reciprocal stance records, and confirm non-target record attribute dictionaries unchanged.
2. Stage-time refusal tests individually cover nonstandard/empty SoL, absent reciprocal stance, missing tension/alarm, unsupported taught skill, missing storedGoods, invalid equipment/movement combinations, missing XP and unknown movement cap.
3. Representative real FreeCol roundtrips: numeric set (tax/XP/moves); colony set (created goods and SoL); diplomacy set (war then peace, tension/alarm); equipment set (soldier/dragoon and Pioneer tools). Each: load → advance a turn → save → reload, including observations of game-side reactions.
4. Original FSG SHA-256 unchanged; refuse source/existing destination overwrite; CI green at final tested SHA; Windows check staged markers remain visible on selected rows.

## 13. Formal plan acceptance — 26 October 2026

Claude independently reviewed the initial plan in docs/PHASE2C_PLAN_REVIEW.md and returned PASS WITH CAVEATS. The user approved the amendments and explicitly requested that the plan be updated. These amended implementation requirements are ACCEPTED. This is authorization to proceed with development under branch and test safeguards, **not** acceptance of C1–C4, a PR merge or final Phase 2 completion.
