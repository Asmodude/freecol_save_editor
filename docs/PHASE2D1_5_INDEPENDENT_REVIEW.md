# Phase 2D-1.5 Independent Review

_Independent review by Claude (Anthropic), 27 October 2026, of `feature/phase2d1-5-component-performance` at **`3a5e7f5`** (draft PR #8; 37 commits ahead of `main` @ `9bf270b`, 0 behind). It answers `docs/PHASE2D1_5_INDEPENDENT_REVIEW_REQUEST.md`. Reviewer only: no application code was changed._

## Verdict: **PASS WITH CAVEATS**

- **No blockers. Data integrity is intact.**
- The shared numeric editor and the lazy rules index are correct, and the index produces **identical** validation results to the uncached path.
- The headline caveat is item 3 of the request: the hard-coded `_NON_EQUIPPABLE_TYPES` list is **safe but not the authority**. The B2 root cause has not been proven against a real save. Before merge, run the one-minute verification in §3.4 and record the result.

**Evidence base:**
- **CI:** push run #745 and pull_request run #746 both **green on `3a5e7f5`** (the exact head).
- **Local suite:** run twice with `run_headless_tests.py`, **336 tests OK** each time, clean exit.
- **Live off-screen Qt probes** on synthetic saves with an embedded ruleset and realistic `role`/`roleCount` and explicit closing tags.
- **Parity harness:** cached vs uncached validation.
- **2C combined-export regression harness**, re-run.
- **FreeCol `1690a5f` (1.2.0) sources:**
  - `data/rules/classic/specification.xml`;
  - `common/model/BuildableType.java` (`isAvailableTo`);
  - `common/model/Specification.java` (abstract types are not re-serialised).

---

## 1. Shared `NumericStageEditor` (request item 1) — PASS

`qt_numeric_stage_editor.py` (53 lines) now backs **Overview** (gold, tax, experience, movesLeft, SoL), **Colony Goods**, **Workers XP** and **Native Alarm**. Live probes with every table sorted **descending** before staging:

| Check | Result |
|---|---|
| Goods: Enter on the row showing "Tools" | staged exactly `(colony:1, model.goods.tools): (1100, 1500)` ✅ |
| Goods: Stage Change button on "Lumber" | staged exactly `(colony:1, model.goods.lumber): (50, 77)`; the Tools edit kept ✅ |
| Active tab after staging | stays **Goods** ✅ |
| Typing without staging | status "Not staged"; session unchanged ✅ |
| Workers XP (sorted) | staged on the unit shown in that row (`unit:13`) ✅ |
| Native Alarm (sorted) | staged on the correct directed relation (`indianSettlement:1`, `alarm|player:1`) ✅ |
| Source `.fsg` after all stages | byte-identical (SHA-256) ✅ |
| Exceptions | 0 ✅ |

- **Identity:** each integration binds the record id, field or goods type through lambda default arguments at construction and receives only the text. No widget references are captured, so no dangling callbacks are possible after rebuilds.
- **Semantics:** source and staged values are kept separate (`_committed` vs edit text). The "was X" label, or for Alarm the compact source tooltip, is shown only when staged. Validation stays with the callers (`stage_overview_edit`, `stage_colony_goods`, `stage_relation`). ✅
- **Width:** the Goods cell's minimum size hint (201 px) fits the column (289 px) at a 1400 px window. See §5.3 for narrow windows.

## 2. Lazy `EquipmentRulesIndex` (request item 2) — PASS

`movement_rules.EquipmentRulesIndex` makes one `root.iter()` pass that collects `role`, `unit-type` and `player` elements. Duplicate role and unit-type ids are kept as tuples, so the existing "not defined uniquely → refuse" behaviour is preserved. `SaveDocument.equipment_rules_index` is lazy and document-owned.

| Check | Result |
|---|---|
| Cached vs uncached `validate_equipment`, all units × 5 roles × counts {0, 1, 4, 6}, plus `movement_cap` | **0 differences / 180 cases** |
| Same, with a **duplicated `model.role.scout`** and a **player-level `movementBonus` modifier** | **0 differences / 180 cases** (both paths refuse identically) |
| Index per opened save | distinct objects for different `SaveDocument`s; created once per document ✅ |
| Players: `setdefault` (first in document order) vs uncached `next(root.iter('player'))` | same semantics ✅ |
| Full `root.iter()` cost | a single pass; the request's Windows figure of 12.7 ms is plausible. Not a regression. |
| Mutability | the source XML is never mutated, so caching immutable rule data per document is sound. Unit, owner and session state are **not** cached (owner lookup still per unit). ✅ |
| Backend | `edit_backend.change_equipment` still calls `validate_equipment(root, …)` **uncached** on the export XML. The final export is independent of the UI cache. ✅ |

## 3. `_NON_EQUIPPABLE_TYPES` (request item 3 — mandatory high scrutiny)

### 3.1 What FreeCol actually does

- **Role eligibility:** `Role` extends `BuildableType`, and its `isAvailableTo(player, unitType)` checks each of the role's `required-ability` entries. A required ability is satisfied if **any** of the supplied objects (the **player or the unit type**) has it.
- **Standard roles (classic spec):** soldier, dragoon, scout and pioneer require `model.ability.canBeEquipped = true`, `model.ability.native = false` and `model.ability.refUnit = false`.
- **`canBeEquipped` comes from:** the abstract `colonist` type (inherited by all colonist types), plus `brave` and `colonialRegular`. The **`wagon` and `ship` families never get it:** `artillery`, `damagedArtillery`, `treasureTrain`, `wagonTrain`, and caravel through privateer.
- **Saved specifications:** `Specification.java` notes that abstract types "no longer" appear "after reserialization", so a saved `<freecol-rules>` holds concrete types with their abilities **already inherited**. This is also why equipping colonists works in the editor at all: their `canBeEquipped` must be present on the concrete type in the save.

### 3.2 Consequence

For a **standard** FreeCol save, the existing check in `equipment_rules.validate_equipment` already refuses every non-default role for wagons, treasure trains, artillery and ships, because they lack `canBeEquipped`. That check (explicit `canBeEquipped` plus evaluation of each `required-ability`) runs **after** the new guard. So the hard-coded list:
- is **redundant** for standard saves;
- is **not authoritative**: it's name-based, and its entries `sloop` and `kingmanowar` don't exist in standard FreeCol;
- **does not reproduce FreeCol's real rule** either, because player-level abilities are ignored.

The B2 regression test (`test_phase2d1_5_windows_findings.py:38`, `…even_with_positive_ability`) *constructs* a wagon with `canBeEquipped=true`. That isn't how FreeCol defines it, so the test doesn't prove what the Windows symptom was.

**Likely real B2 symptom:** the editor offered a **Default-only** selector ("Unequipped colonist" plus an enabled Stage Change) for non-personnel units. Default has no required abilities, so it always validates. Commit `36b9863` (disable Default-only editors) fixes exactly that, and is the meaningful part of the B2 fix.

### 3.3 Safety assessment

- **False positives (blocking legitimate equipment):** none in the standard or `freecol` rulesets. No personnel type id is in the list. Braves are blocked for standard roles, consistent with FreeCol, since roles require `native=false`.
- **False negatives (allowing illegitimate equipment):** only for a *modded* non-personnel type that both lacks those names and wrongly carries `canBeEquipped=true`. FreeCol itself would then allow it too, so the editor stays consistent with the game.
- **Player-level abilities** (FreeCol's union rule): ignored by both the list and the existing check. For standard saves this only matters for REF players, whose units fail through their unit type's own `refUnit` ability anyway. It's a theoretical gap, not an observed one.
- **Conclusion:** safe to keep as defence in depth. **It is not sufficient as the authority, and it must not be extended into the rule.**

### 3.4 Required action (major, before merge — verification and documentation, not code)

1. **Verify on the Project Director's real save** which unit types carry `canBeEquipped` in the embedded spec. For example:
   ```powershell
   py -c "import zipfile,xml.etree.ElementTree as E,sys;r=E.fromstring(zipfile.ZipFile(sys.argv[1]).read('savegame.xml'));print(sorted(t.get('id') for t in r.iter('unit-type') if any(a.get('id')=='model.ability.canBeEquipped' and a.get('value','true')=='true' for a in t.findall('ability'))))" "PATH\TO\save.fsg"
   ```
   Expected: colonist types, brave and colonialRegular only. If wagons or ships appear, the save's spec differs from FreeCol's and B2 had a different root cause; investigate before merge.
2. **Record the result** in `OUTSTANDING_COMMITMENTS.md` OC-005, and correct the code comment in `equipment_rules.py` (lines 5–7), which claims the saved ability flags "may be incomplete or inherited".
3. **Recommended (during 2D, before 2D-2):** make the authority explicit by implementing FreeCol's `isAvailableTo` union rule (required abilities checked against unit-type **and** owner-player abilities) in `validate_equipment`. Keep `_NON_EQUIPPABLE_TYPES` only as a documented secondary guard, or drop it. **A more authoritative rules-based solution is warranted, and is mostly present already.**
4. **Replace the synthetic test premise:** add a test using FreeCol-shaped types (a wagon *without* `canBeEquipped`) to prove refusal through the rules path. Keep the defence-in-depth test, labelled as such.

## 4. Default-only blocking (request item 4) — PASS

The selector is disabled only when the **sole** eligible choice is Default.
- If the unit's current role is Default, staging Default is a no-op, so nothing legitimate is lost.
- If the current role is non-default and still valid, it's in the list, so there are ≥2 choices and the editor isn't blocked.
- If the current role is invalid or outside `ROLES` (REF and native roles), the editor was already disabled in 2C/2D-1 (`selected < 0`), so no behaviour changed.
- **Backend:** rejection of non-default roles is enforced in `validate_equipment` at both stage time (preflight) and export time (`change_equipment`).

Minor: the Default-only disabling is duplicated at `qt_equipment_editor.py:110` and `:128`. Keep one.

## 5. Performance benchmark (request item 5)

**Methodology** (`benchmark_phase2d1_5.py`):
- **Pairing:** uncached vs indexed, paired on the same loaded document. The uncached side is a `SimpleNamespace(root=…)` without the index (line 57).
- **Repeats:** median of 3.
- **Sample:** the first 15 owned units (`sample_units`, line 20).

**Independent confirmation:** on a 7.3 MB synthetic save, construction per equipment editor dropped from **77 ms (2D-1) to 4 ms** here. That's the same order as the Windows result (645 → 13 ms for 15 editors, 48×).

**Scope and limits** — state these with the figures:
1. It measures **equipment-editor construction only**, not the full colony refresh the plan specified (plan §3: "15-unit colony refresh"). The refresh also includes table rebuild, the other editors and the stage-time preflight (which re-parses the XML; see the 2D review §3.4). **"48×" is the editor-construction speed-up, not the refresh speed-up.**
2. Widgets are not shown or painted, so this is CPU construction time only.
3. The uncached side runs first, so Qt/style warm-up falls on the baseline. The median of 3 limits but doesn't remove that.
4. The 15 sampled units may include ships, wagons and repeats (the list is cycled), so this isn't specifically "a colony's stationed units".
5. One machine, no variance reported.

None of this undermines the conclusion. The improvement is real, and the user confirmed it subjectively ("noticeably faster").

Minor: move `benchmark_phase2d1_5.py` from the repository root to `tools/`, so it isn't mistaken for application code.

### 5.3 Narrow-window layout (plausible risk)

The A7 overlap was fixed for Alarm with the compact mode. **Goods and Workers still use the inline "was X" label**, so the same clipping can recur in narrow windows or with long values (up to 2,147,483,647). Recommend compact mode below a width threshold, or a minimum column width, plus a Windows check at minimum window width.

## 6. Deferred obligations (request item 6) — confirmed explicit

`docs/OUTSTANDING_COMMITMENTS.md` keeps:
- **OC-001** (Special Resources: Bells, Crosses, Hammers) **before C3**;
- **OC-002** (movement-error cascade, C3 gate);
- **OC-004** (2D-0 deletion safety before destructive Qt UI).

**2D-1.5 approval does not satisfy, defer or waive any of them.** This branch contains no deletion-engine changes, so the 2D-0 risks are unchanged.

## 7. Regressions, tests and further findings (request item 7)

| # | Finding | Severity | Reference | Recommended fix and test |
|---|---|---|---|---|
| 1 | Hard-coded type list is not the authority; B2 root cause unverified; the test premise is not FreeCol-shaped; the code comment is misleading | **Major** (verify before merge) | `equipment_rules.py:5–24, 41`; `test_phase2d1_5_windows_findings.py:38` | §3.4 |
| 2 | Benchmark scope stated as refresh but measures construction | Minor (documentation) | `benchmark_phase2d1_5.py`; OC-005 entry | State "editor construction" next to the 48× figure; optionally add a refresh benchmark |
| 3 | All staging buttons have the same accessible name "Stage Change"; screen readers can't tell which field | Minor | `qt_stage_controls.py:14`; `qt_numeric_stage_editor.py` | `setAccessibleName(f"Stage Change: {field label}")` in each integration; test the names |
| 4 | Object names built with `.title()` give `inlineMovesleftInput` and `inlineSonsoflibertytargetInput` | Minor | `qt_overview_panel.py:265` | Use an explicit mapping; keep old names if tests or automation depend on them |
| 5 | Colours still hard-coded in the new widget (third copy) | Minor | `qt_numeric_stage_editor.py:28` | Theme module (2D-1 review §4.1) |
| 6 | Duplicate Default-only disabling | Minor | `qt_equipment_editor.py:110, 128` | Keep one |
| 7 | Goods/Workers inline "was" label can clip in narrow windows | Minor (plausible) | `qt_detail_tabs_view.py` (Goods and Workers integrations) | §5.3 |
| 8 | `EquipmentRulesIndex` lives in `movement_rules.py` | Nit | `movement_rules.py:10` | Optional move to `equipment_rules.py` or a `rules_index.py` |

**Regression status:**
- No regressions found in accepted Phase 1, 2A, 2B, 2C or 2D-1 behaviour.
- The 2C combined-export harness again produced only the intended attribute changes; the source and other archive members are byte-identical.
- The 2D-1 review findings M1–M4 are confirmed fixed on this base:
  - the Inspector shows source gold;
  - equipment markers are key-based (`equipment_marker`);
  - artwork is resolved via `resources.properties`;
  - the fatal building-ambiguity check is gone.

## 8. Recommendation

**PASS WITH CAVEATS.** Before merging PR #8:
1. Run the §3.4 real-save check and record the result, then correct the `equipment_rules.py` comment.
2. Label the benchmark figure as editor construction.

Items 3–8 can follow during 2D. Making FreeCol's role-availability rule (unit type ∪ player abilities) the explicit authority should be done before 2D-2.

As always: merge, tag and branch deletion need the Project Director's separate approval. OC-001, OC-002 and OC-004 remain open gates.
