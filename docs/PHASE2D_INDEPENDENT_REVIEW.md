# Phase 2D Independent Review — Plan, Architecture and Efficiency

_Independent review by Claude (Anthropic), 27 October 2026. Baseline `main` @ `64dc15c` (Phase 2C merged; `feature/phase2d-ux-and-deletion-parity` currently identical). Review only: no code was modified, committed or branched._

**Evidence base:**
- source reading of all core and Qt modules;
- the full suite run 5× with `run_headless_tests.py`: **309 tests OK every time, no shutdown crash**, so the 2C flaky-segfault fix holds; CI green on `64dc15c`;
- targeted probes of the deletion engine against synthetic saves;
- a parse/timing measurement on a 7.3 MB save;
- FreeCol source at `1690a5f` for role semantics.

---

## Verdict: PASS WITH CAVEATS — with a hard gate

The four-checkpoint shape is right, and the 2C review findings (default-role count, phantom movement edit, docs, flaky CI) are all fixed on `main`. However, **the deletion engine is not ready to be exposed more widely**:
- I found a confirmed corruption path (§1.1);
- the engine allows a colony to be emptied of all its units (§1.2).

So:
- **2D-1 (UX) may start now**, ideally together with the editor consolidation in §4.
- **No deletion UI (2D-2 onward) until a new checkpoint "2D-0 — deletion engine hardening" is done and accepted.**

---

## 1. Critical findings in the deletion engine (must fix before 2D-2)

### 1.1 Self-closing tags make deletion remove unrelated data (confirmed corruption path)

`deletion_engine._element_spans()` and `_remove_native_unit()` find an element's end by searching for the next `</unit>` (or `</indianSettlement>`, `</aiUnit>`) after the start tag. They never check whether the start tag itself is self-closing (`<unit … />`).

**Probe:** a save where the target unit is written as `<unit … />` and a later unit uses an explicit `</unit>`. Calling `remove_unit(xml, 'unit:21')` returned "successfully" but removed **`unit:21`, `unit:22`, `unit:23`, `unit:30`, `indianSettlement:1` and `tile:2`**. Everything between the self-closing tag and the next `</unit>` was gone.

The result still parsed, and the engine's final check (`uid` no longer referenced) passed, so `produce()` would have written it.

- **Reachability:** FreeCol's own writer emits explicit closing tags for units as far as we know, which is why the Tk deletions tested in-game were fine. But the engine must not depend on that, especially for **cached copies**, which can be small or empty elements, and for **colony deletion**, which will remove much larger subtrees.
- **Fix:**
  1. Detect a self-closing start tag and use its own end as the span end (or refuse).
  2. **Add an exact-removal guard to every destructive operation:** compare the set of id-bearing elements (and ideally a per-element attribute hash) before and after. Assert that the removed set equals exactly the planned set (target, its `aiUnit`, `ownedUnits` entries, planned cached copies) and that **every other element is unchanged**. This one generic guard would have caught §1.1 and will protect colony deletion.
  3. Add tests with self-closing, explicit-closing and mixed forms.

### 1.2 Deleting a colony's last unit is allowed (confirmed)

`remove_unit()` accepts any unit whose parent is a `building` or `colonyTile`. Probe: deleting all four workers of a colony in turn succeeded and left a colony with **0 units**, still claiming `sonsOfLiberty="50" tories="2"`. A FreeCol colony must have at least one unit, so this state is invalid.

**Fix:**
- Refuse deletion of the last unit inside a colony, counting the **whole staged set**: two staged deletions can together empty it, and preflight already evaluates the whole set.
- Point the user to colony deletion (2D-4) instead.
- Also decide whether to recompute or flag the colony's SoL/tories after a worker is deleted. FreeCol likely recalculates at the next turn; verify that in the roundtrip test.

### 1.3 Unit-deletion coverage is narrower than "any unit" suggests

