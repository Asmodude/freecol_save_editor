# FREECOL SAVE EDITOR — CROSS-CHAT HANDOVER
**Prepared 22 October 2026 — continuity document, NOT a release note.**

> This document is written to allow a new ChatGPT conversation to resume development without losing the decisions, tests, architecture, historical pitfalls, or artwork direction. **Read this entire file and the linked repository files before modifying code.** User wants cumulative, non-regressing development and does NOT want repetitive assurances in every answer that previously accepted features are retained.

## 0. USER'S IMMEDIATE PROBLEM AND NEXT ACTION
- The newest `colony_small.png` pilot file was linked via `sandbox:/mnt/data/colony_small.png`, but **clicking its chat download link scrolls the conversation back to a very old message**, instead of downloading. Repeating the link did NOT help. The user therefore requested this handover early, after suffering lost context in a previous Elemental Regression project.
- **DO NOT suggest the same broken sandbox link without a different delivery mechanism.** Best durable route: commit an actual asset through GitHub to the feature branch (the current GitHub tools handle UTF-8 text; discover whether a GitHub binary-upload method exists, or use git push via another supported tool). Otherwise supply a verified fresh ZIP as an alternative and fully explain limitations. The pilot may require file attachment re-upload in a new conversation.
- User intentionally remains on `main` during experimental artwork work. Do not merge the development branch without approval.
- Immediately next: **test ONE image (`colony_small.png`) in the editor at actual map scale**, inspect readability, transparency and placement. Do not generate the other 11 production assets until acceptance.
- Current design direction fully approved: 12 **nation-neutral** variants in early New England/Boston style, unfortified -> wooden stockade -> timber-and-earth frontier fort (Fort William Henry inspiration) -> substantial stone fortress. No national emblems or fortification overlays baked on top of base colony art; each variant is its own complete PNG. Fort tier must not resemble stone fortress tier.
- The most recent pilot `colony_small.png` was a **provisional extracted concept thumbnail** (approximately 368×172 PNG with alpha), NOT final production artwork; quality/edges need review.

## 1. PROJECT AND GITHUB
- Project: **FreeCol Save Editor**, Python/Tkinter desktop savegame editor for the open-source FreeCol game, user's installed version **1.2.0**, Windows 11. `.fsg` saves are ZIP files containing large `savegame.xml`.
- Repository: https://github.com/Asmodude/freecol_save_editor
- GitHub Desktop is installed and user has cloned the repository on Windows, current branch **`main`**.
- GitHub repository access through ChatGPT GitHub connector was verified; user granted push permissions. ALWAYS fetch actual current files/branch before modifications. `main` should stay safe.
- Accepted map geometry release committed on `main`: **v0.6.2.6.3**; this is the app shown in user's correct 9×9 screenshot.
- **Experiment**: `v0.6.2.6.4-dev2` prototype implementing Java-like road/river art was distributed as a ZIP, **not merged to main**. On user's Windows machine it **worked beautifully**: actual dark textured, winding rivers, correct branches; native-looking brown curved roads. User exclaimed “Aaaannd BINGO!” The experiment needs further compare/acceptance and porting to GitHub branch before becoming a release.
- Current independent dev branch: **`feature/better-colony-graphics-foundation`**, based on main. Files:
  - `colony_graphics.py`: population+fortification -> 12 asset keys, fallback drawing.
  - `map_window.py`: colony placeholder rendering, optional Pillow PNG loading from `assets/colonies/`, chosen image key printed in inspector.
  - `test_colony_graphics.py`: initial unit tests (written, not executed by ChatGPT).
  - `assets/colonies/README.md`: technical design.
  - Branch's `CHANGELOG.md` and `ROADMAP.md` updated.
