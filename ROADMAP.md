# FreeCol Save Editor — Development Roadmap

_Last revised: 2026-10-22. Planning document; targets are not deadlines._

## Development principles
- **Non-regression:** every user-accepted capability is a continuing requirement. Changes require regression testing; deliberate changes to accepted behaviour require agreement.
- **Save integrity first:** edits are staged; never overwrite the original or any existing save; validate ZIP/XML and affected relationships and test loading, advancing a turn and resaving in FreeCol.
- **Documentation:** `README.txt` summarises accepted major series (0.1, 0.2, etc.). `CHANGELOG.md` preserves detailed changes for every build. This file records future work and evolves as decisions change.
- **Workflow:** use GitHub branches and reviewed changes for experimental features; only mark milestones accepted after Windows and in-game testing.
- **Original FreeCol artwork:** load from users' installed game rather than redistributing assets.

## Current status
- **Latest visually accepted map milestone:** `v0.6.2.6.3` — compact connected 9×9 isometric map (user-verified).
- **Current development series:** 0.6. Terrain editing is not yet enabled.
- **Immediate next milestone:** **v0.6.2.6.4** — native-look road and river graphics. Requires verifying FreeCol renderer semantics; do not falsely claim pixel-perfect support.

## 0.6 — Terrain viewer and editing
| Milestone | Goal | Status |
|---|---|---|
| 0.6.2.6.3 | Correct 81-tile 9×9 isometric neighbourhood | Visually accepted |
| **0.6.2.6.4** | FreeCol-like roads and rivers: source/asset research, directional rendering, joins and magnitude; visual comparison at (69,111) | In development |
| 0.6.2.6.5 | Ocean/lake coastline masks, river mouths, forest/terrain transitions | Planned |
| 0.6.3 | Safe add/remove road and plow operations with connection validation | Planned |
| 0.6.4 | Resource quantity and compatible resource add/remove | Planned |
| 0.6.5 | Terrain-type/forest changes with ruleset validation | Planned |
| 0.6.6 | Undo/revert staged map edits, map-editing validation and game-load regression | Planned |

### Map regression fixtures
- Even-Y neighbour topology: Christiansborg (83,118)
- Odd-Y neighbour topology and three-way major river: (69,111), style 2220
- Four adjoining lake tiles: (66,109), (67,108), (67,109), (68,110); centred for inspection on (67,110)
- Precise clickable tile boundaries and resizing in 9- and 81-tile views
- Native road and river appearance compared with user-supplied FreeCol screenshots

### Custom settlement artwork — separate development initiative
- Prototype twelve nation-neutral replacement images: colony/stockade/fort/fortress × small/medium/large.
- Preserve distinct artwork per state, no national variants or fortification overlays.
- Validate population/fortification mapping before commission of final original artwork.
- Later prepare independent Better Colony Graphics mod if asset quality and FreeCol packaging permit.

## 0.7 — European colony management
| Milestone | Goal | Status |
|---|---|---|
| 0.7.0 | Safely delete European colonies; remove attached buildings/working inhabitants, preserve stationed/visiting units when references can be safely relocated; refuse unknown dependencies | Planned, high priority |
| 0.7.1 | Add/remove/upgrade colony buildings, including chain and worker dependencies | Planned |
| 0.7.2 | Inspect/manage colony workforce and assignment in Units interface | Planned |
| 0.7.3 | Create population units with correct identity/ownership/location/reference graph | Research required |

Population deletion belongs in Units, not a separate colony-specific deletion interface.

## 0.8 — Advanced world editing
| Milestone | Goal | Status |
|---|---|---|
| 0.8.0 | Territory ownership edits, safely reflecting claims and relationships | Research required |
| 0.8.1 | Native territory/settlement refinements | Planned |
| 0.8.2 | Unit placement and map location editing | Research required |
| 0.8.3 | Regional selections and bulk map operations (only after single-tile validation) | Planned |

## 0.9 — Release candidate programme
| Milestone | Goal | Status |
|---|---|---|
| 0.9.0 | Structure source code, separate tests, clean artefacts, centralise version, remove dead code | Planned |
| 0.9.1 | Automated regression suite and GitHub Actions | Planned |
| 0.9.2 | Windows portable .exe using PyInstaller; install-free startup and application icon | Planned |
| 0.9.3 | Release-candidate verification against representative FreeCol saves | Planned |

## 1.0 — First stable release
Accept only when supported player, unit, settlement, colony and terrain operations are validated; unsupported/risky features should be explicitly deferred rather than shipped untested.

## Known technical debt and guardrails
- Native game renderer uses specialised Java logic for road and river composition; image-name guesses are not sufficient.
- Visual inspection and XML validation alone do not prove save edits are safe: test turn processing and resaving.
- Avoid changing native-settlement handling when introducing European-colony deletion.
- UI actions should be contextual; tool quantities should match game terminology (20–100 tools).
- Maintain an independent, versioned source repository; exclude local savegames, generated `__pycache__` and FreeCol graphics.
