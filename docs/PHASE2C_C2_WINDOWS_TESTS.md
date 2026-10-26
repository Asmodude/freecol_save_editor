# Phase 2C — Checkpoint C2 Windows acceptance tests

**Status:** TEST HANDOVER — not accepted. Use branch `feature/phase2c-editing-parity`; capture the exact head SHA and corresponding green GitHub CI before testing. Preserve the original .fsg. Launch the **Qt compare/model view** used for C1.

Mark each as PASS, FAIL, or N/A (with reason). Report test ID, actual behavior and screenshots for failures. Reuse the same known-good save as C1 where possible.

## Equipment (C2-01–C2-08)
- **C2-01** Units → ordinary equippable land unit → Overview. Role dropdown lists only verified ruleset-legal choices; role and count are presented as one composite editor. No change staged merely by choosing a role.
- **C2-02** Choose another legal role and stage; verify exactly one Equipment entry in Staged Changes, corresponding role shown in Units list, and source record remains unchanged until export.
- **C2-03** Change role again; verify the same staged entry updates rather than becoming a duplicate. Undo and verify initial equipment restored.
- **C2-04** Find a Hardy Pioneer saved as default role, if present. Pioneer should be suggested (not automatically staged), with count 1–5 displayed as 20–100 tools. Set 4 and stage; expect Pioneer ×4 / 80 tools.
- **C2-05** Confirm equipment changes do not subtract tools, horses or muskets from colony warehouse stock; no implicit inventory consumption.
- **C2-06** Stage Dragoon role and a move count legal for Dragoon but above Soldier cap; reverting role alone must be refused. Adjust/undo movement first, then revert role. N/A if no eligible unit.
- **C2-07** Naval/native/otherwise non-equippable units must not offer unsupported role changes.
- **C2-08** Navigate between Units and relevant colony workers/stationed units. Staged equipment must remain attached to the correct unit ID.

## Colony stock and Sons of Liberty (C2-09–C2-17)
- **C2-09** Colony → Goods: edit an existing nonzero stockpile using Enter/pencil. Verify staged value, original amount and correct full goods-type identity.
- **C2-10** Find a listed goods type with absent/zero stock, stage positive stock; verify pending change and successful safe export to **new** file (not source overwrite). N/A if no eligible type/warehouse.
- **C2-11** Sort Goods table before staging two different types. Confirm both changes target their correct goods, not their former row positions.
- **C2-12** Invalid goods amounts (negative, text, >2,147,483,647) must be refused with existing changes intact.
- **C2-13** With Goods tab active, stage edit and confirm tab remains Goods. Navigate away/back; staged value persists. Undo one and verify other staged goods unchanged.
- **C2-14** National Goods aggregates must clearly indicate whether they reflect **source** or **staged** amounts; report ambiguity or discrepancies.
- **C2-15** In eligible populated colony Overview, stage Sons of Liberty target (0–100); verify explicitly marked as proposed/staged, not yet changed in source XML.
- **C2-16** Reject negative or >100 Sons of Liberty target and unusual colonies where ordinary liberty/population formula cannot be established; N/A if not reproducible.
- **C2-17** Export SoL to a new file and reopen: liberty, sonsOfLiberty, oldSonsOfLiberty, tories, oldTories and productionBonus must all reflect backend recalculation; no claim that these were already changed before export.

## Diplomacy (C2-18–C2-26)
- **C2-18** Diplomacy remains two separate tables: Rival Nations and Natives. Each counterpart appears once, not duplicated.
- **C2-19** Stage a source-backed Stance change (e.g. peace → war) in a relationship with an existing equal reciprocal entry; one staged change. Reverse nation view must show the proposed Stance, too.
- **C2-20** Inspect Staged Changes: Stance is explicitly identified as affecting **both directions**. Attempt to stage the reverse direction independently; must refuse, leaving original staged change intact.
- **C2-21** Stage a different Tension amount; verify direction-specific change, that opposite direction remains unaltered, and Staged Changes distinguishes it from reciprocal Stance.
- **C2-22** Stance and Tension invalid/unsupported values must be refused; pre-existing staged values preserved.
- **C2-23** Missing Stance/Tension relations must be shown as absent/non-editable, never implicitly created.
- **C2-24** With either Rival Nations or Natives tab active, stage a relationship and confirm tab, selected counterpart, staged controls and right-hand Inspector remain consistent.
- **C2-25** Sort a diplomacy table and stage a change: correct counterpart must receive it regardless of display row. Undo selected change and confirm both visible directions revert.
- **C2-26** Save As staged diplomacy to a new FSG, reopen in editor and verify reciprocal Stance records and directional Tension values. Full FreeCol behavior deferred to C3.

## Native settlement (C2-27–C2-32)
- **C2-27** Settlement Overview → Learnable skill selector displays only skills available from real native settlements in opened save.
- **C2-28** Select another skill, stage and navigate away/back; staged skill remains visible and is attached to correct settlement.
- **C2-29** Unsupported/nonexistent skills cannot be chosen; source settlement unchanged until export.
- **C2-30** Settlement → Alarm: edit a present colonial-player Alarm value. It must target the correct counterpart and not alter national Tension or another alarm.
- **C2-31** Missing Alarm entries remain non-editable; negative/text/out-of-range Alarm input must be refused.
- **C2-32** Sort Alarm and stage an edit; verify correct player identity. Undo restores original while other staged changes remain.

## Combined staging, export and regression (C2-33–C2-38)
- **C2-33** Stage at least one change in each available C2 category and C1 Gold/Tax/XP/Moves. Verify Staged Changes count, source/staged labels, and no duplicate keys.
- **C2-34** Undo one C2 edit while retaining unrelated changes; then Unstage all and verify all views return to source values.
- **C2-35** Stage changes, cancel Save As and confirm no file written; source FSG must remain byte-for-byte unchanged.
- **C2-36** Export to a new filename and reopen in editor; verify every staged change available in the test save. Refuse overwriting source or existing destination.
- **C2-37** Check existing C1 inline editing and selected-row staged markers after C2 changes; C1 functionality must remain intact.
- **C2-38** Navigate repeatedly between Units, Colonies, two Diplomacy tables and Native Settlements after staging/undo. No crashes, wrong-tab jumps, stale selection, or incorrect target.

## C2 acceptance boundary
These Windows tests prove Qt staging and non-destructive export/reopen; they do **not** replace Phase 2C C3's mandatory combined automated export, non-target-attribute preservation and full FreeCol **load → advance turn → save → reload** roundtrips. Do not merge/tag/delete the branch or call C2 accepted until the user confirms results and any omissions are resolved.
