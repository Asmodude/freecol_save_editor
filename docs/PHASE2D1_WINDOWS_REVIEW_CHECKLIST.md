# Phase 2D-1 — Review and Windows Acceptance Checklist

**Status: DRAFT / NOT ACCEPTED.** Source branch: `feature/phase2d-ux-and-deletion-parity`.
**Scope:** PySide6 staging clarity and shared equipment UI, **no deletion work**.
**Gate/order:** green CI on exact tested commit → user Windows usability/functional tests → fixes and focused Windows retests → independent Claude code review → any review-driven corrections/retests → explicit user acceptance. Do not merge/tag/delete branch without explicit permission.

## Independent review (Claude) — after initial Windows testing and fixes, before final sign-off
- Inspect `qt_stage_controls.py`, `qt_equipment_editor.py`, `qt_overview_panel.py`, `qt_detail_tabs_view.py`, `qt_diplomacy_view.py`, `qt_readonly.py` and new tests against `docs/PHASE2D_IMPLEMENTATION_PLAN.md`.
- Check that duplicated equipment code is truly consolidated and no view-specific behaviour regressed (including Hardy Pioneer natural suggestion, roleCount=0 for default, 20–100 tools, role-dependent moves, mouse-wheel protections and sorting identity).
- Check that all eight staging-action controls say **Stage Change**, with Enter-to-stage behaviour intact and no accidental relabel of Undo.
- Audit layout overflow/resizing in Workers, Stationed Units, Goods, diplomacy and narrow windows. Check screen-reader names/focus/tooltips.
- Check Inspector and Raw XML source-only labels are accurate on all selection types; staged changes stay in staged panel until Save As.
- Identify missing behavioural tests, unintended UI changes or leftover duplicated code. Return PASS / PASS WITH CAVEATS / REVISE.

## Windows checks (user) — before Claude's independent review
1. Pull latest `feature/phase2d-ux-and-deletion-parity`; run `py -m unittest discover -v` (with `FREECOL_TEST_SAVE` set if available).
2. Launch `py qt_readonly.py`. The instruction line is *always visible* directly below toolbar, including after loading save and switching sections.
3. Check Stage Change in Players Gold/Tax; Units Experience/Moves/Equipment; Colonies Goods/Workers XP/Stationed Equipment; Native Settlement Skill/Alarm; rival/native Diplomacy. Each click stages precisely one change; Enter staging remains functional.
4. Resize window narrow and wide. Verify readable button labels, access to fields and tables, no clipped or inaccessible controls.
5. Compare same unit between Units Overview and colony Stationed Units: role labels match; valid choices match; pending state matches; switching role updates quantity consistently.
6. Hardy Pioneer with default role: both editors suggest Pioneer with 100 tools *without staging automatically*. Selecting 80 tools stages `roleCount=4`. Selecting Default stages `roleCount=0`. Check movement behaviour retains previously accepted proportional conversion.
7. Mouse-wheel scroll over unfocused role dropdown and tool quantity: must not silently change equipment selection.
8. Stage Pioneer/100 tools, inspect Raw XML: source still says `model.role.default` and `roleCount=0`. Source-only notice explains this. Staged panel shows proposed change. Undo restores state.
9. Stage multiple edits, Save As new unused path, verify source byte-for-byte unchanged, reopen edited save in FreeCol, advance one turn, save, reload.
10. Close/reopen with unexported changes: existing discard warnings and undo actions still work.

**Report:** screenshot(s) for button width and layout, PASS/FAIL per test, exact branch SHA, CI run URL and any FreeCol roundtrip findings.

**Not approved:** deletion engine hardening and all destructive UI (2D-0 onward).
