# Phase 2 research item — Reveal Entire Map (staged save edit)

_Status: PLANNED / RESEARCH-GATED. Recorded 25 October 2026. No implementation authorised by this document._

## User intent

Provide a **Reveal Entire Map** command that marks the entire map as **explored for one explicitly selected European player** while preserving the normal **fog of war** (currently visible versus explored-but-not-currently-visible tiles). Do not disable fog of war, expose live units, grant exploration bonuses, or change other players' knowledge. This is a **savegame edit**, not merely an editor-only display toggle.

## FreeCol representation to investigate

FreeCol's Java implementation distinguishes exploration from line of sight:

- `ServerPlayer.exploreMap(boolean reveal)` calls `Tile.setExplored(player, reveal)` and invalidates visible-tile calculations separately.
- `Tile.isExploredBy(player)` uses the player's cached tile when running on the server.
- Authoritative map `tile` elements may contain per-player `cachedTile` children, with `player` and `copied` attributes. For `copied="true"`, an embedded tile can hold a restricted/stale player view; it must **not** be discarded or replaced by an unrestricted tile.

Relevant upstream source:
- https://github.com/FreeCol/freecol/blob/master/src/net/sf/freecol/server/model/ServerPlayer.java
- https://github.com/FreeCol/freecol/blob/master/src/net/sf/freecol/common/model/Tile.java

**Hypothesis only:** For previously unexplored authoritative tiles, adding a scoped `<cachedTile player="..." copied="false"/>` may reproduce FreeCol's exploration marker. This XML transformation **is not yet validated** against representative savegames or a load/advance/resave cycle. The correct representation and visibility/security implications must be established empirically before enabling the edit.

## Implementation sequence (after foundational Phase 2 Qt editing work)

1. Build a **read-only exploration coverage report** per European player: total authoritative map tiles, explored count, unexplored count, and any anomalous cached-tile entries. Exclude nested cached snapshots from the authoritative tile count.
2. Verify the exact XML patterns and invariants against representative real saves and the current FreeCol version, including tiles with `copied="true"`, native settlements, and multiple colonial players.
3. Implement a **player-specific staged operation**, with a preview showing which authoritative tiles would change and an exact count. Never auto-select an ambiguous player; never stage on mere button press without explicit confirmation.
4. Apply only the researched minimum safe edits using `EditSession` and the existing safe **Save As** pipeline. Never overwrite the original or an existing destination. Preserve existing caches and nested player-specific information.
5. Validate the resulting ZIP/XML and savegame relationships, then test in FreeCol: load → confirm terrain is discovered, current fog of war remains active → advance turn → resave → reload.

## Non-regression / acceptance tests

- Only the chosen player's exploration state changes; other players' exploration entries are byte-for-byte or semantically unchanged, as appropriate.
- Existing cached-tile snapshots, including `copied="true"`, native settlement internals and hidden information, are preserved.
- The normal line-of-sight/fog-of-war setting and behaviour remain unchanged; newly explored tiles do **not** become permanently visible.
- No exploration events, Lost City Rumour triggers, rewards, score changes, or other gameplay effects arise solely from the save edit.
- Stage/unstage and safe Save As work; original .fsg hash stays identical; repeated reveal is idempotent.
- Fail closed when tile records, player identifiers, or save format cannot be validated.
- Windows and in-game testing plus explicit user acceptance required before marking feature complete.

## Scheduling and versioning

This is a proposed **Phase 2 editing capability**, **not an initial Phase 2 prerequisite**. Prioritise Qt model/view decomposition and safe edit-session integration first. Phase labels do not change the original `0.6 → 0.7 → 0.8 → 0.9 → 1.0` version roadmap. No implementation, merge, or acceptance is implied by this planning entry.
