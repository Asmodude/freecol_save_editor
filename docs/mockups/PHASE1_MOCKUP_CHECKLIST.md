# Phase 1 Approved Mockup — Written Checklist

Image: [`phase1_approved.png`](phase1_approved.png) (1536×1024). Approved by the user on 23 October 2026, with two changes:

1. No duplication between the workspace and the contextual inspector.
2. A conspicuous Map Editor entry point in the top toolbar.

_This checklist exists so the design survives outside any chat conversation. Written by Claude (Anthropic) on 24 October 2026 from the image itself. **The repository copy of the image and this file are the source of truth for the Phase 1 visual design.**_

---

## 0. How to read the mockup (important)

The mockup is a **visual design target, not a data specification.** It was drawn with illustrative values, and some of its columns do not exist in a FreeCol save:

- **France's colonies** (Fort Louis, Quebec …), all **coordinates** and all **counts** are illustrative.
- **Defence %, Status (Growing/Established/Flourishing/Poor), Prosperity (Rich/Middling/Destitute), "Connected to Europe" and a colony "Learnable Skill"** are not saved colony attributes.
- There is no **Production** tab data source today.

**Rule:** show only values that are stored in the save or that are derived from documented FreeCol rules and labelled as derived (the existing project rule: never invent or infer data). Where a mockup column has no real source:
- replace it with a real field of similar visual weight, e.g. the existing Colonies columns: Established, Liberty, Sons of Liberty, Production bonus, Population, Buildings; or
- omit it.

Follow the **look**: icons, flags, layout, typography and grouping. Do not follow the **numbers or invented fields**.

---

## 1. Window frame

- [ ] Window title: `FreeCol Save Editor — Qt Preview (READ ONLY)`, with a small app icon (crown motif in the mockup).
- [ ] **Menu bar:** `File`, `View`, `Help`.
  - Minimum: File → Open Save…, Exit; Help → About.
  - Add View entries as they become real; no menu item may be non-functional.
- [ ] **Status bar, left:** `17 players · 64 colonies · 227 native settlements · 2520 units` (real counts).
- [ ] **Status bar, right:** `Morten2.fsg · Turn 155 · READ ONLY`.

## 2. Toolbar

- [ ] `Open Save…` button **with a folder icon**, visually primary.
- [ ] `Open Map Editor` button **with an icon**, shown disabled/greyed until Phase 3, with the existing explanatory tooltip.
- [ ] To the right, a **file metadata strip** separated by thin vertical dividers: file name · Turn · human nation · Difficulty · Map · Version.
  - Only show items present in the save, e.g. from the Game properties data. Omit any item that isn't available rather than guessing it.
- [ ] Keep the existing `Search all…` global search. It is not in the mockup, but it is an accepted Phase 1 feature: place it consistently in the toolbar (or as a search field) with a magnifier icon.

## 3. Navigation tree (left pane, header "Savegame")

General:
- [ ] **Every node has a meaningful icon.** No generic OS folder/file/computer icons (`QStyle.StandardPixmap.*` must be gone).
- [ ] Nation rows are bold, with the nation's **flag** to the left.
- [ ] Counts in parentheses on collection nodes: `Colonies (11)`, `Units (28)`, native nations `Aztecs (18)`, `All native settlements (227)`.
- [ ] Expand/collapse chevrons. Comfortable row height; icons ~16–20 px, vertically centred with the text.

Structure and icons, in mockup order:

| Node | Icon in mockup | Notes |
|---|---|---|
| `Denmark (Player)` | Danish flag | Human nation; label uses real nation name |
| ‣ Overview | document/scroll | |
| ‣ Diplomacy | seal/medallion | Required for Phase 1 (see `docs/PHASE1_ASSESSMENT.md` §4.1) |
| ‣ Colonies (n) | small colonial house | Expands to named colonies (existing behaviour) |
| ‣ Units (n) | red cross/soldier motif | Keep existing colony/ship/field sub-grouping |
| ‣ Goods | barrel/sack | |
| ‣ Research | globe | Not Phase 1 scope; may stay "(planned)" |
| ‣ Founding Fathers | statue/figure | |
| ‣ Player Options | gear | Not Phase 1 scope; may stay "(planned)" |
| `Rival Nations` | crown | Section heading, bold |
| ‣ England / France / Spain / Netherlands … | **each nation's flag** | Same child structure as the player nation |
| `Native Nations` | sun/feather emblem | Section heading, bold |
| ‣ All native settlements (n) | settlement icon | |
| ‣ Aztecs (n), Inca (n), Sioux (n) … | **round tribal emblem per nation** | Count = that nation's settlements; must also expose the native player Overview (assessment §4.1) |
| `Map` | globe | Phase 3; stays "(planned)" |
| `Game Options` | gear | The mockup's name for the current **Game properties** node; rename or keep, but use the gear icon |

