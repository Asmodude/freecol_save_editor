# Independent Claude review request — Phase 2D-1.5 (PR #8)

**Review target:** `feature/phase2d1-5-component-performance`, compared to `main`.  
**Windows:** A1–A9/B1–B6/C1–C3 accepted (18/18); focused A7 overlap and B2 non-personnel equipment corrections explicitly accepted 27 October 2026.  
**CI:** Require green push and pull_request jobs at review HEAD; check SHA, not just a historic green run.  
**Status:** Independent review not yet returned; review findings are blocking until triaged.

Please act as independent reviewer, **not implementer**. Read the actual changed code and relevant existing tests, plus `docs/PHASE2D1_5_IMPLEMENTATION_PLAN.md`, `docs/OUTSTANDING_COMMITMENTS.md`, and `docs/PHASE2D_IMPLEMENTATION_PLAN.md`.

1. Verify shared `NumericStageEditor` integrations in Overview, Colony Goods, Workers, Native Alarm: stable identity when sorted, source/staged semantics, tooltips, width, validation, Enter/button actions, undo, source immutability and no dangling UI callbacks.
2. Review lazy `EquipmentRulesIndex` lifecycle, cached/uncached parity, duplicate specification elements, unit-owner dynamics, save switching and whether indexing full `root.iter()` creates regressions.
3. **Mandatory high scrutiny:** Determine whether hard-coded `_NON_EQUIPPABLE_TYPES` in `equipment_rules.py` is sufficient and consistent with actual standard FreeCol specification, unit-type inheritance and dynamic/modded units; check movement rules and role eligibility as used at export. Identify unsafe false positives/negatives. Explicitly state if a more authoritative rules-based solution is required.
4. Check that blocking all options except Default for certain units does not inadvertently disable legitimate staging of current equipment, and that rejection happens in backend as well as GUI.
5. Review performance benchmark methodology and actual-save Windows data: 7,855,956-byte XML; load 206.6 ms; lazy index 12.7 ms; 15 widgets 645.4 ms uncached vs 13.4 ms indexed (48.20x); first indexed pass incl. index 26.1 ms. State scope/limits.
6. Ensure deferred obligations remain explicit: OC-001 Special Resources before C3, OC-002 movement-error gate, OC-004 deletion safety before destructive Qt UI. Do not mistake 2D-1.5 approval for permission to skip these.
7. Identify regressions in existing tests/CI and propose focused fixes with severity (blocker/major/minor). Deliver **PASS**, **PASS WITH CAVEATS** or **FAIL** with file/line references, exact reproduction paths and recommended regression tests.

**Governance:** Do not merge, tag, delete branches or silently broaden implementation. Report findings to Project Director; ChatGPT coordinates fixes only after review.
