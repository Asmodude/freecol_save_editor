# Phase 2C — Tk → Qt Parity Matrix

**Status:** C1 audit established, numeric editing underway; implementation evidence is recorded per operation, not inferred from plan acceptance.  
**Baseline:** Phase 2B merged on main. **Independent source audit:** Claude, [PHASE2C_PLAN_REVIEW.md](PHASE2C_PLAN_REVIEW.md), 26 October 2026 (confirmed complete non-destructive operation inventory against `freecol_explorer.py`, `EditSession` and `edit_backend.py`).  
**Source of truth:** [Accepted implementation plan](PHASE2C_IMPLEMENTATION_PLAN.md), especially §12.

| Field / operation | Authoritative edit key | Validation and notable behavior | Qt implementation | Automated | Windows | FreeCol |
|---|---|---|---|---|---|---|
| Gold | `(player_id, gold)` | 0–2,147,483,647; native sentinel excluded | Phase 2B; C1 preflight integration | Preflight tests added; full regression pending | 2B passed; C1 recheck pending | 2B passed |
| Tax | `(player_id, tax)` | 0–100; present numeric source attribute | Inline shared player numeric control implemented on branch | Qt behavior and preflight tests pass in CI #451 | Pending | Pending |
| Experience | `(unit_id, experience)` | 0–200; present numeric attribute; full unit Overview editing gives capability parity | Not started | Pending | Pending | Pending |
| Moves left | `(unit_id, movesLeft)` | 0–movement cap with **staged role** | Not started | Pending | Pending | Pending |
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