- `main` contains `README.txt` (MAJOR versions only), `CHANGELOG.md` (ALL detailed versions), `ROADMAP.md` (future), and Python source.
- Recent files include `freecol_explorer.py`, `map_window.py`, `map_geometry.py`, `terrain_art.py`, `edit_backend.py`, `deletion_engine.py`, `equipment_rules.py`, `movement_rules.py`, various `test_*.py`. Do not delete/reorganize before 0.9 refactor and regressions.
- A prior chat assistant sometimes claimed compilation/ZIP validation without enough independent evidence. Use honest evidence. No false “published” or “passed tests.”
- User wants eventually bundled Windows executable via PyInstaller including Python, Tkinter, Pillow; source runs via Python. User has Python **3.14** and installed **Pillow 13.0.0** and pip **26.2.2**. Regular non-admin PowerShell works.
- User's game artwork location: `C:\Program Files\FreeCol\app\data\default\resources\images\` (Windows Explorer Danish UI may label Program Files as `Programmer`). Do not redistribute FreeCol art in external mod/editor bundles; use local installed resources.
- Savegame path historically `C:\Users\morte\OneDrive\Dokumenter\freecol\save`; actual current path may vary. Never overwrite saves or put user saves into GitHub.

## 2. VERSION / ACCEPTANCE HISTORY (tested user reports)
### 0.1–0.5.5 — functional editor
- 0.1 read-only Players, Colonies, Native settlements, Units; 0.2 colony buildings, goods, side-by-side detail, filtering.
- 0.3 safe staged edits, Save As, no overwrite; 0.3.1 IN-LINE editing preferred (no editing popups).
- 0.4 editable player gold/tax/unit XP; XP 0–200, later learning chance; 0.4.1 create missing goods stock; 0.4.2 edit XP in colony unit view; 0.4.3 edit local SoL, correctly recompute local rebel count/liberty while **never changing national Founding Father liberty**. Validated in game.
- 0.5 native diplomacy: tension, stance, local alarm, learnable skills. Tupi/Cururu example: local alarm 1100→500 remains “Content” after turn despite nation Hateful/War.
- 0.5.1 only authoritative native settlements—XML contains duplicate cached copies by other players; avoid owner ambiguity.
- 0.5.3 unit/native settlement deletion with dependency checks; tested in game, with refusal for unsafe references. `indianSettlement:31267` = Cururu; a brave `unit:30212` associated with Roraima; caution around mission references and AI.
- 0.5.4 movement max from actual unit+role rules (Soldier 3, Veteran Soldier Dragoon 12). 0.5.5 equipment editing (Soldier muskets, Dragoon muskets/horses, Scout horses, Pioneer 20–100 tools) without removing goods from warehouses. Keep inline selection.
- Outstanding caveats user explicitly stated: hardy pioneer with zero tools shows `model.role.default`, inconvenient; edit label should show **20,40,60,80,100 tools**, not pioneer sets 1–5. Some context-sensitive UI refinements were accepted; controls should only appear when relevant unit/native settlement selected.

### 0.6 map progress
- 0.6.1 click/select nine colony tiles, parser finds resources and tile improvements under `<tileItemContainer>`; user verified 36/36 adjacent tile coords across 4 colonies.
- **Staggered coordinate rule** from official Java `Direction.java`: all N/S = `(x,y±2)`; E/W = `(x±1,y)`; diagonals change with **Y parity**:
  - ODD Y: NE `(+1,-1)`, SE `(+1,+1)`, SW `(0,+1)`, NW `(0,-1)`.
  - EVEN Y: NE `(0,-1)`, SE `(0,+1)`, SW `(-1,+1)`, NW `(-1,-1)`.
