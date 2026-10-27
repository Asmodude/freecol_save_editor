# Phase 2C Plan Review

_Independent review by Claude (Anthropic), 26 October 2026, of `docs/PHASE2C_IMPLEMENTATION_PLAN.md` on `feature/phase2c-editing-parity` (`0579982`). The plan was checked against the accepted `docs/PHASE2_DEVELOPMENT_PLAN.md` and the **actual** Tk handlers (`freecol_explorer.py`), `EditSession`, `edit_backend.py`, `equipment_rules.py` and the current Qt code. Review only; nothing was implemented._

## Verdict: PASS WITH CAVEATS

- **Priorities.** The mapping is faithful: O1 (non-destructive part), O2, O3, O4, A2, A5 and A10 are Must; O6 is Could. 2D and 2E items are correctly excluded and nothing required is deferred.
- **Inventory.** The operation list in §3 is **complete**: the Tk code contains no further non-destructive edit. It needs the precise rules below, because several backend rules differ from what the plan assumes.
- **One Must-level design rule is missing** (§2.1): refusals must surface at staging time, not at export.

---

## 1. Confirmed Tk → backend contract (answers to questions 2 and 3)

These are the rules the Qt editors must reproduce. Each was taken from code, not documentation.

| Operation | Edit key | Original (from source XML) | Validation actually enforced | Notes for Qt |
|---|---|---|---|---|
| Player gold | `(player_id, 'gold')` | `int(gold)` | 0 to 2,147,483,647; not the native sentinel `-2147483648` | Done in 2B. |
| Player tax | `(player_id, 'tax')` | `int(tax)` | 0–100 | Applies to any player with a numeric `tax`, as in Tk. |
| Unit experience | `(unit_id, 'experience')` | `int(experience)` | 0–200; unit must have a numeric `experience` attribute | Tk edits worker XP from **three places**: the main Units table, the colony Units tab and the Players/settlement Units tabs. Parity is **capability-level**: editing XP in the unit's lower Overview, reached via "Open full unit record", satisfies it. |
| Unit moves left | `(unit_id, 'movesLeft')` | `int(movesLeft)` | 0 to `movement_cap(root, unit)`; refuse if the cap is unknown | **The cap depends on the staged equipment** (see §2.3). |
| Equipment | `(unit_id, 'equipment')` | `(role or 'model.role.default', int(roleCount or 1))` | Role ∈ `ROLES` (default, soldier, dragoon, scout, pioneer); `validate_equipment()` checks ruleset `maximum-count`, `canBeEquipped`, naval and native refusal, and required abilities; refused if the same unit is staged for deletion | One composite key holding a tuple. Pioneer quantity shown as 20/40/60/80/100 tools (`roleCount` 1–5). Tk pre-selects Pioneer for a Hardy Pioneer with the default role. No warehouse goods are consumed. |
| Colony stored goods | `(colony_id, 'model.goods.<type>')` | Stored amount, or **0 if absent** | 0 to 2,147,483,647; goods type must exist in the save | **An absent stock is created** only when the original is 0 and the new value is > 0. The colony must have a `storedGoods` element. No warehouse-capacity rule (accepted Tk behaviour; do not invent one). |
| Sons of Liberty | `(colony_id, 'sonsOfLibertyTarget')` | `int(sonsOfLiberty)` | 0–100; colony population > 0; **current SoL must equal the standard formula** `min(100, liberty*100 // (population*200))`, otherwise refused | Changes **six attributes** locally: `liberty`, `sonsOfLiberty`, `oldSonsOfLiberty`, `tories`, `oldTories`, `productionBonus`. Never touches national liberty. Colonies with SoL modifiers are refused; this is likely in real games once fathers such as Simón Bolívar take effect. |
| Stance | `(player_id, 'stance|<other>')` | Existing value | ∈ {peace, war, cease_fire, alliance}; the **reciprocal stance must exist and be equal**; `produce()` rejects editing both directions in one batch | **Writes both players' stance records.** Works for native players as well as Europeans. |
| Tension | `(player_id, 'tension|<other>')` | Existing value | 0 to 2,147,483,647; the entry must exist | Both European and native players. |
| Settlement alarm | `(settlement_id, 'alarm|<colonial player>')` | Existing value | 0 to 2,147,483,647; the entry must exist | **Missing relationships cannot be created** ("Cannot add a missing relationship in this safety release"). |
| Learnable skill | `(settlement_id, 'learnableSkill')` | Existing value | New value must be a skill **already taught by some authoritative settlement in this save** (`SaveDocument.professions`) | **Not** "all professions in the ruleset": a ruleset-wide list would let users stage values that `produce()` refuses. |

### Corrections to the plan

