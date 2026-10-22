import sys
sys.path.insert(0,'/mnt/data/freecol_v061')
from freecol_explorer import Explorer
from tkinter import filedialog
import xml.etree.ElementTree as ET
from pathlib import Path
x=Explorer();x.withdraw()
filedialog.askopenfilename=lambda **kw:'/mnt/data/Morten2.fsg'
x.open_save();assert x.current_path
cs=next(c for c in x.records['Colonies'] if c.get('name')=='Christiansborg')
x.render_terrain_preview(cs)
center=next(t for t in x.terrain_by_xy.values() if t.get('id')==cs.get('tile'))
print('christiansborg center',center.get('x'),center.get('y'))
coords=[(int(center.get('x'))+dx,int(center.get('y'))+dy) for d,(dx,dy) in x.TERRAIN_OFFSETS.items() if d!='C']
print('8 tiles',coords, 'oceans',sum('ocean' in x.terrain_by_xy.get(c,ET.Element('x')).get('type','').lower() for c in coords))
unit=next(u for u in x.records['Units'] if u.get('id')=='unit:34488')
x.tabs.select(3);x.active='Units';x.refresh()
i=x.records['Units'].index(unit)
x.tables['Units'].selection_set(str(i));x.update_inline_equipment()
print('unit',x.equip_unit.cget('text'),'roles',x.equip_select['values'])
assert 'model.role.dragoon' in x.equip_select['values']
x.equip_choice.set('model.role.dragoon');x.toggle_equipment_sets();x.stage_inline_equipment()
assert x.edits[('unit:34488','equipment')][1]==('model.role.dragoon',1)
print('staged',x.edits[('unit:34488','equipment')]);x.destroy()
