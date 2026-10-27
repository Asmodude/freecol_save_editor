FreeCol Save Editor
===================

A Windows-oriented Python savegame viewer and editor for the open-source strategy game FreeCol, with an actively developed PySide6/Qt interface and the established Tkinter editor.

PROJECT STATUS
--------------
Current accepted integration: v0.6.2.6.4 through Phase 2B (Qt staged editing).
Phase 2C non-destructive Qt editing parity: user Windows acceptance recorded 2026-10-27; independent review and merge are PENDING on feature/phase2c-editing-parity.
The application is still in active development; it is NOT a finished release candidate.
The entire 0.6 series remains in development pending terrain-editor acceptance.
No original FreeCol artwork is redistributed: the application reads artwork from a locally installed FreeCol game.

GETTING STARTED
---------------
Requirements:
- Python and dependencies from requirements.txt for Qt (Windows acceptance environment: Python 3.14.3, PySide6 6.12.0, Pillow 13.0.0)
- Tkinter for the legacy editor; see the project's Python compatibility notes
- FreeCol savegame files (.fsg)
- FreeCol installed locally to display its original map artwork

Run the Phase 2C Qt editor:
  py qt_readonly.py

Run the legacy Tk editor:
  python freecol_explorer.py

Open a .fsg save and inspect players, European colonies, native settlements, units, diplomacy, Founding Fathers, national goods and game properties. The Qt editor offers validated, staged non-destructive edits to player Gold/Tax; unit Experience, movement and equipment; colony goods and Sons of Liberty; supported diplomacy (Stance/Tension); native settlement alarm and learnable skill. Edits are applied only by guarded Save As to a NEW .fsg file. The original and any existing destination must not be overwritten. Staged Changes supports per-item undo, unstage-all and discard warnings. Terrain inspection is READ ONLY.

Phase 2C scope excludes destructive deletion controls. Accepted Tk deletion functions remain in the legacy editor; full Qt destructive-edit parity, including cross-owner unit deletion and European colony deletion, is planned for Phase 2D. Do not interpret Phase 2C acceptance as complete Phase 2 acceptance.

The Map Editor window provides a 9 x 9 read-only terrain viewport with coordinate navigation. Select a tile to inspect its terrain, resources and improvements. You can navigate to a European colony from its tile.

MAJOR RELEASE HISTORY
---------------------
0.1 - Savegame exploration
  Initial read-only browsing of players, European colonies, native settlements and units.

0.2 - Richer colony inspection
  Colony building tiers, goods inventories, player settlement counts, contextual detail panels and search.

0.3 - Safe savegame editing
  First editable colony goods, inline editing and export through guarded Save As. Original savegames remain untouched.

0.4 - Player and unit management
  Editable player gold and tax, unit experience, Sons of Liberty and other refinements.

0.5 - Native relations and entity management
  Native diplomacy and local settlement alarm, individual unit and native-settlement deletion, and validated movement and equipment editing.

0.6 - Terrain and world-map functionality (IN DEVELOPMENT)
  Staggered-row neighbourhood mapping, graphical terrain inspection, lake/road/river previews and a standalone 9 x 9 Map Editor. This major entry is provisional until the 0.6 milestone is accepted.

Within the 0.6 development series, Phases 0, 1, 2A and 2B have been accepted and merged. Phase 2C non-destructive Qt parity passed user Windows checks on 27 October 2026; independent review and merge remain outstanding. Detailed build-by-build changes and fixes are maintained in CHANGELOG.md, including interim and hotfix releases. Major release summaries are promoted here only after acceptance; historic changelog entries are retained.

SAFETY AND LIMITATIONS
----------------------
- Preserve existing saves. Never overwrite the original .fsg or any other existing file.
- Changes are staged; validate generated archives and game references before Save As.
- Terrain editing and Qt European colony deletion are planned, not implemented; the existing Tk interface has its previously accepted deletion capabilities.
- Unsupported edit targets and unresolved references must be refused, not silently staged.
- FreeCol 1.2.0 has exhibited intermittent automatic-unit-movement MOVE_NO_MOVES cascades in an original unedited save; this is tracked separately from Qt staging correctness. Its underlying cause has not been conclusively established.
- Native road/river rendering and coastline transitions are not yet visually identical to FreeCol.
- This tool is an independent project; it is not affiliated with or endorsed by FreeCol.

DEVELOPMENT
-----------
Accepted functionality is cumulative: later releases should not break previous accepted behaviours without explicit agreement. Use tests, game-load verification and changelog records to catch regressions.

License: MIT for original project code, subject to the licensing terms of incorporated third-party material.

For evidence about the intermittent FreeCol 1.2.0 automatic-movement/Lumberjack anomaly, see docs/FREECOL_MOVEMENT_DIAGNOSTIC.md. The engine investigation is parked, not resolved.

See CHANGELOG.md for detailed changes.
