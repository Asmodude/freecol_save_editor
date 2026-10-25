"""Qt navigation-tree construction, extracted from the main window.

The mixin intentionally uses the owning window's document, icon services,
and navigation widget to preserve Phase 1 rendering and selection semantics.
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QBrush
from PySide6.QtWidgets import QTreeWidgetItem

import presentation
from qt_navigation import human_player_id
from qt_unit_groups import unit_groups, unit_group_scope
from qt_flag_icons import flag_icon


class NavigationBuilderMixin:
    def install_navigation(self):
        """Build the approved navigation structure; disable views not implemented yet."""
        self.navigation.blockSignals(True)
        self.navigation.setUpdatesEnabled(False)
        self.navigation.clear()
        def entry(parent, label, group=None, scope=None, ready=True, kind='section', nation_id=None, native=False):
            item = QTreeWidgetItem([label])
            item.setIcon(0, flag_icon(nation_id, 17) if kind == 'nation' and nation_id and not native and not flag_icon(nation_id, 17).isNull() else self.navigation_icons.icon(kind, nation_id, native))
            if nation_id:
                # Diagnostic provenance for mismatched or unfamiliar faction art.
                item.setToolTip(0, f'Saved nation ID: {nation_id}')
            if kind == 'nation':
                font = QFont(item.font(0))
                font.setBold(True)
                item.setFont(0, font)
            if parent is None:
                self.navigation.addTopLevelItem(item)
            else:
                parent.addChild(item)
            if group and ready:
                item.setData(0, Qt.ItemDataRole.UserRole, (group, scope))
            else:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                if not ready:
                    item.setText(0, label + '  (planned)')
                    item.setForeground(0, QBrush(self.palette().color(self.foregroundRole()).lighter(135)))
                    item.setToolTip(0, 'Not yet implemented in the Phase 1 Qt preview')
            return item

        def grouped_unit_entries(parent, owner):
            if not doc or not owner:
                return
            groups = unit_groups(doc, owner)
            colonies = [c for c in doc.colonies if c.get('owner') == owner and c.get('id')]
            for colony in sorted(colonies, key=lambda c:(c.get('name') or '').casefold()):
                key = ('colony', colony.get('id'))
                count = len(groups.get(key, ()))
                if count:
                    entry(parent, f"{colony.get('name') or colony.get('id')} ({count})",
                          'Units', unit_group_scope(owner, 'colony', colony.get('id')), kind='colony')
            aboard = groups.get(('ship', ''), ())
            if aboard:
                ships_node = entry(parent, f'Aboard ships ({len(aboard)})',
                                   'Units', unit_group_scope(owner, 'ship'))
                carriers = sorted(
                    (unit for unit in doc.units
                     if unit.get('owner') == owner
                     and ('vessel', unit.get('id')) in groups
                     and groups[('vessel', unit.get('id'))]),
                    key=lambda unit: (presentation.readable(unit.get('unitType')).casefold(),
                                      unit.get('id') or ''))
                for carrier in carriers:
                    passengers = groups[('vessel', carrier.get('id'))]
                    name = presentation.readable(carrier.get('unitType'))
                    entry(ships_node, f'{name} — {carrier.get("id")} ({len(passengers)})',
                          'Units', unit_group_scope(owner, 'vessel', carrier.get('id')))
            for label, kind in (('In the field', 'field'), ('Other locations', 'other')):
                count = len(groups.get((kind, ''), ()))
                if count:
                    entry(parent, f'{label} ({count})', 'Units',
                          unit_group_scope(owner, kind))
        
        doc = self.document
        own = human_player_id(doc) if doc else None
        human = doc.players.get(own) if doc and own else None
        nation = presentation.readable(human.get('nationId')) if human is not None else 'My Nation'
        my = entry(None, nation + ' (Player)', kind='nation', nation_id=human.get('nationId') if human is not None else None)
        overview = entry(my, 'Overview', 'Players', 'mine', kind='overview')
        entry(my, 'Diplomacy', 'Diplomacy', 'mine', kind='diplomacy')
        my_colonies = entry(my, 'Colonies', 'Colonies', 'mine', kind='colonies')
        if doc and own:
            for colony in sorted((c for c in doc.colonies if c.get('owner') == own),
                                 key=lambda c: (c.get('name') or '').casefold()):
                entry(my_colonies, colony.get('name') or colony.get('id'),
                      'Colonies', 'colony-id:' + colony.get('id'), kind='colony')
        my_units = entry(my, 'Units', 'Units', 'mine', kind='units')
        grouped_unit_entries(my_units, own)
        entry(my, 'Goods', 'National Goods', 'mine', kind='goods')
        entry(my, 'Founding Fathers', 'Founding Fathers', 'mine', kind='fathers')
        entry(my, 'Player Options', ready=False, kind='options')

        rivals = entry(None, 'Rival Nations', kind='nation')
        entry(rivals, 'All European rivals', 'Players', 'rivals')
        natives = entry(None, 'Native Nations', kind='nation', native=True)
        entry(natives, 'All native settlements', 'Native settlements', 'native')
        if doc:
            for player in doc.players.values():
                pid = player.get('id')
                if pid == own:
                    continue
                nation_id = player.get('nationId') or player.get('nation')
                if player.get('playerType') == 'colonial':
                    label = presentation.readable(nation_id) or pid
                    rival = entry(rivals, label, kind='nation', nation_id=nation_id)
                    entry(rival, 'Overview', 'Players', 'player:' + pid, kind='overview')
                    entry(rival, 'Diplomacy', 'Diplomacy', 'player:' + pid, kind='diplomacy')
                    colony_group = entry(rival, 'Colonies', 'Colonies', 'player:' + pid)
                    for colony in sorted((c for c in doc.colonies if c.get('owner') == pid),
                                         key=lambda c: (c.get('name') or '').casefold()):
                        entry(colony_group, colony.get('name') or colony.get('id'),
                              'Colonies', 'colony-id:' + colony.get('id'))
                    rival_units = entry(rival, 'Units', 'Units', 'player:' + pid)
                    grouped_unit_entries(rival_units, pid)
                    entry(rival, 'Goods', 'National Goods', 'player:' + pid)
                    entry(rival, 'Founding Fathers', 'Founding Fathers', 'player:' + pid)
                    entry(rival, 'Player Options', ready=False)
                elif player.get('playerType') in ('indian', 'native'):
                    label = presentation.readable(nation_id) or pid
                    native = entry(natives, label, kind='nation', nation_id=nation_id, native=True)
                    entry(native, 'Overview', 'Players', 'player:' + pid, kind='overview')
                    entry(native, 'Diplomacy', 'Diplomacy', 'player:' + pid, kind='diplomacy')
                    settlements = entry(native, 'Settlements', 'Native settlements', 'native-owner:' + pid)
                    for village in sorted((v for v in doc.native_settlements if v.get('owner') == pid),
                                          key=lambda v: (v.get('name') or '').casefold()):
                        if village.get('id'):
                            entry(settlements, village.get('name') or village.get('id'),
                                  'Native settlements', 'settlement-id:' + village.get('id'),
                                  kind='colony')
                    native_units = entry(native, 'Units', 'Units', 'player:' + pid)
                    grouped_unit_entries(native_units, pid)

        entry(None, 'Map', ready=False, kind='map')
        entry(None, 'Game properties', 'Game properties', 'game', kind='options')
        my.setExpanded(True)
        rivals.setExpanded(True)
        natives.setExpanded(True)
        self.navigation.blockSignals(False)
        self.navigation.setCurrentItem(overview)
        self.navigation.setUpdatesEnabled(True)

