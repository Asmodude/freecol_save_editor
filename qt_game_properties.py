"""Exact, read-only metadata and option values from saved XML."""
from xml.etree.ElementTree import Element


def _option_nodes(node, path):
    """Visit only option-related branches; never walk the potentially huge game map."""
    for index, child in enumerate(node):
        tag=child.tag.lower()
        if 'option' not in tag:
            continue
        child_path=path + '/' + str(index)
        yield child, child_path
        yield from _option_nodes(child, child_path)


def game_property_rows(document):
    rows=[]
    for label, node in (('Savegame',document.root),('Game',document.game)):
        for name, value in sorted(node.attrib.items(),key=lambda kv:kv[0].casefold()):
            rows.append(Element('gamePropertyView',{
                'id':label + ':' + name, 'source':label,
                'name':name, 'value':value, 'path':''}))
        for option, path in _option_nodes(node, ''):
            # Only actual persisted values. Empty groups have no value to report.
            if 'value' not in option.attrib:
                continue
            option_name=option.get('id') or option.get('name') or option.tag
            rows.append(Element('gamePropertyView',{
                'id':label + ':' + path, 'source':label + ' options',
                'name':option_name, 'value':option.get('value'), 'path':path}))
    return rows


def game_property_source(document, row):
    """Resolve a view row to its original source XML element, never a copy."""
    label=row.get('source','')
    node=document.root if label.startswith('Savegame') else document.game
    path=row.get('path','')
    if not path:
        return node
    for step in path.strip('/').split('/'):
        node=list(node)[int(step)]
    return node
