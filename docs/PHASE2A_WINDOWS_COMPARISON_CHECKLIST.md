# Phase 2A — Windows comparison checklist

This is a **preview**, not an acceptance declaration. The protected `main`
branch and the accepted Tkinter editor remain unchanged.

## Launch both variants from the feature branch

From a PowerShell prompt at the repository root, with PySide6 installed:

- Accepted read-only Qt interface: `py qt_readonly.py`
- Experimental QTableView interface: `py qt_readonly.py --compare-model-view`

The switch is **opt-in per launch**. Remove the argument to restore the
accepted view. It does not enable save editing or modify any FSG file.

## Compare using the same existing .fsg save

1. Open the save in both versions. Check **Players**, **Units** and
   **Colonies**: names, headers, numerical values, icons, tooltips, row
   heights, and column widths.
2. Sort numeric columns (e.g. Gold and Established); confirm numeric order
   and that selecting a row opens the **correct** Inspector record.
3. In both versions use global search to open a colony/unit, and test the
   contextual **Open Unit** action from the detailed Inspector.
4. Switch rapidly between owned and rival player scopes, and between
   categories, after selecting and sorting a row. The Inspector must never
   show a stale record.
5. Check **Native settlements**, **Founding Fathers**, **National Goods**,
   **Game properties**, and the separate **Diplomacy** tables for Rival
   Nations and Natives. Report any missing features or layout differences.
6. Verify the accepted Tkinter editor and map editor still launch and edit
   exactly as before.

## Exit criteria

- Required CI green on the **current** feature-branch HEAD.
- No known loss of accepted features or visual regressions.
- Windows smoke test of the experimental view with a real save.
- Explicit user acceptance before merging Phase 2A or making the new table
  the default.

Please include the category, steps and a screenshot for any discrepancy.
