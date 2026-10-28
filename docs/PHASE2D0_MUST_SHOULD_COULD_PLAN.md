# Phase 2D-0 — Deletion Engine Safety Hardening
## Implementation plan for independent review — **PROPOSED, NOT APPROVED**
**Prepared:** 28 October 2026. **Purpose:** prerequisite to any *new* destructive Qt controls in Phase 2D-2 / 2D-3 / 2D-4.
**Baseline:** merged `main` `a97ae1aa9362c6a22a4cc1025b1eb9ccd9d87e5d`, tag `v0.6.2.6.4-oc001`. Documentation reconciliation on PR #10 is not yet merged; this plan is filed there for review.
**Decision authority:** Project Director. **Review:** Claude independently evaluates this *plan* before implementation. No changes to application code, feature implementation, acceptance, merge or tag are authorized by this document.
**Relevant accepted requirements:** [PHASE2D_IMPLEMENTATION_PLAN.md](PHASE2D_IMPLEMENTATION_PLAN.md), [CURRENT_STATUS.md](CURRENT_STATUS.md), [OUTSTANDING_COMMITMENTS.md](OUTSTANDING_COMMITMENTS.md), `ROADMAP.md`.

### Evidence-based starting point (checked against merged code)
- `deletion_engine.py`: `_element_spans()` pairs a matching opening tag with the next `</tag>` without checking for self-closing, nested or ambiguous structures. `remove_unit()` and `remove_settlement()` are conservative but have no general exact-removal/survivor invariant checker. `plan_settlement()` exists; `plan_unit_deletion()` does not.
- `edit_backend.py`: `change_field` dispatches `deleteUnit`, `deleteNativeUnit`, `deleteSettlement`; a distinct `_remove_native_unit` exists. `ordered_edits_for_application` sorts deletions before property edits.
- `edit_session.py`: legacy `stage_unit_deletion`, `stage_native_unit_deletion`, `stage_settlement_deletion` can write staged keys directly, without the full Qt `stage_checked` transaction protocol.
- `edit_preflight.py`: `preflight` independently checks some conflicts and runs `change_field` across the whole proposed edit set. Backend `produce` has additional checks; those checks must not diverge.
- FreeCol cached representations can repeat IDs; apparent ID uniqueness in one XML traversal is not proof of authoritative-record uniqueness. Existing cached-missionary refusals must remain.
- Phase 2D-1, 2D-1.5, and OC-001 are already merged. C1/C2 suspected game movement-error investigation is CLOSED BY DECISION, not a blocker. The deferred OC-001 Claude review must be bundled into the next independent *implementation* review, not silently considered complete by this plan review.

## Prioritization definitions
- **Must:** safety or correctness gate; failure prevents 2D-0 sign-off and **blocks 2D-2 destructive Qt UI**.
- **Should:** strongly recommended supporting work; can be deferred only with an explicit recorded reason, no impact on Must safety, and owner approval.
- **Could:** optional enhancement, not required for safety gate; never allow it to grow the 2D-0 implementation scope without owner approval.

## Must — ordered implementation checkpoints

### M0. Lock the baseline and capture a reproducible deletion matrix
1. Branch from the verified current `main` *after* the docs reconciliation is merged/otherwise resolved; confirm SHA and CI. No unrelated source refactor.
2. Inventory existing deletion entry points and accepted Tk behavior, `deleteUnit` / `deleteNativeUnit` / `deleteSettlement` keys, backend `produce`, `edit_preflight.stage_checked`, Save As and relevant Qt non-destructive components. Record which delete cases currently succeed/refuse; avoid expanding support accidentally.
3. Build a **red/green behavioural baseline** with small FreeCol-shaped XML byte fixtures: explicit closing and self-closing `unit`, `aiUnit`, `ownedUnits`, cached `indianSettlement`, nested structures, repeated cached IDs, surviving sibling records. Include cases that currently expose flaws, marked expected failures until fixed.
4. Preserve a stable golden exported XML fixture and source .fsg SHA-256. Capture exact expected deletion targets and expected refusals before changing the engine.
**Exit:** fixtures characterize genuine deletion behavior, existing Tk APIs and source integrity; failing cases documented with their reason.

