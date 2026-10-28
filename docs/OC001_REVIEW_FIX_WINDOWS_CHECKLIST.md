# OC-001 review fixes — Windows acceptance checklist (28 October 2026)

**Review:** Claude independent review of PR #9 at `e59feb1`, PASS WITH CAVEATS / not mergeable.

## Review corrections included

- H1: report source SHA-256 is bound to the exact archive bytes loaded by `SaveDocument.load`, not an arbitrarily changed file on disk. Loading a fresh save clears the report.
- M1: malformed JSON shapes, invalid checksum types and non-text probe data raise `HammerProbeError`, displayed as a Qt warning rather than an uncaught slot exception.
- M2: national liberty editor and backend export are restricted to living colonial players whose embedded nation type (including inherited abilities) grants `model.ability.electFoundingFather`. Conservative rule: rebel/independent player liberty edits remain unsupported; the FreeCol option `continueFoundingFatherRecruitment` is **not** emulated.
- M3: status reconciled in the OC-001 plan, Hammers audit and Outstanding Commitments.
- L1: Hammers label clarifies values are from the opened save and exclude staged changes.

## Focused Windows verification (project owner)

1. Pull latest `feature/special-resources-oc001`; verify branch + PR CI green on that exact SHA. Launch `py qt_readonly.py`.
2. Open `Morten.fsg`, import the previously generated Hammers JSON from **the exact same unmodified save**. Confirm Frederiksborg 14, Charlotte Amalie 0, and switching colonies updates the display.
3. **Stale-file rejection (safe copy, not original):** make a copy `A.fsg` and open that in Qt; create a production report from a *different turn/save* `B.fsg` with matching colony identities. Overwrite only `A.fsg` on disk with B **while Qt still has the old A loaded**, then import B's report: expect **rejection**, despite the disk file now matching. Do not overwrite your original `Morten.fsg`. In automated coverage this case is `test_oc001_loaded_snapshot_binding.py`.
4. **Malformed-report warning:** using a separate text file named `bad-hammers.json` containing just `[]`, choose File → Import verified Hammers report… and select it. Expect a warning dialog, no crash, no change to previously displayed figures.
5. **Liberty UI eligibility:** for Danish human player ensure National liberty points is editable/stageable. For Unknown / ineligible nation and dead colonial players, if present, ensure no liberty staging control is shown.
6. **Liberty FreeCol roundtrip (still mandatory):** make a backup of the original save; stage a modest, non-threshold-crossing national liberty change for your Danish player, use Save As to a **new** .fsg; verify exported national `liberty` attribute, open exported .fsg in FreeCol, inspect Continental Congress, advance one turn, save, and reopen in both FreeCol/Qt. Record observed liberty and relevant Founding Father changes, including any automatic recruitment. Never overwrite the original source. If unexpectedly unable to load the exported save, record FreeCol's error without advancing further.
7. If any test fails, report exact step, symptoms and relevant screenshots/log output.

**Merge gate:** No merge/tag until corrected-head CI, Windows rechecks, liberty FreeCol roundtrip, independent review closure and explicit project owner approval. OC-002 and OC-004 remain outside this PR and unresolved.
