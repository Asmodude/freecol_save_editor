"""UI-free global record search, preserving authoritative source elements."""
import presentation

SEARCH_GROUPS=('Players','Colonies','Native settlements','Units')

def global_results(document, query, limit=250):
    term=query.strip().casefold()
    if not term:
        return []
    found=[]
    for group in SEARCH_GROUPS:
        for item in document.records.get(group, ()):
            owner=item.get('owner')
            fields=(item.get('id',''), item.get('name',''), item.get('username',''),
                    item.get('nationId',''), item.get('unitType',''), item.get('role',''),
                    document.owner_name(owner) if owner else '')
            if not any(term in str(field).casefold() or
                       term in presentation.readable(field).casefold()
                       for field in fields if field):
                continue
            name=(item.get('name') or item.get('username') or
                  presentation.readable(item.get('unitType') or item.get('nationId')) or item.get('id'))
            found.append((group,item,name,document.owner_name(owner) if owner else ''))
            if len(found)>=limit:
                return found
    return found