`remove_unit()` only accepts units directly on a tile, in a colony, a colony tile or a building. It refuses:
- units in Europe;
- units aboard ships;
- carriers with passengers or cargo;
- units with any unknown reference (e.g. teacher/student links, other units' destinations, trade routes).

That fail-closed behaviour is correct. But 2D-2 must **state the supported coverage explicitly**, show a clear refusal reason in the UI, and test each refusal class. Otherwise "delete units of any nation" will look broken in Windows testing.

### 1.4 Two native-unit deletion implementations

Native units can be deleted either via `remove_unit(…, allow_settlement=…)` (key `deleteUnit`) or via `edit_backend._remove_native_unit()` (key `deleteNativeUnit`). They have different checks and different span code, and both contain the §1.1 weakness. 2D-2 should converge on one implementation, keeping the Tk keys readable for compatibility.

---

## 2. Part A — the proposed Phase 2D plan

### 2.1 Sequencing

| Proposed | Assessment |
|---|---|
| 2D-1 UX (Stage Change, instructions, source labelling) | ✅ Appropriate first. **Do it together with the editor consolidation (§4.1).** Relabelling the 8 stage-button sites by hand would add to the duplication. |
| *(missing)* | **Add 2D-0 — deletion engine hardening** (§1.1, §1.2, §1.4) plus a `plan_unit_deletion()` impact API, mirroring `plan_settlement()`. It must be accepted before any deletion UI. 2D-1 and 2D-0 can run in parallel. |
| 2D-2 Unit deletion | ✅ After 2D-0. Add **O5** (destructive actions visually separate and confirmed): it's a Should in the accepted matrix and is missing from the proposal. |
| 2D-3 Native settlement deletion | ✅ Parity port. Note that `plan_settlement()` refuses villages containing another nation's unit ("Mixed owner units"), e.g. a European missionary. That's accepted Tk behaviour, but explain it in the UI alongside the cached-missionary refusal. |
| 2D-4 European colony deletion (separate branch and gate) | ✅ Agree with the separate branch. Precede the coding with a **written dependency matrix from real saves** (§2.3), reviewed before implementation. |

### 2.2 Scope gaps to add to the plan

1. **O5 confirmation design.** One shared confirmation dialog fed by the engine's impact plan. It names the owner nation, the units, AI records, cached copies and claimed tiles affected, with Cancel as the default.
2. **Staged-deletion presentation.** A unit or settlement staged for deletion must be **marked** in every view (workspace row, Overview, the colony tabs that list it, and the Staged Changes panel as "Delete … (owner)"). It must not silently vanish or look unchanged. Undo restores it.
3. **Interaction with existing staged edits.**
   - Refuse deleting a record that has staged edits (and the reverse); `produce()` and preflight already do this.
   - Refuse a colony deletion while edits to its goods, SoL or workers are staged.
   - Show the reason before staging.
4. **Route all deletion staging through `stage_checked()`.** Every deletion key already passes through `change_field()`, so preflight works. Tk's `EditSession.stage_*_deletion()` methods do **not** preflight and should not be reused by Qt.
5. **Cached-missionary refusal.** It stays intact and deferred to after 1.0, as decided. Add one test asserting the refusal message, so a future refactor can't silently "fix" it into a wrong deletion.

### 2.3 European colony deletion (2D-4): dependencies to research and test

In addition to the items already listed in `PHASE2_DEVELOPMENT_PLAN.md` (cached copies, AI state, tiles, units, last colony):

- **What stays on the tile needs no move.** Units standing on the colony's tile (stationed soldiers, wagons, ships in port) are XML children of the `<tile>` with `location="tile:…"`, so they remain valid when the `<colony>` element is removed. Workers inside `building` and `colonyTile` must be **deleted with the colony**, or else moved, which is a new operation class (not pure removal) and should be deferred. Recommend: delete workers, keep tile units, refuse if anything else references the colony.
- **External references to search for and refuse or clear:**
  - any unit's `destination`, `entryLocation` or `location` pointing to the colony, its buildings or its colony tiles (including other players' units);
  - trade-route stops;
  - AI records such as `aiColony`, goods wishes, tile-improvement plans and transport missions;
  - the colony tile's `owningSettlement` and the ownership of worked tiles;
  - model messages and history entries referencing the colony id;
  - REF and intervention targeting.
