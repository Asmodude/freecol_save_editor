# Development changelog

This is the detailed, permanent development history. It includes point releases, internal iterations and hotfixes. When a major release (0.1, 0.2, etc.) is accepted, a concise summary is also entered in README.txt. Detailed entries remain here.

> Current accepted integration baseline: **v0.6.2.6.4**. The 0.6 major milestone is still under development. Entries below distinguish tested/accepted features from experimental previews.

## 0.6 — Terrain inspection and map work (ongoing)

### Phase 0: initial core extraction (in progress, unaccepted)
- **Windows checkpoint, 2026-10-23:** user ran all 55 tests successfully (0 failures, 0 skips), including real-save Save As integrity against `Morten2.fsg`; independently confirmed editor/map smoke test, intact native-mask rivers, visible colony art, staging and saving edits. Directional vector roads remain intentionally unchanged; no Phase 0 native-road redesign.

- Branched from accepted `main` as `refactor/phase0-core-extraction`; `main` remains unchanged.
- Added UI-free `SaveDocument.load()`, moved ZIP/XML parsing and authoritative indexes out of Tk `Explorer.open_save()` while retaining messageboxes, status formatting and initial selection in Tk.
- Added UI-free `EditSession`, wired existing inline numeric and choice validation/staging into it, preserving the original `self.edits` dictionary format and visible validation messages.
- Added `test_save_document.py` and `test_edit_session.py` (headless).
- Missing historical `Morten(5).fsg` is not a Phase 0 prerequisite; synthetic cached missionary tests and currently available real saves are valid baselines.
- Equipment staging, deletion staging and Save As delegation now flow through `EditSession`. The original `produce()`, equipment validator, deletion planner and user-facing confirmation dialogs remain in place.
- Added tests for legacy delete-key encodings, equipment-versus-deletion conflict, and no-overwrite protection.
- **Pending:** Windows execution of all tests, byte-for-byte real-save round trip on this branch, UI smoke testing, remaining presentation/renderer extraction and full no-visible-change acceptance. No application code has been merged into `main`.



### Phase 0 boundaries and baseline fixtures — 2026-10-23
- The user created a `v0.6.2.6.4` Git tag for the accepted main baseline; Phase 0 must compare against that exact tag and make no user-visible or save-editing behaviour changes.
- Human-player auto-selection is explicitly **deferred until after Phase 0**; preserve current load-time tab, filter and selection behaviour throughout the refactor.
- For the audited `Morten(5).fsg`, expect 2,520 authoritative unit IDs from 2,525 raw nested `unit` elements; Xaymaca must have one authoritative Danish missionary. These are save-specific reference observations, and the live UI confirmation is still open.
- Maintain the missionary cached-snapshot deletion caveat as a known issue rather than changing behaviour in Phase 0.


### Accepted Phase 0 comparison baseline — 23 October 2026
- Integration merge: `f1178c7` on `main`, followed by release housekeeping (window titles and documentation).
- `v0.6.2.6.4` scope: FreeCol-inspired native-mask rivers where source assets exist; vector-road renderer remains unchanged; twelve approved geography-neutral colony graphics.
- Evidence: 40/40 Windows headless regression tests, real-save Save As integrity, in-game equipment/deletion confirmation, map art and river visual approvals, and post-preview-removal Map Editor smoke test.
- Known follow-up: explicit live UI verification of the cached-missionary unit count and Xaymaca occurrence remains open. Cached missionary deletion semantics remain a separate future fix, **not** part of no-visible-change Phase 0.
- Phase 0 must make no visible changes or change save-editing behaviour. Retire or replace obsolete GUI tests in an isolated refactor branch; keep `main` unchanged until accepted.


### Final Windows regression verification — 2026-10-23
- User executed `py -m unittest -v test_colony_graphics test_map_regression test_edit_safety test_unit_records test_location_names test_real_save_integrity` on Windows (Python 3.14.3) after the 12-state preview cleanup.
- Actual output: **Ran 40 tests in 0.685s; OK** (0 failures, 0 errors, 0 skips). The real-save integration test ran successfully.
- User previously confirmed Save As equipment modification and unit deletion both load and behave correctly in FreeCol.
- All 12 colony graphics received user visual approval; software merge into `main` remains a separate explicit decision.
- Outstanding pre-merge sanity check: launch the cleaned Map Editor and confirm normal colony rendering with no TEST sprite selector; review any development-only code/doc discrepancies.



