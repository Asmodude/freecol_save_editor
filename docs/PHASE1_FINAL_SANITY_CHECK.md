# Phase 1 Final Sanity Check

_Independent review by Claude (Anthropic), 25 October 2026, of branch `feature/phase1-qt-readonly-shell` at commit `1a56fa3` (249 commits ahead of `main` @ `232eca3`, 0 behind). This document follows up `docs/PHASE1_ASSESSMENT.md` and `docs/mockups/PHASE1_MOCKUP_CHECKLIST.md`. It is a review only: it does not change accepted behaviour, and it does not override `ROADMAP.md` or the project guardrails._

---

## Verdict: **FAIL (narrowly)**

The application itself passes every functional and read-only check below. Phase 1 fails only on the project's own acceptance rule that **all tests must pass with evidence**: the suite fails locally and CI has been red for about 100 commits.

Both blockers are small and mechanical. **Once they are fixed and CI is green, the verdict becomes PASS**, subject to the user's Windows visual sign-off.

---

## 1. Verified, passing

Verified with real PySide6 6.12.0 (`QT_QPA_PLATFORM=offscreen`) against a synthetic save. The save contains a human colonial player, a European rival and a native player; a colony with a building, a worker and stored goods; a ship carrying a unit and cargo; and a native settlement with an `alarm` entry.

| Check | Result |
|---|---|
| Startup and full navigation walk | All 33 navigation entries visited, every grid row selected, every detail tab opened (Overview, Buildings, Workers, Stationed units, Goods, Affiliated units, **Alarm**, By colony, In transit) and every detail row selected. **0 exceptions.** |
| Sorting keeps record identity | Every Units column sorted ascending and descending, every row selected: **0 row/record mismatches** |
| Filtering | `chris` → 1 colony; `zzz` → 0 rows; clearing restores the list |
| Diplomacy (assessment §4.1) | Per-counterpart stance and tension in separate Rival/Native tables; settlement Alarm tab; missing values shown as `(absent)`, never inferred. Inspector updates on selection. |
| Native player overview and search (assessment §4.1, §4.2) | Native nations have an Overview node; global search for a native leader now lands on that nation's Overview with the player record selected. **Fixed.** |
| Read-only guarantee | No table has edit triggers. The loaded XML tree is **byte-identical** after the full walk. The source `.fsg` is **byte-identical** (SHA-256) afterwards. No `produce()`, `save_as()` or XML serialisation-to-disk in Qt code. The only persistent write is the FreeCol installation choice, stored in Qt `QSettings`, which is never a savegame. |
| Machine-specific paths | Developer save path removed. Artwork discovery uses only generic candidates (Program Files variants, `Path.home()`-relative folders). |
| Mockup checklist | Faction flags, meaningful navigation icons (no `QStyle.StandardPixmap` placeholders remain), workspace header with integrated filter, row artwork, structured graphical Overview and Inspector, and Research removed from navigation. Final visual comparison remains the user's Windows sign-off. |

---

## 2. Confirmed defects — must fix before acceptance

### 2.1 Test suite is red (local and CI)

**Local failure.** One test fails:

```
test_qt_shell_contract.py:53
    self.assertIn('self.grid.setRowHeight(row, 36)', self.source)
AssertionError
```

Commit `13e1ad0` refactored row heights into a loop (`height = 44 if self.group == 'Units' else 36` … `self.grid.setRowHeight(row, height)`). The behaviour is still correct, but the test checks for literal source text that no longer exists. This is the source-text-test brittleness described in `docs/PHASE1_ASSESSMENT.md` §5.1.

**Fix:** replace the literal assertion with a behavioural off-screen check. For example, open a Colonies view and assert `self.grid.rowHeight(r) == 36` for every row, and the same for Units with `44`. Alternatively, delete the assertion if an existing off-screen test already covers row heights.

**CI failure.** Every push since `fa87707` (24 Oct 2026, 15:32 UTC: "execute Qt artwork regressions offscreen in GitHub Actions") has ended in **failure**. That is roughly 100 consecutive red runs, including all of the "final audit" commits. The last green run was `53e38bb`.

