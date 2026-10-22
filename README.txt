FreeCol Save Editor
===================

A Windows-oriented, Python/Tkinter savegame viewer and editor for the open-source strategy game FreeCol.

PROJECT STATUS
--------------
Current development build: 0.6.2.6 (standalone, READ-ONLY Map Editor preview).
The application is still in active development; it is NOT a finished release candidate.
The entire 0.6 series remains in development pending terrain-editor acceptance.
No original FreeCol artwork is redistributed: the application reads artwork from a locally installed FreeCol game.

GETTING STARTED
---------------
Requirements:
- Python 3.9 or later with Tkinter
- FreeCol savegame files (.fsg)
- FreeCol installed locally to display its original map artwork

Run:
  python freecol_explorer.py

Open a .fsg save, inspect Players, Colonies, Native Settlements and Units, and stage supported edits. Use "Save As edited .fsg" to export a NEW savegame. The original savegame must never be overwritten. Terrain inspection is READ ONLY.

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

Detailed build-by-build changes and fixes are maintained in CHANGELOG.md, including interim and hotfix releases. Major release summaries are promoted here only after acceptance; historic changelog entries are retained.

SAFETY AND LIMITATIONS
----------------------
- Preserve existing saves. Never overwrite the original .fsg or any other existing file.
- Changes are staged; validate generated archives and game references before Save As.
- Terrain editing and European colony deletion are planned, not implemented.
- Native road/river rendering and coastline transitions are not yet visually identical to FreeCol.
- This tool is an independent project; it is not affiliated with or endorsed by FreeCol.

DEVELOPMENT
-----------
Accepted functionality is cumulative: later releases should not break previous accepted behaviours without explicit agreement. Use tests, game-load verification and changelog records to catch regressions.

License: MIT for original project code, subject to the licensing terms of incorporated third-party material.

See CHANGELOG.md for detailed changes.
