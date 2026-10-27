"""Tk-independent staged edit state and accepted validation rules.

Phase 0 preserves the existing edit dictionary schema for edit_backend.produce().
"""
from movement_rules import movement_cap, UnknownMovement
from equipment_rules import validate_equipment
from deletion_engine import plan_settlement
from edit_backend import produce
from pathlib import Path


class EditValidationError(ValueError):
    """A validation refusal whose message is already part of the Tk UI contract."""


class EditSession:
    def __init__(self):
        self.edits = {}
        self.exported_snapshot = {}
        self.exported_path = None

    @property
    def has_unexported_changes(self):
        return self.edits != self.exported_snapshot

    @property
    def count(self):
        return len(self.edits)

    def clear(self):
        self.edits.clear()

    def unstage(self, key):
        self.edits.pop(key, None)

    def is_changed(self, key):
        return key in self.edits

    def staged_value(self, key, default):
        return self.edits.get(key, (None, default))[1]

    def items(self):
        return self.edits.items()

    def stage(self, key, original, new):
        # A staged display value must never replace the opened-save original.
        if key in self.edits:
            known_original = self.edits[key][0]
            if original != known_original:
                raise EditValidationError('Original value differs from opened save')
        if new == original:
            self.unstage(key)
        else:
            self.edits[key] = (original, new)
        return new

    def validate(self, key, raw_value, *, original, root=None, units=(), professions=()):
        """Validate the same numeric/choice edits as the v0.6.2.6.4 cell editor."""
        raw = raw_value.strip()
        field = key[1]
        choice = field == 'learnableSkill' or field.startswith('stance|')
        if choice:
            allowed = professions if field == 'learnableSkill' else ('peace', 'war', 'cease_fire', 'alliance')
            if raw not in allowed:
                raise EditValidationError('Invalid choice')
            return raw
        if not raw.isascii() or not raw.isdecimal():
            raise EditValidationError('Invalid quantity: enter a non-negative whole number. Press Esc to cancel.')
        new = int(raw)
        if field == 'movesLeft':
            unit = next((u for u in units if u.get('id') == key[0]), None)
            if unit is None:
                raise EditValidationError('Movement edit unavailable: Unit not found in authoritative records')
            try:
                ceiling = movement_cap(root, unit)
            except (UnknownMovement, TypeError) as exc:
                raise EditValidationError('Movement edit unavailable: ' + str(exc)) from exc
        else:
            ceiling = 100 if field in ('tax', 'sonsOfLibertyTarget') else 200 if field == 'experience' else 2_147_483_647
        if new > ceiling:
            raise EditValidationError(f'Invalid value: maximum is {ceiling}. Press Esc to cancel.')
        return new

    @staticmethod
    def editable_fields(group, element):
        """Existing Overview editability, including native gold sentinel."""
        if group == 'Players':
            return {'tax'} | ({'gold', 'liberty'} if element.get('gold') != '-2147483648' else set())
        if group == 'Units':
            return {'experience', 'movesLeft'}
        if group == 'Colonies':
            return {'sonsOfLiberty'}
        if group == 'Native settlements':
            return {'learnableSkill'}
        return set()

    def stage_equipment(self, root, unit, role, amount):
        """Preserve the historical equipment/delete conflict and role validation."""
        uid=unit.get('id')
        if (uid,'deleteUnit') in self.edits or (uid,'deleteNativeUnit') in self.edits:
            raise ValueError('Unit is already staged for deletion')
        if role == 'model.role.default': amount = 0
        validate_equipment(root,unit,role,amount)
        original=(unit.get('role','model.role.default'),int(unit.get('roleCount','1')))
        return self.stage((uid,'equipment'),original,(role,amount))

    def stage_unit_deletion(self, unit_id):
        """Stage a confirmed standard unit deletion (confirmation stays in UI)."""
        self.edits[(unit_id,'deleteUnit')]=('present','delete')

    def plan_settlement_deletion(self, xml_bytes, settlement_id):
        """Validate settlement dependency graph before presenting confirmation."""
        return plan_settlement(xml_bytes,settlement_id)

    def stage_settlement_deletion(self, settlement_id):
        """Stage a previously planned and confirmed settlement deletion."""
        self.edits[(settlement_id,'deleteSettlement')]=('present','delete')

    def stage_native_unit_deletion(self, unit_id, village_id):
        """Retain the historical composite key for native unit deletion."""
        self.edits[(unit_id+'|'+village_id,'deleteNativeUnit')]=('present','delete')

    def save_as(self, source, destination):
        """Delegate to the accepted fail-closed producer; never overwrite a file."""
        source=Path(source)
        destination=Path(destination)
        if source.resolve()==destination.resolve():
            raise ValueError('You cannot overwrite the opened save. Choose another filename.')
        if destination.exists():
            raise ValueError('For safety, this editor never overwrites an existing file. Choose a new filename.')
        result = produce(source,destination,self.edits)
        # Only acknowledge the exact exported changes after successful production.
        self.exported_snapshot = dict(self.edits)
        self.exported_path = destination
        return result
