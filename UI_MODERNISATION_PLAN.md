# FreeCol Save Editor — UI Modernisation & PySide6 Port Plan

_Analysis prepared 23 October 2026 by Claude (Anthropic), from the user's screenshots of v0.6.2.6.3 and a read of `main` at commit `a24c569` plus the `feature/better-colony-graphics-foundation` branch. This is a planning document for the coding assistant. It does **not** change any accepted behaviour and does **not** override `ROADMAP.md`'s non-regression and save-integrity principles._

---

## 1. Decision summary

- **Agreed sequence:**
  1. Finish colony graphics, then merge `feature/better-colony-graphics-foundation` to `main` after user acceptance.
  2. Bring the dev2 road/river renderer (currently only in a ZIP) onto `main` as **v0.6.2.6.4**, accepted on Windows.
  3. **Phase 0 refactor**, still on Tkinter, producing no visible change.
  4. Only then continue with 0.6.2.6.5 (coastlines), 0.6.3+ (terrain editing) and the PySide6 port.
- **Hard checkpoint:** do not start 0.6.2.6.5 or any terrain-editing work before phase 0 is done. Both would add validation and drawing logic into the class that phase 0 is meant to split up.
- **Long-term toolkit:** port the UI from Tkinter to **PySide6 (Qt)**. Python stays the language. Packaging stays PyInstaller.
- Phase 0 is worth doing even if the Qt port were later cancelled.

---

## 2. UI problems observed (motivation for the redesign)

From the v0.6.2.6.3 screenshots on a ~2560px Windows display:

1. **Not DPI-aware.** Tiny 9pt text and large dead space. Tk needs `ctypes.windll.shcore.SetProcessDpiAwareness(1)` plus scaled fonts. Qt handles this natively.
2. **Raw IDs instead of names.** Locations show as `building:34830`, `colonyTile:34822`, `unit:33935`, and roles as `model.role.dragoon`. These should resolve to e.g. "Carpenter's House, Christiansborg" or "aboard Merchantman". Raw IDs can stay available in the Raw XML tab or a details row.
3. **Flat 2,525-row unit list.** It should be grouped by colony and location (inside colony / outside / aboard ship), which suits a tree view.
4. **Owner filter defaults to "All players".** It should default to the human player (`ai="false"`), with rivals and natives secondary.
5. **Editing is hidden.** The only cues are blue text and an undiscoverable double-click. Staged edits appear only as a status-bar count, and the status bar is partly cut off. Editable fields need to look editable, changed values need a visible mark, and there should be a persistent "Save (N changes)" control that opens a review list with per-item undo.
6. **Irrelevant inspector tabs are greyed out rather than hidden.** For example, Buildings and Goods appear disabled when a player is selected.
7. **Table basics are missing.** Numbers should be right-aligned. Rows should alternate background colour. Column widths should fit content. Booleans should show as ✓ or blank. Natives and Europeans should be split, since half the columns are N/A for natives.
8. **"Delete selected unit…" sits right next to "Stage equipment change".** Destructive actions should be visually distinct and placed apart.
9. **Map rendering is duplicated.** It appears once as the inspector's Terrain preview and again in a separate Map Editor window. Target state: one map view, available as a main tab.

### Target layout (Qt)

```
┌──────────────────────────────────────────────────────────────────┐
│ Morten.fsg · Turn 155 · Danish        [🔍 Search all…]  [Save (3)]│
├────────────┬───────────────────────────────┬─────────────────────┤
│ MY NATION  │  Christiansborg               │  INSPECTOR          │
│  Overview  │  [Overview|Units|Goods|Build- │  Veteran Soldier    │
│  Colonies ▸│   ings|Map]                   │  ─────────────────  │
│   Christ.. │                               │  Role   [Dragoon ▾] │
│   Carlsborg│  table / tree / map here      │  Moves  [12   ]     │
│  Units     │                               │  Exp    [0    ]     │
│  Ships     │                               │  ─────────────────  │
│ RIVALS ▸   │                               │  Location: Taphus   │
│ NATIVES ▸  │                               │  ▸ Raw XML          │
│ MAP        │                               │  [Delete unit…]     │
└────────────┴───────────────────────────────┴─────────────────────┘
```

The existing user-accepted UI rules still apply: inline editing, no editing popups (confirmation dialogs only), and controls that appear only when relevant.

### Why PySide6 rather than ttkbootstrap or CustomTkinter

- **ttkbootstrap:** lowest effort and keeps the Treeview, but only cosmetic.
- **CustomTkinter:** has no table widget, which rules it out for an app built around tables.
- **PySide6:** offers model/view tables that sort and filter thousands of rows, editor delegates that replace the hand-rolled cell editors, dockable panels, native high-DPI support, and `QGraphicsView`, which suits the isometric map far better than a Tk Canvas.
  - Licence is LGPL, which is compatible with this repo's MIT licence when bundled unmodified.
  - Expected exe size is about 60–100 MB.
  - **First check:** confirm `pip install pyside6` works on the user's Python 3.14.

---

## 3. Code analysis (main @ a24c569)

