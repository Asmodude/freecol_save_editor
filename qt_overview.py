"""Read-only contextual summaries for Phase 1 Qt.

Only fields present in the savegame are shown; absent values are not guessed.
"""
from qt_colony_details import colony_sections
from qt_final_visual_format import established_turn
import presentation


def record_overview(group, element, document):
    name = element.get('name') or element.get('username') or element.get('id') or 'Unnamed record'
    lines = [name, '']
    def field(label, value):
        if value is not None and value != '':
            lines.append(f'{label}: {value}')
    if group == 'Colonies':
        sections = colony_sections(element, document)
        field('Owner', document.owner_name(element.get('owner')))
        field('Map location', document.location_name(element.get('tile')))
        field('Established', established_turn(element.get('established')))
        field('Colony liberty points', element.get('liberty'))
        # The save serializes goods stock, not FreeCol's calculated production.
        # An explicit unavailable state is safer than a guessed per-turn rate.
        field('Hammers per turn', 'Unavailable — requires FreeCol production calculation')
        field('Sons of Liberty', element.get('sonsOfLiberty'))
        field('Production bonus', element.get('productionBonus'))
        lines.extend(['', 'Population and activity'])
        field('Workplace workers', len(sections['Workers'][1]))
        field('Stationed units', len(sections['Stationed units'][1]))
        field('Buildings', len(sections['Buildings'][1]))
        field('Stored goods types', sum(1 for _, amount in sections['Goods'][1] if amount.isdigit() and int(amount) > 0))
        field('Warehouse goods total', sum(int(v[1]) for v in sections['Goods'][1] if v[1].isdigit()))
        # Briefing-style summary: top stockpiles and the largest workplaces.
        # Values come exclusively from the authoritative colony XML.
        stockpiles = []
        for goods_name, quantity in sections['Goods'][1]:
            try:
                amount = int(quantity)
            except (TypeError, ValueError):
                continue
            if amount > 0:
                stockpiles.append((amount, goods_name))
        stockpiles.sort(key=lambda item: (-item[0], item[1].casefold()))
        if stockpiles:
            lines.extend(['', 'Largest warehouse stockpiles'])
            lines.extend(f'  {goods_name}: {amount:,}' for amount, goods_name in stockpiles[:5])
            if len(stockpiles) > 5:
                lines.append(f'  …and {len(stockpiles) - 5} more goods types')
        occupied = [(building, int(count)) for building, _, _, count
                    in sections['Buildings'][1] if count.isdigit() and int(count) > 0]
        if occupied:
            lines.extend(['', 'Occupied buildings'])
            lines.extend(f'  {building}: {count} worker{"s" if count != 1 else ""}'
                         for building, count in occupied)
        lines.extend(['', 'Select Buildings, Workers, Stationed units or Goods for item-level details.'])
    elif group == 'Native settlements':
        field('Nation', document.owner_name(element.get('owner')))
        field('Location', document.location_name(element.get('tile')))
        field('Learnable skill', presentation.readable(element.get('learnableSkill')))
        for i in range(3):
            field(f'Wanted goods {i+1}', presentation.readable(element.get(f'wantedGoods{i}')))
        lines.extend(['', 'Select Affiliated units for units with this settlement as home or explicit affiliation.'])
    elif group == 'Founding Fathers':
        field('Status', element.get('status'))
        field('FreeCol identifier', element.get('id'))
        lines.extend(['', 'This is a read-only view of the owning player’s father membership.'])
    elif group == 'Players':
        field('Nation', presentation.readable(element.get('nationId')))
        field('Type', element.get('playerType'))
        field('Gold', element.get('gold'))
        if element.get('playerType', '').lower() not in ('native', 'indian') and element.get('gold') != '-2147483648':
            field('Tax', element.get('tax'))
        field('Score', element.get('score'))
        # Progress attributes are sourced from the player, never warehouse goods.
        field('National liberty points', element.get('liberty'))
        field('Immigration points', element.get('immigration'))
        field('Immigration required', element.get('immigrationRequired'))
        accumulated = element.get('immigration')
        threshold = element.get('immigrationRequired')
        if (accumulated and threshold and accumulated.isascii() and accumulated.isdecimal()
                and threshold.isascii() and threshold.isdecimal() and int(threshold) > 0):
            field('Next immigrant progress', f'{int(accumulated):,} / {int(threshold):,}')
        field('Colonies', document.colony_counts.get(element.get('id'), 0))
        field('Native settlements', document.native_counts.get(element.get('id'), 0))
    elif group == 'Units':
        field('Type', presentation.readable(element.get('unitType')))
        field('Owner', document.owner_name(element.get('owner')))
        field('Location', document.location_name(element.get('location')))
        field('Role', presentation.readable(element.get('role')))
        field('Experience', element.get('experience'))
        field('Moves left', element.get('movesLeft'))
        field('State', element.get('state'))
    return '\n'.join(lines)
