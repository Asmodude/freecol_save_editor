# Phase 2D-0 Plan Review

_Independent review by Claude (Anthropic), 28 October 2026, of `docs/PHASE2D0_MUST_SHOULD_COULD_PLAN.md` on `docs/reconcile-status-2026-10-28` @ `61249af`. Checked against the code on that branch (identical to `main` @ `a97ae1a` for all application files), `docs/PHASE2D_IMPLEMENTATION_PLAN.md`, `docs/PHASE2D_INDEPENDENT_REVIEW.md` and FreeCol 1.2.0 source (rev `1690a5f`). Planning review only: no application code was changed. The deferred OC-001 follow-up is **not** part of this review; it stays reserved for the next implementation review._

## Verdict: **PASS WITH CAVEATS**

The plan identifies the right problem, puts the gates in the right order and keeps destructive Qt UI out of scope. It can start once the corrections below are adopted. They are amendments, not a rewrite:

- **One missing safety class (High):** a deletion can kill a player in FreeCol (§2, H1).
- **Two specification gaps (High):** the byte-offset method has a known trap (H2), and the verifier must be provably independent of the locator (H3).
- **One simplification:** M1 should *refuse* exotic XML rather than "support" it (M5). M2's manifest can be the parsed original tree rather than a new data model (§4).

---

## 1. Evidence gathered for this review

| Check | Result |
|---|---|
| Self-closing unit deletion, current engine | **Collateral damage confirmed.** Deleting `<unit id="unit:5" …/>` on a tile also removed the following, unrelated `unit:6`. The output was well-formed and passed the engine's final "no dangling reference" check. |
| Self-closing cached settlement copy, current engine | Swept across element boundaries. Refused only because the result happened to be malformed (`mismatched tag`). This is fail-closed **by luck**, not by design. |
| Nested same-name `<unit>` (passenger inside carrier) | A real FreeCol structure. It is currently **latent**: `remove_unit` refuses passengers (parent not an allowed container) and carriers (has children). It becomes live as soon as policy is widened, so M1 must handle it. |
| Structure-aware locator prototype (expat byte offsets, about 30 lines, scratch only) | Correct spans for explicit, self-closing, `<x />`, nested same-name, `>` and `/` inside quoted attribute values, and look-alike tags inside comments and CDATA. Each slice re-parses to an element with identical attributes. **Feasible.** |
| FreeCol inhabitant definition | `Colony.getUnitCount()` = sum of units over *current work locations* (buildings and colony tiles). Units on the colony's map tile or aboard ships are not inhabitants. |
| FreeCol player death | `ServerPlayer.checkForDeath()`: a native player with **zero units** is dead. A colonial player with **no colonies** dies unless it still has a colonist or offensive unit in the New World (or can get one from Europe before 1600). Rebels need a coastal colony. |
| Preflight conflict checks | `edit_preflight` checks `deleteUnit` and `deleteSettlement` conflicts by `key[0]`. The native key's `key[0]` is `unit:N|indianSettlement:M`, so `deleteNativeUnit` combined with an edit or a `deleteUnit` of the same unit is **not detected** by preflight. It fails later in `change_field` because the unit is already gone, so it is fail-closed by accident, with a confusing message. |
| Native path in `remove_unit` | With `allow_settlement`, the container, location and carrier checks are **skipped**. Only the European path has them. |

---

## 2. Findings by severity

### High

**H1. Player-survival dependency is missing (new Must refusal class).**
The plan refuses colony depopulation but not *player* death. Deleting a native nation's last unit, or the last colonist or offensive unit of a colonial player with no colonies, makes FreeCol declare that player dead on the next turn. For the human player, that means game over.
- **Correction (M3/M4):** refuse a staged set that leaves:
  - any native player with zero units; or
  - any colonial player with zero colonies **and** zero non-carrier units.