- 0.6.2 series load original FreeCol terrain textures, forests, plows; map imagery atlas; accurate diamond click selection user verified.
- 0.6.2.5.X fixed odd/even coordinate parity in river map.
- 0.6.2.6 standalone Map Editor opens separate window, arbitrary coord centre and 9×9 map, read-only.
- 0.6.2.6.1/2 failed geometric attempts (ribbon or gaps). **0.6.2.6.3 succeeded** selecting 81 tiles along map NE and SE *diagonal screen axes*, producing compact connected diamond-shaped 9×9 world around centre. User enthusiastically accepted screenshot. Geometry implemented `map_geometry.py` and `map_window.py`. **Do not revert to rectangle of X/Y coordinates or change spacing alone**.
- 0.6.2.6.4-dev2 native renderer experimental ZIP (off-main) **visually succeeded**; next user report confirmed roads near Christiansborg. Need preserve and integrate carefully via proper branch and regression tests.
- Current map centre test `(67,110)`: adjacent four water/lake tiles `(66,109)`, `(67,108)`, `(67,109)`, `(68,110)`; river junction `(69,111)` has style `2220`, magnitude 2, terrain savannah; test all river branches and correct parity.
- Christiansborg `colony:32435` at `(83,118)`. Several Danish colonies listed (Charlotte Amalie, Carlsborg, Taphus, Frederiksborg, Augustborg, Koralbugt) in prior saves.
- Important resource: silver finite quantity example **438** at `(82,127)`; `quantity=-1` means unlimited. Coastline special fish bonus encoded tile improvement rather than ordinary resource.
- Currently terrain editing **READ ONLY**. Do NOT enable until all rules and dependency checks developed.

## 3. OFFICIAL FREECOL JAVA RENDERER RESEARCH — FINDINGS
Official source: https://github.com/FreeCol/freecol
- `src/net/sf/freecol/client/gui/mapviewer/RoadPainter.java`: roads drawn as Java vector paths, NOT native road PNGs. Detect neighbouring `getRoad()` and `isComplete()`. 0 exits => crossing strokes; 1 => straight from centre; 2 => quadratic Bézier through centre; 3–4 => specific skipped adjacent connection pairs; >=5 => centre rays. Road color defined in resources: `color.map.road=urn:color:0x804000`.
- `src/net/sf/freecol/client/gui/mapviewer/TileViewer.java`: terrain, improvements, settlements, river transitions order.
- `src/net/sf/freecol/client/gui/images/RiverAnimationImageCreator.java`: river composited from `image.tile.river.pebbles`, `image.tile.river.water`, directional masks; variants from connections NE/NW/SE/SW; minor vs major based on magnitude; minor-to-major transitions, alpha masks, enlarged bank mask, tile boundary clip. Native image URLs from `data/default/resources.properties`, e.g. `terrain/river/pebbles.png`, `terrain/river/center0.png`, `terrain/river_masks/river_mask_ne_nw_se.png`, `river_mask_minor_ne_sw.png`, `river_mask_to_major_ne.png`.
- Preserve locally installed FreeCol graphics rather than embedding game's copyrighted artwork.
- `src/net/sf/freecol/client/gui/ImageLibrary.java` selects colony images by *apparent population* 1–3 small, 4–7 medium, 8+ large, then fortification level `stockade`, `fort`, `fortress`, plus nationality graphic family. Existing Danish stock uses Dutch sprite; Swedish English, Russian French, Portuguese Spanish. User dislikes how original colony art blends into terrain.
- Crucial: comparing current Java `master` to FreeCol v1.2.0 where necessary.

