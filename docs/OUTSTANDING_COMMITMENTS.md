# Outstanding commitments and release gates

**Status: ACTIVE — must be reconciled before declaring any phase complete.**  
**Recorded:** 27 October 2026.  
**Owner:** ChatGPT development coordinator; the Project Director approves scope, acceptance, merges and tags.  
**Authority:** Project Director's explicitly accepted decisions. An earlier commitment cannot be silently postponed by a later, narrower implementation plan.

## OC-001 — Special Resources (mandatory C2 follow-up, BEFORE C3)

**Decision recorded from 26 October discussion; NOT IMPLEMENTED and NOT ACCEPTED.**

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