| Module | Lines | Tk dependency | In the port |
|---|---|---|---|
| `edit_backend.py` | 350 | none | unchanged |
| `deletion_engine.py` | 116 | none | unchanged |
| `movement_rules.py`, `equipment_rules.py` | 62 | none | unchanged |
| `map_geometry.py` | 18 | none | unchanged |
| `terrain_art.py` | 205 | `tk.PhotoImage` only | small adaptation |
| `map_window.py` | 126 | Toplevel + Canvas | rewrite; geometry maths reused |
| `colony_graphics.py` (feature branch) | 82 | Canvas drawing in `draw_colony_placeholder` only | resolver unchanged; drawing rewritten |
| `freecol_explorer.py` | 1,134 | one `Explorer(tk.Tk)` class does everything | split in phase 0, UI rewritten later |

**The save-integrity core is already UI-free.** This covers byte-level XML patching, deletion dependency checks, post-save verification, and the no-overwrite logic in `produce()`. All of it carries over untouched, which is the most important finding.

### Tangles inside `freecol_explorer.py`

1. **Save loading and indexing live in the window class.** This includes `open_save` (ZIP/XML parsing, duplicate-ID checks), `records`, `players`, `locations`, `tiles`, `terrain_by_xy`, `colony_counts`, `goods_types` and `professions`.
2. **Display formatting lives in the window class.** This includes `row_values`, `owner_name`, `loc_name`, `readable`, `short`, `experience_towards`, `building_tier` and the staged-value overlay (`self.edits.get(key, ...)[1]`).
3. **Edit validation is buried in a Tk callback.** `commit_cell_edit()` holds business rules:
   - tax and SoL ≤ 100
   - experience ≤ 200
   - movesLeft ≤ `movement_cap()`
   - other numbers ≤ 2,147,483,647
   - non-negative integers only
   - allowed stances `peace/war/cease_fire/alliance`
   - learnable skill ∈ `professions`
   - drop the edit when the new value equals the original

   Other rules are scattered elsewhere: which fields are editable per entity type (the `permitted=` expression in `render_details` and the guards in `edit_overview`, `edit_unit_list` and `edit_colony_unit`), and the delete-versus-edit conflict checks in `stage_inline_equipment`.
4. **Inline editing is hand-built.** A `ttk.Entry` or `ttk.Combobox` is placed over `Treeview.bbox()`, with `cell_editor`/`editing_cell` state and manual cross-view syncing (`sync_unit_views`). Roughly 200 lines that Qt delegates and models make unnecessary.
5. **Terrain drawing is duplicated and cross-coupled.**
   - The inspector preview has `paint_terrain`, `paint_directional_road`, `paint_directional_river`, `paint_shore_edges` and `direction_endpoint`, plus hit-testing in `diamond_contains` and `on_terrain_click`.
   - `map_window.py` calls straight into the main window's internals: `app.paint_directional_road`, `app.paint_directional_river`, `app.diamond_contains`, `app.tile_item_summary`, `app.readable`, `app.terrain_art` and `app.terrain_by_xy`.
6. **Treeview row IDs are list indices** (`iid=str(i)` into `records[group]`), so selection depends on list position.
7. **Image scaling is low quality.** `terrain_art.py` scales with integer `zoom()`/`subsample()` ratio approximations. `QPixmap.scaled(..., SmoothTransformation)` will look better and may remove the need for Pillow for the colony sprites.

### Existing tests

`test_v061.py` is stale and cannot pass:
- It references `x.TERRAIN_OFFSETS`, which no longer exists; it is now the `terrain_offsets()` method.
- It hard-codes `/mnt/data/...` paths.
- It drives the Tk GUI directly, so it won't survive any UI change.

Replace it during phase 0 with headless tests against the extracted modules.

---

## 4. Phase 0 — refactor on Tkinter (no visible change)

**Precondition:** colony graphics and dev2 are merged and v0.6.2.6.4 is accepted on `main`. Do the work on a new branch (e.g. `refactor/phase0-core-extraction`); `main` stays untouched until the user accepts it.

**Goal:** move every non-UI responsibility out of `Explorer` into modules that import neither `tkinter` nor any UI toolkit, so that a Qt UI can be built on the same core later. **The user must see no difference in behaviour or appearance.**

### Proposed modules

1. **`save_document.py` — `SaveDocument`**
   - `SaveDocument.load(path)` contains today's `open_save` parsing and validation: the ZIP check, the `<game>` check, and the authoritative colony/settlement duplicate-ID checks. It raises on error and contains no messageboxes.
   - Attributes: `path`, `xml_bytes`, `root`, `game`, `players`, `colonies`, `native_settlements`, `units`, `tiles`, `terrain_by_xy`, `colony_counts`, `native_counts`, `goods_types`, `professions`, `turn`.
   - Lookups: `owner_name(id)`, `location_name(id)`, `unit_by_id(id)`, `colony_at_tile(tile_id)`, `tile_items(tile)`, `tile_item_summary(tile)`.
   - Keep the *authoritative-records-only* rules from 0.5.1 exactly as they are.

