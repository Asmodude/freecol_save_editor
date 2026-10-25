# Phase 2B — Windows and FreeCol Acceptance Checklist

**Status:** Test instructions; no acceptance claimed.  
**Baseline:** `docs/PHASE2B_IMPLEMENTATION_PLAN.md` (accepted); independent review `docs/PHASE2B_PLAN_REVIEW.md`.  
**Design decisions accepted 25 October 2026:** Inline editing in the lower middle Overview, staged changes beneath the right Inspector, and automatic selection/inspection whenever the normal upper-middle record table contains exactly one visible record. No new editing fields are authorized by the illustrative mockup.

## Preparation

1. Check out the tested head of `feature/phase2b-safe-qt-editing` (record exact SHA and corresponding green required `headless` run).
2. Open a **copy** of a known playable save in `py qt_readonly.py`. Keep an unchanged backup.
3. Record source file SHA-256 before and after with PowerShell: `(Get-FileHash -Algorithm SHA256 'C:\\path\\save.fsg').Hash`.

## A. Layout and selection

- [ ] Select Danish player Overview: the sole player row is automatically selected, showing the lower Overview and Inspector without clicking a second time.
- [ ] Select another singleton ordinary list or narrow a multi-record list to one result: it is automatically selected and inspected.
- [ ] Verify that a multi-record list does not automatically choose an arbitrary record.
- [ ] Verify editable player Gold is in the **lower middle Overview**, with a recognisable blue-outlined input and pencil; Inspector remains informational.
- [ ] Verify Staged Changes is in a vertically resizable section **beneath the right Inspector**, not in a bottom-of-window dock. Resize it and check both regions remain usable.
- [ ] Confirm non-editable values are not deceptively styled as editable; native-player sentinel Gold never offers an editor.

## B. Staging and undo

- [ ] Note original Danish player Gold. Enter a different valid nonnegative integer and stage with Enter or the pencil. Check main workspace, lower Overview, pending count and right-hand staged entry.
- [ ] Edit the same Gold field again: the staged entry must retain the **original save value** as its source, not the first staged value.
- [ ] Click the row-level undo icon in the right-hand review: the value returns to the original from the opened save, and pending count decreases.
- [ ] Test Unstage All with **Cancel** and then **Discard**; verify both results.
- [ ] Invalid text, a negative number and an out-of-range integer must be rejected without staging.
- [ ] After staging, navigate to another record or sort/filter the table. The edited player must remain the correct target and pending changes must persist. No edits should land on another player.
- [ ] Confirm selected row behavior and Inspector identity remain sensible when a filter hides the edited record.

## C. Safe Save As / session state

- [ ] Stage Gold and choose Save As. A non-existing `_edited.fsg` name is offered.
- [ ] Attempt to choose the opened source or any other existing file: export must refuse, preserving both files and pending edits.
- [ ] Export to a new destination. Confirm success feedback. Staged changes remain visible against the original source.
- [ ] On attempting to exit or open another save **before export**, Cancel keeps the original save and staged changes intact.
- [ ] After successful export, exit/open should not prompt if no changes have been made **since that export**.
- [ ] After export, stage a further change or undo a staged change. Exit/open should warn again (including if the staged count becomes zero).
- [ ] Exporting again to another fresh destination after additional edits should apply the **full current staged edit set** to the original baseline.
- [ ] A canceled Open dialog or failed replacement load must not discard current session state.

## D. FreeCol integrity

- [ ] Recalculate source SHA-256. It must match the value recorded before testing.
- [ ] Open the exported `.fsg` in FreeCol and verify Gold changed to the staged value.
- [ ] Verify other players' values remain intact in the scenario.
- [ ] Advance a turn, save in FreeCol and reload successfully.
- [ ] Record the exported file path, test results, application/FreeCol version, tested Git commit and any deviations.

## Gate

Phase 2B is **not accepted** solely because CI is green. Complete relevant Windows/UI checks and real-game roundtrip, resolve blocking issues, record the actual final tested commit, and obtain explicit user approval before merge. The branch remains draft until that approval.