### M1. Safe structural removal-span extraction
1. Replace `_element_spans` opener/first-close heuristic with a **structure-aware byte-span locator**. It must support XML self-closing elements, explicit closing elements, nested same-name elements, and mixed forms without assuming a regex can balance XML.
2. Match the **specific parsed element and its byte interval/context** (not only ID). Define how namespace prefixes, quote variants, attributes containing `>`, comments, CDATA and whitespace are handled; if exact byte tracking cannot be established, **refuse the operation**. Preserve untouched original byte slices rather than serializing the complete XML.
3. Support deletion of permitted authoritative elements and their specifically associated AI/cached elements; no accidental removal of a same-ID cached element, adjacent sibling or enclosing container. Reject overlapping, duplicated or unresolved target spans.
4. Verify every target span starts/ends on the intended element boundary. Reject truncation or unexpected parser/byte disagreement before exporting.
**Exit:** tests for explicit, self-closing, nested, mixed and adversarial syntax pass; all non-target bytes are preserved except separately authorized attribute edits.

### M2. Exact-removal invariant verifier (the corruption gate)
1. Establish a **pre-operation manifest** of authoritative records, cached copies and structurally identified dependencies, using full element context/path/ordinal where IDs repeat. Do not compare only unique-ID sets.
2. Build the **planned change manifest**: exact target elements, permitted associated AI/owned-unit/cached elements and permitted `owningSettlement` attribute removals (as applicable).
3. After mutation, parse resulting XML and compare against the pre-operation manifest: every survivor retains its identity, parent relation, attributes, text/children and serialized bytes except specifically authorized changes. Verify deleted objects and known references are absent. Preserve order and unrelated comments/metadata.
4. Fail closed on extra removals, extra modifications, missing required removals, mismatched cached copies, unresolved external references or malformed ZIP/XML. Do not rely on `ET.fromstring` alone as a safety proof.
5. Test failures that produce **well-formed XML with collateral damage** (not merely unparseable output), including repeated cached identities, same-name nesting, neighboring elements and XML text that resembles a target tag.
**Exit:** exact removal and survivor equality are enforced for all supported delete operations and tested independently of the edit UI.

### M3. Common native + European unit deletion engine and impact planner
1. Define a UI-neutral, **read-only `plan_unit_deletion(xml, unit_id, ...)`** result (e.g., owner, type, location, containing colony/village, authoritative record, AI counterpart, cached representations, cargo/passengers, known reference impacts, refusal reasons). The plan must not mutate XML and must not claim unsupported operations are safe.
2. Consolidate `edit_backend._remove_native_unit` with `deletion_engine.remove_unit` through **one shared path** with explicit context/policy for supported native cases, while preserving the old Tk key schema and observed refusal behavior.
3. Inventory and fail closed on carrier/cargo, aboard ships, inaccessible Europe/trade route locations, teacher/student, settlement-owned units, AI missions, unknown destinations/references, cached missionaries, ambiguous owner/location and unrecognized modded relationships. **Do not broaden support** to these cases on the assumption that they are safe.
4. Have the backend **revalidate the plan against current export XML**, never trust a stale UI preview. Preserve mixed-owner native-settlement refusals and existing settlement planner behavior.
5. Verify property edit versus deletion, native key versus ordinary unit deletion key, and duplicate deletion attempts cannot produce an invalid transaction.
**Exit:** planner truthfully describes supported targets/refusals; one backend implementation underlies deletion variants; legacy Tk regressions pass.

