# Phase 1 Assessment — Qt Read-Only Shell

_Independent review by Claude (Anthropic), 24 October 2026, of branch `feature/phase1-qt-readonly-shell` at commit `c570ce9` (149 commits ahead of `main` @ `232eca3` / tag `v0.6.2.6.4-phase0`). Measured against the Phase 1 goals in `UI_MODERNISATION_PLAN.md` §5. This is a review document: it does not change any accepted behaviour, and it does not override `ROADMAP.md` or the project guardrails._

---

## 1. Verdict

Phase 1 is functionally close and of good quality, but it is **not ready for sign-off**:

- **Exit criterion not met.** "Everything findable in Tk is findable in Qt" fails because Diplomacy is missing (§4.1).
- **Acceptance gate open.** The mockup icons and faction flags are still outstanding (§4.3).
- **Structural issue before Phase 2.** The Qt shell is repeating the monolith pattern that Phase 0 removed from Tk, and it uses widget-based tables instead of models (§5.2). This should be fixed at the start of Phase 2.

---

## 2. What was verified

| Check | Result |
|---|---|
| Branch base | Cleanly based on current `main`; no conflicts expected |
| Headless test suite (`python -m unittest discover`) | 128 tests OK, 1 expected skip (no real save in CI) |
| Real Qt execution | PySide6 6.12.0, `QT_QPA_PLATFORM=offscreen`, synthetic save with human, rival and native players, a colony with building/worker/goods, a ship with passenger and cargo, a native settlement with alarm. **All 33 navigation entries visited, every grid row selected, every detail tab opened and every detail row selected: 0 exceptions.** |
| Helper modules (`qt_colony_details`, `qt_navigation`, `qt_national_goods`, `qt_unit_groups`, `qt_founding_fathers`, `qt_global_search`, `qt_overview`, `qt_display`, `qt_sorting`, `qt_game_properties`, `qt_raw_xml`, …) | All UI-free despite the `qt_` prefix, and covered by headless tests. **This correctly continues the Phase 0 pattern.** |
| Read-only boundary | No `produce()`, `save_as()` or XML mutation in the Qt shell; `NoEditTriggers` on all tables |
| Phase 0 core reuse | Uses `SaveDocument`, `EditSession` (for staged-value display only), `presentation` |

---

## 3. Phase 1 goals versus current state

| Priority | Goal | Status |
|---|---|---|
| 🔴 | PySide6 installs and runs on Python 3.14 | Works in practice on the user's machine, but **not recorded** in CHANGELOG/ROADMAP and **no version pinned** (no `requirements.txt`) |
| 🔴 | Three-pane layout (navigation, workspace, inspector) | ✅ |
| 🔴 | Tables on Qt **models** with sorting and filtering | ⚠️ Sorting and filtering work, but via `QTableWidget` with full rebuilds, not `QAbstractTableModel` + `QSortFilterProxyModel` (see §5.2) |
| 🔴 | Location names instead of raw IDs; raw IDs available in Raw XML | ✅ |
| 🔴 | Correct high-DPI rendering | ✅ 11 pt application font; Qt 6 scales natively |
| 🔴 | Tk version keeps working | ✅ Untouched |
| 🟡 | Units grouped by colony / ship / field | ✅ Exceeds plan (per-vessel passengers) |
| 🟡 | Irrelevant inspector tabs hidden, not greyed out | ✅ |
| 🟡 | Global search across categories | ✅ (one navigation bug, §4.2) |
| 🟡 | Table basics: right-aligned numbers, alternating rows, ✓ booleans, natives/Europeans separated | ✅ |
| 🟢 | Human player selected by default | ✅ |
| 🟢 | Dark mode follows Windows | Not verified |
| **Exit** | **Everything findable in Tk is findable in Qt, faster** | ❌ **Not met** (§4.1) |

### Scope additions beyond the plan

Founding Fathers (with portraits and Continental Congress view), National Goods with per-colony and in-transit breakdown, and Game properties with nested options and long-value handling.

