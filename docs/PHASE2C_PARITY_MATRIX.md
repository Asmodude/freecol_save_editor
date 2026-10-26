# Phase 2C — Tk → Qt Parity Matrix

**Status:** C1 Windows ACCEPTED on tested commit `deb5cec` (28 pass, 0 fail, 1 N/A plus 2/2 follow-up retests); C2 not yet accepted. implementation evidence is recorded per operation, not inferred from plan acceptance.  
**Baseline:** Phase 2B merged on main. **Independent source audit:** Claude, [PHASE2C_PLAN_REVIEW.md](PHASE2C_PLAN_REVIEW.md), 26 October 2026 (confirmed complete non-destructive operation inventory against `freecol_explorer.py`, `EditSession` and `edit_backend.py`).  
**Source of truth:** [Accepted implementation plan](PHASE2C_IMPLEMENTATION_PLAN.md), especially §12.

| Field / operation | Authoritative edit key | Validation and notable behavior | Qt implementation | Automated | Windows | FreeCol |
|---|---|---|---|---|---|---|
| Gold | `(player_id, gold)` | 0–2,147,483,647; native sentinel excluded | Phase 2B; C1 preflight integration | Preflight tests added; full regression pending | 2B passed; C1 recheck pending | 2B passed |
| Tax | `(player_id, tax)` | 0–100; present numeric source attribute | Inline shared player numeric control implemented on branch | Qt behavior and preflight tests pass in CI #451 | Pending | Pending |
| Experience | `(unit_id, experience)` | 0–200; present numeric attribute; full unit Overview editing gives capability parity | Shared inline numeric unit Overview editor implemented | Offscreen stage/source integrity test added; CI #456 passed | Pending | Pending |
| Moves left | `(unit_id, movesLeft)` | 0–movement cap with **staged role** | Shared inline unit Overview editor and backend-preflight staging implemented | Offscreen cap rejection test added; equipment/movement stage and undo combinations covered by automated tests #460–461 | Pending | Pending |
| Equipment | `(unit_id, equipment)` | Composite (role,roleCount); valid roles/abilities, native/naval, deletion conflict; may clamp moves | Not started | Pending | Pending | Pending |
| Colony goods | `(colony_id, model.goods.<type>)` | Known type; 0 if absent; positive stock creation only with storedGoods | Not started | Pending | Pending | Pending |
| Sons of Liberty | `(colony_id, sonsOfLibertyTarget)` | 0–100; population >0 and standard formula; changes six attributes | Not started (C2) | Pending | Pending | Pending |
| Stance | `(player_id, stance|<other>)` | Four permitted choices; existing equal reciprocal; changes both ways | Not started (C2) | Pending | Pending | Pending |
| Tension | `(player_id, tension|<other>)` | Existing directed relation; numeric nonnegative ≤2,147,483,647 | Not started (C2) | Pending | Pending | Pending |
| Settlement alarm | `(settlement_id, alarm|<colonial player>)` | Existing directed relation only; no creation of missing records | Not started (C2) | Pending | Pending | Pending |
| Learnable skill | `(settlement_id, learnableSkill)` | Only skills taught by authoritative settlements in the opened save | Not started (C2) | Pending | Pending | Pending |

**Scope:** Deletion actions are intentionally Phase 2D, not omissions in this 2C matrix. The native Tk limitation allowing staging of a nonexistent alarm that fails export must **not** be copied: present those relations as non-editable with explanation. Do not introduce warehouse capacity rules, arbitrary derived-value edits or ruleset-wide skill choices.

**Audit conclusion:** The independently reviewed inventory contains no additional accepted non-destructive Tk operations (Claude §1, §8). Stage-time backend preflight must refuse all unsupported combinations **before** modifying session, and remains supplemental to final producer validation.

**Status policy:** Implementation, automated, Windows and FreeCol outcomes will be updated separately with evidence. No unchecked category is marked accepted.

**C1 partial implementation (26 October 2026):** `edit_preflight.py` provides cloned in-memory backend validation and checked stage/undo APIs; Qt player Gold and Tax staging uses it. `RecordTableModel` exposes persistent bold/italic staged-value font roles, including selected rows. Draft PR #6 holds all development; CI #451 passed at `507129f`. Unit XP, movement and all C2 categories remain unimplemented; no Windows acceptance claimed.

**C1 continued (26 October 2026):** Inline Unit Experience and Moves Left, identity-bound staging through backend preflight and workspace staged markers implemented; headless CI #456 green at `a104f36`. Selected-row staged FontRole has additional automated assertions (subsequent commit; requires CI). The dependency with staged equipment is mechanically evaluated by whole-set preflight, but dedicated dragoon/soldier staging/undo permutations are **not yet verified**. C1 is not signed off.

**C1 dependency verification (26 October 2026):** The Staged Changes panel now preflights Undo against the remaining staged set when a loaded document is available. Added dragoon↔soldier movement-cap tests (including undo order) and a Qt panel refusal test. CI #461 passed on `ac39b59`; no Windows sign-off or checkpoint merge authorized. C1 integration remains pending user Windows verification and any final independent review.

**Windows finding — colony Workers inline XP (26 October 2026):** User found that unit `unit:34590` working silver at Charlotte Amalie could edit Experience via Units → Overview but not at its natural colony Workers location. C1 now embeds an inline Experience editor in each eligible colony Workers row, bound to the authoritative unit ID before sorting, routed through the existing stage-time preflight. It explicitly stages only on Enter or the pencil button. Offscreen identity-under-sort regression test added; Windows retest required on branch head before signing off C1.

**C1 Windows test run (26 October 2026, commit `6603874`):** 28 PASS, 0 FAIL, 1 N/A (C1-11: no applicable unit found). User reported two accepted-test caveats: native tribe Tax wrongly editable/displayed (C1-08), and after colony Workers inline XP staging the active tab resets to Overview (C1-12; reproduced in Charlotte Amalie and Koralbugt). The subsequent branch revision hides native Tax in the UI and prevents staging, and restores the active contextual tab after staged refresh. Regression tests for both passed in GitHub CI #471 at `1bd8e99`. **Windows retest of both specific caveats is required; C1 is not yet accepted.**

## C1 acceptance decision — 26 October 2026

**Windows acceptance: PASSED, confirmed by user.** Initial comprehensive Windows run against `6603874`: 28 PASS, 0 FAIL, 1 N/A (C1-11 — no suitable unit encountered). Two issues were identified despite pass totals: native Tax was shown/editable, and staging worker XP from a colony reset the Workers tab to Overview. Both were fixed and tested on commit **`deb5cec4e3c79bd9f916f425209c54940cd5fd30`**. User explicitly confirmed on 26 October 2026 that both focused Windows retests **PASSED**. Headless GitHub Actions CI **#472 completed successfully** on the exact tested commit.

**Checkpoint C1 Windows gate: ACCEPTED.** This does not constitute C2 acceptance, completed Phase 2 acceptance, or authorization to merge/tag/delete the branch. Development may continue on `feature/phase2c-editing-parity` under draft PR #6. Any future C1-affecting changes require appropriate regression evidence.