### M4. Whole-staged-set safety and shared validation
1. Implement a shared **transaction-level invariant validator** used by both `edit_preflight.preflight` and `edit_backend.produce`; export must independently validate, not blindly trust earlier UI staging.
2. Model the colony's effective surviving **inhabitant population** using authoritative worker/in-colony unit relationships, as defined/verified against FreeCol game rules. Reject a staged set that removes the final inhabitant—even when each of several deletions is individually legal; account for all applicable deletion keys.
3. Refuse conflicts involving a deleted unit plus its equipment, XP, moves or other edits; settlement deletion plus edits to that settlement/owned units; and any cross-record dependency that cannot be safely resolved. Explicitly preserve existing goods, reciprocal diplomacy and movement preflight requirements.
4. Make **safe checked staging** the required path for future Qt destructive controls, without changing the legacy Tk public functions' behavior. Support safe undo and revalidation when a stage is removed; Save As validates again against opened source.
5. Verify that a rejected combined transaction leaves the entire staged set unchanged and original source .fsg byte-identical, including after failed export.
**Exit:** combined-stage deletions cannot bypass population/dependency checks; preflight and export return consistent pass/refusal decisions.

### M5. Adversarial and real-save acceptance gate
1. Automated suite: unit and settlement deletions across explicit/self-closing/mixed XML; cached duplicate IDs; intended AI and village links; cargo/passenger/aboard-ship refusals; colonial last-inhabitant cases individually and in combination; refusal/undo, stale plan, conflicted staging, unknown references, source immutability, Save As overwrite refusal, preservation of all unrelated data.
2. Regression on accepted existing editor behavior: Qt Bells/Crosses/Hammers, equipment role eligibility, stage/undo, SoL and colony goods, diplomacy, native alarm, proportional moves, source-value Inspector, legacy Tk deletion behavior and session keys. **No new destructive Qt controls are part of this phase.**
3. Run CI on exact final branch head, with meaningful negative fixtures that fail before fixes and pass after; report test command, count, skips, status and SHA.
4. Produce a **Windows real-save checklist** naming expected allowed and refused deletes, actual export paths (new filenames), exact original-file hash verification, and FreeCol **load → advance one turn → save → reload** on representative *safe* deletion cases. Compare affected units/colonies/settlements and unrelated state; record version, result and any limits.
5. Submit code and detailed diff plus acceptance evidence for **independent Claude deletion-safety review**. Bundle the outstanding OC-001 post-correction follow-up into this review request, clearly separated from 2D-0.
6. Resolve all blocking review findings and rerun impacted regressions, CI and focused Windows/FreeCol checks; obtain **explicit Project Director acceptance**. Merge/tag/branch deletion require separate explicit approvals.
**Exit:** all Must criteria evidenced and signed off; only then may Phase 2D-2 start.

## Should — recommended without being an independent merge blocker
### S1. Structured impact and refusal vocabulary
Give the planner stable machine-readable reason codes and counts, alongside understandable error descriptions; use consistent terminology for authoritative versus cached objects and reference impact. Avoid GUI coupling.

### S2. Transaction snapshots for efficient validation
Parse/reference-index the save once per planning/transaction where this does not reduce independent export verification. Benchmark representative real-save operations (especially deletion sets) before/after; record time and memory, but do not optimize ahead of correctness.

### S3. Deletion diagnostics and test readability
Add narrowly focused fixture builders and diagnostic reports which state requested IDs, contexts, missing/mismatched references and permitted changes without leaking real private save data to version control. Keep tests behavioural, not source-string assertions.

### S4. Documentation and capability matrix
Maintain a table of **supported / refused / not yet verified** unit and settlement cases, scope-by-owner and location, and what later 2D-2/2D-3 UI can expose safely. Clarify that valid owner eligibility does not prove any location is delete-safe.

### S5. Future Qt wiring contract
Publish planner-to-UI contract for 2D-2: explicit owner, impact summary, cancel default, undo, displayed refused reasons, stable record identity after sorting and no action on speculative supported cases. **Do not build Qt delete UI here**.

## Could — explicitly deferrable
### C1. Dedicated local read-only delete-preview command
A diagnostic CLI to print planned impacts/refusals for a given save, without mutating or exporting; helpful for field-testing but not necessary for safe backend.