These are well built and tested. They are, however, additions to Phase 1's planned scope, and they explain much of the overrun against the "~2 sessions" estimate. Future additions should be logged as scope changes **before** they are implemented, so they don't delay acceptance of the planned goals.

---

## 4. Must fix before Phase 1 sign-off

### 4.1 Diplomacy: parity gap with Tk (🔴, exit criterion)

The Tk editor shows, in readable form:
- for each player: **stance** and **tension** towards every other player;
- for each native settlement: **alarm** towards each colonial player.

In Qt this data is only reachable by reading Raw XML. In addition, **native player records are not reachable through Qt navigation at all.** Native nations only have *Settlements* and *Units* entries, with no player Overview.

**Required:**
- Implement the **Diplomacy** view, read-only, for the human player, each European rival, and native nations.
  - Players: stance and tension per other player.
  - Native settlements: alarm per colonial player, shown in the settlement's detail tabs.
- Add an **Overview** entry for each native nation (its player record).
- Keep the data logic in a UI-free helper (e.g. `qt_diplomacy.py`) with headless tests, consistent with the other helpers.
- Show absent entries honestly (e.g. "(absent)", as Tk does). Never infer values.

**Research** and **Player Options** never existed in Tk, so they are new features, not parity. Remove them from the Phase 1 exit gate and record them as later-phase items. They can stay visible as "(planned)" navigation entries.

### 4.2 Bug: native player results in global search do nothing

Search for a native leader (e.g. "Segoyewatha") and double-click the **Players** result. Nothing happens. This was reproduced in the off-screen Qt run.

`navigate_to_global_result()` computes the scope `('Players', 'player:<id>')`, no navigation item exists for it, and the function returns silently. Fixing §4.1 (native nation Overview entries) resolves this.

As a general rule, any search result that cannot be navigated to should give visible feedback rather than fail silently.

### 4.3 Mockup icons and faction flags (🔴, already recorded as exit gate)

This item is correctly recorded in the plan (`UI_MODERNISATION_PLAN.md` §5, "Mockup fidelity"). Two additions:

- **Done 24 Oct 2026:** the mockup is now committed as `docs/mockups/phase1_approved.png`, with its written checklist `docs/mockups/PHASE1_MOCKUP_CHECKLIST.md`. Implement icons and flags against that checklist.
- **Root cause and prevention.** The approved mockup exists only as an image in a past chat conversation; it is not in the repository. Chat context does not persist between conversations and is eventually truncated within long ones, which is how this requirement was lost.
  - Commit the mockup image (e.g. `docs/mockups/phase1_approved.png`).
  - Next to it, commit a written checklist of its visual elements: which icon for each navigation node type, flags for which entries, sizes and spacing.
  - Treat the repository, not chat history, as the source of truth for design decisions.
- **Test conflict.** `test_qt_shell_contract.py::test_load_batches_navigation_and_supports_diagnostics` asserts the literal source line `icons = {kind: self.style().standardIcon(icon)`. That is exactly the generic placeholder icon code that must be replaced, so the test will fail when the requirement is implemented correctly. Resolve this together with §5.1.
- **Artwork policy unchanged.** Load from the local FreeCol installation (via `freecol_art_source`), never bundle copyrighted artwork, and provide tasteful fallbacks.

### 4.4 Record and pin the PySide6 dependency (🔴, housekeeping)

- Add `requirements.txt` (or `pyproject.toml`) with `PySide6` and `Pillow`, pinned to the versions confirmed on the user's Windows Python 3.14.
- Record the confirmation in CHANGELOG. Phase 4 packaging depends on this.

---

## 5. Fix before or at the start of Phase 2

### 5.1 Replace source-text tests with real off-screen Qt tests

`test_qt_shell_contract.py` and `test_qt_phase1_exit_audit.py` mostly assert that specific lines of source code exist (`assertIn('self.grid.selectRow(display_row_index)', source)` and similar). Such tests:
- pass even if the window is broken at runtime;
- fail when correct refactors or requirements are implemented (see §4.3).

Qt runs headlessly with `QT_QPA_PLATFORM=offscreen`, which this review confirmed works. **Recommended replacement:**

