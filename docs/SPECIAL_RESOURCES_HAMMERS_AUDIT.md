# Hammers-per-turn correctness investigation (OC-001 / SR-2)

**Status: OPEN — do not merge PR #9 or mark OC-001 complete until resolved.**

## Authoritative source audit

Consulted the current upstream FreeCol Java source:

- `src/net/sf/freecol/common/model/Colony.java`:
  - `getTotalProductionOf(GoodsType)` sums `getCurrentWorkLocations()` production;
  - `getNetProductionOf(GoodsType)` delegates to `productionCache.getNetProductionOf`;
  - `writeAttributes()` serializes `liberty`, `immigration` and `productionBonus`, **not** a per-turn Hammers quantity.
- `src/net/sf/freecol/common/model/WorkLocation.java`: `getTotalProductionOf` is obtained from `getProductionInfo().getProduction()`; actual per-unit productivity evaluates production types, unit-specific bonuses and other modifiers.
- `src/net/sf/freecol/common/model/Building.java`: production modifiers depend on building type, unit type, colony, owner and turn.
- `src/net/sf/freecol/common/model/ProductionCache.java` `reallyUpdate()`: combines outdoor production and building production; building output is adjusted to available input goods, consumption, and the current store.

Therefore the following are **not** valid calculations:

- `storedGoods[model.goods.hammers].amount` is **not Hammers/turn**.
- `colony.liberty` is **not Bells/turn**.
- Worker count × an assumed fixed hammer rate is **not authoritative**.

For faithful per-turn production, the implementation must either:

1. Reuse FreeCol's own production model in a read-only Java helper tied to the relevant game/ruleset version, which loads a copy of the saved game and returns source-scoped colony `getTotalProductionOf(model.goods.hammers)` or `getNetProductionOf`, explicitly naming which metric; or
2. Implement and independently parity-test a Python production simulator covering building production types, per-unit assignments, building upgrade level, expertise, colony and owner production modifiers, consumable inputs, applicable turn, and game specification options.

**Preference:** option 1 for correctness; option 2 is a considerable port with nontrivial maintenance and modded ruleset implications. A Java helper must be strictly read-only and optional. The editor must not invoke FreeCol silently or assume it can load an arbitrary save version.

## Proposed acceptance gate

- A real-save comparison for at least three different colony arrangements: a Carpenter's House with one free colonist, a Master Carpenter in an upgraded building, and a colony with no hammer production, including input-limited conditions if rules allow.
- Verify the unit of measure and whether value shown is gross or net; don't silently substitute one for the other.
- FreeCol and helper version compatibility checks, timeout/error handling, and source-archive immutability.
- If exact production cannot be obtained, show **“Hammers per turn: unavailable (requires FreeCol production calculation)”**, not a misleading number.
- This is not acceptance of the promised Hammers-per-turn display; the unresolved requirement remains an explicit **blocker**.
