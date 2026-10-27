# Phase 2C (C3) Independent Code and Documentation Review

_Independent review by Claude (Anthropic), 27 October 2026, of `feature/phase2c-editing-parity` at `068a0cd` (draft PR #6; 124 commits ahead of `main` @ `e75c14e`, 0 behind; required `headless` check green on that commit). Review only: no application code was changed._

## Verdict: PASS WITH CAVEATS

The C1–C3 fixes have landed well. Every non-destructive edit type stages, refuses and exports correctly, and a combined export changes **exactly** the intended attributes and nothing else.

**Two confirmed defects** and **one documentation gap** should be fixed before merging (§3). On the FreeCol movement anomaly, nothing in the 2C code or the evidence implicates the Phase 2C editor. One provenance check is still recommended before calling it a pure FreeCol bug (§5).

---

## 1. What was verified

| Check | Result |
|---|---|
| Local suite (`QT_QPA_PLATFORM=offscreen python -m unittest discover`) | **303 tests OK**, 1 expected skip |
| CI | Required `headless` check **green** on `068a0cd` |
| Code review | `edit_backend.py` (proportional movement, ordered application), new `edit_preflight.py`, `presentation.py`, and the Qt editors in `qt_readonly.py`, `qt_overview_panel.py`, `qt_detail_tabs_view.py`, `qt_diplomacy_view.py`, `qt_equipment_controls.py`, `qt_staged_changes_panel.py`, `qt_record_table_model.py` |
| Identity binding | Every new editor captures its record id, field and source original in its signal lambda at creation, and stages only on Enter or button click (no focus-out commits). The goods editor carries the full goods-type id. Diplomacy rows carry owner and counterpart in item data. ✅ |
| Preflight | `stage_checked()` / `unstage_checked()` run the real backend `change_field()` chain (same order as `produce()`) on an in-memory copy before the session changes. `produce()` remains the final authority. ✅ |
| FreeCol source | Checked against FreeCol `1690a5f` (`Unit.java`, client `InGameController.java`) for role semantics and goto/move handling. |

### Live end-to-end test (real Qt window, off-screen)

**Fixture.** A synthetic save with a **real embedded ruleset**:
- unit types with movement and abilities;
- roles with `maximum-count` and dragoon/scout movement bonuses;
- goods types;
- reciprocal stances, tensions and native alarms;
- a colony whose SoL matches the standard formula;
- authoritative settlements with `lastTribute` and `convertProgress`;
- an extra archive member.

**Staging results.**
- **Players:**
  - gold and tax staged;
  - native tax and native (sentinel) gold refused;
  - tax 101 refused.
- **Units:**
  - XP staged on own and rival units; XP 201 refused;
  - moves 2 staged on a soldier; moves 5 refused with the backend cap message;
  - **dragoon → soldier** staged, with export writing `movesLeft` 12 → 3;
  - **soldier → dragoon** after a staged moves value of 2 produced (3, 8), proportional;
  - the explicit override of 3 (equal to source) afterwards was **retained** as (3, 3). This was the C3 fix.
- **Equipment refusals:** pioneer × 6 refused (ruleset maximum 5); native brave refused.
- **Colony:**
  - goods: existing 30 → 250, **absent → 50 (created)**, food 120 → 0; −1 refused;
  - SoL 50 → 75 staged; 101 refused.
- **Diplomacy:**
  - stance peace → war staged; the reverse direction refused; an invalid stance refused;
  - European tension, native tension and alarm staged;
  - an **absent alarm refused** up front.
- **Native skill:** a skill present in the save staged; a skill not taught in the save refused.

**Panel.** Staged Changes listed 16 readable entries, including *"Stance ⇄ Charles XI (both directions)"*.

**Export.**
- Source `.fsg` byte-identical; the other archive member byte-identical.
- An attribute-level diff of **every** id-bearing element and every stance, tension, alarm and goods entry showed **only** the intended changes:
  - SoL changed `liberty` 400→600, `sonsOfLiberty`/`oldSonsOfLiberty` 50→75 and `tories`/`oldTories` 2→1 (`productionBonus` correctly unchanged at 1);
  - both stance records changed;
  - no stray edits anywhere.
- 0 exceptions.

---

## 2. Bugs from the C2/C3 cycle: verification

| Reported issue | Status in code | Independent evidence |
|---|---|---|
| Native Tax shown/editable (C1-08) | Fixed: hidden in Overview and table (`N/A`), and refused in `stage_overview_edit` | Refused in live test |
| Workers tab reset after XP staging (C1-12) | Fixed: active tab restored after refresh | Covered by branch tests |
| National Goods ambiguity (C2-14) | Fixed: "Source → proposed" projection | See wording note §4.2 |
| Mouse wheel changing equipment (C2-F06) | Fixed: `WheelSafeComboBox` / `WheelSafeSpinBox` | Covered by branch tests |
| Diplomacy cell overpaint / sort (C2-F04) | Fixed: sort uses `SourceSortRole` source value | Covered by branch tests |
| **Movement override equal to source dropped after equipment (C3)** | Fixed in `edit_preflight.stage_checked` | **Reproduced the scenario live: override retained as (3, 3), exported correctly** |

---

## 3. Confirmed defects and gaps — fix before merge

### 3.1 Default role: spurious edit writing a role count FreeCol never produces (defect)

FreeCol always writes `role` and `roleCount`. For the default role the count is **0**: `Unit.changeRole()` forces `setRoleCount(role.isDefaultRole() ? 0 : roleCount)`.

The Qt role editors (`qt_overview_panel.py` and `qt_detail_tabs_view.py`) bound the count to `setRange(1, …)`, so "no equipment" is always staged as `(model.role.default, 1)`. Reproduced live with a Hardy Pioneer saved as `role="model.role.default" roleCount="0"`:
- Stage Pioneer × 4, then switch back to default: the session holds `((default, 0), (default, 1))` instead of dropping the edit.
- Choosing "default" on an **untouched** default unit also stages `((default, 0), (default, 1))`.
- Export would write `roleCount="1"` on a default-role unit, a state FreeCol itself never creates.

It's probably harmless in play, but it's an unintended edit, it inflates the pending count, and it's the kind of non-FreeCol state that muddies investigations like §5. **The Tk editor has the same behaviour** (`amount = 1` for non-pioneer roles).

**Fix (recommended in the shared layer, which also fixes Tk as an allowed bug fix):**
- normalise any `(model.role.default, n)` to `(model.role.default, 0)` when staging;
- compare against the original after normalising, so returning to default drops the edit;
- have `change_equipment` write `roleCount="0"` for the default role;
- add tests for default/0 → pioneer → default (no edit remains) and for "default" on an untouched unit (no edit).

### 3.2 Phantom movement edit after undoing equipment (defect, low severity)

In the C3 scenario (soldier → dragoon, explicit moves 3 = source → `(3, 3)`), **undoing the equipment** leaves `('unit:21','movesLeft'): (3, 3)` staged. It's a no-op that is still counted ("Save As (1)"), listed in the panel as *"Moves Left 3 → 3"*, and keeps the session dirty. Reproduced live via the panel's undo.

**Fix:** after any equipment unstage or restage, drop a dependent `movesLeft` edit whose new value equals its source original once no equipment edit remains for that unit. Add a test.

### 3.3 Shared backend change affects the frozen Tk editor (documentation gap)

`change_equipment()` in `edit_backend.py` changed from **clamping** remaining moves (`min(moves, new_cap)`) to **proportional** conversion. The backend is shared, so **Tk equipment exports now behave differently too**. Dragoon 12 → soldier still gives 3, but soldier 3 → dragoon now gives **12 instead of 3**, and 2 → 8 instead of 2.

The change is reasonable and consistent with Qt. However, the project rule is "Tk frozen, bug fixes only", so record it explicitly in the CHANGELOG as an intentional Tk-visible behaviour change, or confirm it with the user.

### 3.4 Parity matrix not brought to final state (documentation)

`docs/PHASE2C_PARITY_MATRIX.md` contradicts the code and the later sections of the same file:
- The header says *"C2 not yet accepted"*; the end of the file records C2 accepted.
- The table still shows **"Not started (C2)"** for Stance, Tension, Settlement alarm and Learnable skill, which are all implemented and tested. Most Windows/FreeCol cells still say *"Pending"* although C1, C2 and C3 were accepted.
- The **Colony goods** row has **8 cells for a 7-column table**, an extra "Pending", so it renders malformed.
- There is **no C3 section**: C3 acceptance and the movement-override fix appear only in `CHANGELOG.md`.

**Fix:** update every row to its final status with evidence references (commit, CI run, Windows test IDs, FreeCol roundtrip), mark the C1/C2 progress paragraphs as history, and add a C3 section.

---

## 4. Recommendations (not blocking)

1. **Remove duplicated validation.** `edit_preflight.preflight()` re-implements `produce()`'s pre-checks (unknown goods types, reciprocal stance duplicates, delete/edit conflicts). Extract them into one function used by both, so the two cannot drift.
2. **National Goods wording.** The Inspector text shows "Proposed total with staged edits: X" and then *"Staged warehouse edits are excluded until exported and reopened."* (`qt_readonly.py` ~line 931). This reads as contradictory. Suggest: *"Source total excludes staged edits; proposed total includes them."*
3. **Readable skill labels.** The Staged Changes panel shows learnable skills as raw ids (`model.unit.expertFurTrapper → model.unit.expertLumberJack`). Use `presentation.readable` as for other fields (O4: readable entries).
4. **Game-rule note: experience on role change.** FreeCol's `Unit.changeRole()` resets experience when switching to an *incompatible* role; the editor (Qt and Tk) does not. This is not save corruption, but record it as a known divergence, or adopt FreeCol's rule in a later phase.
5. **Preflight cost.** Each stage parses the whole XML several times. That was acceptable on the user's saves. Watch it if staging feels slow on very large saves.

---

## 5. FreeCol movement anomaly (`docs/FREECOL_MOVEMENT_DIAGNOSTIC.md`)

**Assessment: the diagnostic is careful and honest, and its conclusion holds.** The Phase 2C editor is not implicated.

- **The unedited control reproduces it.** The Hardy Pioneer cascade (260 `MOVE_NO_MOVES`) occurred on the control save, which 2C never touched. Removing three goto orders made 4/4 fresh runs clean. The 2C editor never writes destinations or goto orders.
- **2C writes only these unit attributes:** `experience`, `movesLeft`, `role`, `roleCount`. My attribute-level export diff confirms nothing else changes.
- **FreeCol's client code is consistent with a desync explanation:**
  - `moveTile()` marks a unit `SKIPPED` after a server rejection, specifically "so we do not end up retrying indefinitely";
  - `movePath()` treats a client-side `MOVE_NO_MOVES` as an expected stop.
  - A storm of server-side `MOVE_NO_MOVES` from one tile toward two alternating targets therefore suggests the **client and server disagree about the unit's remaining moves or the move cost**, while the client keeps re-entering the goto loop.
  - This matches the observed "1/1 before, 0/1 after" readings and the dependence on load order. The exact mechanism is still not established, as the document correctly says.

**One caveat before calling it a pure FreeCol bug: the control's provenance.** "Unedited" here means not edited in *this* test. The ongoing Danish game has been edited by the Tk editor in earlier versions (gold, XP, movement, equipment and deletions since 0.4–0.5.5), and FreeCol carries attributes such as `roleCount` forward unchanged through later saves. Defect §3.1 shows the editor *can* write states FreeCol never produces.

Two cheap checks would close this gap:
1. **Search the control save** (`savegame.xml` inside `Morten.fsg`) for `role="model.role.default" roleCount="1"`, or any non-zero `roleCount` on a default-role unit, especially unit `34454`. Finding none removes the most plausible editor-originated anomaly.
2. **Run a never-edited control:** start a fresh FreeCol game, never open it in the editor, give a pioneer and a lumberjack goto orders across rough terrain, save, then reload several times from a fresh start. A reproduced cascade there would prove it is a FreeCol bug.

If either check implicates an editor-written state, investigate it separately. Neither blocks the 2C merge.

---

## 6. Merge recommendation

Fix §3.1 and §3.2 (small, testable) and update the docs (§3.3, §3.4). Confirm green CI on the final head, do a quick Windows check of the default-role round trip, then merge PR #6 with a merge commit and tag `v0.6.2.6.4-phase2c`. §4 items and the §5 checks can follow without blocking.