- **CI:** install `PySide6` in `.github/workflows/headless-tests.yml` and set `QT_QPA_PLATFORM: offscreen`.
- **Add `test_qt_smoke.py`**, which should:
  1. Build a small synthetic `.fsg` in a temp dir. It needs a human colonial player, a European rival, a native player, a colony with a building, a worker and stored goods, a ship carrying a unit and cargo, and a native settlement with an `alarm` child.
  2. Monkeypatch `QFileDialog.getOpenFileName` to return it, construct `QtExplorer`, call `open_save()`.
  3. Recursively visit every navigation item. Select every grid row, open every detail tab, and select every detail row, calling `app.processEvents()` throughout.
  4. Capture exceptions via `sys.excepthook`, because Qt slots swallow them otherwise, and assert there are none.
  5. Assert behaviour rather than source text. Examples:
     - The status bar counts match `SaveDocument`.
     - The irrelevant tabs are absent.
     - A sorted grid still maps rows to the correct XML element.
     - Global-search navigation lands on the right record, including native players.
     - The tables are not editable.
- Keep the read-only guard (no `produce(` / `save_as(` in `qt_readonly.py`), but retire the remaining literal-source assertions once behavioural equivalents exist.

### 5.2 Prevent `qt_readonly.py` from becoming the next monolith

`qt_readonly.py` is a single 878-line `QtExplorer` class.
- `populate()` and `inspect()` branch on `self.group` across seven view types.
- The navigation lookup logic (`find_item` / `matching_item`) is duplicated three times.
- This is the pattern Phase 0 removed from `freecol_explorer.py`.

In addition, all tables are `QTableWidget`s that are rebuilt on every filter or refresh. That is acceptable for read-only use, but Phase 2 inline editing works far better with models:
- `QAbstractTableModel` exposing data from `SaveDocument` plus `EditSession` staged values;
- `QSortFilterProxyModel` for sorting and filtering without rebuilds and without the manual `UserRole` row-identity bookkeeping;
- item delegates calling `EditSession.validate()`;
- changed-value styling via the model's `data()` roles, and single-cell updates via `dataChanged`.

**Recommended first step of Phase 2, with no visible change, accepted the same way as Phase 0:**
- one view class per section (Players, Colonies, Native settlements, Units, Founding Fathers, National Goods, Game properties, Diplomacy) with a common interface (`populate`, `inspect`, detail sections);
- a shared model/proxy table base class;
- one navigation helper for "find item by (group, scope)";
- `QtExplorer` reduced to window layout, navigation and routing.

### 5.3 Minor clean-ups

- `populate()` sets `self.breakdown_target = None` twice.
- `inspect()` contains a `Founding Fathers` branch that is unreachable, since that group returns early.
- The development-only default save path (`C:\Users\morte\...`) is acceptable for now, documented and test-guarded. It must be replaced before Phase 4, as already recorded.

---

## 6. Recommended order to close Phase 1

1. ~~Commit the approved mockup image and its written checklist (§4.3).~~ Done: see `docs/mockups/`.
2. Implement Diplomacy and native-nation Overview entries, which also fixes §4.2.
3. Implement mockup icons and faction flags (§4.3).
4. Add the off-screen Qt smoke test and PySide6 in CI. Retire the conflicting source-text assertions (§5.1).
5. Add `requirements.txt` and record the PySide6/Python 3.14 confirmation (§4.4).
6. Move Research and Player Options out of the Phase 1 exit gate (§4.1).
7. Do the Windows end-to-end tour: high-DPI, dark mode, every navigation area, search, Raw XML. Then get user sign-off, merge to `main` with a merge commit, and tag `v0.6.2.6.4-phase1`.

Then start Phase 2 with the structural refactor in §5.2.

---

## 7. Guardrails (unchanged)

- The Qt shell stays read-only until Phase 2; `main` changes only after user acceptance on Windows.
- Report test results with actual evidence. CI passing is not GUI acceptance.
- Never redistribute FreeCol artwork; load it from the local installation.
- Never overwrite saves; all future edits go through `EditSession` and `produce()`.