### Better Colony Graphics — all 12 artworks accepted (2026-10-23)
- User visually approved all three sizes of Colony, Stockade, Fort and Fortress in the Windows 9×9 map viewer.
- Removed the temporary 12-state TEST sprite dropdown after approval; the map now uses authoritative savegame classification.
- Preserved 40%-enlarged artwork scale, deferred sprite compositing and optional selection outline.
- No savegame mutation. Final combined release regression passed and integration was merged to `main` in `f1178c7`.


### Unit list: cached missionary duplication — 2026-10-23 (fix merged; numeric count verification outstanding)
- Real-save finding: `Morten(5).fsg` contains 2,525 nested `unit` elements but only 2,520 distinct IDs. Four missionaries have an additional five snapshots beneath `cachedTile`, including Danish Jesuit Missionary `unit:34086` at Xaymaca.
- `freecol_explorer.py` now indexes unit records using `unit_records.authoritative_units(game)`, which excludes cached tile snapshots and **fails closed** on genuinely repeated authoritative unit IDs.
- Added `test_unit_records.py` with isolated cached-missionary, duplicate-authoritative-ID, carried-unit and reference-node cases.
- The original save is untouched. **Important:** current unit deletion engine still traverses cached XML and may refuse missionary deletion; that is a distinct safety concern and **not fixed by a display-only indexing change**. Avoid deleting affected missionary units until specifically tested.
- Authoritative-unit tests passed as part of 40/40 Windows suite. **Still to confirm explicitly in UI:** the expected unit count and single Xaymaca missionary for the audited save.



### Regression suite expansion — 2026-10-23 (completed)
- Added `test_edit_safety.py` with 13 headless tests covering supported and unsupported equipment changes and conservative unit deletion (external references, cargo, ambiguous IDs and unexpected containment).
- Tests use synthetic XML and make no changes to user save files.
- Run headlessly on the current feature branch: `python -m unittest -v test_colony_graphics test_map_regression test_edit_safety test_real_save_integrity`.
- `test_real_save_integrity` is skipped unless `FREECOL_TEST_SAVE` points to a private sample save; when enabled it checks source immutability and no-overwrite Save As.
- Completed: user executed all 40 headless tests successfully on Windows including the real-save round trip; user also verified equipment/deletion Save As in FreeCol.



### v0.6.2.6.4 — native-mask river integration (ACCEPTED; 2026-10-23)
- Integrated the original v0.6.2.6.4-dev2 experimental river-mask compositor into `terrain_art.py` using FreeCol assets from the local installation and optional Pillow.
- Both the inspector terrain preview and 9×9 Map Editor now try the native-mask composite, then native exact-style sprite, then the existing directional vector fallback. Roads retain the existing vector painter; no pixel-identical RoadPainter implementation is claimed.
- Preserved accepted colony sprite compositing, improved scale, selectable tile-outline visibility, map geometry, and the FreeCol `buildingType` fortification classification.
- Retired the temporary `colony_large` forced-preview control after visual acceptance.
- Windows visual check at (69,111) passed; the user confirmed the major river and existing road presentation. Roads remain the established directional vector painter, not native RoadPainter-equivalent. Full Windows headless suite: 40 tests, 0 failures/skips. User confirmed Save As equipment and deletion in FreeCol; merged to `main` in `f1178c7`.



### Better Colony Graphics — completed and visually accepted
- Added a nation-neutral twelve-state colony image resolver (size × fortification).
- Added optional transparent-PNG artwork loading from `assets/colonies/` and visible placeholder markers.
- Added unit tests and an asset specification for the potential Better Colony Graphics mod.
- Population and fortification resolution await validation on real FreeCol saves.


### v0.6.2.6.3 — Isometric 9x9 area projection
- Replace the 9x9 rectangle of saved coordinates with a local neighbourhood along the NE and SE screen axes.
- Derive both tile placements and viewport dimensions from the same diamond geometry, avoiding wide ribbons or floating diamonds.
- Add 81-tile topology and edge-sharing regression tests for odd/even centre rows.
- Read-only; pending Windows visual acceptance.

### v0.6.2.6.2 — 9×9 shared-edge lattice correction
- Fixed screen placement so adjacent odd/even staggered rows share edges rather than leaving large gaps.
- Verified the diamond lattice for both odd- and even-Y centres; Windows acceptance testing pending.

### v0.6.2.6.1 — 9×9 local map spacing fix
- Corrected vertical spacing between staggered rows so the 81-tile viewport is no longer compressed into a ribbon.
- Kept coordinate lookup, read-only mode and selection hit testing unchanged.
- Awaiting Windows acceptance testing.

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