- **§2C.7 (learnable skill).** The choices are `SaveDocument.professions` (skills present in this save), not "legitimate professions from the ruleset".
- **§2C.6 (diplomacy).**
  - A stance edit is **symmetric by design**: one staged key changes both nations' records.
  - "Reverse-direction protection" therefore means refusing to stage the counterpart direction while one direction is staged; it is not about preserving directional difference.
  - Tension and alarm are directional and independent.
- **§2C.5 (goods).** The "absent → create" semantics already exist and are accepted; implement them. **The goods type identity must come from the stored type id** (`model.goods.tools`), never by reversing the readable row label.
- **§2C.5 (SoL).** Expect real-save refusals for colonies with modifiers. The UI must explain the refusal (§2.1) rather than offer an editor that fails at export.

### Known Tk limitation (record it; do not replicate)

The Tk Diplomacy tab shows a missing alarm as `(absent)` and lets the user stage a value starting from 0. The backend then refuses the whole export. Qt must show absent relations as non-editable, with an explanation. Record this in the parity matrix as an accepted limitation ("missing relationships cannot be created").

---

## 2. Required amendments (Must-level, for C1/C2 acceptance)

### 2.1 Surface every backend refusal at staging time (A2, A10, O3)

`produce()` applies **all** staged edits and aborts the **whole** export on the first refusal. Several backend rules are richer than `EditSession.validate()`:
- the SoL formula check and the empty-colony check;
- stance reciprocity and symmetry;
- relationship existence;
- the learnable-skill set;
- the goods `storedGoods` presence check;
- the cross-field equipment / moves cap (§2.3).

If these are only checked at export, a user can stage many edits and then be unable to export any of them, with no clear indication of which edit is the problem.

**Required:**
- On every stage, run a **dry-run preflight** of exactly the backend change: call `edit_backend.change_field()` on the in-memory source XML (`SaveDocument.xml_bytes`) for that single edit, without writing anything. Refuse the stage with the backend's own message if it raises.
- For edits that interact (equipment + movesLeft; stance in either direction), preflight against the source **with the related staged edits applied** in the same order `produce()` uses.
- Keep `produce()` as the final authority; preflight is only for early feedback.
- **Disable editors up front** where the outcome is already known: absent relations, colonies refused by the SoL formula, empty colonies, units without an `experience` attribute, an unknown movement cap. Show the reason in a tooltip or inline note.

**Tests:** for each refusal class, staging is refused with the backend message and the session is unchanged. A combined export of every accepted edit type succeeds.

### 2.2 Edit identity must never come from display text (A2)

Several current Qt tables identify rows by readable text. One example is `open_breakdown_colony`, which matches goods with `presentation.readable(good_id)`. That is lossy and unsafe for editing.

**Required:**
- Every editable cell or row carries its **full edit key** (record id plus field, or goods type id, or counterpart id) in item data (`Qt.UserRole`) or in the model.
- Editors capture `(key, original)` at creation (2B pattern) and commit only to the captured key.
- Commit only on Enter or the stage button, not on focus loss. 2B already does this; keep it for every new control, including dropdowns.
- After any stage, undo or re-render, editors are rebuilt from the session. Old widgets are detached before deletion (2B fix `1524a59`). Tests must flush deferred deletions before looking up widgets by name.

### 2.3 Cross-field dependency: equipment ↔ moves left (A2)

`movement_cap()` depends on the unit's role: a Veteran Soldier as dragoon has 12, but 3 without horses. `produce()` applies `equipment` before `movesLeft` (alphabetical key order), so the movesLeft check at export uses the **new** role's cap.

**Required:**
- When staging `movesLeft`, validate against the cap of the **staged** role if equipment is staged.
- When staging or undoing `equipment`, re-check any staged `movesLeft` for that unit. If it now exceeds the cap, refuse the equipment change with a clear message, or require the user to adjust moves first. Never leave an unexportable combination staged.
- Undoing equipment while a moves value valid only for the staged role remains staged must likewise be refused or flagged.

**Tests:** dragoon (12) → soldier (3) with moves 12 staged; the reverse; and undo in both orders.

### 2.4 Diplomacy identity and staged display (O2, A2)

- Each diplomacy row and cell must carry its owner, counterpart and kind (`stance` / `tension` / `alarm`). Sorting must not change the target.
- Editing happens in the lower contextual area for the selected relation, consistent with the 2B placement rule. The upper Diplomacy tables are the navigation surface.
- **Stance is symmetric:** after staging Danish → Swedish = war, the Swedish diplomacy view must show its Danish stance as staged war too. Staging from the Swedish side while the Danish side is staged must be refused (matches `produce()`).
- The Staged Changes entry for a stance must say it affects both nations (e.g. *"Stance — Danish ⇄ Swedish: peace → war (both directions)"*).