- This is deliberately more conservative than FreeCol's rule. Refuse rather than model the Europe-recruitment and year-1600 branches.
- Rebel/independent players: refuse if the set removes the last unit of their last coastal colony. This is already covered by the last-inhabitant rule. State it explicitly.

**H2. Byte-offset method: specify it, including its trap.**
With expat, `CurrentByteIndex` at the *end* event of an empty element points to the **next** token, which may be the parent's `</…>`. A naive "is the end position at `</`?" test therefore misclassifies `<u/></a>` as an explicit close.
- **Correction (M1):** decide empty versus explicit by a **quote-aware scan of the element's own start tag** (`…/>` versus `…>`).
- Cross-check: for an empty element, the scan's end must equal the end-event index. For an explicit element, the bytes at the end-event index must be `</` plus the same tag name.
- Any disagreement → refuse.
- Parse the whole document in one buffer so offsets are absolute.

**H3. M2 must be independent of M1, and proven so.**
M2 is described as a manifest comparison but does not require that a wrong locator be caught.
- **Correction:** M2 compares the **parsed result** with **the parsed original minus the planned nodes**. Planned nodes are identified by element path and ordinal in the original tree, not by byte offsets. Only the authorized attribute removals are allowed.
- Add a **fault-injection test**: a deliberately wrong locator (for example, the current next-close-tag heuristic) must be rejected by M2 on the self-closing fixture.

### Medium

**M1. Define "inhabitant" in the plan, from FreeCol, once.**
- Inhabitants are the `<unit>` children of the colony's `<building>` and `<colonyTile>` elements (FreeCol's current work locations).
- Not inhabitants:
  - units on the colony tile (`location="tile:…"`, children of `<tile>`);
  - units aboard carriers in port;
  - units in Europe.
- `remove_unit` currently also accepts a unit whose parent is `<colony>`. FreeCol's model has no such work location. **Refuse that container until research shows a real save producing it.**
- `edit_backend` line 66 counts `colony.iter('unit')` for SoL. One shared helper must define population for both the SoL edit and the deletion rule, so they cannot disagree.

**M2. Normalize deletion keys to target unit IDs before conflict checks.**
Today, preflight misses `deleteNativeUnit` combined with an edit or `deleteUnit` of the same unit (see §1). M4.3 should state that all deletion keys are reduced to a *target unit ID* before conflict checks.

**M3. One structural policy for native and European units.**
The consolidated path must apply the container, carrier, cargo and location checks to native units as well. Native units can carry goods. Refuse anything outside the settlement or tile container.

**M4. The reference scan must also catch IDs embedded in values.**
The current scans compare *whole* attribute values only. **Correction (Must, cheap):** refuse when the target ID appears as a delimited token inside any attribute value or in text content anywhere outside the removed subtrees. This stays conservative and costs one extra regex over the bytes.

**M5. Simplify M1: refuse rather than "support".**
"Define how namespace prefixes … comments, CDATA … are handled" invites over-engineering.
- A real parser already ignores look-alike tags in comments and CDATA (verified).
- **Refuse:**
  - `<!DOCTYPE` or entity declarations;
  - any encoding other than UTF-8;
  - namespace-prefixed element names.
- FreeCol saves use none of them. This removes a whole class of edge-case work at no safety cost.

**M6. The "no destructive Qt UI" rule needs an automated guard.**
Package D relies on review discipline alone. **Add a Must test:** no `qt_*.py` module calls `stage_unit_deletion`, `stage_native_unit_deletion`, `stage_settlement_deletion` or `stage_checked` with a deletion field. A narrow source scan is acceptable here; it is a guard, like the read-only guard used in Phase 1.

### Low

