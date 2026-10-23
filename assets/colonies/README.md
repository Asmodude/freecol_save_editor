# Better Colony Graphics — asset specification

**Status:** Design Direction Sheet Version 3 approved 2026-10-22. All 12 settlement graphics visually accepted by the user in the Windows Map Editor on 2026-10-23. Software release acceptance remains separate.

## Authoritative art direction — Version 3
- Early Boston / New England colonial architecture; hand-painted three-quarter-isometric strategy-game illustrations, neutral across nations.
- **Geography-neutral:** no coastlines, docks, boats, shoreline/water, or fixed terrain features baked into any core settlement sprite. Future harbour decorations must be separately placed using actual terrain geography.
- **Colony:** unfortified buildings and courtyards; **Stockade:** vertical palisades; **Fort:** unmistakable earthworks with exterior horizontal timber revetments and low, sloped embankments inspired by Fort William Henry; **Fortress:** massive permanent stone masonry.
- At ~80–120 px, `fort_large` must not resemble `fortress_small`; silhouettes and building materials must differ clearly.
- Full artwork must fit inside the PNG with genuine transparent margins, consistent camera perspective and an appropriate anchor; verify these per production asset against FreeCol's rendered map.
- The original harbour-bearing `colony_large.png` was replaced by a geography-neutral production asset, which passed Windows map-scale acceptance.
- All twelve production PNGs are now present, and every state has passed user visual inspection using the temporary 12-state development preview (subsequently removed).

The planned nation-neutral artwork consists of twelve complete replacement images. Fortification level is **baked into** each sprite (never composed as an overlay):

| Fortification | Small (1–3) | Medium (4–7) | Large (8+) |
|---|---|---|---|
| None | `colony_small.png` | `colony_medium.png` | `colony_large.png` |
| Stockade | `stockade_small.png` | `stockade_medium.png` | `stockade_large.png` |
| Fort | `fort_small.png` | `fort_medium.png` | `fort_large.png` |
| Fortress | `fortress_small.png` | `fortress_medium.png` | `fortress_large.png` |

## Production artwork acceptance (2026-10-23)

| State | Acceptance | Evidence |
|---|---|---|
| `colony_small` | Accepted | Windows map preview |
| `colony_medium` | Accepted | Windows map preview (Frederiksborg) |
| `colony_large` | Accepted visually | Revised geography-neutral asset, normal map layering verified |
| `stockade_small` | Accepted | User inspected and approved |
| `stockade_medium` | Accepted | Taphus Windows screenshot |
| `stockade_large` | Accepted | User inspected and approved |
| `fort_small`, `fort_medium`, `fort_large` | Accepted | Windows 12-state map preview; timber-and-earth design |
| `fortress_small`, `fortress_medium`, `fortress_large` | Accepted | Windows 12-state map preview; stone-masonry design |

User acceptance here is **visual artwork acceptance**, not acceptance of the combined software branch or of savegame editing regressions.

## Visual requirements
- A strong, distinctive silhouette at typical 9×9 map zoom levels.
- No nationality or owner indicators baked into the sprite (**Option A**).
- Clearly distinguish 4 defence tiers and 3 settlement sizes.
- Transparent-background PNGs, visually centred over the settlement tile.
- Consistent visual projection and footprint across all 12 images.
- Artwork must be original and suitable for potential separate **Better Colony Graphics** FreeCol mod.

## Rules and limitations
- `colony_graphics.py` maps population and fortification to a key. No save modification.
- The initial population reader counts nested worker `unit` objects; confirm against FreeCol's `getApparentUnitCount()` in actual saves before acceptance.
- The stockade/fort/fortress detection scans building type IDs and chooses the highest tier found.
- Missing PNGs are represented by an unmistakable high-contrast **placeholder marker**.
- The development Map Editor currently loads available `assets/colonies/{key}.png` images with Pillow, scales them without distortion, and uses a placeholder where missing.
- Native settlements require separate treatment and are outside this first implementation.

## Validation
Run `python -m unittest test_colony_graphics.py`.
Verify all 12 resolution keys, both nationality-independent cases, graphic footprint, map hit-testing, and navigation to colony on Windows.