- **Game-level consequences:**
  - a player's last colony (a human player may be declared defeated; an AI nation may be destroyed, with events);
  - player score;
  - Founding Father effects that depend on colony count.

  Research these in FreeCol's server code, and roundtrip-test them for both human and rival.
- **Performance.** `remove_settlement()` calls `remove_unit()` once per unit, and each call re-parses the whole save and rebuilds a parent map. Colony deletion with many workers must not repeat that pattern (§3.4).

---

## 3. Part B — code efficiency and architecture audit

### 3.1 Duplication

| Issue | Where | Assessment |
|---|---|---|
| **8 stage-button sites** | `qt_overview_panel.py` `_render` (lines ~238, 319, 380), `qt_detail_tabs_view.py` `update_detail_tabs` (~101, 139, 205, 270), `qt_diplomacy_view.py` `populate_diplomacy` (~64) | **Unnecessary duplication, not separation of concerns.** Each site rebuilds the same pattern: holder widget, `QHBoxLayout`, editor, `QPushButton('✎')`, a lambda capturing the record id, field and editor, the same green/blue stylesheet strings (copied in 6 places), and a "was X" or staged-status label. Placement differs legitimately; construction does not. |
| **Two equipment editors that have already diverged** | `qt_overview_panel._render` (Unit Overview) vs `qt_detail_tabs_view.update_detail_tabs` (Stationed units) | Different role labels ("Unequipped colonist" vs "Unequipped"; "Equip with Tools (Pioneer)" vs "Pioneer (tools)"). Different tools display (label vs spin-box suffix). The Hardy Pioneer suggestion exists in only one. Duplicated `sync_count`/`sync_role` logic. **This is where the next behavioural bug will come from.** |
| Role display names | 3+ places, including the Staged Changes panel | Should be one table in `presentation.py`. |
| Two staging paths | `EditSession.stage()` (Tk, no preflight) vs `edit_preflight.stage_checked()` (Qt), which bypasses `stage()` and rewrites `session.edits` directly | Two invariant sets for one state object. Move preflight into `EditSession` (e.g. `stage(key, original, new, xml_bytes=…)`) so there's one path. |
| Duplicated validation | `edit_preflight.preflight()` and `edit_backend.produce()` both implement the unknown-goods, reciprocal-stance and delete/edit-conflict checks | Extract one `validate_edit_set()` used by both (also noted in the 2C review §4.1). |
| Alarm editor counterpart mapping | `qt_detail_tabs_view.update_detail_tabs` uses `colonial[row]`, i.e. the table row matched against the source order of `settlement_alarm_rows()` | Positional coupling across modules. It's safe only while the table is filled unsorted. Carry the counterpart id in the row data, as diplomacy does. |

### 3.2 Large functions with too many responsibilities

| Function | Lines | Responsibilities mixed |
|---|---|---|
| `qt_overview_panel.OverviewPanel._render` | **308** | layout reflow, section grouping, icons, and *six* different inline editors (gold/tax/XP/moves/SoL, skill, equipment), each with its own signal wiring |
| `qt_detail_tabs_view.update_detail_tabs` | **272** | tab visibility, table filling for 7 sections, and 4 inline editor types |
| `qt_readonly.QtExplorer.__init__` | 243 | whole window construction |
| `qt_readonly.QtExplorer.populate` | 171 | branching over all groups, presentation roles, staged markers, national-goods projection |
| `qt_navigation_builder.install_navigation` | 129 | acceptable (one responsibility, declarative) |