2. **`edit_session.py` — `EditSession`**
   - Owns the `edits` dict and keeps today's key shape `(object_id, field) → (old, new)` exactly, so `edit_backend.produce()` works unchanged.
   - `editable_fields(entity_kind, element)` gives one central answer to "what may be edited here?"
   - `validate(key, raw_value)` returns the parsed value or raises with today's error messages. It contains all the ceilings and choice lists listed in §3.
   - `stage(key, original, new)` includes the existing "equal to original, so remove the edit" behaviour and the delete-versus-edit conflict checks.
   - Also: `unstage(key)`, `staged_value(key, default)`, `is_changed(key)`, `count`, `items()`.
   - `stage_equipment(...)`, `stage_unit_deletion(...)` and `stage_settlement_deletion(...)` wrap the existing `validate_equipment` and `plan_settlement` calls.
   - `save_as(source, destination)` delegates to `produce()` and keeps every existing no-overwrite guard.

3. **`presentation.py`** — pure formatting functions: `readable`, `short`, `experience_towards`, `building_tier`, and `row_values(kind, element, doc, session)`. These return plain tuples.

4. **`map_render.py`** — renderer-neutral map logic.
   - Inputs: tile, centre, tile width and height.
   - Outputs: lists of primitives, e.g. `("polygon", points, style)`, `("polyline", points, width, colour)`, `("image", key, x, y)`.
   - Covers road and river paths (including whatever dev2 introduces), shore edges, `direction_endpoint`, `diamond_contains` and click resolution. `terrain_offsets` moves here or into `map_geometry.py`.
   - Tk Canvas and `map_window.py` then just *execute* these primitives. Later, Qt executes the same list with `QPainter` or `QGraphicsScene`.
   - Merge the two duplicated painting paths (inspector preview and Map Editor) into one.

5. **`terrain_art.py`** — separate *finding and reading image bytes* (installation search, JAR/ZIP reading, candidate filenames: UI-free) from *turning bytes into a `tk.PhotoImage`* (a thin Tk adapter). Qt then gets its own adapter producing `QPixmap`.

6. **`colony_graphics.py`** — keep `resolve_colony_graphic`/`population_size` UI-free and treat `draw_colony_placeholder` as Tk adapter code.

After phase 0, `freecol_explorer.py` and `map_window.py` contain only widgets, layout, event wiring, and calls into the modules above.

### Tests to add (headless, no Tk)

- `SaveDocument` loads the user's sample save. Counts match the current status bar (e.g. turn 155, 17 players, 64 colonies, 227 native settlements, 2,525 units for `Morten.fsg`).
- Map regression fixtures from `ROADMAP.md`:
  - even-Y neighbours at Christiansborg (83,118)
  - odd-Y neighbours and the three-way major river at (69,111), style 2220
  - the four lake tiles around (67,110)
- `EditSession.validate`: each ceiling, the non-negative-integer rule, the choice lists, equal-to-original unstaging, and the delete-versus-edit conflicts.
- Round trip: stage a representative set of edits, `save_as` to a temp file, and confirm `produce()`'s post-save validation passes and the original file is byte-identical.
- `map_render`: hit-testing at diamond edges and road/river primitives for known styles.

Use a small redacted sample `.fsg` kept outside git, or a path from an environment variable. Never commit user saves.

### Phase 0 acceptance

- Every existing feature behaves identically on the user's Windows machine. Compare against the screenshots accepted at 0.6.2.6.4.
- An edited save made after the refactor loads in FreeCol, advances a turn and resaves. This is the existing acceptance standard.
- Headless tests pass, with evidence shown (actual command output).

---

## 5. Later phases (PySide6), for orientation

| Phase | Content | Rough size |
|---|---|---|
| 1 | Qt main window, read-only: navigation tree, `QAbstractTableModel` + `QSortFilterProxyModel` tables (name-resolved locations, grouping, right-aligned numbers), context-sensitive inspector, global search, human player as default focus | ~2 sessions |
| 2 | Editing: item delegates wired to `EditSession.validate`, visible changed-value marking, staged-changes panel with per-item undo, equipment and deletion actions (destructive actions separated), Save As via `produce()` | 1–2 sessions |
| 3 | Map as a `QGraphicsView` tab executing `map_render` primitives; `QPixmap` terrain adapter with smooth scaling; colony sprites; one map widget reused for the colony neighbourhood view | 1–2 sessions |
| 4 | PyInstaller spec for PySide6, clean-machine test, exe size check, FreeCol artwork still loaded from the local install only | 1 session |

Estimated total, including phase 0: **about 6–8 working sessions**, plus the user's Windows and in-game testing between phases. During phases 1–3 the Tk UI keeps working, because both UIs sit on the same core. The Tk UI is retired only after the Qt version is accepted.

---

## 6. Guardrails (unchanged from the project's own rules)

- Never overwrite the original or any existing save. Edits are staged and written only through Save As.
- `main` stays safe. Each phase goes on its own branch and is merged only after the user accepts it on Windows.
- Report test results honestly with actual evidence. A build that compiles is not an accepted build.
- Do not redistribute FreeCol artwork; load it from the user's installation.
- Do not change accepted map geometry (the 0.6.2.6.3 diagonal-axis 9×9 layout, staggered-row parity rules).
