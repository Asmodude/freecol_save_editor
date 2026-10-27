# FreeCol Save Editor — Development Roadmap

_Last revised: 2026-10-27. Planning document; targets are not deadlines._

## Development principles
- **Non-regression:** every user-accepted capability is a continuing requirement. Changes require regression testing; deliberate changes to accepted behaviour require agreement.
- **Save integrity first:** edits are staged; never overwrite the original or any existing save; validate ZIP/XML and affected relationships and test loading, advancing a turn and resaving in FreeCol.
- **Documentation:** `README.txt` summarises accepted major series (0.1, 0.2, etc.). `CHANGELOG.md` preserves detailed changes for every build. This file records future work and evolves as decisions change.
- **Workflow:** use GitHub branches and reviewed changes for experimental features; only mark milestones accepted after Windows and in-game testing.
- **Original FreeCol artwork:** load from users' installed game rather than redistributing assets.

## Planned Qt editing UX — Stage Change clarity (deferred until after Phase 2C merge)
- **User-requested, 27 October 2026. Not implemented.** Replace the small, ambiguous icon-only stage buttons across **all supported Qt inline editing locations** with a consistently labelled **Stage Change** button. Scope includes Overview fields, colony Workers/Stationed units/Goods, diplomacy and native settlement editors; audit the actual UI for every staging action.
- Add brief, **always-visible** editing instructions in a stable part of the Qt editor chrome (prefer a compact line beneath the top toolbar / above the work area, not inside a context-dependent Inspector tab): **"To make edits: Edit data one at a time followed by clicking \"Stage Change\" next to that edit."**
- Ensure the labelled controls remain usable with window resizing, long labels, keyboard focus, accessible names and tooltips; do not change stage-on-click semantics, validation, original/staged indicators, undo or Save As.
- **Inspector clarity (user-approved, 27 October 2026; not implemented):** label Inspector Details and Raw XML explicitly as **original/source save values, excluding staged changes**; explain that proposed role, roleCount, movement and other edits are held separately until Save As, when exported XML contains them. Keep staged indicators clearly visible in the editing view. Include in the same early Phase 2D usability pass and Windows visual verification.
- **Scheduling:** early **Phase 2D UI/UX preparation**, after Phase 2C has been independently reviewed and merged, before expanding destructive editing controls. Include Windows visual acceptance and focused regression tests. This enhancement must not delay the already pending Phase 2C merge gate.

## Phase 2B — accepted and merged (2026-10-25)
- Inline validated player-gold editing in lower middle Overview; staged values explicitly marked in the workspace and their original values shown next to the editor.
- Staged-change review is in the resizable lower right pane under the Inspector, with per-item undo and confirmed Unstage All.
- Save As preserves source, refuses existing paths, and retains staged values after successful export with exported/dirty-state tracking.
- **Singleton selection** is a general standard-workspace behavior: one visible record (including filtered result) is automatically selected and inspected.
- User confirmed Windows editing tests, a successful FreeCol roundtrip and the staged-value markers; PR #5 merged with green CI. Tag `v0.6.2.6.4-phase2b` on the merge commit.
- See `docs/PHASE2B_IMPLEMENTATION_PLAN.md`, `docs/PHASE2B_PLAN_REVIEW.md`, `docs/PHASE2B_WINDOWS_FREECOL_CHECKLIST.md`, and `docs/PHASE2B_ACCEPTANCE_EVIDENCE.md`.
- **Next: Phase 2C** — non-destructive Tk-to-Qt editing parity.

## Phase 2A — accepted and merged (2026-10-25)
- User accepted the experimental `QTableView` behaviour on Windows (25 Oct 2026).
- In PR #4, the new model-backed `QTableView` is now the **only** workspace table by default. The old `QTableWidget` workspace, `--compare-model-view` flag, and comparison mode have been removed.
- Navigation, sorting/filtering, Inspector record identity, search and drill-down use the sole table. Diplomacy and detail-tab tables can remain `QTableWidget` until editing support in 2C.
- Also accepted as visible changes: role-based unit sprites, direct inspection of uniquely scoped colonies/native settlements, and matching Workers/Stationed units row heights.
- **Accepted and merged:** the user passed the final single-table Windows re-check on 2026-10-25; CI green; PR #4 merged with a merge commit. **Next: Phase 2B** (safe Qt editing workflow; see `docs/PHASE2_DEVELOPMENT_PLAN.md`).
- Post-merge: tag **the merge commit** `v0.6.2.6.4-phase2a`, then delete the feature branch.
- Carry into 2B: gradually replace the remaining source-text tests with behavioural tests; split the remaining section-specific `populate`/`inspect` logic into per-section classes as needed during 2C.

