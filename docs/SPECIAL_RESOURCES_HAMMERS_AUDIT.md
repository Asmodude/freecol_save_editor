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

## Prototype (28 October 2026)

- `tools/java/HammerProductionProbe.java`: **source-only prototype** calling FreeCol's `FreeColServer.readGame` and both `Colony.getTotalProductionOf` (gross) and `getNetProductionOf` (net), without write calls.
- `qt_hammer_probe.py`: typed and fail-closed parser; requires unique colony IDs, exact owner matches, complete coverage and numeric bounds. Tests in `test_qt_hammer_probe.py`.
- **Important: not yet compiled or run against a matching FreeCol classpath/save**, so Java ABI compatibility, initialization requirements, and full-production parity remain unverified. The existing Overview continues to display `Unavailable`; no unverified quantity is displayed.
- **Acceptance requirement:** compile the helper with the exact FreeCol distribution version used to load the save; independently check numbers in the game's colony UI for multiple colonies; validate unchanged source SHA-256; test version mismatch and failure handling. Only then wire verified results into a clearly labeled read-only UI.
- The Java probe outputs `FREECOL_HAMMERS_V1` with `colony_id / owner_id / gross / net`. Treat this as a potential interface, NOT as accepted evidence.

## Controlled Windows execution (28 October)

The repository now contains `tools/run_hammer_probe.py`. It requires **an explicitly supplied FreeCol JAR from the installation that reads the target save** and Java/Javac in PATH. It compiles the bridge into a temporary folder, uses a **temporary copy of the save**, applies subprocess timeouts and verifies SHA-256 of both the copy and the original. It does not integrate with Qt or modify editor state.

Example (replace the JAR path with the actual local installation path):

```powershell
py tools/run_hammer_probe.py --jar "C:\\path\\to\\freecol.jar" --save "C:\\Users\\morte\\OneDrive\\Dokumenter\\freecol\\save\\Morten.fsg"
```

Expected success format: header `FREECOL_HAMMERS_V1` followed by tab-separated colony IDs, player IDs, gross and net numbers. **Do not assume successful output**: the Java API and runtime dependency/classpath compatibility have not been confirmed against the user's installation, and startup may require additional FreeCol initialization. Do not activate dynamic Qt display until successful run, source hash comparison, and manual comparison with FreeCol's colony production values.

On error, record full stderr, FreeCol version and Java version, and correct the bridge/launcher before further testing.

## Qt integration — opt-in verified report (28 October)

The seven Danish colonies in `Morten.fsg` were compared against in-game FreeCol production: Frederiksborg 14, Christiansborg 14, Taphus 12, Carlsborg 12, Koralbugt 6, Charlotte Amalie 0, Augustaborg 0. **Seven of seven gross Hammers/turn match.** The other nation's results and other saves are not gameplay-parity verified.

The Qt Overview now displays **Hammers per turn (gross)** as read-only *only after importing a report bound to the exact original .fsg SHA-256*. Save loading and staging remain independent of Java. If the user loads another save, the report state clears. Imported values are non-editable and not serialized in save exports.

From the repository root, in the same PowerShell session where Java/Javac are on PATH:

```powershell
py tools/run_hammer_probe.py --jar "C:\\Program Files\\FreeCol\\app\\Freecol.jar" --save "C:\\Users\\morte\\OneDrive\\Dokumenter\\freecol\\save\\Morten.fsg" --report "$env:TEMP\\freecol-hammers-report.json"
py qt_readonly.py
```

Open the **same** `Morten.fsg` inside Qt, then choose **File → Import verified Hammers report…** and select the JSON report from `%TEMP%`. Open a Danish colony's Overview and verify the gross number. If the save differs, Qt must reject the report. There is no automatic Java launch from Qt, so Java absence cannot prevent opening a save.

Windows acceptance still required on this Qt integration, followed by independent review, before PR #9 can be accepted/merged.