- **L1. Branch name.** CI runs on `feature/**` and on PRs, not on `docs/**`. Name the 2D-0 branch `feature/phase2d0-…` so every push is tested.
- **L2. Whitespace rule.** Removing an element leaves its surrounding indentation and newline. Decide that the span is exactly the element, and the whitespace stays. In M2, normalize **whitespace-only** text and tails, and nothing else.
- **L3. Writer form in real saves.** Record in M0, locally and without committing the save, how a FreeCol 1.2.0 save writes `unit`, `aiUnit`, `ownedUnits` and cached `indianSettlement` (self-closing or explicit). The locator must handle both anyway. The count tells us how often the old heuristic was actually exposed.
- **L4. Stale plans.** Simplest rule: the backend **never consumes** a plan object. It always recomputes from the bytes being exported, and the plan is advisory, for display only. No plan fingerprinting is needed.
- **L5. Performance.** Locator, verifier and reference scan each parse the document. Measure one representative large save in M5 and record the figure. Optimize under S2 only if needed.

---

## 3. Answers to the six plan questions

| # | Answer |
|---|---|
| 1 | **Yes, implementable without reserializing.** Use `xml.parsers.expat` over the original bytes in one buffer. Take start offsets from `CurrentByteIndex`. Decide the end by a quote-aware scan of the start tag (empty) or by the end-event index at `</tag` scanned to `>` (explicit). Cross-check both, as in H2. Key elements by tree path and ordinal. Remove by slicing the original bytes; never serialize the tree. **Wrongly called safe today:** self-closing targets, and nested same-name elements (latent). **Should be refused, not supported:** DOCTYPE/entities, non-UTF-8, namespaces (M5). |
| 2 | **Strong enough in intent, under-specified.** Make it concrete: (a) each removed slice parses standalone to exactly one element equal to the planned node (tag, attributes, subtree); (b) the parse of the result equals the original tree minus the planned nodes, with only the listed attribute removals and whitespace-only text normalized; (c) every byte outside the removed spans and authorized attribute edits is preserved in order. Repeated cached IDs are handled by path and ordinal identity, never by ID sets. Add the fault-injection test (H3). |
| 3 | **Not yet; the plan must state the rule (M1).** Inhabitants are units under `<building>` and `<colonyTile>`. `<colony>` as a direct parent should be refused. Units on the colony tile and carried or visiting units are not inhabitants. **Research before implementation:** (a) whether a real save ever has a `<unit>` directly under `<colony>`; (b) schoolhouse `teacher`/`student` attributes; the generic unknown-reference refusal already blocks these, so keep it; (c) player death (H1). |
| 4 | **Yes, if two things hold:** the composite key `unit|indianSettlement` stays in the session schema, with an adapter to the shared engine, and the existing refusal conditions are kept as regression fixtures with their messages. **Additional Must refusals:** player-survival (H1), embedded-token references (M4), uniform structural checks for native units (M3), and normalized-key conflicts (M2). Carrier/cargo, aboard, unknown attribute reference, mixed-owner settlement and cached-missionary refusals are already Must. Keep them. |
| 5 | **Sharing the rules is fine. The verifier must not share the mechanism.** Share the transaction validator (population, survival, conflicts) between preflight and export. Keep three independent layers: locator (expat offsets), verifier (ElementTree tree comparison, no offsets) and the existing `produce()` post-save checks. Prove independence with fault injection (H3). Export must recompute everything and trust nothing from staging (L4). |
| 6 | **Boundaries are right; add one automated gate** (M6) so no destructive Qt control can arrive before acceptance. Priority changes are in §4. |

---

## 4. Proposed Must / Should / Could changes

