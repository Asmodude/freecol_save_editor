from tkinter import filedialog
from freecol_explorer import Explorer
x=Explorer();x.withdraw()
filedialog.askopenfilename=lambda **kwargs:'/mnt/data/Morten2.fsg'
x.open_save()
colony=next(c for c in x.records['Colonies'] if c.get('name')=='Christiansborg')
x.render_terrain_preview(colony)
selected=x.terrain_by_xy[(83,116)]
x.inspect_terrain_tile(selected,0,-2)
result=x.terrain_info.get('1.0','end')
print(result)
assert 'Sugar' in result and 'Plow' in result
assert 'None saved' not in result
assert 'Coordinates: (83, 116)' in result
x.destroy()