## Current status
- **Latest accepted integration baseline:** `v0.6.2.6.4` — 9×9 map, native-mask river prototype, established directional roads, and 12 accepted colony sprites (user-verified on Windows).
- **Phase 0 (core extraction):** accepted and merged 2026-10-23, tag `v0.6.2.6.4-phase0`. UI-free core: `save_document.py`, `edit_session.py`, `presentation.py`, `map_render.py`, `freecol_art_source.py`; 65 headless tests in CI on `main`. No user-visible changes.
- **Current development series:** 0.6. Terrain editing is not yet enabled.
- **Phase 1 (read-only PySide6 shell): ACCEPTED by user and merged to `main` on 2026-10-25**, tag `v0.6.2.6.4-phase1`. The Qt explorer (`py qt_readonly.py`) is strictly read-only; the accepted Tk editor and Map Editor remain the editing and map interfaces. Windows UI and save-file hash checks completed; CI green on the merged head. Dependencies pinned in `requirements.txt` (PySide6 6.12.0, Pillow 13.0.0; Windows Python 3.14.3).
- **Integration status:** Phase 1 is integrated on `main`. The existing 0.6.x application version roadmap is unchanged; Phase 1 is an internal UI milestone, not version 0.7.
- **Immediate next milestone — Phase 2 (editing in Qt):** begin the Qt model/view and component decomposition described in `docs/PHASE1_ASSESSMENT.md` before introducing Qt editing. Terrain work remains on the established 0.6.x roadmap; native RoadPainter-style roads remain deferred to Phase 3.

## Phase 2 research-gated proposal — Reveal Entire Map
- **Status: planned; not implemented.** Add a staged, player-specific **Reveal Entire Map** save edit that marks all authoritative tiles explored for the selected European player **without disabling or changing fog of war**.
- Research and verify FreeCol's per-player `cachedTile` / `copied` serialization first. Preserve cached snapshots, restricted native-settlement information and every other player's knowledge.
- Start with a read-only per-player exploration coverage report. Only after real-save validation should the operation become stageable, reversible and exportable through safe Save As. Verify no exploration rewards/events, normal visibility, original-file integrity and FreeCol load → advance turn → resave → reload.
- **Detailed research and acceptance criteria:** `docs/PHASE2_REVEAL_ENTIRE_MAP.md`. This is not a prerequisite for the initial Phase 2 architecture/editing work and does not change the 0.6–1.0 version roadmap.

## Application startup and navigation — planned usability refinement (delivered in Phase 1 Qt explorer)
- **Default post-load selection:** After an `.fsg` file is successfully loaded, open the **Players** view and automatically select the human-controlled player.
- Determine the human player from authoritative savegame data rather than relying on player order or a hard-coded identifier.
- If no unique human player can be identified, use a safe, clearly defined fallback without selecting an arbitrary player.
- Add regression tests for successful loads, missing/ambiguous human-player data, and switching between savegames.
- **Status:** Phase 0 is complete, so this is no longer blocked. Planned as a 🟢 Phase 1 item in the Qt UI (or a separately accepted Tk release).

## Phase 0 acceptance fixtures (no behaviour changes) — historical, Phase 0 accepted
- **Authoritative unit indexing:** In the audited `Morten(5).fsg` baseline, 2,525 raw nested `<unit>` elements represent 2,520 distinct unit IDs (cached terrain snapshots are excluded from the editable unit list). The expected post-fix UI status is **2,520 units**. These numbers are save-specific, not global invariants; the current `Morten(6).fsg` may differ.
- **Xaymaca:** The Arawak capital must show **exactly one authoritative Danish missionary**, not the cached duplicate. Keep the cached missionary deletion caveat in scope as a known limitation; do not change deletion semantics during Phase 0.
- **Superseded:** the live `Morten(5).fsg` comparison is no longer possible because that save is unavailable. Authoritative-unit indexing and cached-snapshot exclusion are covered by synthetic headless regression tests; real-save checks use a currently available save (see `UI_MODERNISATION_PLAN.md` §5).
- These checks establish the existing baseline; they do **not** authorise a user-visible fix during Phase 0.

## 0.6 — Terrain viewer and editing
| Milestone | Goal | Status |
|---|---|---|
| 0.6.2.6.3 | Correct 81-tile 9×9 isometric neighbourhood | Visually accepted |
| **0.6.2.6.4** | Native-mask river prototype + existing directional vector roads; 12 accepted colony graphics; 40/40 Windows tests | Accepted integration baseline |
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
- Twelve user-approved nation-neutral replacement images: colony/stockade/fort/fortress × small/medium/large.
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