## 4. BETTER COLONY GRAPHICS — ARTWORK DIRECTION DECIDED
Potential future independent mod **“Better Colony Graphics”** in addition to editor. User wants sprites to be prominent, distinguishable at a glance, rather than blend in.
- **Nation-neutral OPTION A**: no nation-specific skins or flags in image, no owning-nation indicators baked in. A separate optional ownership indicator may be considered later, but user explicitly chose A over B.
- Names exactly:
```
colony_small.png    colony_medium.png    colony_large.png
stockade_small.png  stockade_medium.png  stockade_large.png
fort_small.png      fort_medium.png      fort_large.png
fortress_small.png  fortress_medium.png  fortress_large.png
```
- **Standalone composite final illustration for each state**; NOT “colony size PNG plus a fortification overlay.”
- Relative population sizes: 1–3 small, 4–7 medium, 8+ large. Need validate with `getApparentUnitCount()` against actual saves. Prototype naïvely counts nested XML units; may differ; treat as unverified.
- **ART STYLE NOW ACCEPTED FOR CONCEPT SHEET**: isometric 17th/18th-century early Boston / New England wooden colonial buildings, pitched shingle roofs, chimneys, small yards/workshops; earth-toned cohesive hand-painted strategy art, recognizable silhouettes.
- Avoid initial **Roman/Mediterranean look** (domed towers, stucco stone arches, red terracotta tile roofs). That design was rejected.
- User enthusiastically approved complete 12-image **concept sheet** across 4 defence tiers and 3 settlement sizes.
- Fort row **revised from stone to earth-and-timber frontier fort** after discussing British **Fort William Henry** at Lake George (built 1755, destroyed 1757, NOT 1760s; user explicitly appreciated correction). Earth ramparts, timber revetments, cannons, no massive masonry; may have bastions, but visually distinct from massive permanent stone fortresses. User approved revised sheet (“Now we're talking!!!”, “Yes I love it.”).
- Progression:
  - Colony: no defenses, small 2 modest houses -> medium village -> large town with meeting house.
  - Stockade: timber houses inside vertical wooden palisade, gate/watchtower.
  - Fort: serious timber and earth military defenses, cannon positions, varied footprint, Fort William Henry reference.
  - Fortress: very substantial masonry fortifications / angled bastions and more heavy artillery.
- User wants **exactly one image pilot** before producing full 12 sprite set. Target `colony_small.png`, true alpha transparency, just settlement, no labels, consistent isometric scale and proportions; test in map viewer.
- Prior image-generation attempts repeatedly produced **entire 12-cell concept sheets despite request for one sprite**. Finally prior assistant cropped 368×172 `colony_small.png` from sheet with transparency (pilot only), placed in `/mnt/data/colony_small.png`; the user **couldn't download** due to chat-link scrolling bug.
- Need assess source crop alpha and fidelity and perhaps render a new isolated sprite properly. Don't assume the crop is high-quality finished art. Check readability at approximately ~100 px width in actual editor. Need maintain consistent footprints for future mod.
- User's artwork concept filenames in this chat included `kolonier_og_befæstninger_i_isometrisk_stil.png` and `bedre_koloni_grafik_bosættelser_og_fæstninger.png` (actual sandbox availability across new chat NOT assured). Original screenshot/concept sheets can be reuploaded if needed; source brief here should suffice.

## 5. FEATURE BRANCH STATE AND RISKS
`feature/better-colony-graphics-foundation`:
- `colony_graphics.py` provides dataclass `ColonyGraphic`, functions `population_size`, `resolve_colony_graphic`, and `draw_colony_placeholder`; builds key `{tier}_{size}`. `FORT_RANK` maps building types `model.building.stockade`, `model.building.fort`, `model.building.fortress`. Uses `assets/colonies/{key}.png` if present.
- `map_window.py` overlays placeholders or image via Pillow and `ImageTk.PhotoImage`; scaling currently `factor=min(tw*.68/sprite.width, th*1.28/sprite.height)`. Map uses tile IDs to identify colonies from authoritative records. Do not replace original terrain with colony sprite.
- In known branch code, placeholder marker may be drawn **beneath selection outline**, image is on top of terrain and improvements.
- `test_colony_graphics.py` was written but **NOT VERIFIED RUNNING**; also no GUI test on user Windows.
- Known potential problem: image and rendering parts may not port to accepted dev2 river renderer yet (they are in different artifact lines). Need integrate only after evaluating safe merge.
- Need verify source version and `map_window.py` actual state on each branch; don't rely on old snippets.

## 6. USER INTERFACE AND GUARDRAILS
- Inline edits; avoid modal popups except confirmation/unsafe-operation refusal; context-sensitive controls only when relevant.
- Unit equipment edits under Units detail; no permanent unit/native-settlement deletion buttons when those types not selected.
- Separate Map Editor button beside Owner at top of main window; opens freely navigable map at any coordinate; if selected tile has colony, Go to colony opens conventional detail.
- Selection and mouse hits precisely coincide with visible diamonds; resizing must preserve proportions. Tests with extreme border clicks previously passed.
- Future native settlements also need map icons but separate design decision.
- No user-save corruption: original `.fsg` never overwrite, staged edits, Save As a new filename, ZIP/XML integrity check, after-turn FreeCol verification.
- User expects release nomenclature and strict acceptance: completed compilation != passed actual Windows/game test.

## 7. REMAINING ROADMAP
Detailed `ROADMAP.md` in GitHub controls milestones. Broadly:
- 0.6.2.6.4 official-like roads/rivers — prototype visual success but NOT accepted/merged yet. Need compare river and road style against actual game, esp (69,111).
- Coastline/terrain transitions later; current ocean/lake tiles lack natural shoreline blending.
- 0.6.3 roads and plow editing, 0.6.4 resource changes incl finite quantities, 0.6.5 terrain type/forest changing, 0.6.6 validation.
- 0.7 European colony deletion (delete working units and buildings but preserve visiting/stationed units when safe), building add/remove/upgrade, workforce management, adding population requires separate research.
- 0.8 advanced ownership, native territory, unit placement, bulk operations after single-tile safety.
- 0.9 refactor, tests + GitHub Actions, Windows exe with embedded Pillow and Tkinter (PyInstaller), release candidate.
- 1.0 verified first stable release.
- **No regressions**, do not need to tell user on every build that accepted functionality remains.

## 8. NEXT CHAT — SPECIFIC FIRST MOVES
1. Read this handover and `ROADMAP.md`, `CHANGELOG.md`, code on both GitHub branches. Do not ask user to repeat established design.
2. Address unreliable sandbox link directly. Consider supplying **GitHub-hosted binary asset** instead, or a distinct verified ZIP, and instruct workflow avoiding UI scroll glitch. Do not assume files carry forward to new session; only link paths verified in that session.
3. Continue **single `colony_small` sprite pilot**; establish size, transparent alpha, visual quality; use user screenshots to assess against terrain. Avoid generating entire 12-sheet as substitute for individual PNG.
4. Integrate image on development branch, run Python tests and GUI rendering checks and have user switch branch explicitly for testing; `main` unchanged.
5. Only after user's acceptance generate other 11 final assets, commit artwork responsibly with clear original-art licensing/mod plan.

## 9. TONE / RELATIONSHIP
User enjoys our ongoing playful roleplay of Danish Admiral **Ove Gjedde**, **Sir Thorwald Kilgannon Inter** (joke expansion of Tkinter), assistant Petersen, Royal Archivist, Roland Crappé, Fort Dansborg; “**Tribulations**” is favourite vaguely archaic expression. Keep jokes light and often after clear practical instructions.
But careful technical accuracy and robust continuity are more important than comedy. User specifically suffered significant time and context loss in prior **Elemental Regression** project; this handover exists to prevent recurrence. User likes enthusiastic “BINGO” when screenshots validate success, but does not want premature claims.

## 10. VERIFIED GITHUB LINKS
- Repo: https://github.com/Asmodude/freecol_save_editor
- Main roadmap: https://github.com/Asmodude/freecol_save_editor/blob/main/ROADMAP.md
- Main changelog: https://github.com/Asmodude/freecol_save_editor/blob/main/CHANGELOG.md
- Better Colony Graphics branch: https://github.com/Asmodude/freecol_save_editor/tree/feature/better-colony-graphics-foundation
- Prototype resolver: https://github.com/Asmodude/freecol_save_editor/blob/feature/better-colony-graphics-foundation/colony_graphics.py
- Concept/asset specification: https://github.com/Asmodude/freecol_save_editor/blob/feature/better-colony-graphics-foundation/assets/colonies/README.md

**END HANDOVER — next assistant should continue work rather than reconstruct the project's history by guesswork.**