| Item | Plan | Proposed | Reason |
|---|---|---|---|
| Player-survival refusal (new) | — | **Must** (M3/M4) | H1: game-over risk |
| Embedded-token reference refusal (new) | — | **Must** (M3) | M4: cheap and conservative |
| No-Qt-delete guard test (new) | — | **Must** (M5) | M6 |
| Locator round-trip over every element (new) | — | **Must** (M1 exit) | Every element in each fixture, and locally in a real save: slice re-parses equal. Cheap and catches whole classes of bugs. |
| Fault-injection test for the verifier (new) | — | **Must** (M2) | H3 |
| M1 "support namespaces/comments/CDATA" | Must | **Must, reworded as "refuse"** | M5 simplification |
| M2 manifest data model | Must | **Must, simplified** | The original parsed tree plus a list of planned paths *is* the manifest; no new persistent structure |
| S4 capability matrix | Should | **Must**, as a short table in the M3 exit | It is the contract for what 2D-2 may expose |
| S5 Qt wiring contract | Should | Should, but **an entry gate for 2D-2** | Not needed for 2D-0 itself |
| S1 reason codes | Should | Should | Useful; not safety |
| S2 parse-once snapshots | Should | Should, **after** M5 measurement | Correctness first (L5) |
| S3 diagnostics | Should | Should | — |
| C1 CLI preview | Could | Could | — |
| C2 manifest diff report | Could | Could, now nearly free | Falls out of the M2 tree diff |
| C3 fuzzing | Could | Could | The deterministic round-trip Must covers the core |
| C4 profiling | Could | Could | — |

---

## 5. Recommended sequencing and tests

Change the **mechanism first, with no policy change**, then the **policy**. This keeps every regression attributable to one change.

1. **A1 — M0 baseline.** Fixtures and current-behaviour matrix. Mark the known-bad fixtures as expected failures: self-closing unit sweep, self-closing cached settlement. Record the writer form of a real save (L3).
2. **A2 — M1 locator, standalone.** Implement the locator only. Tests:
   - all syntax forms from §1;
   - round-trip of every element;
   - refusals for DOCTYPE, non-UTF-8 and namespaces;
   - the offset cross-check that refuses on disagreement.
3. **B1 — M2 verifier, standalone.** Tests:
   - fault injection with the old heuristic as the locator;
   - well-formed collateral damage;
   - repeated cached IDs;
   - whitespace normalization limited to whitespace-only text.
4. **B2 — swap mechanics, no policy change.** Route `remove_unit`, `_remove_native_unit` and `remove_settlement` through locator plus verifier. **Every existing Tk regression and refusal must pass unchanged**, and the expected-failure fixtures from A1 now pass.
5. **B3 — M3 policy.** Shared native/European path (M3), `plan_unit_deletion` (advisory), the new refusals (H1, M4), and the capability matrix.
6. **C — M4 transaction.** Normalized keys (M2), shared population helper (M1), last-inhabitant and player-survival rules across the whole staged set. Tests: preflight and export give the same decision; a rejected set leaves the session and source unchanged.
7. **D — M5 acceptance.** Exact-SHA CI. The no-Qt-delete guard test. Windows FreeCol load → advance one turn → save → reload on safe cases. Record timing for one large save (L5). Then the independent implementation review, **bundled with the deferred OC-001 follow-up**, clearly separated.

**Minimum Must fixture list:**
- explicit, self-closing and `<x />` forms;
- nested passenger;
- `>` inside an attribute;
- a look-alike tag in a comment and in CDATA;
- a cached settlement copy before **and** after the authoritative one;
- repeated cached ID;
- native unit with goods;
- unit directly under `<colony>` (refused);
- teacher/student reference (refused);
- embedded-token reference (refused);
- last inhabitant, singly and across two deletions;
- last native unit;
- colonial player with no colonies;
- `deleteNativeUnit` combined with an edit of the same unit;
- `deleteNativeUnit` combined with `deleteUnit` of the same unit.

---

## 6. Summary for the Project Director

The plan is sound. Adopt these amendments before implementation starts:
1. **Add a player-survival refusal.** Deleting the wrong units can end the game.
2. **Pin down the byte-offset method and its known trap.**
3. **Prove the verifier catches a faulty locator.**
4. **Define colony inhabitants from FreeCol's own rule.**
5. **Refuse unusual XML instead of supporting it.**
6. **Add an automated guard against Qt delete controls.**

Then build in the order mechanism → verifier → swap with no behaviour change → new policy → transaction rules → acceptance.
