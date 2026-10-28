# Phase 2D-0 Package A — baseline and red/green ledger

**Branch:** `feature/phase2d0-package-a`, branched from merged documentation `647c3a82ae371982d33b4d84795fcccf30c95950`.
**Scope:** M0 baseline tests only; no deletion implementation changes. Implementation plan and accepted Claude amendments: `docs/PHASE2D0_MUST_SHOULD_COULD_PLAN.md`.

## Baseline implementation mapping
- `deletion_engine.py`: `_element_spans` currently pairs openings with the next closing tag; known self-closing collateral deletion.
- `edit_backend.py`: `change_field` dispatches three deletion keys; `_remove_native_unit` is separate.
- `edit_preflight.py`: checks several edit conflicts but native composite unit keys are not normalized.
- `edit_session.py`: retains accepted Tk deletion session key entry points.
- `test_edit_safety.py`: accepted legacy unit deletion refusals.
- `test_real_save_integrity.py`: optional real save smoke suite, requiring private `FREECOL_TEST_SAVE`.

## Synthetic baseline cases in `test_phase2d0_package_a_baseline.py`
| Case | Baseline expectation |
|---|---|
| Explicit unit deletion with sibling | PASS, sibling preserved |
| Self-closing unit deletion with sibling | **Expected failure**: current implementation can delete sibling while XML remains valid |
| Unit with cargo | PASS, conservative refusal |
| Unknown external unit reference | PASS, conservative refusal |
| Self-closing cached native settlement copy with neighbor | **Expected failure**: current span heuristic may sweep into neighbor |

**Important:** expectedFailure is a *temporary red-test marker*, not safety acceptance. M1/M2 must make the two intended assertions pass normally and must then remove the decorators. Unexpected success is a reason to recheck the fixture, not to claim the underlying defect is resolved.

## Remaining Package A steps (not yet delivered)
1. M0: record supported/refused cases and writer forms for real FreeCol saved `unit`, `aiUnit`, `ownedUnits`, cached settlement, without committing any private save.
2. M1: implement structure-aware expat-based byte locator with quote-aware self-closing detection; reject malformed/unsupported forms and cross-check with ElementTree.
3. M1: roundtrip all element slices including nested same-name, quoted `>`, look-alikes in comments/CDATA, mixed form and repeated cached IDs.
4. M2 follows separately: independent tree-based survivor verifier with faulty-span injection. No policy expansion until mechanical swap and legacy tests pass.

## Governance
- No new Qt destructive controls. No change to accepted safe Tk behavior. Unsafe paths must be repaired/refused, not retained for compatibility.
- Complete Tk retirement is mandatory before stable v1.0, scheduled as release gate in 0.9 RC.
- No new work on closed FreeCol C1/C2 movement investigation.
- Branch implementation requires CI, user Windows and FreeCol evidence, independent code review (with deferred OC-001 follow-up) and Project Director's explicit approval before integration.
