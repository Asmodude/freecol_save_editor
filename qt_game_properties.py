"""Read-only saved game metadata; no assumption about option schema."""
from xml.etree.ElementTree import Element


def game_property_rows(document):
    """Expose persisted root/game attributes with explicit provenance."""
    rows=[]
    for label, node in (('Savegame',document.root),('Game',document.game)):
        for name, value in sorted(node.attrib.items(),key=lambda kv:kv[0].casefold()):
            rows.append(Element('gamePropertyView',{
                'id':label + ':' + name, 'source':label,
                'name':name, 'value':value}))
    return rows
