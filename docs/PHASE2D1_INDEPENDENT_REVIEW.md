# Phase 2D-1 Independent Code Review

_Independent review by Claude (Anthropic), 27 October 2026, of `feature/phase2d-ux-and-deletion-parity` at **`5e3b4bb`** (draft PR #7; 46 commits ahead of `main` @ `64dc15c`). Scope: the completed 2D-1 implementation only. 2D-0, 2D-2, 2D-3 and 2D-4 appear here only as plans. No application code was changed by this review._

---

## 1. Executive verdict: **PASS WITH CAVEATS — not yet ready for integration**

- **Data integrity: no defects found.**
  - Staging never touches the source XML.
  - Save As is unchanged.
  - The 2C combined-export regression produces exactly the same diff as at 2C.
  - The deletion engine and the Tk editor are untouched.
  - **2D-1 does not worsen the 2D-0 deletion risks.**
- **Presentation correctness: four confirmed defects** in exactly the features this checkpoint delivers, all small to fix:
  - the "source" Inspector shows staged values;
  - role highlighting gives false signals;
  - unit artwork is wrong for several common units;
  - a display-only lookup can make a save unopenable.
- They don't endanger saves, but they contradict what the UI tells the user. Fix M1–M4 (§3) and do a focused Windows recheck before merging.

**Evidence base:**
- Full suite run twice: **320 tests OK**, 1 expected skip, clean exit both times.
- CI `headless` green on `5e3b4bb`.
- Live off-screen Qt probes on synthetic saves with a real embedded ruleset, using realistic FreeCol `role`/`roleCount` attributes.
- Re-run of the 2C combined edit/export/attribute-diff harness.
- Comparison with FreeCol's own image mapping, `data/default/resources.properties` at `1690a5f` (FreeCol 1.2.0).

---

## 2. Critical findings (must fix before merge)

**None.** No defect found that corrupts data, writes to the source save, or makes currently exposed functionality unsafe.

---

## 3. Major findings (should fix before merge)

### M1 — "Details (source)" Inspector shows staged values (confirmed)

**Requirement C:** Inspector Details and Raw XML are labelled as original/source values excluding staged changes (`qt_readonly.py`: tab texts "Details (source)" and "Raw XML (source)", plus `inspector_source_notice`).

**Defects:**
- `qt_readonly.py` ~line 1001 (`inspect()`, Players branch) builds **Gold** from `self.session.staged_value((id, 'gold'), …)`.
- **Live probe:** gold staged 7225 → 9999. Details showed **9999**; the source value 7225 appeared nowhere.
- Tax in the same block shows the source value, so the panel is internally inconsistent too.
- `qt_diplomacy_view.inspect_diplomacy` (~lines 103–110) shows staged **Stance** and **Tension** (deliberately, from 2C) under the same "source" Details tab.

**Fix:**
- Make Details strictly source: use `element.get('gold')`, and the source stance and tension.
- If staged values are useful there, add a separate, clearly labelled "Staged: …" line, as the Overview does.

**Tests:** for player gold/tax and diplomacy, after staging, assert that Details contains the source value and not the staged one.

### M2 — Role highlighting falsely signals "no pending change" (confirmed)

`qt_readonly.populate()` (~line 839–848) decides the Units-table role marking by comparing **role ids** (`effective_role != actual_role`). It only runs for a non-default effective role. **Live probe** (realistic `role`/`roleCount`):

| Staged change | Expected | Actual |
|---|---|---|
| Pioneer 100 → 80 tools (same role, different count) | staged marker | **amber "existing equipment"**: falsely says nothing is pending |
| Dragoon → unequipped | staged marker | **no marker at all**: the staged unequip is invisible in the table |
| Unequipped → Soldier | staged marker | staged marker ✅ |

**Fix:**
- Drive the staged marker from the session key: `self.session.is_changed((unit_id, 'equipment'))`.
- Apply the amber "equipped" style only when there is no staged equipment edit and the source role is not default.

**Tests:** cover all three rows above, plus undo.

This matters beyond 2D-1: **2D-2 will add staged-deletion markers**, which must follow the same rule ("marker = staged key exists"), not inferred value differences.

### M3 — Role-aware artwork picks the wrong sprite for common units (confirmed against FreeCol's mapping)

FreeCol maps unit artwork explicitly, per unit type and role, in `data/default/resources.properties` (`image.unit.model.unit.<type>[.<role>]`). `qt_unit_icons.effective_icon` (line 79) instead guesses using `_local_image(role)`, with an index that also matches **bare filenames** (`_index_images`: `paths.setdefault(image.name.casefold(), …)`, where the first match in sorted path order wins). Compared with FreeCol 1.2.0's mapping:

| Unit / role | FreeCol shows | Editor shows |
|---|---|---|
| Seasoned Scout, scout | `scout/seasonedScout.png` | `scout/scout.png` (generic): **specialist lost** |
| Veteran Soldier, soldier | `soldier/veteranSoldier.png` | `soldier/soldier.png` (generic): **specialist lost** |
| Hardy Pioneer, pioneer | `pioneer/hardyPioneer.png` (with tools) | `civilian/hardyPioneer.png` (unequipped variant) |
| Free Colonist (or any non-specialist), dragoon | `dragoon/dragoon.png` | `civilian/freeColonist.png`: **no dragoon at all** |
| Jesuit Missionary, missionary | `missionary/jesuitMissionary.png` | `missionary/missionary.png` (generic) |
| Brave, default | `civilian/brave.png` | `armedBrave/brave.png` (the first `brave.png` in sorted order). *Pre-existing since Phase 1 (`f047d5d`), not new in 2D-1* |

The Hardy Pioneer special case fixed one symptom of this general cause, and picked the unequipped variant.

**Fix (simpler and authoritative):** read `resources.properties` from the user's installed FreeCol (already located by `freecol_art_source`). Resolve `image.unit.<unitType>.<roleSuffix>`, fall back to `image.unit.<unitType>`, then to the neutral fallback. This removes every special case and the bare-filename index. Native variants (`.native`) and native roles (`armedBrave`, `mountedBrave`, `nativeDragoon`) come for free.

**Tests:** a fixture `resources.properties` plus a fake image tree covering the table above.

### M4 — A display-only building-name lookup can make a save unopenable (confirmed)

`location_names.colony_building_names` (line 31) **raises `ValueError`** when the same building id maps to two colonies. It runs inside `SaveDocument.load()`, so the **whole save fails to open**. Probe: a second colony reusing `building:1` produced *"SAVE CANNOT BE OPENED: Ambiguous building location building:1"*.

Refusing to guess is right, but refusing the whole save over a display label is disproportionate, and a regression from Phase 1/2C, where such a save opened.

**Fix:** exclude ambiguous ids from the map, so they fall back to the raw id or another resolution. Optionally record them in a document-level diagnostics list. Test that a save with a duplicate building id opens, and that the affected units show the raw id.

The rest of the mapping is sound:
- it covers only authoritative `./map/tile/colony` (cached copies excluded);
- it uses `colony.iter('building')`;
- it is checked before other location sources;
- it is also used by `SaveDocument.location_name`, so all unit lists benefit;
- "aboard" chains pass the map through recursion;
- the original XML `location` values are untouched.

---

## 4. Minor findings (polish and maintainability)

1. **Colour convention is inconsistent across surfaces.**
   - Editors: **blue = editable**, **green = staged** (`qt_stage_controls.style_stage_choice`, inline numeric editors).
   - Workspace table: **blue (`#DCEEFF`) = staged** and **amber (`#FFF0C9`) = existing equipment** (`qt_record_table_model.data`, lines ~43–45).

   So the same blue means opposite things a few centimetres apart. Choose one meaning per colour, and keep all hex values in one small theme module. They are currently spread over `qt_stage_controls.py`, `qt_overview_panel.py` (~271–273), `qt_detail_tabs_view.py` (~101–103, ~189–191) and `qt_record_table_model.py`.
2. **The numeric field kit was not built.** Only `StageChangeButton`, `style_stage_choice` and `EquipmentEditor` were extracted. The 3 numeric inline-editor sites still each build their own holder, layout, line edit, stylesheet string and "was X" label. That's acceptable for 2D-1, but it's the remaining half of the duplication item from the 2D review.
3. **Role terminology is not centralised** (the plan said "in `presentation.py` as appropriate"):
   - `qt_equipment_editor.ROLE_LABELS` says "Unequipped colonist", while the Staged Changes panel uses `presentation.readable`, giving **"Default (roleCount: 0)"**;
   - the "20 tools per count" knowledge is in two places (`qt_equipment_editor` `update_display`/suffix and `qt_staged_changes_panel`);
   - 50 muskets / 50 horses / 20 tools are hard-coded, although the ruleset's role definitions state the required goods.

   Move the labels and quantity formatting into `presentation.py` (ideally derived from the ruleset) and use them in both places.
4. **Combo stylesheet has no state rules.** `style_stage_choice` sets the border, background and a fixed text colour, but no `:disabled` or `:focus` rules. A disabled combo (e.g. "No eligible roles…") looks exactly like an editable one. Add `QComboBox:disabled { … }` (greyed) and a visible focus border. Windows visuals were accepted, so treat this as polish.
5. **The equipment status tooltip leaks internals.** `qt_equipment_editor.update_display` shows `str(planned)`, e.g. `('model.role.pioneer', 4)`. Use the readable formatter from item 3.
6. **Equipment editor cost.** `EquipmentEditor.__init__` runs `validate_equipment` for 5 roles, each traversing the whole document (`root.iter('role')`, `iter('unit-type')`, `movement_cap`), plus another full `root.iter('role')` for `limits` (line 56). **Measured: about 77 ms per editor on a 7.3 MB save.** A colony with 15 stationed units therefore adds about 1.2 s to every refresh after each stage. Cache the ruleset's role and unit-type definitions once per `SaveDocument`. This fits the 2D performance item already scheduled before 2D-4.

---

## 5. Regression risks and missing tests

**Tests added in 2D-1 are good in kind.** Of the 6 changed test files, 5 are behavioural or off-screen Qt tests. One source-text assertion was *removed* in favour of model-level tests. Good direction.

**Missing tests:**
- M1: Details shows source values after staging (players, diplomacy).
- M2: role-marker matrix (same role/different count, unequip, equip, undo; survives sort/filter).
- M3: artwork resolution against a fixture `resources.properties` (the table in M3).
- M4: a save with an ambiguous building id still opens.
- Enter-to-stage on **each** line-edit site, and that a Stage Change button stages only its own key (one probe per view).
- Disabled-state rendering of styled combos (at least `isEnabled()` paired with a visual distinction).

**Regression risk:** low for data, moderate for perception. M1 and M2 can lead a user to believe an edit is (or isn't) pending.

---

## 6. Architecture assessment

- **`StageChangeButton`** (`qt_stage_controls.py`): right size; presentation only; accessible name and tooltip set once. ✅
- **`EquipmentEditor`** (`qt_equipment_editor.py`): a genuine consolidation.
  - The two previously divergent copies (about 100 lines each in `qt_overview_panel._render` and `qt_detail_tabs_view.update_detail_tabs`) are gone, and both contexts now behave identically: Hardy Pioneer suggestion, `roleCount=0` for default, 20–100 tools, wheel-safe controls, status.
  - Validation stays in `equipment_rules`, and staging stays in `stage_unit_equipment`.
  - It emits `stage_requested(uid, role, count)` with the unit id captured at construction, so identity is bound correctly.
  - It is rebuilt from session state on every render, so the two contexts stay synchronised by construction.
  - No stale-signal or re-entrancy problem was found: the old widgets are released through Qt's `setCellWidget`/layout replacement, and the 2C detach-before-delete fix is still in place.
- **Remaining duplication:** the numeric editor sites, colour constants and role terminology (§4.1–4.3).
- **Coupling:** no new backend-to-UI coupling. `location_names` and `save_document` stay UI-free. `qt_unit_icons` depends only on the art source.
- **Answers to the brief's questions:**
  1. Duplication genuinely eliminated for equipment; role labels and quantity calculations are still replicated (§4.3).
  2. Original/proposed/exported states: not everywhere (M1, M2).
  3. Stale widgets/signals: none found.
  4. Realistic nesting: fine; uncommon structures: M4.
  5. Specialist identity: no (M3).
  6. Colours and typography: inconsistent (§4.1).
  7. Tests: mostly behavioural ✅.
  8. Regressions: none in data or accepted workflows; M4 is a narrow load regression.
  9. Dependencies and performance: no new dependencies; performance §4.6.
  10. Risk for 2D-0/2D-2: the marker logic (M2) must become key-based before deletion markers are added.

---

## 7. Non-regression and data integrity

| Check | Result |
|---|---|
| Source XML never mutated by staging | ✅ (2C harness: loaded tree and source `.fsg` unchanged) |
| Save As non-destructive | ✅ (existing-path refusal unchanged; other archive members byte-identical) |
| 2C combined export | ✅ **Identical attribute diff to the 2C review**: only the intended gold/tax/XP/role/movesLeft/goods/SoL/diplomacy/skill changes |
| Proportional movement on role change | ✅ (dragoon → soldier 12 → 3; soldier → dragoon 3 → 12) |
| `roleCount=0` for default | ✅ (editor range 0–0; backend normalisation from 2C intact) |
| Deletion engine | Untouched by 2D-1. The 2D-0 risks are **unchanged, not worsened** |
| Tk editor | Untouched |
| Test suite / CI | 320 OK (2 local runs, clean shutdown); CI green on `5e3b4bb` |

---

## 8. Recommended corrective actions, in priority order

1. **M1** Inspector Details strictly source (players, diplomacy), plus tests.
2. **M2** key-based staged markers for equipment, plus the marker matrix tests. This is the same rule that 2D-2's deletion markers will use.
3. **M4** non-fatal handling of ambiguous building ids, plus a test.
4. **M3** artwork resolution via FreeCol's `resources.properties`, plus fixture tests. It also fixes the pre-existing brave issue.
5. Focused Windows recheck of M1–M4 on the corrected head; green CI on that exact SHA.
6. (During 2D, not blocking) §4.1 colour convention and theme module, §4.3 central role terminology, §4.4 combo states, §4.5 tooltip, §4.6 ruleset caching, §4.2 numeric field kit.

## 9. Final recommendation

**Not yet ready for integration.** Merge Phase 2D-1 after M1–M4 are corrected with tests, CI is green on the corrected head, and the user has passed a short focused Windows recheck: Inspector source values, role markers for the three equipment cases, artwork for Seasoned Scout / Veteran Soldier / Hardy Pioneer / colonist dragoon, and opening the user's normal save. No new data-integrity or deletion-safety risk was introduced, so 2D-0 can proceed in parallel.
