# Phase 2C — Tk → Qt Parity Matrix

**Final C1–C3 Windows status: ACCEPTED by user on 27 October 2026.** C1 accepted 26 October (`deb5cec`, CI #472), C2 accepted 26 October (`cd10b2c`, CI #546), C3 accepted 27 October (movement override, representative FreeCol Save As/load/reload, editing non-regression). Claude's independent review (`docs/PHASE2C3_INDEPENDENT_REVIEW.md`) was **PASS WITH CAVEATS** at `068a0cd`. Post-review fixes and focused Windows verification were subsequently **accepted by user on 27 October 2026**, including default-role/roleCount=0, Soldier→Dragoon→Soldier restored movement, and approval of proportional movement in both Qt and Tk. PR #6 remains unmerged pending integration decision.

**Scope:** Phase 2C delivers non-destructive parity. Destructive deletion parity is Phase 2D. Source-of-truth details: `docs/PHASE2C_IMPLEMENTATION_PLAN.md` and `docs/PHASE2_DEVELOPMENT_PLAN.md`.

| Field / operation | Authoritative key | Qt and validation | Automated evidence | Windows evidence | FreeCol evidence |
|---|---|---|---|---|---|
| Gold | `(player_id,gold)` | Inline, integer 0–2,147,483,647; native sentinel excluded | 2B suite, C1 preflight; independent review §1 | C1 PASS | 2B and C3 roundtrip |
| Tax | `(player_id,tax)` | Inline 0–100; native tax refused | CI #451 onward, independent §1 | C1 PASS incl. focused native-tax retest | C3 representative roundtrip |
| Experience | `(unit_id,experience)` | Inline 0–200 in Units Overview and colony Workers | CI #456 and Workers identity tests; independent §1 | C1 PASS incl. Workers-tab retest | C3 representative roundtrip |
| Moves left | `(unit_id,movesLeft)` | Cap from effective staged equipment; explicit override preserved | C3 fix; independent §2 live export | C1, C2, C3 PASS | C3 PASS |
| Equipment | `(unit_id,equipment)` | Role/count composite, ruleset validation, proportional moves; Unit Overview and Stationed | CI #476, #544; independent §1–3 | C2 PASS; post-review default/0 retest PASS | C3 PASS; post-review retest PASS |
| Colony goods | `(colony_id,model.goods.<type>)` | Eligible existing and absent stock, validation and proposed national projection | CI #483; independent §1 | C2 PASS incl. projection correction | C3 representative roundtrip |
| Sons of Liberty | `(colony_id,sonsOfLibertyTarget)` | Eligible colony; dependent fields calculated on export | CI #487; independent §1 | C2 PASS | C3 representative roundtrip |
| Stance | `(player_id,stance|other)` | Reciprocal source-backed, valid options, reject opposite-direction duplicate | CI #502; independent §1 | C2 PASS | C3 representative roundtrip |
| Tension | `(player_id,tension|other)` | Directional, existing source-backed relation | CI #502; independent §1 | C2 PASS | C3 representative roundtrip |
| Settlement alarm | `(settlement_id,alarm|player)` | Directional, existing source-backed relation, reject absent | CI #503; independent §1 | C2 PASS | C3 representative roundtrip |
| Learnable skill | `(settlement_id,learnableSkill)` | Only skills present among authoritative settlements in opened save | CI #497; independent §1 | C2 PASS | C3 representative roundtrip |

**Evidence precision:** C3 verified representative real-game export and reload; it was **not** an exhaustive individual FreeCol roundtrip for all eleven rows. Independent off-screen combined export confirmed every supported edit type. Historic paragraphs below document their state **at the time**, including earlier pending labels; the table above is authoritative as of 27 October.

## C1 and C2 development history (historic snapshots, not current status)

**C1 partial implementation (26 October 2026):** `edit_preflight.py` provides cloned in-memory backend validation and checked stage/undo APIs; Qt player Gold and Tax staging uses it. `RecordTableModel` exposes persistent bold/italic staged-value font roles, including selected rows. Draft PR #6 holds all development; CI #451 passed at `507129f`. Unit XP, movement and all C2 categories remain unimplemented; no Windows acceptance claimed.

**C1 continued (26 October 2026):** Inline Unit Experience and Moves Left, identity-bound staging through backend preflight and workspace staged markers implemented; headless CI #456 green at `a104f36`. Selected-row staged FontRole has additional automated assertions (subsequent commit; requires CI). The dependency with staged equipment is mechanically evaluated by whole-set preflight, but dedicated dragoon/soldier staging/undo permutations are **not yet verified**. C1 is not signed off.

**C1 dependency verification (26 October 2026):** The Staged Changes panel now preflights Undo against the remaining staged set when a loaded document is available. Added dragoon↔soldier movement-cap tests (including undo order) and a Qt panel refusal test. CI #461 passed on `ac39b59`; no Windows sign-off or checkpoint merge authorized. C1 integration remains pending user Windows verification and any final independent review.

**Windows finding — colony Workers inline XP (26 October 2026):** User found that unit `unit:34590` working silver at Charlotte Amalie could edit Experience via Units → Overview but not at its natural colony Workers location. C1 now embeds an inline Experience editor in each eligible colony Workers row, bound to the authoritative unit ID before sorting, routed through the existing stage-time preflight. It explicitly stages only on Enter or the pencil button. Offscreen identity-under-sort regression test added; Windows retest required on branch head before signing off C1.

**C1 Windows test run (26 October 2026, commit `6603874`):** 28 PASS, 0 FAIL, 1 N/A (C1-11: no applicable unit found). User reported two accepted-test caveats: native tribe Tax wrongly editable/displayed (C1-08), and after colony Workers inline XP staging the active tab resets to Overview (C1-12; reproduced in Charlotte Amalie and Koralbugt). The subsequent branch revision hides native Tax in the UI and prevents staging, and restores the active contextual tab after staged refresh. Regression tests for both passed in GitHub CI #471 at `1bd8e99`. **Windows retest of both specific caveats is required; C1 is not yet accepted.**

## C1 acceptance decision — 26 October 2026

**Windows acceptance: PASSED, confirmed by user.** Initial comprehensive Windows run against `6603874`: 28 PASS, 0 FAIL, 1 N/A (C1-11 — no suitable unit encountered). Two issues were identified despite pass totals: native Tax was shown/editable, and staging worker XP from a colony reset the Workers tab to Overview. Both were fixed and tested on commit **`deb5cec4e3c79bd9f916f425209c54940cd5fd30`**. User explicitly confirmed on 26 October 2026 that both focused Windows retests **PASSED**. Headless GitHub Actions CI **#472 completed successfully** on the exact tested commit.

**Checkpoint C1 Windows gate: ACCEPTED.** This does not constitute C2 acceptance, completed Phase 2 acceptance, or authorization to merge/tag/delete the branch. Development may continue on `feature/phase2c-editing-parity` under draft PR #6. Any future C1-affecting changes require appropriate regression evidence.

**C2 initial implementation (26 October 2026):** Unit Overview supports role selection filtered by the saved ruleset and a roleCount selector bounded by maximum-count. Stage creates exactly `(unit_id, 'equipment')` as a composite role/count tuple. Stage-time ruleset validation and complete staged-set preflight refuse unsupported roles, deletion conflicts and movement incompatibilities. Qt regression confirms stable unit identity, stage and original-source immutability; CI #476 green at commit `2c8586d`. **This is an engineering increment, not C2 acceptance.** Pioneer default-role special case, equipment permutations on real saves and Windows usability still require attention.

**C2 continued (26 October 2026):** Hardy Pioneer default-role units now suggest Pioneer equipment without implicitly staging; tool quantities are displayed as 20/40/60/80/100 for roleCount 1–5. A regression test caught the first selection implementation and was corrected before further work. Colony Goods tab now offers inline stock editing for existing and absent goods, retaining the full goods-type ID under sorting and preflighting the whole set. CI #483 passed at `dac8299`. Neither equipment nor colony Goods has undergone Windows testing; C2 is not accepted.

**C2 colony SoL increment (26 October 2026):** Added editable SoL target in the colony Overview only if source population and ordinary liberty formula can be verified. Backend preflight refuses unsafe requests, and UI indicates that liberty, rebel/tory values and production bonus are recomputed on export rather than immediately modified in the source XML. Automated test covers target and all six resulting XML attributes; CI #487 passed on `3c580a0`. Still needs real-save and Windows acceptance. Diplomacy/native skill editing remain pending.

**C2 native/diplomacy increment (26 October 2026):** Native settlement Overview now has a learnable-skill selector restricted to `SaveDocument.professions` (skills observed in the opened save), with stage-time backend preflight. Both existing separate diplomacy tables now offer stance and tension staging for source-backed relationships only; stance remains reciprocal and tension directional. Native settlement Alarm tab offers source-backed directional staging, refusing missing relations. CI #497 passed on `d7940ab`. A new direct Qt relation staging test was added subsequently at `86d1338` and needs its own CI confirmation. The new controls still require more end-to-end validation and Windows acceptance; C2 remains IN PROGRESS.

**C2 regression consolidation (26 October 2026):** Diplomacy staging now preserves the active Rival Nations/Natives category and reselects the same source-backed relationship after rebuilding views; inspector Stance and Tension display their staged values. Automated tests confirm reciprocal Stance changes, directional Tension, refusal of duplicate opposite-direction Stance staging and safe undo (CI #502 passed). Native settlement Alarm test uses two colonial players with identical visible names, sorts the Alarm table, and verifies that only the source-backed player ID is edited and source XML stays immutable; CI #503 passed at commit `0f90731`. C2 Windows acceptance, game roundtrip, and any independent review remain pending. C1 acceptance remains unchanged.

## C2 comprehensive Windows feedback and correction cycle — 26 October 2026

User completed all 38 Windows C2 checks at `f594e3a`: **37 PASS, 1 FAIL, 0 N/A**. C2-14 failed because National Goods showed source-only warehouse totals without labelling exclusion of staged goods. C2-12's 900-unit goods test was valid (actual maximum 2,147,483,647); the true overlimit boundary was not exercised.

The following changes were requested during acceptance and bundled after the run:

- **C2-F01**: Player-facing equipment descriptions and stock quantities (50 muskets, 50 horses, or 20–100 tools), without changing conjured equipment / no colony stock consumption.
- **C2-F02**: Equipment selection and staging directly in Colony → Stationed units → Role, retaining unit identity under sorting and existing validation.
- **C2-F03**: Proportional conversion of remaining movement on role changes; half-up rounding. Dragoon 12→3, 9→2, 6→2, 3→1, 0→0 when downgrading to Soldier. Soldier at full movement 3→Dragoon 12. Explicit staged movement is converted atomically with the role change, and preflight/export use identical ordering.
- **C2-F04**: Source cell text no longer paints behind Stance/Tension widgets; editor row/column sizing improved, source sort key retained.
- **C2-F05**: National Goods table headings and Inspector/Overview now explicitly identify figures as **source-only** excluding staged colony warehouse edits. No staged quantities are falsely included in the aggregate.
- **UX-XML**: Earlier formatting enhancement renders unit XML attributes on individual indented lines; user Windows retest outstanding.

These changes require green final CI and **focused Windows retests**. The initial 37-pass run is not retrospectively converted into C2 acceptance. C1 remains previously accepted subject to non-regression.

**C2 Windows end-of-test follow-up (26 October 2026):** User confirmed Soldier 3→Dragoon 12 shown consistently in Units and Unit Overview and verified 2/3→8 proportional conversion for Soldier to Dragoon. National Goods source → proposed projection accepted following Christiansborg Fish 0→100 staged change. Final C2-F06 discovered: mouse wheel while hovering Stationed units equipment combo could silently change selection in long scrollable table. Implemented wheel-safe equipment combo and tool spinbox in both Unit Overview and colony Stationed units. Original role, staged role and current unstaged selection are distinguished by Staged / Not staged status and explanatory tooltip; selectors remain bound to authoritative unit IDs. Wheel tests and role staging regressions passed on CI #544 (commit `eef35f2`); additional status-label assertion at `52b883d` awaiting CI. **Windows C2 sign-off is still pending the focused retest of C2-F06 and remaining corrections.** No merge authorized.

## Formal C2 Windows acceptance — 26 October 2026

**C2 WINDOWS ACCEPTED** by user on implementation commit `cd10b2ca5d916eb662055e90e03d31a92fc6048e`, after GitHub headless regression **#546 PASSED**.

- Original 38-case C2 Windows run: 37 PASS, 1 FAIL (National Goods stage visibility), with C2-12 upper-bound subcase not exercised (900 is valid; limit is 2,147,483,647).
- Subsequent consolidated corrections: equipment terminology, inline Stationed units roles, proportional movement staging and display, diplomacy overlap/sorting, proposed National Goods aggregates, XML formatting and wheel-safe controls/staged status.
- National Goods projection and Soldier→Dragoon view consistency passed focused Windows checks; proportional movement separately verified.
- **Final six-case Windows retest on `cd10b2c`: 6 PASS, 0 FAIL, 0 N/A.** Equipment scrolling PASS; role staging status PASS; equipment terminology PASS; diplomacy layout PASS; Raw XML PASS; Dragoon→Soldier movement downgrade PASS. User comments: **None**.

**C2 Windows gate ACCEPTED.** No merge, tag, branch deletion or C3/game roundtrip acceptance is implied. Preserve all accepted C1/C2 behavior. Next: C3 safe export and actual FreeCol load → advance turn → save → reload validation.


## C3 Windows acceptance — 27 October 2026

The tester reported **PASS** for all three closing criteria:
1. Equipment plus explicit movement override staged/exported with the requested final movement value.
2. Guarded Save As → FreeCol load → reload with representative edits.
3. Editing non-regression.

Headless CI before the independent review: **303 tests, 1 expected skip** (run #554 on `c86ab48`); Claude independently executed the same suite and a synthetic real-Qt offscreen full-operation export at commit `068a0cd`, finding **no unintended attribute changes** and issuing **PASS WITH CAVEATS**.

### Post-review corrections (Windows accepted 27 October 2026)

Claude found default-role units could stage `roleCount=1` instead of FreeCol's required 0, and equipment undo could leave a no-op dependent movement edit `3→3`. Both defects were corrected. The user passed focused Windows checks of default-role/roleCount=0 and the Soldier→Dragoon→Soldier movement return; shared proportional Tk movement was explicitly approved. Shared Tk backend proportional movement semantics differ from earlier Tk clamp behavior and are documented in CHANGELOG. See `docs/PHASE2C3_INDEPENDENT_REVIEW.md`.

The intermittent FreeCol automatic movement/Lumberjack anomaly is documented separately in `docs/FREECOL_MOVEMENT_DIAGNOSTIC.md`, with root cause unconfirmed. It is not silently attributed to the editor or treated as proof of FreeCol-only causation.

**Merge gate:** final CI and independent integration review; merge/tag/branch deletion require separate explicit authorization.


## Final user acceptance and integration review preparation — 27 October 2026

- User accepted all closing C3 tests, post-review default-role count, and shared Qt/Tk proportional movement behaviour; subsequent Soldier→Dragoon→Soldier explicit movement regression also passed Windows.
- Pioneer newly selected tool quantity defaults to five bundles (100 tools); covered by updated headless test.
- CI #580: 309 tests passed (1 expected skip) after the movement regression; CI #581: green on subsequent roadmap-only branch head `274bb74`.
- The Inspector/source-XML clarification and explicit Stage Change button text are scheduled for early Phase 2D, not part of the Phase 2C merge.
- No 2C feature-branch merge, tag or deletion performed by this document.
