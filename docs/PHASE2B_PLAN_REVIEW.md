# Phase 2B Plan Review

_Independent review by Claude (Anthropic), 25 October 2026, of `docs/PHASE2B_IMPLEMENTATION_PLAN.md` and the actual code on `feature/phase2b-safe-qt-editing` at `c2b680f` (draft PR #5; required `headless` check green on that commit). Measured against the accepted `docs/PHASE2_DEVELOPMENT_PLAN.md`. Review only; no implementation changes were made._

## Verdict: PASS WITH CAVEATS

The plan faithfully captures every 2B-applicable requirement:
- **Must:** O2, O3, O4, A2, A5, A10.
- **Could:** O6.

It keeps 2C, 2D and 2E out of scope and does not invent new requirements. The checkpoint sequence B1–B4 is sound.

The caveats are design gaps that must be closed **within B1/B2** (§2). None requires rewriting the plan; adopt them as amendments.

---

## 1. Answers to the review questions (plan §7)

| # | Question | Answer |
|---|---|---|
| 1 | Requirement coverage | ✅ Complete and correctly scoped. |
| 2 | Player gold as first edit | ✅ Suitable. `EditSession.editable_fields('Players', …)` already excludes the native gold sentinel (`-2147483648`); `presentation.row_values` shows it as `N/A`; `produce()` checks the old value before replacing. Keep the Tk rule unchanged; don't widen or narrow editability in 2B. |
| 3 | `EditSession` / `produce()` support | Partially. Staging, unstage, validation and export are sound and fail closed (`_replace_span` verifies the old value). **Gaps:** no dirty/exported state; `original` is trusted from the caller (§2.2, §2.3). |
| 4 | Qt identity / lifetime risks | Yes: editor-to-record binding across navigation, and row movement after re-sorting (§2.4). |
| 5 | Staged-changes panel | Functionally correct for undo and count, and keys keep their Python types. **Display is not acceptable for O4**, and "Unstage all" violates A10 (§2.1, §2.5). |
| 6 | Hash / ZIP / XML / existing-file gates | ✅ Sufficient in the backend: `produce()` writes to a temp file in the target folder, verifies the archive and every non-XML member, then copies with exclusive create (`'xb'`). Add the dialog behaviour in §2.6. |
| 7 | Save As session contract | Keep edits staged and mark the session as exported (§2.3). |
| 8 | B1–B4 checkpoints | ✅ Achievable. On a separate 2B merge, see §3. |
| 9 | Missing tests / conflicts | See §2 (tests listed per item) and §4. No conflicts with accepted roadmap decisions found. |
| 10 | Verdict | **PASS WITH CAVEATS.** |

---

## 2. Required amendments (blockers for B1/B2 acceptance)

### 2.1 Staged-changes panel must show human-readable, unambiguous entries (O4)

`qt_staged_changes_panel.py` renders `str(key[0])`, `str(key[1])`, `str(original)`, `str(staged)`. As 2C and 2D add edit types, users would see raw internal keys and Python reprs, for example:
- `player:19 | gold | 7225 | 9000` (acceptable for gold alone);
- `colony:32435 | sonsOfLibertyTarget`;
- `player:19 | stance|player:97`;
- `colony:… | model.goods.food`;
- `unit:5|indianSettlement:1 | deleteNativeUnit | present | delete`;
- equipment as `('model.role.dragoon', 1)`.

**Required:**
- Add a UI-free formatter (e.g. `staged_change_labels(key, original, staged, document)`) returning: record name and type (e.g. *Morten Olsson (Danish player)*, *Christiansborg (colony)*), owner where relevant, a readable field label, and readable original and staged values.
  - Use `SaveDocument` lookups and `presentation`.
  - Format equipment as role plus tools.
  - Show deletions as an explicit "Delete" action.
  - Name the counterpart nation for diplomacy keys.
- Keep the raw key available as a tooltip or detail.
- Bind each tree item to its key through item data (`Qt.UserRole`), not through a parallel list index. The current index mapping works only because the tree is unsorted; it breaks if sorting or grouping is ever enabled.
- Unit-test the formatter for every key shape that currently exists in `EditSession`, even those whose Qt editors arrive in 2C/2D, so the panel is ready when they do.

### 2.2 `original` must always come from the source XML (A2)

`EditSession.stage(key, original, new)` trusts its caller. If the Qt editor passes the *currently displayed* (staged) value as `original`:
- undo semantics become wrong;
- `produce()` will refuse at export (fail-closed, so no corruption), but only at the end, with a confusing error.

**Required:**
- Qt editors take `original` from the authoritative `SaveDocument` element, never from the display. Follow the Tk pattern: `original` from XML, initial editor text = `staged_value(key, original)`.
- Add a test: stage 7225 → 8000, edit again → 9000. The session holds `(7225, 9000)`; undo restores 7225; export succeeds.
- Optionally, add an `EditSession` guard (or a debug assertion in tests) that a re-stage for an existing key keeps the first-recorded `original`.

Document the undo semantics in the UI: **per-item undo reverts the field to its value in the opened save**, not to the previous staged value.

### 2.3 Add dirty / exported state to `EditSession`, and define the Save As contract (A10, plan 2B.3/2B.4)

`EditSession` has no notion of "unexported changes", so A10 cannot be implemented reliably in the UI alone.

**Required (UI-free, tested headlessly):**
- Track a snapshot or revision of the edits at the last successful export, e.g. `exported_snapshot` plus `exported_path`.
- Expose `has_unexported_changes`. It is true when the current edits differ from the snapshot, including after undo or unstage changes the set.
- A failed export leaves the state unchanged.

**Recommended Save As contract (safest):**
- **Keep the opened save as the document and keep all edits staged after a successful export.** Mark the session as exported (clean), and show: *"Exported N changes to X.fsg. Edits remain staged against the original save."*
- Offer, without forcing, *"Open exported save"* to continue from the new file. Opening goes through the normal A10 path: no prompt if clean.
- Any further edit makes the session dirty again. The next Save As produces a new file containing **all** staged edits applied to the original source.
- **Do not clear the session on export.** The displayed values would revert to the source values and look as if the edits were lost.
- **Do not silently switch the baseline to the exported file.** The user would lose track of what the original was.

**Tests:**
- Clean after a successful export; dirty after a new edit or undo; unchanged after a failed export.
- No prompt on exit or open when clean.
- A second export after an extra edit contains both edits.

### 2.4 Bind editors to record identity at creation; handle re-sorting (A2, plan 2B.1)

Two classic Qt failure modes need explicit handling and tests:
- **Commit after navigation.** An editor commits on focus-out *after* the selection has changed and stages the value onto the newly selected record.
  - The editor must capture the full edit key `(element id, field)` and `original` when it opens, and commit only to that captured key.
  - On navigation, scope change, filter change or save switch, explicitly commit-or-cancel the open editor *before* switching. The Tk version used `editing_cell` context for this.
  - **Test:** start an edit, change selection via navigation, and assert that the staged key is the original record's (or that the edit was cancelled, per the chosen rule). It must never be the newly selected record's.
- **Row movement after staging.** If the edit is made in the workspace table, a staged value in the sorted column re-sorts the proxy and the row moves. Selection and Inspector must follow record identity, not row position. If a filter now hides the record, the Inspector must not go stale.
  - **Test:** sort by Gold, stage a value that changes the order, and assert that the selection and Inspector still show the same player.

**Placement suggestion (not a requirement):** put the first editor in the Inspector's structured property grid for the selected record, which matches the mockup's Inspector and Actions area, rather than as an in-table delegate. That avoids the row-movement problem for the first field. Either placement is acceptable if the tests above pass.

### 2.5 "Unstage all" must confirm (A10)

`StagedChangesPanel.unstage_all()` clears every staged edit with one click and no confirmation. A10 requires a warning before *any* action that discards staged work.

**Required:** a confirmation dialog stating the number of changes to be discarded, with Cancel as the default button. Test both the cancel and confirm paths. Undoing a single selected item may stay unconfirmed, since it's small and easily redone.

### 2.6 Save As dialog behaviour (A2, plan 2B.4)

- On Windows, `QFileDialog.getSaveFileName` asks "replace existing file?" by itself. If the user confirms, the editor then refuses (correctly), which is confusing.
  - Use `QFileDialog.Option.DontConfirmOverwrite` and show the editor's own clear refusal; or
  - re-prompt for a new name when the chosen path exists.
- Suggest a non-existing default name, e.g. `<stem>_edited.fsg`, then `_edited_2` and so on.
- **Test:** an existing target is refused, no file is touched, and the session state is unchanged.

---

## 3. Recommendations (not blockers)

- **Merge after 2B acceptance.** The accepted plan names merges after 2A and 2C, and the 2B plan correctly asks for an explicit decision. Recommendation: **approve a 2B merge once 2B is accepted.** Phase 1 showed the cost of long-lived branches (about 250 commits; red CI unnoticed). 2B is a self-contained, safety-critical checkpoint, and 2C builds directly on it.
- **Single source for staged display.** `presentation.row_values()` already overlays staged values for Players, Colonies and Units. Make the Overview, Inspector and staged panel all read staged values through the same `EditSession` accessors, so there is one source of truth and no per-widget caching of values.
- **Read-only wording.** Several labels state "READ ONLY" or "no values can be changed": title, heading, status bar, Inspector hint, About dialog, and the shell/audit tests that guard them. Update them deliberately and consistently once editing exists. Keep a clear indicator of which fields are editable.
- **Source-text tests.** The plan correctly asks to replace brittle source assertions where practical. Expect some to break when "read-only" guards change; replace them with behavioural checks, for example "no editable field outside the supported list", rather than deleting the guarantee.
- **O6 keyboard (Could):** fine as optional. If a field editor is built, Enter-to-stage and Esc-to-cancel cost little; Tab order can wait for 2C.

---

## 4. Additional tests to include in 2B.6

Beyond those listed in the plan:
1. Re-staging keeps the source `original` (§2.2).
2. Dirty/exported state transitions, including failed export and undo after export (§2.3).
3. Commit-after-navigation never targets the newly selected record (§2.4).
4. Sorted-column re-ordering keeps Inspector identity (§2.4).
5. "Unstage all" cancel and confirm (§2.5).
6. Save As to an existing path through the real dialog flow, with the dialog monkeypatched (§2.6).
7. Staged panel formatter for every existing key shape (§2.1).
8. An exported file reloaded with `SaveDocument.load()` shows the new gold value, and every other player's gold is unchanged.
9. A native player (sentinel gold) offers no gold editor in Qt.

---

## 5. Summary for the user

The plan is right and faithful to the accepted scope. Before B1/B2 can be accepted, five design points must be built in:
1. readable staged-change entries;
2. the source-derived `original`;
3. dirty/exported state in `EditSession`, with the recommended Save As contract;
4. editor identity binding;
5. confirmation for "Unstage all" and correct Save As dialog behaviour.

Also recommended: approve merging 2B into `main` once it is accepted.