### C2. Human-readable manifest diff report
Optional sanitized before/after summary of deleted/retained nodes and permitted attribute changes, using M2's mandatory verification data. Never substitute this report for the verifier.

### C3. Property-based/fuzz testing
Additional generated XML variants and random deletion sequences in CI, once deterministic adversarial Must fixtures are solid; keep resource use bounded.

### C4. Broader delete performance profiling
Opt-in microbenchmarks for huge native-settlement / AI-heavy saves; performance does not justify relaxing validation.

## Explicitly out of scope for 2D-0
- **No new Qt deletion UI**, bulk-delete workflow, or new unsupported deletion cases.
- **No European colony deletion implementation** or speculative unit relocation; these belong to separately reviewed 2D-4 and its prerequisite real-save dependency matrix.
- No repair of cached missionaries (existing refusal stays until after v1.0, if requested).
- No investigation of the closed C1/C2 suspected FreeCol game movement issue without new owner authorization.
- No unrelated Tk feature work, broad module reshuffling, terrain/RNG/reveal-map expansion or weakening of previous accepted features.

## Implementation order and proposed delivery packages
| Package | Steps | Required evidence | Gate |
|---|---|---|---|
| A — Baseline + XML boundaries | M0 → M1 | Red/green XML tests; self-closing, nested and mixed structures; exact byte preservation | Stop if structural span safety unresolved |
| B — Verified deletion + planner | M2 → M3 | Whole-survivor equivalence, dependency and native/European unit plan tests; Tk parity | No unverified deletions |
| C — Transaction safety | M4 | Multi-stage last-inhabitant rejection, shared preflight/export parity, undo and conflict tests | No unsafe combined deletion |
| D — Acceptance | M5 | Exact SHA CI, Windows/FreeCol roundtrip evidence, independent Claude review including OC-001 follow-up | Project Director approves separately |

## Questions for Claude's independent PLAN review
1. Is the proposed structure-aware **byte-span** technique realistically implementable without silently reserializing the document? What parser/offset strategy minimizes risk? Are any XML forms incorrectly called safe?
2. Are M2's survivor invariants sufficiently strong, especially when cached IDs are repeated, attributes are permitted to be removed, and literal XML bytes must otherwise be preserved?
3. Does our staged population rule correctly identify FreeCol colony inhabitants across `building`, `colonyTile`, `colony` and carried/visiting units? What real game semantics require research before implementation?
4. Does consolidation preserve Tk `deleteNativeUnit` semantics and existing safe refusals? Are any additional dependency/refusal classes **Must**, rather than Should?
5. Are plan/preflight/export checks independent enough to catch correlated defects while sharing validation logic?
6. Are package boundaries and tests sufficient to prevent introducing destructive Qt UI before safety review and explicit acceptance? What changes to Must/Should/Could priorities do you recommend?

**Reviewer permissions:** Claude may create/commit/push *review-only* documents and proposed plan edits on this documentation branch, including a structured Must/Should/Could findings table. Claude must **not** implement source code, merge PRs, tag releases, delete branches or change agreed scope without the Project Director's explicit permission.

