# Phase 2A Sanity Check

_Independent review by Claude (Anthropic), 25 October 2026, of branch `feature/phase2a-qt-refactor` at `830a7ca` (PR #4; 92 commits ahead of `main` @ `d7307f7`, 0 behind). Measured against `docs/PHASE2_DEVELOPMENT_PLAN.md` §2A. This is a review only._

## Verdict: PASS WITH CAVEATS

The refactor is real and well tested, but 2A is not complete until the model/view table is the **only** table.

**User decision (25 Oct 2026): the switch-over happens in 2A, before merging.**

---

## 1. Verified

| Check | Result |
|---|---|
| Local suite (`QT_QPA_PLATFORM=offscreen python -m unittest discover`) | 249 tests OK, 1 expected skip |
| CI | PR #4 run #368 green on `830a7ca` |
| `main` protection | Ruleset active: required `headless` check (strict), PR-only merges (merge commits), deletion and force-push blocked |
| Component extraction | Navigation builder, navigation lookup, global search, Diplomacy, Founding Fathers, detail tabs and workspace header are separate modules. `qt_readonly.py` is down from 1,170 to 803 lines. |
| Live off-screen walk, **default view** | 33 navigation entries; every row, tab and detail row selected; 0 exceptions; 0 sort/selection identity mismatches; filtering correct; no editable tables; loaded XML and source `.fsg` byte-identical afterwards |
| Live off-screen walk, **`--compare-model-view`** | 33 navigation entries; every column sorted both ways with every row selected through the `QTableView` (502 selections); **0 identity mismatches**; all detail tabs reached; 0 exceptions; read-only and non-mutation confirmed |

---

## 2. Required before merge

### 2.1 Make the model/view table the only workspace table (🔴, plan 2A items 2 and 5)

**Current state.** `QTableView` + `RecordTableModel` + sort/filter proxy exist and match the accepted UI, but they are only shown with `--compare-model-view`. The default window still uses the legacy `QTableWidget` (`self.grid`, about 34 references in `qt_readonly.py`), and `populate()` fills **both** implementations on every refresh.

**Required:**
1. Make `self.model_view` the workspace table in all modes. Route `inspect()`, sorting, filtering, global-search navigation, contextual unit/colony drill-downs and auto-inspection exclusively through the model/proxy, using source-record identity (already implemented and tested in comparison mode).
2. Remove the legacy `self.grid` population path, `SortableItem` use for the main grid, `_compare_model_view`, `set_model_view_comparison()` and the `--compare-model-view` CLI flag.
3. Remove or rewrite tests that exist only to compare the two implementations (shadow/parity tests), keeping their **behavioural** assertions against the single model/view table:
   - cell text and numeric sort order;
   - icons, tooltips and row heights;
   - record identity after sort and filter;
   - stale-selection rejection when scope or group changes;
   - search and drill-down targeting.
4. Out of scope for this step: the Diplomacy tables and detail-tab tables may stay `QTableWidget` for now. Record in the CHANGELOG that they will move to models when they become editable in 2C.
5. Update `docs/PHASE2A_WINDOWS_COMPARISON_CHECKLIST.md` into a short single-view Windows re-check covering the same steps, without the comparison launch.

**Evidence required:** green CI on the final head, the local suite output, and a short Windows re-check of Players, Units, Colonies, Native settlements, Founding Fathers, National Goods and Game properties (sorting, selection, search, drill-downs). Tk editor and Map Editor still launch.

### 2.2 Record 2A in CHANGELOG and ROADMAP (🔴)

Neither has been updated for 2A. Record:
- the scope delivered;
- the user's Windows acceptance;
- the single-table switch-over;
- the CI run on the final head.

**Also log the user-visible changes that entered this "no visible change" refactor, as accepted visible changes:**
- role-aware unit sprites (e.g. dragoon artwork) in the Units table and detail tables;
- automatic Inspector display when navigating to a uniquely scoped colony or native settlement;
- matched Workers / Stationed units row heights.

---

## 3. Carry into 2B (not blocking the 2A merge)

- **Source-text tests.** About 70 literal-source assertions remain (`test_qt_shell_contract.py`, `test_qt_phase1_exit_audit.py`, `test_qt_goods_drilldown_contract.py`, `test_qt_father_view_contract.py`). Plan 2A item 4 asks for their replacement. Retire them progressively as behavioural tests cover the same ground; keep only genuine read-only guards (no `produce(` or `save_as(` in Qt code until 2B introduces the controlled Save As path).
- **Per-section view classes.** Players, Colonies, Units, Native settlements, National Goods and Game properties still share branching inside `populate()` and `inspect()`. This is acceptable once there is a single model table, but split them as each becomes editable in 2C.

---

## 4. Merge procedure after 2.1 and 2.2

1. Green `headless` check on PR #4's final head (enforced by the ruleset).
2. User sign-off on the Windows re-check.
3. Merge PR #4 with a merge commit.
4. Tag the merge commit `v0.6.2.6.4-phase2a` (on the merge commit itself, not a later `main` commit). Delete the branch.