- [ ] Selected node: full-width soft blue highlight, legible in light and dark themes.
- [ ] "(planned)" nodes: dimmed, but still with their proper icon, not a generic one.

## 4. Workspace (centre)

**Header band:**
- [ ] Large emblem of the scoped nation at the left (fleur-de-lis for France in the mockup; use that nation's flag or coat of arms).
- [ ] Title in large bold text: `France — Colonies (15)`.
- [ ] Subtitle in smaller muted text: `All colonies owned by France`.
- [ ] The **filter field sits in the header, right-aligned**, with a magnifier icon and contextual placeholder (`Filter colonies…`). It replaces the current full-width filter line above the grid.

**Main grid:**
- [ ] **A small icon at the start of each row** for the record type (colony sprite or house icon for colonies; unit-type icon for units; goods icon for goods).
- [ ] Sort indicator on the active column header.
- [ ] Numbers right-aligned, alternating row shading, soft blue selected row. These are already implemented; keep them.
- [ ] Value icons where the value has an obvious symbol (shield before a defence-type value, coloured icons for categorical values), **only for real fields** (see §0).

**Detail tabs below the grid:**
- [ ] Underlined/pill style with the active tab highlighted.
- [ ] The mockup shows `Overview | Buildings | Units | Goods | Production | Location` for a colony.
  - Keep the existing real tabs: Buildings, Workers, Stationed units, Goods.
  - Add `Location` only if it has real content (tile type, river, road, special resource from the colony tile, all available via `SaveDocument` tile lookups).
  - Omit `Production` until there is a real data source.
- [ ] **The Overview tab is a visual layout, not plain text:**
  - **colony artwork** on the left (use the project's own approved Better Colony Graphics sprite for the colony's size and fortification tier, which the project owns and may display);
  - the record name as a bold heading;
  - **two bordered two-column property grids** (label | value) side by side;
  - owner shown with its flag.
  - This replaces the current `QPlainTextEdit` overview.

## 5. Inspector (right pane)

- [ ] Header: `Inspector — <selected name>`.
- [ ] **Artwork at the top** for the selection: colony sprite for colonies, and a unit or nation image where available locally.
- [ ] A **two-column property grid** (label | value), with flag and icon decorations on values such as Owner and categorical fields. This replaces the plain-text Details box.
- [ ] Section heading `Additional information` with a second property grid.
- [ ] Section `Actions`, showing a muted rounded box: `Read only — no values can be changed in this version.` In Phase 2 this box becomes the action area.
- [ ] **No duplication with the workspace** (approval condition 1).
  - The workspace Overview shows the *scoped record in context*; the inspector shows the *currently selected object*.
  - When both refer to the same record, the inspector should add value (Raw XML access, identifiers, jump actions) rather than repeat the same grid.
  - Keep the existing `Raw XML` access and jump buttons (`Open colony Goods →`, `Open full unit record →`) in or near the Actions area.

## 6. Visual style

- [ ] Light, clean, Windows 11-like look: white panes, light grey separators, soft blue selection.
- [ ] Consistent spacing; panes separated by thin borders; rounded inputs and buttons.
- [ ] Section headings bold, secondary text muted grey.
- [ ] All colours must come from the palette or a single stylesheet, so the dark theme stays legible. Verify both themes on Windows.

## 7. Artwork sources and rules

- **Nation flags, native emblems, unit/goods icons:**
  - Load from the **locally installed FreeCol** resources via `freecol_art_source` (locate the actual resource keys and files on the user's installation; verify them, don't assume paths).
  - Never bundle FreeCol artwork in the repository or the exe.
- **UI glyphs with no FreeCol equivalent** (Overview, Diplomacy, Research, Player Options, Game Options, Map, folder, magnifier): use a small, licence-compatible icon set committed to the repo with its licence noted, or simple drawn icons.
- **Colony artwork:** the project's own `assets/colonies/*.png` (Better Colony Graphics).
- **Fallbacks:** if an asset is missing, show a neutral, tasteful placeholder of the same size. Never leave a blank gap or a broken image.

## 8. Acceptance

Phase 1 is visually accepted only when the user has compared the running Qt window side by side with `phase1_approved.png` on Windows and confirmed:

- every navigation node has a meaningful icon and every nation has its flag or emblem (§3);
- the header band, header filter and row icons are present (§4);
- the Overview and Inspector use property grids and artwork rather than plain text (§4, §5);
- light and dark themes are both legible (§6);
- **no invented data appears anywhere** (§0).
