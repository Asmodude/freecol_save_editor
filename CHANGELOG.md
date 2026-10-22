# Development changelog

This is the detailed, permanent development history. It includes point releases, internal iterations and hotfixes. When a major release (0.1, 0.2, etc.) is accepted, a concise summary is also entered in README.txt. Detailed entries remain here.

> Current working baseline: **v0.6.2.6**. The 0.6 major milestone is still under development. Entries below distinguish tested/accepted features from experimental previews.

## 0.6 — Terrain inspection and map work (ongoing)

### v0.6.2.6 — Standalone Map Editor preview
- Introduced a separate, initially read-only 9 × 9 map window with coordinate navigation, tile selection and an inspector.
- Added a Go to colony action for selected European-colony tiles.
- Improved Pioneer equipment display: Hardy Pioneers can be re-equipped via the Pioneer role; quantities are labelled 20/40/60/80/100 tools instead of 1–5 sets.
- **Not yet accepted through the full Windows test cycle.**

### v0.6.2.5.5 — Context-sensitive interface (accepted with two minor caveats)
- Hide irrelevant unit-equipment and deletion controls unless the appropriate object is selected.
- Avoid showing controls for a unit selected earlier in another tab.
- Acceptance feedback requested more intuitive Hardy Pioneer re-equipping and tool-quantity terminology; addressed for test in v0.6.2.6.

### v0.6.2.5.4 — Duplicate European-colony listing fix
- Derive colony lists and counts from authoritative settlements under map tiles rather than recursively collecting cached copies.
- Guard against duplicate authoritative colony IDs.

### v0.6.2.5.3 — Native river-artwork experiment
- Attempted to load matching native river artwork when available, retaining connected vector rivers as fallback.
- Follow-up Windows test still showed vectors; pixel-faithful road and river rendering remains unfinished.

### v0.6.2.5.2 — Staggered-row coordinate correction (accepted)
- Corrected diagonal neighbour lookup according to parity of the centre tile's Y coordinate.
- Fixed incorrect neighbour placement and apparently disconnected river systems around (69,111).
- Preserved even-row mapping for Christiansborg (83,118).

### v0.6.2.5 — Consolidated terrain inspection
- Combined previous connected-waterway rendering with manual coordinate-centred terrain preview.
- Added direct lake test at (67,110), centred on the four-tile lake.

### v0.6.2.4 — Connected waterways preview
- Decode road direction strings and four-direction river connection styles for provisional vector paths.
- Distinguish river improvements from fish-production bonuses.
- Add preliminary water/land edge markings and lake continuity.
- Interim rendering delivery; consolidated into v0.6.2.5.

### v0.6.2.3.3 — Precise tile selection (accepted)
- Replaced overlapping canvas-image hit targets with diamond-coordinate hit testing.
- Verified click selection close to tile borders on Windows.

### v0.6.2.3.2 — Terrain layout hotfix
- Corrected viewport clipping and scaling; preview entire nine-tile neighbourhood.
- Render underlying ground before forest sprites.
- Replace improvised plow strokes with local FreeCol plowed artwork.
- Follow-up ZIP packaging correction aligned internal folder and application version.

### v0.6.2.3.1 — Startup hotfix
- Restored a renamed terrain-art import that prevented the GUI from launching.
- Strengthened validation beyond syntax compilation.

### v0.6.2.3 — Layered terrain preview
- Added experimental forest, road, plow, river and resource overlays.
- Initial build exposed startup and graphic-layout issues corrected above.

### v0.6.2.2 — Connected Terrain Atlas
- Enlarged, connected nine diamond tiles; remove most overlaid terrain labels.
- Introduced magenta selected-tile border and tile-detail pane.

### v0.6.2.1 — FreeCol graphics path hotfix
- Added the common Windows installation location `C:\Program Files\FreeCol\app\data\default\resources\images`.
- Confirmed actual terrain textures load instead of using placeholder diamonds.

### v0.6.2 — Graphical terrain preview
- Began loading representative original FreeCol textures from the user's local installation.
- No FreeCol artwork redistributed.

### v0.6.1.1 — Tile-item parser fix
- Parse resources and improvements nested under `tileItemContainer`.
- Verified terrain coordinates and resource data across multiple colonies.

### v0.6.1 — Nine-tile colony map
- Introduced read-only clickable isometric nine-tile terrain inspection.

### v0.6.0 — Terrain mapping prototype
- Investigated FreeCol map coordinates, tile types, resources and improvements.
- Early mapping assumed one diagonal-neighbour pattern for all rows, later corrected in v0.6.2.5.2.

## 0.5 — Native relations and unit management

### v0.5.5 — Equipment
- Add inline unit-equipment and Pioneer-tool-role staging with validation.
- Role/equipment changes do not change unit type or add free movement.

### v0.5.4 — Movement
- Editable `movesLeft` subject to game-unit and role-specific movement limits.
- Tested Soldier and Dragoon movement constraints.

### v0.5.3 — Deletion
- Combined individual unit and native-settlement deletion workflows with reference cleanup and refusal of unresolved dependencies.
- Verified load/turn/save behaviour for representative safe deletion cases.

### v0.5.2 — Native unit deletion test
- Prototyped removal of individual units and related references.

### v0.5.1 — Authoritative native settlements
- Corrected duplicated settlement representations and owner ambiguity.

### v0.5 — Native diplomacy
- Editable nation tension, stances, local settlement alarms and learnable skills, with guarded handling of existing relationships.
- Confirmed distinct national and local tension/alarm effects.

## 0.4 — Player and unit editing

### v0.4.3 — Colony Sons of Liberty
- Added colony-local SoL editing and derived colony counters without incorrectly changing nation-level Founding Father liberty.

### v0.4.2 — Unit experience in colony view
- Enable experience editing from colony unit lists as well as global units.

### v0.4.1 — Goods and XP improvements
- Add missing stock entries where appropriate and present experience toward promotion.

### v0.4 — Player and unit values
- Editable player gold, tax and unit experience. Subsequent validation limited supported unit experience edits to the game's observed cap.

## 0.3 — First editing release

### v0.3.1 — Inline goods editing
- Replace pop-up numeric editors with inline editing.

### v0.3 — Guarded save editing
- Stage colony-goods updates; save to a new `.fsg` only.
- Preserve other ZIP members and validate generated save output.

## 0.2 — Colony inspection

### v0.2.1 — Incremental preview and display refinements
- Minor post-0.2 refinement; exact historical per-file diff remains to be reconstructed.

### v0.2 — Details and inventories
- Expose colony buildings, goods and player colony counts.
- Support search and context-sensitive details; hide native-player gold sentinel.

## 0.1 — Initial read-only explorer

### v0.1
- Read-only FreeCol savegame exploration: players, colonies, native settlements and units.

## Planned, not implemented

- Native graphical road/river compositing and improved shoreline transitions.
- First safe terrain operations: roads/plowing, followed by compatible resources and terrain types.
- European colony deletion with dependency analysis and worker-versus-stationed-unit distinction.
- Building add/remove/upgrade; extended unit/population management.
- Source and distribution cleanup, regression suite, and Windows executable.
