> **OC-007 — MANDATORY PRE-1.0 Tk RETIREMENT (Project Director decision 28 October 2026):** Tk/Tkinter must be completely removed as runtime/UI/dependency/packaging/entry points before the stable v1.0 release; historical records may remain marked as history. Complete Qt/shared-backend parity, CI static no-Tk guards, Windows packaging and actual FreeCol roundtrips first. Planned for v0.9 release-candidate cleanup. Until then, preserve safe accepted Tk behavior; unsafe deletion defects are fixed or refused, not perpetuated for compatibility. **OC-004 / 2D-0 PLAN APPROVED with all eight Claude amendments**; implementation, CI/Windows and independent code acceptance are still pending.

> **AUTHORITATIVE RECONCILIATION — 28 October 2026:** See [CURRENT_STATUS.md](CURRENT_STATUS.md). The detailed entries below are a *dated historical record*, including stale status claims from before merges. Present disposition: **OC-001 DONE** (PR #9 merged; user-accepted Windows and FreeCol roundtrip; 673/673 threshold match; follow-up Claude re-review deferred and remains explicitly OPEN as a review obligation); **OC-002 CLOSED by explicit owner decision** (probable FreeCol bug; do not investigate further or treat as C3 gate); **OC-003 DONE** (Phase 2D-1.5 merged PR #8); **OC-004 OPEN and NEXT** (mandatory 2D-0 safety); **OC-005 DONE** (Windows issues fixed, retested, merged); **OC-006 mandatory premerge items completed and PR #8 merged**, with minor follow-ups still tracked. Phase 2D-1 was merged separately in PR #7. No rerun of accepted Phase 2C gates. The permanent reconciliation rule in CURRENT_STATUS.md applies **before every future planning decision, development phase, release and merge**. Do not read older OPEN / not merged text below as current status.

# Outstanding commitments and release gates

**Status: ACTIVE — must be reconciled before declaring any phase complete.**  
**Recorded:** 27 October 2026.  
**Owner:** ChatGPT development coordinator; the Project Director approves scope, acceptance, merges and tags.  
**Authority:** Project Director's explicitly accepted decisions. An earlier commitment cannot be silently postponed by a later, narrower implementation plan.

## OC-001 — Special Resources (mandatory C2 follow-up, BEFORE C3)

**Decision recorded from 26 October discussion; implemented on draft PR #9, NOT ACCEPTED or merged.**

Bells, Crosses and Hammers represent production/progress rather than ordinary physical warehouse stock.

**Required presentation and editing:**

- **Colony Goods** and **National Goods:** exclude Bells, Crosses and Hammers from ordinary goods lists and ordinary warehouse editing/aggregation.
- **Bells:** show relevant colony production/progress in **Colony Overview**; national liberty/Bells in **Nation Overview** and **Continental Congress**, with the separately agreed editable **national liberty-points** value (subject to source-of-truth verification and safe validation). Do not confuse production per turn with accumulated liberty points.
- **Crosses:** show national immigration progress in **Nation Overview**, including progress toward the next immigrant threshold. Determine the authoritative save fields; do not invent a derived value.
- **Hammers:** show colony production per turn in **Colony Overview**, **read-only initially**. Do not treat ongoing production as warehouse inventory.
- Preserve visibility of legitimate physical goods and saved source XML, do not hide or delete authoritative XML data. Rendering/aggregation changes must not corrupt existing exports.

**Acceptance:** precise source-field mapping documented; Qt displays implemented; no leakage into either Goods list; regressions for colony/national listing, sorting, edit eligibility, Save As and FreeCol roundtrip. Obtain focused Project Director Windows acceptance. Implementation branch/PR and merge gate separate from Phase 2D-1.5 refactor.

**Original dependency:** Complete after C2 and **before C3 FreeCol roundtrip**. The movement-error interruption did NOT cancel or defer this commitment.

## OC-002 — C1+C2 movement-error cascade / C3 gate

**Status: unresolved/needs current verification.** A C1+C2 exported-save movement-error cascade was previously reported as blocking C3. The root cause and exact reproduced save/error log are not documented here; do **not** claim resolved without explicit evidence from a real FreeCol test.

**Acceptance:** reproduce/triage against a representative C1+C2 save if still present, implement a narrowly scoped fix if required, regression-test movement bounds/conversions and run the real FreeCol export/load/turn/save/reload roundtrip. Any movement correction must preserve accepted equipment/movement behaviour.

## OC-003 — Phase 2D-1.5 numeric UI and equipment performance

**Status:** Implemented on `feature/phase2d1-5-component-performance`; draft PR #8; automated tests/CI, Windows acceptance and independent Claude review have distinct gates.

**Testing sequence agreed 27 October:**
1. Complete **A/B/C** functional Windows tests and benchmark **now**; fix failures.
2. Reconcile and implement OC-001 on a **separate focused branch** based on the tested 2D-1.5 work (no accidental merge into main).
3. Address OC-002 if still reproducible.
4. Run the **deferred D integration / real FreeCol roundtrip**, regression tests and independent review in the appropriate branches.
5. Seek explicit approval before **each merge or tag**. Do not claim any phase accepted merely because CI is green.

This is a *testing-order adjustment*, NOT an authorization to drop OC-001 or merge Phase 2D-1.5 early.

## OC-004 — Destructive deletion safety prerequisite

**Status:** Mandatory Phase 2D-0 deletion-engine hardening before Phase 2D-2 destructive UI. Review `docs/PHASE2D_IMPLEMENTATION_PLAN.md`; preserve conservative refusals, structural XML exact-removal safeguards and independent review.

## Change-control rule (effective immediately)

Before marking a phase accepted, proposing integration, or producing the next Windows checklist:
- Reconcile this file with the phase plan, independent-review findings and new Project Director decisions.
- Add every new explicit commitment as a numbered item with acceptance criteria, dependencies and a status.
- Identify every unresolved blocker in the release/Windows checklist (do not quietly move it to generic "later" scope).
- Mark a commitment DONE **only** after evidence: implementation reference, green CI, required Windows/FreeCol verification and explicit acceptance.
- Changes to committed order/scope need an explicit Project Director decision and an entry here.

## OC-005 — Windows findings from Phase 2D-1.5 (27 October)

**Status: OPEN; reported while A1–A9 and B1–B6 passed, C1–C2 passed, C3 PASS — noticeably faster in actual use.**

- **A7 layout clipping:** In Native Settlement Alarm editor, the staged-source label `was 1100` overlaps adjacent text. Treat as a Qt cell-width/layout defect; reproduce with a four-digit original value and fix without losing record identity, stage indicators or sorting.
- **Equipment eligibility — potentially invalid role choices:** Project Director reports Treasure Trains, Wagon Trains, ships and artillery can be offered roles disallowed by FreeCol. Inspect saved unit-type inheritance and Java game rules, especially whether `canBeEquipped` reflects final inherited abilities and whether default-role checks bypass necessary restrictions. Enforce conservative fail-closed eligibility; add representative regression fixtures and Windows retest. Do not consider B2 functional PASS as acceptance of this new defect.
- **Measured performance:** Real 7,855,956-byte XML: load 206.6 ms, lazy rules index 12.7 ms, 15 editor construction uncached 645.4 ms vs indexed 13.4 ms (48.20x warm); first indexed pass + index 26.1 ms. Benchmark PASS, subjective C3 PASS (noticeably faster).
- **Acceptance gate:** Fix both observations on PR #8, automated CI and focused Windows retest, before proposing 2D-1.5 acceptance or Claude final review. Continue to respect OC-001 and OC-002 for deferred C3 FreeCol roundtrip.

**Windows acceptance update (27 October):** Project Director confirmed **C3 PASS — noticeably faster**. Initial A1–A9, B1–B6 and C1–C3 checks now all passed (18/18). This does **not** close OC-005: A7 label overlap and invalid equipment eligibility require correction and focused retest. Full integration/FreeCol roundtrip remains deferred behind OC-001/OC-002.

**OC-005 implementation update:** Alarm table uses a compact source tooltip (including original `1100`) instead of a colliding inline `was` label. Equipment eligibility now conservatively refuses equipment for standard treasure/wagon/artillery/ship types and explicit naval/carry-treasure/native abilities; no-change equipment controls disabled for units with only Default role. Regression fixture added in `test_phase2d1_5_windows_findings.py`. **Status: fixes implemented, CI and focused Windows retest not yet accepted; independent review still needed**, especially comparison with game unit-role inheritance and modded specifications.

**Windows focused retest (27 October 2026):** Project Director explicitly **ACCEPTED BOTH** A7 Alarm-cell overlap correction and B2 specialized-unit equipment restriction. Both latest CI runs on `f3608fd37bee5bb7f8fe5faa0eca73104836a214` passed (branch push and draft PR #8). **OC-005 Windows defect corrections CLOSED; Phase 2D-1.5 remains awaiting independent Claude review and explicit release approval.** OC-001 Special Resources and OC-002 C3 movement gate remain open.

## OC-006 — Phase 2D-1.5 independent review follow-up (27 October 2026)

**Independent review:** `docs/PHASE2D1_5_INDEPENDENT_REVIEW.md`, Claude, PASS WITH CAVEATS, reviewed application HEAD `3a5e7f5`; review committed as `4592590`. Both push and PR CI green at `4592590`.

**Pre-merge mandatory verification:** Check the embedded FreeCol specification in Project Director's real `Morten.fsg` for every `unit-type` with explicit `model.ability.canBeEquipped=true`. Expected standard types: colonist types, brave and colonialRegular; not treasureTrain, wagonTrain, artillery or ships. Record actual output here (not just expectation). If any non-personnel unit has the ability, investigate before merge. Correct the misleading code comment on incomplete/inherited save abilities and use a FreeCol-shaped negative-role regression fixture. Explicitly label the 48.20x benchmark as **equipment-editor construction**, not full UI refresh.

**Deferred minor review findings to triage deliberately (not forgotten):** unique accessible Stage Change names; existing `.title()` object-name stability; centralizing UI style tokens; duplicate Default-only disabling; narrow-window Goods/Workers `was` label clipping; optional rules-index module cleanup; optional benchmark relocation. Higher-priority future rule work: faithfully implement FreeCol `Role.isAvailableTo` checking player OR unit-type required abilities, before Phase 2D-2; preserve standard/modded spec correctness.

**Release gate:** no PR #8 merge until real-save check is recorded and pre-merge findings are resolved, CI on final HEAD green, and Project Director authorizes merge. OC-001 Special Resources remains immediate next development after 2D-1.5 review resolution, before C3; OC-002 movement-error gate and OC-004 deletion safety remain binding.

**OC-006 real-save verification COMPLETE — Project Director's Morten.fsg, 27 October 2026.** Read-only enumeration of all unit types carrying explicit `model.ability.canBeEquipped=true` returned 30 types: brave; colonialRegular; elderStatesman; expertFarmer; expertFisherman; expertFurTrapper; expertLumberJack; expertOreMiner; expertSilverMiner; firebrandPreacher; freeColonist; hardyPioneer; indenturedServant; jesuitMissionary; kingsRegular; masterBlacksmith; masterCarpenter; masterCottonPlanter; masterDistiller; masterFurTrader; masterGunsmith; masterSugarPlanter; masterTobaccoPlanter; masterTobacconist; masterWeaver; pettyCriminal; seasonedScout; undead; veteranSoldier. **No treasureTrain, wagonTrain, artillery, damagedArtillery or ship type occurs in the list.** This confirms the standard save rules distinguish personnel from non-personnel; previous misleading saved-inheritance comment corrected, and FreeCol-shaped regression coverage added. The hard-coded type guard remains secondary defence only. The 48.20× figure applies to **equipment-editor construction**, not full colony refresh. No change in binding OC-001 Special Resources → C3 sequence.

**OC-001 implementation opened after accepted 2D-1.5 release:** `feature/special-resources-oc001` based on merge `852e1e5`. See `docs/SPECIAL_RESOURCES_OC001_PLAN.md`. Initial work filters virtual resources from both Qt Goods models and breakdowns without modifying XML; player source `liberty`, `immigration`, `immigrationRequired` are displayed in national overview, immigration threshold progress is read-only, and national `liberty` has a Qt-only staged editor with backend export/preflight. Congress heading includes owner-scoped staged liberty points. **OC-001 status (28 October):** Hammers gross production is implemented through an optional FreeCol Java bridge with read-only Qt import; seven Danish colonies passed in-game production parity and all five Hammers Qt Windows checks passed. Claude independent review `OC001_INDEPENDENT_REVIEW.md` (uploaded externally, not yet committed to this repo) returned PASS WITH CAVEATS / NOT MERGEABLE: H1 (bind report to loaded bytes), M1 (malformed JSON shape), M2 (liberty founding-father ability), M3 (documentation) require corrective regression tests and fresh CI/Windows verification. National liberty Save As → FreeCol load → turn advance → save/reload acceptance remains OPEN. OC-002 movement-error gate and OC-004 deletion safety remain binding. Do not mark OC-001 DONE or merge until owner authorizes. Do not mark OC-001 DONE or merge merely because initial CI passes.
