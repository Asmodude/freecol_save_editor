# Phase 2D-1.5 — Windows Acceptance Checklist

> **27 Oct 2026 sequencing correction:** Perform **sections A, B and C now**. **Defer section D**, including the FreeCol turn-advance roundtrip, until mandatory C2 **Special Resources** (OC-001) and the previously reported C1+C2 movement-error gate (OC-002) have been addressed. See [Outstanding Commitments](OUTSTANDING_COMMITMENTS.md). Green CI does not waive those gates.

**Branch:** `feature/phase2d1-5-component-performance`  
**Phase status:** Awaiting user's Windows test, performance measurements, and independent Claude review.  
**Baseline:** Phase 2D-1 accepted tag `v0.6.2.6.4-phase2d1`.

Use a **copy** of a genuine FreeCol save and launch `py qt_readonly.py` from the feature branch.

## A. Shared numeric editor

- [ ] Player Gold: type a candidate; confirm **Not staged** appears and Staged Changes is unchanged until Enter / Stage Change.
- [ ] Player Tax: Stage Change button stages only that player's tax. After staging, edit styling becomes green and the source `was …` value appears.
- [ ] Colony Sons of Liberty %: Enter and Stage Change both stage the intended colony; existing recalculation and validation stay intact.
- [ ] Unit Experience and Moves Left: values and bounds remain correct; movement edits preserve the accepted projection and staging behaviour.
- [ ] Colony Goods: select a named goods type, enter a new quantity; verify the correct goods type / colony receives the staged change. Check row sorting does not redirect edits.
- [ ] Colony Workers: sort by experience, edit a worker's experience via Enter and button; verify the correct **unit ID** receives the staged edit.
- [ ] Native Settlement Alarm: stage a directional alarm value; verify the correct settlement/nation pair after sorting, the original value remains intact, and source/staged colours and candidate indicator match other numeric editors.
- [ ] Undo selected and Unstage All clear staged styling and restore the source values.
- [ ] No numeric field is written to the original save before Save As.

## B. Equipment editor

- [ ] Open a colony with many stationed units. Confirm noticeably faster refreshes, without missing controls or incorrect roles.
- [ ] Hardy Pioneer naturally offers Pioneer and 100 tools; default role still requires roleCount 0.
- [ ] Pioneer 20/40/60/80/100 tools; Soldier/Dragoon/Scout validation unchanged.
- [ ] Switch units, role choices, and tabs repeatedly. Confirm nothing leaks state between units or saves.
- [ ] Role/movement staging still behaves identically in Overview and Stationed Units.
- [ ] Reopen the same save or a different save. Eligibility and movement must come from **that** save's embedded ruleset, not a stale cache.

## C. Performance measurement

Run in PowerShell, inside the repository folder:

```powershell
py benchmark_phase2d1_5.py "C:\\path\\to\\your\\actual-save.fsg" --units 15
```

The script prints the save XML size, load/index time, uncached and cached construction for 15 editors (median of three repetitions each), and the improvement ratio. Save the output for acceptance. The two comparison cases use the **same XML in one invocation**.

This tests editor **construction time**, a proxy for the equipment-heavy portion of colony refresh; it does not measure the entire Qt repaint and navigation pipeline. Note any actual end-to-end sluggishness separately.

## D. Integration and handoff

- [ ] Save As to a new file; confirm the original archive remains unchanged.
- [ ] Open the exported save in FreeCol, advance one turn, save and reload.
- [ ] Main UI and other accepted Phase 2D-1 capabilities remain functional.
- [ ] Report PASS / NOT YET PASSED per section, numeric benchmark output and observations.
- [ ] Once Windows accepted: commission Claude's independent review on this branch; resolve any findings; seek explicit merge approval before integration. Do **not** tag or merge during this step.
