# Phase 2A — final Windows sanity re-check (single workspace table)

The experimental comparison mode has been **removed**. This is the
pre-merge acceptance check for the permanent, single model-based `QTableView`.
The accepted Tkinter editor and map editor remain unchanged.

## Run the final build
From PowerShell in the feature-branch repository directory:
```powershell
py qt_readonly.py
```
**Do not** use `--compare-model-view`; that flag no longer exists.

Open your normal FreeCol `.fsg` and verify:

1. **Players, Units, Colonies, Native settlements, Founding Fathers,
   National Goods, Game properties:** table headers, sprites, tooltips,
   spacing, row heights and columns look appropriate.
2. **Sort** text and numeric columns in both directions. Clicking a sorted
   row must inspect the correct record, not a record at the original row.
3. **Filter/search:** selecting a global-search result opens the correct
   record. Changing a filter or navigation scope must not leave stale
   Inspector contents.
4. **Colonies:** selecting Christiansborg in the left navigation directly
   opens its Inspector and overview; broad lists are not auto-selected.
5. **Units:** the main list displays role-aware artwork, including Dragoon
   sprites where installed. Workers and Stationed units have appropriately
   tall rows; contextual Open Unit works.
6. **National Goods:** choose a good, select a colony in By colony, click
   Open colony Goods; confirm that colony's Goods tab and selected good.
7. **Diplomacy:** Rival Nations and Natives remain separate. The lower
   detail-tab and Diplomacy tables deliberately remain QTableWidget pending
   editing work in Phase 2C.
8. The Tkinter editor and its Map Editor still launch normally. Qt remains
   read-only, and opening/browsing a save does not modify it.

## Merge gate
- Final HEAD CI `headless` check green.
- Explicit user approval of this single-view Windows re-check.
- Merge PR #4 using a merge commit (never direct-push to protected `main`).
- Tag the **merge commit** `v0.6.2.6.4-phase2a`, then delete the feature
  branch.

Do not declare Phase 2A fully merged or tag it before those gates.