`qt_readonly.py` (1,021 lines) is also **misnamed**: it is now the editor. It contains 54 function-local imports (`from edit_backend import …` inside methods), which hide its real dependencies.

### 3.3 Overengineering

Little. The model/proxy, preflight and session layers each earn their keep, and nothing looks like an abstraction for its own sake. The risk is the opposite: **under-abstraction in the view layer** (§3.1). One deliberate trade-off to keep: byte-level regex XML editing in `edit_backend` preserves the original file byte-for-byte outside the edited spans. It is correct to keep, but it is only as safe as its verification (§1.1).

### 3.4 Performance

Measured on a 7.3 MB synthetic save (typical real saves are several MB):

| Stage action | Staged edits in session | Full XML parses | Time |
|---|---|---|---|
| gold | 1 | 3 | 0.60 s |
| goods | 2 | 3 | 0.62 s |
| SoL | 3 | 4 | 0.70 s |
| stance | 4 | 5 | 1.04 s |
| experience | 5 | 5 | 1.09 s |

- **Every stage replays the whole staged set**, and several `change_field` branches re-parse the full XML per edit (`change_native_field`, `change_equipment`, `change_colony_sol`, movesLeft, plus `ordered_edits_for_application`). The cost per stage grows with the number of staged diplomacy, equipment and SoL edits.
- **Deletions are heavier:** `remove_unit` parses the full XML twice and builds a parent map of the whole tree, and settlement deletion repeats that per unit.
- **After each stage, `refresh_staged_view()` rebuilds the whole workspace** (`populate()`), the detail tabs and the Overview.

Acceptable today, but it will become noticeable with 2D's multi-unit and colony deletions.

**Fix during 2D:**
- parse once per preflight and pass the parsed root (or an index) to the field handlers;
- give `remove_unit`/`remove_settlement` a shared parsed context;
- keep the final `produce()` independent for safety.

### 3.5 Obsolete code from the Tk-to-Qt migration

- `freecol_explorer.py` (1,041 lines, Tk), `map_window.py` and `terrain_art`'s Tk adapter: frozen, needed until Phase 3. Keep.
- `EditSession.stage_equipment`, `stage_unit_deletion`, `plan_settlement_deletion` and `stage_native_unit_deletion` are now **Tk-only**. Keep them for Tk, but don't extend them; Qt should use the preflighted path.
- **Source-text tests remain:** about 93 literal-source assertions across `test_qt_shell_contract.py` (55), `test_qt_phase1_exit_audit.py` (14), `test_qt_goods_drilldown_contract.py` (12) and `test_qt_father_view_contract.py` (12). They will break on the §4.1 refactor. Replace each one touched with behavioural off-screen tests as part of 2D-1, rather than editing strings to match.

### 3.6 Consistency, maintainability, testability

- **CI is now stable:** `run_headless_tests.py` performs explicit Qt teardown and keeps real crashes visible (5/5 clean runs). Good fix.
- **Core and UI separation is strong:** `save_document`, `edit_session`, `edit_backend`, `edit_preflight`, `presentation` and `deletion_engine` are UI-free and well tested.
- **The weakest testability is in the two giant render functions:** editors can only be reached by building the whole panel.

---

## 4. Part C — recommendations

### 4.1 Architectural change before expanding destructive editing

1. **Deletion engine hardening (2D-0):** self-closing handling, the exact-removal diff guard, last-unit refusal, a single native-unit path and a `plan_unit_deletion()` impact API.
2. **A small shared inline-editor kit**, built as part of 2D-1, for example:
   - `StageField` (line edit + labelled **Stage Change** button + "was X" / staged status + shared styles), with the record key, field and original captured at construction;
   - `StageChoice` (combo + button);
   - **one** `EquipmentEditor` widget used both in Unit Overview and Stationed units, with the role labels taken from `presentation.py`.

   Each placement stays in its own view module; only construction is shared. This turns the 2D-1 relabelling into one change, removes the equipment divergence, and makes the editors testable in isolation. **Do not** merge the domain rules into the widgets: validation stays in `EditSession`, preflight and the backend.