## Reviewer-proposed corrections (Claude, 28 October 2026) — ACCEPTED by Project Director, 28 October 2026
Full review: [PHASE2D0_PLAN_REVIEW.md](PHASE2D0_PLAN_REVIEW.md). Verdict: **PASS WITH CAVEATS**. The Project Director approved all eight amendments, subject to the accepted Tk-safety qualification below. They are binding implementation requirements.
1. **New Must refusal (M3/M4):** refuse a staged set that leaves a native player with zero units, or a colonial player with zero colonies and zero non-carrier units (FreeCol `ServerPlayer.checkForDeath`).
2. **M1:** decide empty versus explicit elements by a quote-aware scan of the start tag, cross-checked against expat's end-event offset; refuse on disagreement. **Refuse** DOCTYPE/entity declarations, non-UTF-8 encodings and namespace prefixes rather than supporting them. Exit criterion: every element of each fixture (and locally, a real save) re-parses equal from its slice.
3. **M2:** expected tree = parsed original minus the planned nodes (by path and ordinal) plus the authorized attribute removals; normalize only whitespace-only text. Must include a fault-injection test in which a wrong locator is rejected.
4. **M4:** inhabitants = units under the colony's `<building>` and `<colonyTile>`; refuse units directly under `<colony>` until real-save evidence exists; one shared population helper for SoL and deletion. Normalize all deletion keys to the target unit ID before conflict checks.
5. **M3:** apply the same container, carrier and location checks to native units; refuse IDs embedded as tokens in any attribute value or text.
6. **M5:** add an automated guard that no `qt_*.py` module stages a deletion.
7. **Priorities:** S4 capability matrix → Must (M3 exit); S5 becomes an entry gate for 2D-2; others unchanged.
8. **Sequencing:** locator → verifier → swap mechanics with **no policy change** (all Tk regressions unchanged) → new policy → transaction rules → acceptance. Use a `feature/phase2d0-…` branch so CI runs on every push.


## Binding decision — Claude amendments and Tk retirement (28 October 2026)

**Decision: APPROVED.** All eight reviewer amendments above are promoted from proposals to implementation requirements. Their Must/Should/entry-gate priorities and mechanism-first order are authoritative; the earlier text in M0–M5 is read together with these additions, never as an exception to them. Specific additional gates:

- **M1:** use quote-aware XML start-tag classification with expat byte-offset cross-checks; reject unsupported encoding, DOCTYPE/entities and namespaced element names; test full element-slice round-trip on fixtures and a real save.
- **M2:** independently verify the resulting parsed tree equals the original parsed tree with only planned path/ordinal removals and explicitly authorized attribute edits; normalize whitespace-only text only; prove the verifier rejects a deliberately corrupted span locator.
- **M3:** protect player survival; apply equivalent structural/carrier/location safeguards to European and native units; refuse embedded-token and text references; provide a Must-grade supported/refused/unverified capability matrix. Planner output is advisory and never trusted on export.
- **M4:** define colony inhabitants as work-location units in buildings and colony tiles (not visiting units on the map or aboard ships); use one population helper for deletion and SoL; normalize native composite deletion keys to underlying unit IDs before conflict checks; validate the complete transaction for last-inhabitant and player survival.
- **M5:** enforce an automated no-destructive-Qt-UI guard during 2D-0; the 2D-2 Qt wiring contract is an entry gate for 2D-2 rather than a prerequisite for accepting 2D-0. Run representative large-save timing in the acceptance evidence.
- **Order:** baseline → locator → independently tested verifier → mechanically integrate with existing accepted semantics → new policies → whole-transaction safety → CI/Windows/FreeCol and independent code review. Develop on a `feature/phase2d0-…` branch for push CI.

**Tk compatibility, with a strict safety exception:** during 2D-0, preserve safe, accepted Tk operations, public keys and interfaces. **Never preserve a demonstrably unsafe deletion merely for compatibility**: correct or conservatively refuse it, document and test the intentional behavioural change. The Tk editor is frozen for new features while PySide6 becomes the sole future UI.

**Release-wide mandatory Tk retirement:** before the **first stable public 1.0 release**, remove all Tk/Tkinter runtime code, UI modules, dependencies, imports, entry points, packaging references, obsolete scripts and Tk-only tests/docs that suggest Tk remains supported. Retain necessary historical changelog/review records as history, and preserve functionality in Qt/shared backend before retirement. Add CI/static guards ensuring no Tk runtime dependency and verify Windows packaging and real FreeCol Save As roundtrips. This is a **mandatory 1.0 release gate**, not an instruction to remove Tk during 2D-0; schedule implementation in the 0.9 release-candidate cleanup. The project may not declare stable release while either Tk UI or Tk dependency survives.

**Review governance:** Claude's plan review is accepted with the amendments above. OC-001's deferred independent *implementation* follow-up remains open and must be included in the next independent 2D-0 code review. No source-code changes or checkpoint sign-off are implied by approval of this plan.