### 2.5 SoL staged display honesty (O2)

A staged SoL target changes six attributes at export. Before export, the UI must not imply that liberty, rebels, tories or production bonus have already changed. Show the staged target with its original, and state *"liberty, rebels/tories and production bonus are recalculated on export"* or show the computed values as "will become …". `colony_sol_values()` is pure and can provide them.

---

## 3. Checkpoint grouping (question 4)

The plan's C1 (numeric) / C2 (structured) split is practical, with one move:

- **Move Sons of Liberty from C1 to C2.** It is numeric but has the richest refusal rules (formula, population, six-attribute recalculation). It belongs with goods in the colony work.
- **C1:** Tax; unit Experience and Moves (including the equipment-aware cap logic in §2.3, even before the equipment editor exists); the shared preflight (§2.1); reusable numeric control; marker improvements (§4).
- **C2:** Equipment (completing §2.3), colony goods + SoL, diplomacy (stance, tension, alarm), learnable skill.
- Optional checkpoint merges inside 2C are not needed. The accepted plan names a merge after 2C as a whole, which is fine given C3/C4.

## 4. Existing `QTableWidget` tables (question 5)

Migration is **not mandatory**, but tables that become editing surfaces need staged markers and key-carrying rows:
- **Colony Goods tab:** becomes an editing surface; zero/absent rows are editable. **Recommended: migrate it to `RecordTableModel`**, which already supports identity, `BackgroundRole` staged cells and presentation roles. Otherwise, carry goods type ids in item data and implement staged styling separately.
- **Diplomacy tables:** the same recommendation, given the symmetric stance display in §2.4.
- **Workers / Stationed / Affiliated units:** display only; XP is edited via the unit's Overview. No migration needed.

**Marker visibility (carry-over from the 2B review):** the staged background tint is hidden when the row is selected. Add a role that survives selection, such as italic or bold `FontRole` and/or `ForegroundRole`, so staged values stay recognisable in the selected row.

## 5. Reusable controls versus game rules (question 6)

Agree with the plan: shared Qt primitives for **numeric**, **choice** and **composite** editors, handling styling, the "was X" label, Enter/stage button and capture-at-creation. The game rules stay in `EditSession.validate()`, `equipment_rules`, `movement_rules` and the preflight. Avoid one generic abstraction that hides operation-specific rules.

## 6. State, undo and synchronisation (question 7)

The 2B state model (export snapshot, `has_unexported_changes`, first-recorded original) already covers the new edit types. Additional tests:
- composite equipment re-stage keeps the first original tuple;
- stance staged from one side shows in both views, and undo clears both;
- undoing one goods line leaves the colony's other staged goods and its SoL edit intact;
- the National Goods aggregate reflects staged colony goods, or is explicitly labelled as source values. Decide which, and test it.

## 7. Evidence for mixed exports and FreeCol (question 8)

Add to the plan's evidence list:
1. **One combined export** containing at least one edit of every accepted type: gold, tax, XP, moves, equipment, an existing goods amount, a created goods stock, SoL, stance, tension, alarm and learnable skill. Reload with `SaveDocument.load()` and assert each intended attribute, the six SoL attributes, both stance records, and that every non-target record is unchanged (compare attribute dictionaries).
2. **Preflight refusal tests**, one per refusal class (§2.1).
3. **FreeCol roundtrip** for:
   - a numeric set (tax, XP, moves);
   - a colony set (goods creation + SoL);
   - a diplomacy set (stance change to war and back to peace; tension; alarm);
   - an equipment change (soldier → dragoon, and pioneer tools).

   In each case: load → advance a turn → save → reload, and note any game-side reaction (e.g. a war declaration message).
4. Required `headless` CI green on the exact final SHA; source `.fsg` SHA-256 unchanged.

## 8. Omissions, scope creep, gates (question 9)

- **No missing operations.** The inventory in §3 matches the Tk code; native players' stance and tension are included under diplomacy.
- **No scope creep** found. Keep it that way: no warehouse-capacity rules, no creation of missing relationships, no ruleset-wide skill list, no editing of derived values.
- **Gates** are complete. Also add the 2B lesson: the Windows checklist should include a quick check that **staged markers remain visible on the selected row** (§4).

---

## 9. Summary for the user

The plan is sound and complete in scope. Before implementation is accepted, it must add:
1. **Staging-time preflight** of backend rules, so no edit can be staged that will later block the export.
2. **Key-carrying rows and editors**, never identified by display text.
3. **The equipment ↔ movement cap dependency.**
4. **Symmetric stance handling and display.**
5. **Honest SoL display.**

It also needs the precise rules from §1: learnable skills come from the save, missing relationships can't be created, and SoL is refused when modifiers apply. Move SoL to C2.