- At `fa87707`, the full suite (136 tests) **passes locally** under `QT_QPA_PLATFORM=offscreen`. The CI failure is therefore specific to the GitHub runner, not the code, at least at that point.
- This review could not read the Actions log, because log download is blocked from the review environment. The failure annotation only says `Process completed with exit code 1`.
- **Most likely cause:** Linux system libraries that PySide6 needs are missing on the `ubuntu-latest` runner (typically `libEGL.so.1` or `libxkbcommon`), so Qt modules fail to import.
- **Action:**
  1. Open the failing run's log on GitHub and confirm the actual error.
  2. If it is missing libraries, add a step before installing Python packages:
     ```yaml
     - name: Install Qt runtime libraries
       run: sudo apt-get update && sudo apt-get install -y libegl1 libgl1 libxkbcommon0 libfontconfig1 libdbus-1-3
     ```
  3. Re-run, and confirm **green** on the final commit before requesting acceptance.

**Process note.** CI status must be checked and reported as part of every audit. A summary that describes automated protection while CI is failing does not meet the project's honest-evidence rule.

### 2.2 Dependencies are not pinned or recorded (assessment §4.4, 🔴)

There is still no `requirements.txt` or `pyproject.toml`. PySide6 and Pillow are unpinned, and the PySide6 on Python 3.14 confirmation is not recorded anywhere.

**Fix:**
- Add `requirements.txt` with the exact versions installed on the user's Windows Python 3.14, obtained from `py -m pip show PySide6 Pillow`, e.g.:
  ```
  PySide6==<confirmed version>
  Pillow==<confirmed version>
  ```
- Make CI install from it (`python -m pip install -r requirements.txt`) so CI and Windows use the same versions.
- Record the confirmation in `CHANGELOG.md`.

---

## 3. Potential risks — not blocking acceptance

- **Remaining source-text tests.** Real off-screen Qt tests now exist, which is good. However, `test_qt_shell_contract.py` and parts of `test_qt_phase1_exit_audit.py` still assert literal code lines, and these will keep failing on harmless refactors (see §2.1). Retire them in favour of behavioural off-screen tests at the start of Phase 2. Keep only the genuine read-only guard: no `produce(` or `save_as(` in Qt code.
- **`qt_readonly.py` growth.** It is now 1,170 lines, up from 878 at the previous assessment. The model/view and per-section view-class refactor in `docs/PHASE1_ASSESSMENT.md` §5.2 is now more important as the **first step of Phase 2**, before any editing is added.

---

## 4. Optional improvements

- **Default Open Save folder.** It is now `Path.home()`. That is portable, but less convenient than the Tk editor, whose `default_directory()` already uses generic, non-machine-specific logic: it searches `Documents/freecol/save`, `Dokumenter/freecol/save` and their OneDrive variants, and remembers the last-used folder. Reuse that logic, ideally moved into a UI-free helper, for Qt.
- **Menu bar.** Only `File` exists. The mockup also shows `View` and `Help`. A `Help → About` entry (version, read-only notice, artwork-not-bundled note) would complete it. Never add non-functional menu items.
- **CI action versions.** GitHub warns that `actions/checkout@v4` and `actions/setup-python@v5` run on deprecated Node.js 20. Bump them to current major versions.
- **Dark mode.** Theme legibility still needs the user's Windows visual check (checklist §6).

---

## 5. Path to acceptance

1. Fix the failing test as a behavioural check (§2.1).
2. Find and fix the CI runner failure; confirm **green** on the final commit (§2.1).
3. Add a pinned `requirements.txt`, use it in CI, and record the PySide6/Python 3.14 confirmation (§2.2).
4. Report evidence: the local `py -m unittest discover -v` output on Windows (with `FREECOL_TEST_SAVE`) **and** a link to the green CI run.
5. Do the user's final Windows visual sign-off against `docs/mockups/phase1_approved.png`, light and dark theme.
6. Record Phase 1 acceptance in `CHANGELOG.md` and `ROADMAP.md`, merge to `main` **with a merge commit**, tag `v0.6.2.6.4-phase1`, and delete the feature branch.

Then begin Phase 2 with the structural refactor (`docs/PHASE1_ASSESSMENT.md` §5.2) and retire the source-text tests (§3).