3. **One staging path:** preflight moves into `EditSession`, and Qt calls only that path.

### 4.2 Prioritised issue list

| # | Issue | File / function | Class |
|---|---|---|---|
| 1 | Self-closing span sweep; no exact-removal verification | `deletion_engine._element_spans`, `remove_unit`, `remove_settlement`; `edit_backend._remove_native_unit` | **Fix before 2D** (2D-0) |
| 2 | Last colony unit deletable | `deletion_engine.remove_unit` | **Fix before 2D** (2D-0) |
| 3 | Two native-unit deletion paths | `deletion_engine.remove_unit(allow_settlement)` vs `edit_backend._remove_native_unit` | **Fix before 2D** (2D-0) |
| 4 | 8 duplicated stage sites; two divergent equipment editors | `qt_overview_panel._render`, `qt_detail_tabs_view.update_detail_tabs`, `qt_diplomacy_view.populate_diplomacy` | **Fix during 2D** (2D-1, together with the labelled buttons) |
| 5 | Two staging paths | `edit_session.EditSession.stage` vs `edit_preflight.stage_checked` | **Fix during 2D** (before deletion staging) |
| 6 | Duplicated edit-set validation | `edit_preflight.preflight` vs `edit_backend.produce` | **Fix during 2D** |
| 7 | O5 confirmation and staged-deletion markers missing from the plan | plan / new shared dialog | **Fix during 2D** (2D-2) |
| 8 | Repeated full parses per stage and per deletion | `edit_preflight`, `edit_backend.change_*`, `deletion_engine` | **Fix during 2D** (before 2D-4) |
| 9 | Alarm counterpart mapped by row position | `qt_detail_tabs_view.update_detail_tabs` | **Fix during 2D** |
| 10 | Source-text tests (about 93 assertions) | four `test_qt_*contract*` / audit files | **Fix during 2D** (as touched) |
| 11 | `_render` (308 lines), `update_detail_tabs` (272), `populate` (171) | Qt views | Fix during 2D as far as item 4 allows; **rest Defer to 0.9.0** |
| 12 | `qt_readonly.py` misnamed; 54 inline imports | `qt_readonly.py` | **Defer to 0.9.0** (rename with a compatibility shim at packaging) |
| 13 | Role labels in several places | Qt views, staged panel | Fix during 2D (with item 4) |
| 14 | Tk-only `EditSession` APIs | `edit_session.py` | **Defer to 0.9.0** (retire with Tk after Phase 3) |

### 4.3 Maintainability / architecture rating: **6 / 10**

- **For it:**
  - a genuinely good layered core: UI-free save model, session, preflight, backend and deletion engine, all well tested;
  - a stable 309-test CI;
  - consistent fail-closed design;
  - honest documentation.
- **Against it:**
  - the Qt view layer has grown by accretion: two functions of about 300 lines, duplicated editors that have already diverged, two staging paths, duplicated validation;
  - the destructive engine relies on byte spans with verification too weak to catch collateral removal.

The core would merit an 8. The view layer and the deletion verification pull it down. Items 1–6 above would bring it to about 7.5 before colony deletion.

---

## 5. Summary

The plan is right in shape and order but needs one inserted checkpoint:

- **2D-0, deletion engine hardening,** gating all deletion UI:
  - fix the self-closing-tag sweep and add an exact-removal guard (confirmed corruption path);
  - refuse a colony's last unit;
  - unify native-unit deletion.
- **2D-1** should build a small shared editor kit, rather than relabelling eight hand-built button sites.
- **Add to the plan:** O5 confirmations, staged-deletion markers and explicit coverage statements.
- **Before colony deletion:** a written dependency matrix from real saves.
