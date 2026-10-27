# FreeCol 1.2.0 automatic movement — diagnostic record

**Date:** 27 October 2026. **Status:** parked; root cause unconfirmed. This is evidence for independent review, not proof that all symptoms share one cause.

## Inputs and logs

FreeCol 1.2.0 (revision 1690a5f), Windows 11, Java 21.0.3. The tester used original, unedited `Morten.fsg` as control and `C3_dragoon_only_three_moves.fsg` as the 3-MP Dragoon-only diagnostic. The later `Lumberjack.fsg` is a game-generated snapshot following movement, not the starting diagnostic. Original-save provenance should be checked independently.

Evidence supplied in the testing conversation (not committed in this repository): `FreeCol(3).log`, `FreeCol(4).log`, earlier `FreeCol(1).log` / `FreeCol(2).log`, and screenshots.

## Errors and visual duplication

- `FreeCol(3).log` on 3-MP diagnostic: Expert Lumberjack `unit:35777` twice rejected with `MOVE_NO_MOVES`, from `tile:12614` to `tile:12814` at approximately 09:45:19. Log shows 1/1, 2/3, 1/3 movement readings leading into rejection.
- `FreeCol(4).log` on **unedited** `Morten.fsg`: Hardy Pioneer `unit:34454` generated **260** `MOVE_NO_MOVES` rejections at approximately 10:07:00, all starting from `tile:13111`. Of these, 174 targeted `tile:13110`, and 86 targeted `tile:13211`. The log shows 1/1 movement before the storm, 0/1 afterward.
- Two visually identical Expert Lumberjack sprites were seen in some failed runs near Christiansborg/Frederiksborg. This did **not** establish duplicate in-memory objects. Examination of `Lumberjack.fsg` found one authoritative `unit:35777`; the number of Danish Expert Lumberjacks remained three overall. Visual doubling sometimes appeared without a large cascade, and cascades sometimes appeared without doubling.
- Both logs reported initial **game integrity** and **AI integrity** checks successful. Those are not runtime movement guarantees.

## Two repeated-load sequences

The tester confirmed that **every reload referenced the same original 3-MP diagnostic file**, not a freshly saved or incrementally modified file.

| Load after restarting FreeCol | Application session 1 | Application session 2 |
|---|---|---|
| First | Lumberjack visually doubles; 2 errors | Lumberjack visually doubles; 2 errors |
| Second | No visual double; approximately 200 errors | Lumberjack visually doubles; 2 errors |
| Third and later | Ten consecutive clean attempts | Four consecutive clean attempts |

This suggests possible session/reload-order dependence but the sample is small and a causal mechanism has **not** been demonstrated.

Crucially, fresh-start testing also produced the catastrophic errors on **unedited** `Morten.fsg` (the Pioneer cascade in `FreeCol(4).log`). Previously this control had passed five trials, illustrating the intermittency.

## Controlled goto-order removal

The diagnostic `C3_original_no_three_goto_orders.fsg` was derived from the original control and cleared destination orders for three units only: Hardy Pioneer `34454`, Expert Lumberjack `35777`, Master Carpenter `35720`.

The tester performed **four independent FreeCol application restarts** with this save: **4/4 passed**, with no errors or visual splitting. The result implicates one or more automatic movement orders, but does not isolate the responsible unit or prove whether the destination data itself is invalid.

## Upstream source observations

At revision `1690a5f`, FreeCol's `InGameController.java` follows `doExecuteGotoOrders()` → `moveToDestination()` → `movePath()` → `moveDirection()` → `moveTile()`. The client is intended to set units to `SKIPPED` when movement is exhausted or a server request is rejected. `MoveMessage.java` independently validates a server move via `unit.getMoveType(tile)` and emits the observed illegal-move warning.

- https://github.com/FreeCol/freecol/blob/1690a5f/src/net/sf/freecol/client/control/InGameController.java
- https://github.com/FreeCol/freecol/blob/1690a5f/src/net/sf/freecol/common/networking/MoveMessage.java

It is plausible that client movement requests continue despite the intended stop handling, but the first divergence, any caching/race mechanism, and the explanation for the sprites are **not established**.

## Editor impact and independent-review boundary

The unedited control reproduced the storm: the Phase 2C Dragoon edit is **not required** to trigger it. This does not categorically clear every editor operation. Separately, a **confirmed editor staging defect**—an explicit movement override equal to the original value being dropped following a staged equipment change—was fixed and covered by regression tests.

The user accepted Phase 2C C3 Windows export/round-trip tests on 27 October 2026. The independent Claude code/documentation review is pending; PR #6 remains unmerged. The FreeCol engine investigation is **parked**, not declared solved. If a reviewer identifies specific evidence of editor involvement, investigate that separately. Optional future work includes per-unit goto isolation and client/server instrumentation around the first rejected movement.
