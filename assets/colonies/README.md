# Better Colony Graphics — asset specification

**Status:** technical foundation / placeholder-only development prototype.

The planned nation-neutral artwork consists of twelve complete replacement images. Fortification level is **baked into** each sprite (never composed as an overlay):

| Fortification | Small (1–3) | Medium (4–7) | Large (8+) |
|---|---|---|---|
| None | `colony_small.png` | `colony_medium.png` | `colony_large.png` |
| Stockade | `stockade_small.png` | `stockade_medium.png` | `stockade_large.png` |
| Fort | `fort_small.png` | `fort_medium.png` | `fort_large.png` |
| Fortress | `fortress_small.png` | `fortress_medium.png` | `fortress_large.png` |

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
- A later integration step will load `assets/colonies/{key}.png`, scale it without distortion, and draw it rather than the placeholder.
- Native settlements require separate treatment and are outside this first implementation.

## Validation
Run `python -m unittest test_colony_graphics.py`.
Verify all 12 resolution keys, both nationality-independent cases, graphic footprint, map hit-testing, and navigation to colony on Windows.
