"""Tk-independent staged edit state and accepted validation rules.

Phase 0 preserves the existing edit dictionary schema for edit_backend.produce().
"""
from movement_rules import movement_cap, UnknownMovement


class EditValidationError(ValueError):
    """A validation refusal whose message is already part of the Tk UI contract."""


class EditSession:
    def __init__(self):
        self.edits = {}

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
            try:
                ceiling = movement_cap(root, unit)
            except (UnknownMovement, TypeError) as exc:
                raise EditValidationError('Movement edit unavailable: ' + str(exc)) from exc
        else:
            ceiling = 100 if field in ('tax', 'sonsOfLibertyTarget') else 200 if field == 'experience' else 2_147_483_647
        if new > ceiling:
            raise EditValidationError(f'Invalid value: maximum is {ceiling}. Press Esc to cancel.')
        return new
