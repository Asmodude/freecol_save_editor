"""FreeCol Save Editor v0.5.5 Equipment Test — inline existing-goods editing. Python 3.9+."""
from save_document import SaveDocument
from edit_session import EditSession, EditValidationError
import presentation
import map_render
from unit_records import authoritative_units
from location_names import colony_tile_names, location_label, unit_locations
import collections
import pathlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import zipfile
import json
import os
from terrain_art import FreeColArt, terrain_art_key
from edit_backend import produce
from deletion_engine import plan_settlement, UnsafeDeletion
from movement_rules import movement_cap, UnknownMovement
from equipment_rules import ROLES,validate_equipment
from map_window import MapEditorWindow

class Explorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('FreeCol Save Editor v0.6.2.6.4 — Context-Sensitive Interface (READ-ONLY TERRAIN)')
        self.geometry('1180x750')
        self.records = {}
        self.edit_session = EditSession()
        self.edits = self.edit_session.edits
        self.cell_editor = None
        self.editing_cell = None
        self.xml_bytes = None
        self.root = None
        self.players = {}
        self.locations = {}
        self.active = 'Players'
        self.current_path = None
        self.config_path = pathlib.Path.home() / '.freecol_save_explorer.json'
        self.settings = self.load_settings()
        self.goods_types = []
        self.professions = []
        self.search = tk.StringVar()
        self.owner_filter = tk.StringVar(value='All players')
        self.status = tk.StringVar(value='Open a FreeCol .fsg save to begin. No save files are modified.')
        toolbar = ttk.Frame(self, padding=8)
        toolbar.pack(fill='x')
        ttk.Button(toolbar, text='Open .fsg…', command=self.open_save).pack(side='left')
        ttk.Button(toolbar, text='Save As edited .fsg…', command=self.save_as).pack(side='left', padx=6)
        ttk.Button(toolbar, text='Map Editor…', command=self.open_map_editor).pack(side='left', padx=8)
        ttk.Label(toolbar, text='   Search:').pack(side='left')
        ttk.Entry(toolbar, textvariable=self.search, width=36).pack(side='left', padx=5)
        self.search.trace_add('write', lambda *_: self.refresh())
        ttk.Label(toolbar, text='Search scope:').pack(side='left', padx=(10,4))
        self.scope=tk.StringVar(value='Current tab')
        ttk.Combobox(toolbar, textvariable=self.scope, values=['Current tab','All tabs'], state='readonly', width=13).pack(side='left')
        self.scope.trace_add('write', lambda *_: self.refresh())
        ttk.Label(toolbar, text='Owner:').pack(side='left', padx=(15,5))
        self.combo = ttk.Combobox(toolbar, textvariable=self.owner_filter, state='readonly', width=29)
        self.combo.pack(side='left')
        self.combo['values'] = ['All players']
        self.combo.bind('<<ComboboxSelected>>', lambda _: self.refresh())
        ttk.Label(self, text='SAFE EDIT — double-click numbers in Goods, Player, Unit or Colony SoL overview; Enter stages; Save As never overwrites', foreground='#286d44').pack(anchor='w', padx=12)
        self.split = ttk.PanedWindow(self, orient='horizontal')
        self.split.pack(fill='both',expand=True,padx=9,pady=7)
        left=ttk.Frame(self.split); right=ttk.Frame(self.split)
        self.split.add(left, weight=3); self.split.add(right,weight=2)
        self.tabs = ttk.Notebook(left)
        self.tabs.pack(fill='both', expand=True)
        self.tables = {}
        self.columns = {
            'Players': ('ID','Name','Nation','Type','Colonies','Native settlements','Gold','Tax','Score','AI','Dead'),
            'Colonies': ('ID','Name','Owner','Tile','Founded','Liberty','SoL %','Production bonus'),
            'Native settlements': ('ID','Name','Owner','Tile','Teaches','Goods wanted'),
            'Units': ('ID','Type','Owner','Location','Role','Experience Towards','Experience','Moves Left','Max Moves','Hit points','State'),
        }
        for title, cols in self.columns.items():
            pane = ttk.Frame(self.tabs)
            self.tabs.add(pane, text=title)
            tv = ttk.Treeview(pane, columns=cols, show='headings', selectmode='browse')
            for col in cols:
                tv.heading(col, text=col)
                tv.column(col, width=(170 if col in ('Location','Type','Teaches','Name') else 110), minwidth=65, stretch=True)
            sy = ttk.Scrollbar(pane, orient='vertical', command=tv.yview)
            sx = ttk.Scrollbar(pane, orient='horizontal', command=tv.xview)
            tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
            tv.grid(row=0,column=0,sticky='nsew')
            sy.grid(row=0,column=1,sticky='ns')
            sx.grid(row=1,column=0,sticky='ew')
            pane.columnconfigure(0,weight=1);pane.rowconfigure(0,weight=1)
            tv.bind('<<TreeviewSelect>>', lambda evt, tab=title: self.show_details(tab))
            if title=='Units':
                tv.bind('<Double-1>',self.edit_unit_list)
                tv.bind('<<TreeviewSelect>>',lambda event:self.after_idle(self.update_inline_equipment),add='+')
            self.tables[title]=tv
        self.tabs.bind('<<NotebookTabChanged>>', self.tab_changed)
        self.detail_title=ttk.Label(right,text='Select an item to inspect',font=('Segoe UI',13,'bold'))
        self.detail_title.pack(fill='x',padx=8,pady=(5,2))
        self.detail_tabs=ttk.Notebook(right)
        self.detail_tabs.pack(fill='both',expand=True,padx=5,pady=5)
        self.detail_frames={}; self.detail_tables={}
        for name in ('Overview','Buildings','Goods','Units','Diplomacy','Terrain preview','Raw XML'):
            frame=ttk.Frame(self.detail_tabs)
            self.detail_tabs.add(frame,text=name)
            self.detail_frames[name]=frame
            if name in ('Buildings','Goods','Units','Diplomacy'):
                cols={'Buildings':('Building','Category','Tier','Workers'), 'Goods':('Good','Quantity'), 'Units':('Type','Work','Experience Towards','Experience','Location'), 'Diplomacy':('Other player','Field','Value')}[name]
                tree=ttk.Treeview(frame,columns=cols,show='headings')
                for col in cols:
                    tree.heading(col,text=col);tree.column(col,width=120,minwidth=70,stretch=True)
                sy=ttk.Scrollbar(frame,orient='vertical',command=tree.yview)
                tree.configure(yscrollcommand=sy.set)
                tree.pack(side='left',fill='both',expand=True);sy.pack(side='right',fill='y')
                self.detail_tables[name]=tree
                if name == 'Diplomacy':
                    tree.bind('<Double-1>',self.edit_diplomacy)
                    tree.tag_configure('changed',background='#cdeed0')
                    tree.tag_configure('editable',foreground='#155ba6')
                if name == 'Units':
                    tree.bind('<Double-1>', self.edit_colony_unit)
                    tree.tag_configure('changed', background='#cdeed0', foreground='#194c21')
                    tree.tag_configure('editable', foreground='#155ba6')
                if name == 'Goods':
                    tree.bind('<Double-1>', self.edit_goods)
                    tree.tag_configure('changed', background='#cdeed0', foreground='#194c21')
                    tree.tag_configure('missing', foreground='#777777')
            elif name=='Terrain preview':
                info=ttk.Label(frame,text='Free terrain inspection — READ ONLY. Enter any map coordinate or select a colony. Lakes, rivers and roads are previewed, not edited.',wraplength=560)
                info.pack(anchor='w',padx=8,pady=5)
                controls=ttk.Frame(frame)
                controls.pack(fill='x', padx=8, pady=(1,4))
                ttk.Label(controls,text='Centre X:').pack(side='left')
                self.terrain_x=tk.StringVar(value='67')
                self.terrain_y=tk.StringVar(value='110')
                x_entry=ttk.Entry(controls,textvariable=self.terrain_x,width=7)
                x_entry.pack(side='left',padx=(4,10))
                ttk.Label(controls,text='Y:').pack(side='left')
                y_entry=ttk.Entry(controls,textvariable=self.terrain_y,width=7)
                y_entry.pack(side='left',padx=(4,10))
                ttk.Button(controls,text='Show tiles',command=self.show_coordinate_terrain).pack(side='left',padx=(0,10))
                ttk.Button(controls,text='Lake test (67,110)',command=lambda:self.set_terrain_center(67,110)).pack(side='left')
                x_entry.bind('<Return>',lambda event:self.show_coordinate_terrain())
                y_entry.bind('<Return>',lambda event:self.show_coordinate_terrain())
                self.terrain_art = FreeColArt(self)
                self.terrain_view = tk.Canvas(frame,height=430,bg='#6f816b',highlightthickness=0)
                self.terrain_view.pack(fill='x',padx=5,pady=3)
                self.terrain_view.bind('<Configure>',lambda event:self.paint_terrain())
                self.terrain_view.bind('<Button-1>', self.on_terrain_click)
                self.terrain_tiles={}
                self.terrain_selected='C'
                self.terrain_art_status=ttk.Label(frame,text=self.terrain_art.status,wraplength=440,foreground='#555555')
                self.terrain_art_status.pack(anchor='w',padx=9)
                self.terrain_info=tk.Text(frame,height=9,wrap='word',font=('Consolas',10))
                self.terrain_info.pack(fill='both',expand=True,padx=8,pady=5)
            elif name=='Overview':
                tree=ttk.Treeview(frame,columns=('Property','Value'),show='headings')
                tree.heading('Property',text='Property');tree.heading('Value',text='Value')
                tree.column('Property',width=165);tree.column('Value',width=220)
                tree.pack(fill='both',expand=True)
                self.detail_tables[name]=tree
                tree.tag_configure('changed',background='#cdeed0',foreground='#194c21')
                tree.tag_configure('editable',foreground='#155ba6')
            else:
                text=tk.Text(frame,wrap='word',font=('Consolas',10))
                sy=ttk.Scrollbar(frame,orient='vertical',command=text.yview)
                text.configure(yscrollcommand=sy.set)
                text.pack(side='left',fill='both',expand=True);sy.pack(side='right',fill='y')
                self.detail_tables[name]=text
        self.equip_panel=ttk.LabelFrame(right,text='Selected unit equipment — inline edit',padding=6)
        self.equip_panel.pack(fill='x',padx=8,pady=(2,4))
        self.equip_panel.pack_forget()
        self.equip_unit=ttk.Label(self.equip_panel,text='Select a unit in a unit list')
        self.equip_unit.grid(row=0,column=0,columnspan=4,sticky='w')
        ttk.Label(self.equip_panel,text='Equipment:').grid(row=1,column=0,sticky='w',padx=(0,4))
        self.equip_choice=tk.StringVar()
        self.equip_select=ttk.Combobox(self.equip_panel,textvariable=self.equip_choice,state='readonly',width=25)
        self.equip_select.grid(row=1,column=1,sticky='ew')
        ttk.Label(self.equip_panel,text='Tools:').grid(row=1,column=2,padx=(8,4))
        self.equip_sets=tk.StringVar(value='100 tools')
        self.equip_sets_entry=ttk.Combobox(self.equip_panel,textvariable=self.equip_sets,values=[f'{n} tools' for n in (20,40,60,80,100)],state='readonly',width=11)
        self.equip_sets_entry.grid(row=1,column=3)
        self.equip_apply=ttk.Button(self.equip_panel,text='Stage equipment change',command=self.stage_inline_equipment)
        self.equip_apply.grid(row=2,column=0,columnspan=4,sticky='e',pady=(3,0))
        self.equip_panel.columnconfigure(1,weight=1)
        self.equip_select.bind('<<ComboboxSelected>>',lambda event:self.toggle_equipment_sets())
        self.equip_current_unit=None
        self.equip_apply.configure(state='disabled')
        self.detail_tables['Units'].bind('<<TreeviewSelect>>',lambda event:self.update_inline_equipment(),add='+')
        self.detail_tabs.bind('<<NotebookTabChanged>>',lambda event:self.after_idle(self.update_inline_equipment),add='+')
        self.delete_native_btn=ttk.Button(right,text='Delete selected unit…',command=self.delete_selected_unit)
        self.delete_native_btn.pack(anchor='e',padx=8,pady=(0,3))
        self.delete_native_btn.pack_forget()
        self.delete_settlement_btn=ttk.Button(right,text='Delete selected native settlement…',command=self.delete_selected_settlement)
        self.delete_settlement_btn.pack(anchor='e',padx=8,pady=(0,3))
        self.delete_settlement_btn.pack_forget()
        self.detail_tables['Overview'].bind('<Double-1>', self.edit_overview)
        ttk.Label(self,textvariable=self.status,padding=7).pack(fill='x')
        self.after(150,lambda: self.split.sashpos(0,int(self.winfo_width()*.55)))

    def open_map_editor(self):
        if not getattr(self, 'terrain_by_xy', None):
            messagebox.showwarning('Map Editor', 'Open a FreeCol savegame first.')
            return
        if getattr(self, 'map_editor_window', None) and self.map_editor_window.winfo_exists():
            self.map_editor_window.lift()
            self.map_editor_window.focus_set()
        else:
            self.map_editor_window = MapEditorWindow(self)

    def navigate_to_colony(self, colony):
        if not colony:
            return
        index = next((i for i,c in enumerate(self.records.get('Colonies', []))
                      if c.get('id') == colony.get('id')), None)
        if index is None:
            return
        self.search.set('')
        self.owner_filter.set('All players')
        self.tabs.select(list(self.columns).index('Colonies'))
        self.active = 'Colonies'
        self.refresh()
        tv = self.tables['Colonies']
        row = str(index)
        if tv.exists(row):
            tv.selection_set(row)
            tv.focus(row)
            tv.see(row)
            self.show_details('Colonies')

    def load_settings(self):
        try:return json.loads(self.config_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):return {}

    def default_directory(self):
        saved=self.settings.get('last_directory')
        if saved and pathlib.Path(saved).is_dir():return saved
        home=pathlib.Path.home()
        candidates=[home/'OneDrive'/'Dokumenter'/'freecol'/'save',home/'OneDrive'/'Documents'/'freecol'/'save',home/'Documents'/'freecol'/'save',home/'Dokumenter'/'freecol'/'save']
        candidates += list(home.glob('OneDrive*/Documents/freecol/save')) + list(home.glob('OneDrive*/Dokumenter/freecol/save'))
        return str(next((p for p in candidates if p.is_dir()),home/'Documents' if (home/'Documents').is_dir() else home))

    @staticmethod
    def short(value):
        return presentation.short(value)

    def open_save(self):
        path = filedialog.askopenfilename(initialdir=self.default_directory(),filetypes=[('FreeCol saves','*.fsg'),('ZIP archives','*.zip'),('All files','*.*')])
        if not path: return
        self.cancel_cell_edit()
        try:
            doc=SaveDocument.load(path)
            self.document=doc
            game=doc.game
            players=doc.players
            col=doc.colonies
            nat=doc.native_settlements
            units=doc.units
            self.players=players; self.locations=doc.locations
            self.colony_tile_names=doc.colony_tile_names
            self.unit_locations=doc.unit_locations
            self.xml_bytes=doc.xml_bytes
            self.root=doc.root
            self.edits.clear()
            self.current_path=path
            self.settings['last_directory']=str(pathlib.Path(path).parent)
            try:self.config_path.write_text(json.dumps(self.settings),encoding='utf-8')
            except OSError:pass
            self.colony_counts=doc.colony_counts
            self.native_counts=doc.native_counts
            self.professions=doc.professions
            self.goods_types=doc.goods_types
            self.records=doc.records
            self.tiles=doc.tiles
            self.terrain_by_xy=doc.terrain_by_xy
            self.terrain_tiles={}
            if (67,110) in self.terrain_by_xy:
                self.terrain_x.set('67');self.terrain_y.set('110')
            self.owner_filter.set('All players')
            self.combo['values']=['All players']+[f"{v.get('username','?')} ({k})" for k,v in players.items()]
            self.status.set(f"{pathlib.Path(path).name} | Turn {game.get('turn')} | {len(players)} players | {len(col)} colonies | {len(nat)} native settlements | {len(units)} units | 0 staged edits")
            self.refresh()
        except Exception as exc:
            messagebox.showerror('Could not open save',str(exc))

    def tab_changed(self, _event=None):
        self.active=self.tabs.tab(self.tabs.select(), 'text')
        self.refresh()

    def owner_name(self, key):
        return self.document.owner_name(key)

    def loc_name(self, key):
        return self.document.location_name(key)

    def row_values(self, group,e):
        return presentation.row_values(group,e,self.document,self.edit_session)

    @staticmethod
    def experience_towards(attrs):
        return presentation.experience_towards(attrs)

    def edit_unit_list(self,event):
        table=self.tables['Units']
        if self.active!='Units' or table.identify_column(event.x) not in ('#7','#8'):return
        row=table.identify_row(event.y)
        if not row:return
        unit=self.records['Units'][int(row)]
        field='movesLeft' if table.identify_column(event.x)=='#8' else 'experience'
        if field not in self.edit_session.editable_fields('Units',unit):return
        raw=unit.get(field)
        if raw is None or not raw.isdecimal():
            self.status.set('This unit has no editable '+field+' attribute.')
            return
        if field=='movesLeft':
            try:movement_cap(self.root,unit)
            except UnknownMovement as exc:
                self.status.set('Movement edit unavailable: '+str(exc));return
        self.start_numeric_edit(table,row,'Moves Left' if field=='movesLeft' else 'Experience',(unit.get('id'),field),int(raw))

    def refresh(self):
        table=self.tables[self.active]
        table.delete(*table.get_children())
        query=self.search.get().strip().casefold()
        filt=self.owner_filter.get()
        wanted=filt.rsplit('(',1)[-1].rstrip(')') if filt!='All players' else None
        count=0
        for i,e in enumerate(self.records.get(self.active,[])):
            if wanted and (e.get('owner') if self.active!='Players' else e.get('id'))!=wanted: continue
            vals=self.row_values(self.active,e)
            if query and query not in ' '.join(str(v) for v in vals).casefold() and query not in str(e.attrib).casefold(): continue
            table.insert('', 'end', iid=str(i), values=[v if v is not None else '' for v in vals]);count+=1
        self.cancel_cell_edit()
        self.clear_details()
        if query and self.scope.get()=='All tabs' and not count:
            for other in self.records:
                if other!=self.active and any(query in ' '.join(str(v) for v in self.row_values(other,e)).casefold() for e in self.records[other]):
                    self.tabs.select(list(self.records).index(other))
                    return

    def show_details(self, group):
        """Render selected record; called on Treeview selection changes."""
        tv = self.tables[group]
        selection = tv.selection()
        if not selection:
            self.update_context_actions()
            return
        record = self.records[group][int(selection[0])]
        lines = [f'<{record.tag}>  ({len(record)} immediate child elements)', '']
        lines.extend(f'{key} = {value}' for key, value in record.attrib.items())
        counts = collections.Counter(child.tag for child in record)
        if counts:
            lines.extend(['', 'Immediate child elements:'])
            lines.extend(f'  {tag}: {amount}' for tag, amount in counts.most_common())
        self.render_details(group, record, lines)
        self.after_idle(self.update_inline_equipment)

    def clear_details(self):
        self.cancel_cell_edit()
        self.detail_title.config(text='Select an item to inspect')
        self.update_context_actions()
        for name, widget in self.detail_tables.items():
            if isinstance(widget,ttk.Treeview): widget.delete(*widget.get_children())
            else: widget.delete('1.0','end')

    @staticmethod
    def readable(value):
        return presentation.readable(value)

    def render_details(self,group,e,raw_lines):
        self.clear_details()
        name=e.get('name') or e.get('username') or self.readable(e.get('unitType')) or e.get('id')
        self.detail_title.config(text=f'{name}   ·   {group}')
        self.detail_tables['Raw XML'].insert('1.0','\n'.join(raw_lines))
        summary=[f'{self.readable(k)}: {v}' for k,v in e.attrib.items()]
        summary.extend(['','Direct children:']+[f'{k}: {v}' for k,v in collections.Counter(x.tag for x in e).items()])
        overview=self.detail_tables['Overview']
        for k,v in e.attrib.items():
            key=(e.get('id'),'sonsOfLibertyTarget' if group=='Colonies' and k=='sonsOfLiberty' else k)
            shown=self.edits[key][1] if key in self.edits else v
            if group=='Units' and k in ('role','roleCount') and (e.get('id'),'equipment') in self.edits:
                role_count=self.edits[(e.get('id'),'equipment')][1]
                shown=role_count[0] if k=='role' else role_count[1]
            permitted=k in self.edit_session.editable_fields(group,e)
            tags=('changed',) if key in self.edits else (('editable',) if permitted else ())
            overview.insert('', 'end',iid=k,values=(self.readable(k),shown),tags=tags)
        self.detail_tabs.tab(self.detail_frames['Buildings'],state='normal' if group=='Colonies' else 'disabled')
        self.detail_tabs.tab(self.detail_frames['Goods'],state='normal' if group=='Colonies' else 'disabled')
        self.detail_tabs.tab(self.detail_frames['Units'],state='normal' if group in ('Colonies','Players','Native settlements') else 'disabled')
        self.detail_tabs.tab(self.detail_frames['Diplomacy'],state='normal' if group in ('Players','Native settlements') else 'disabled')
        self.detail_tabs.tab(self.detail_frames['Terrain preview'],state='normal')
        if group in ('Players','Native settlements'):
            self.render_diplomacy(group,e)
        if group=='Players':
            for u in self.records['Units']:
                if u.get('owner')==e.get('id'):self.insert_detail_unit(u)
        if group=='Native settlements':
            sid=e.get('id'); ids={x.get('id') for x in e.findall('ownedUnits')}
            for u in self.records['Units']:
                if u.get('indianSettlement')==sid or u.get('id') in ids:self.insert_detail_unit(u)
        if group=='Colonies':
            self.render_terrain_preview(e)
            for b in e.findall('building'):
                key=b.get('buildingType',''); raw=key.rsplit('.',1)[-1]
                category,tier=self.building_tier(raw)
                self.detail_tables['Buildings'].insert('','end',values=(self.readable(key),category,tier,len(b.findall('unit'))))
            store=e.find('./goodsContainer/storedGoods')
            stock={g.get('type'):int(g.get('amount','0')) for g in store.findall('goods')} if store is not None else {}
            for key in self.goods_types:
                edit_key=(e.get('id'),key)
                quantity=self.edits[edit_key][1] if edit_key in self.edits else stock.get(key,0)
                tags=('changed',) if edit_key in self.edits else ('editable',)
                self.detail_tables['Goods'].insert('', 'end', iid=key, values=(self.readable(key),quantity),tags=tags)
            for u in e.iter('unit'):
                uid=u.get('id')
                if not uid: continue
                key=(uid,'experience')
                xp=self.edits[key][1] if key in self.edits else u.get('experience','')
                self.detail_tables['Units'].insert('','end',iid=uid,values=(self.readable(u.get('unitType')),self.readable(u.get('workType') or u.get('role')),self.experience_towards(u.attrib),xp,self.loc_name(u.get('location'))),tags=('changed',) if key in self.edits else ('editable',))
            self.detail_tabs.select(self.detail_frames['Overview'])
        else:self.detail_tabs.select(self.detail_frames['Overview'])

    @staticmethod
    def terrain_offsets(y):
        return map_render.terrain_offsets(y)

    def set_terrain_center(self,x,y):
        """Set a preview centre without touching the save data."""
        self.terrain_x.set(str(x))
        self.terrain_y.set(str(y))
        self.show_coordinate_terrain()

    def show_coordinate_terrain(self):
        """Inspect any valid map tile, including uncolonised land and water."""
        if not getattr(self,'terrain_by_xy',None):
            messagebox.showwarning('No save loaded','Open a FreeCol savegame first.')
            return
        try:
            x=int(self.terrain_x.get().strip())
            y=int(self.terrain_y.get().strip())
        except ValueError:
            messagebox.showerror('Invalid coordinates','Enter whole-number X and Y coordinates.')
            return
        tile=self.terrain_by_xy.get((x,y))
        if tile is None:
            messagebox.showerror('No such tile',f'No map tile exists at ({x},{y}) in this save.')
            return
        self.terrain_center=(x,y)
        self.terrain_tiles={direction:self.terrain_by_xy.get((x+dx,y+dy))
                            for direction,(dx,dy) in self.terrain_offsets(y).items()}
        self.terrain_selected='C'
        self.paint_terrain()
        self.inspect_terrain_tile(tile,0,0)
        self.detail_tabs.select(self.detail_frames['Terrain preview'])

    def render_terrain_preview(self,colony):
        center_id=colony.get('tile')
        center=next((t for t in self.terrain_by_xy.values() if t.get('id')==center_id),None)
        if center is None:return
        self.terrain_x.set(center.get('x'))
        self.terrain_y.set(center.get('y'))
        self.terrain_center=(int(center.get('x')),int(center.get('y')))
        self.terrain_tiles={direction:self.terrain_by_xy.get((self.terrain_center[0]+dx,self.terrain_center[1]+dy))
                            for direction,(dx,dy) in self.terrain_offsets(self.terrain_center[1]).items()}
        self.terrain_selected='C'
        self.paint_terrain()
        self.inspect_terrain_tile(center,0,0)

    def select_terrain_direction(self,direction):
        self.terrain_selected=direction
        self.paint_terrain()
        tile=self.terrain_tiles.get(direction)
        dx,dy=self.terrain_offsets(self.terrain_center[1])[direction]
        self.inspect_terrain_tile(tile,dx,dy)

    def tile_items(self, tile):
        return self.document.tile_items(tile)

    def tile_item_summary(self, tile):
        return self.document.tile_item_summary(tile)

    def paint_terrain(self):
        canvas=getattr(self,'terrain_view',None)
        if canvas is None: return
        canvas.delete('all')
        if not getattr(self,'terrain_tiles',None): return
        width=max(1, canvas.winfo_width())
        height=max(1, canvas.winfo_height())
        # Fit the ENTIRE diamond neighbourhood in both viewport dimensions.
        # Its bounds are 3 tile widths x 3 tile heights, not just one tile.
        tw=max(2, int(min((width-32)/3.0, (height-32)/1.5)))
        th=max(1, int(tw*0.5))
        cx=width/2
        cy=height/2
        # True edge-sharing diamonds: diagonals at half tile width/height.
        offsets={'N':(0,-1),'NW':(-.5,-.5),'NE':(.5,-.5),
                 'W':(-1,0),'C':(0,0),'E':(1,0),
                 'SW':(-.5,.5),'SE':(.5,.5),'S':(0,1)}
        # Directions now live in the inspector rather than covering the art.
        self.terrain_art_refs=[]
        self.terrain_hit_regions={}
        order=('N','NW','NE','W','C','E','SW','SE','S')
        for direction in order:
            tile=self.terrain_tiles.get(direction)
            ox,oy=offsets[direction]
            x=cx+ox*tw
            y=cy+oy*th
            points=[x,y-th/2,x+tw/2,y,x,y+th/2,x-tw/2,y]
            self.terrain_hit_regions[direction]=(x,y,tw,th)
            group='tile_'+direction
            canvas.create_polygon(points,fill='#7f8f78' if tile is not None else '#505f55',outline='#556755',width=1,tags=(group,))
            if tile is not None:
                img=self.terrain_art.get(tile.get('type'),tw,th)
                if img is not None:
                    canvas.create_image(x,y,image=img,tags=(group,))
                    self.terrain_art_refs.append(img)
                if self.is_water_tile(tile):
                    self.paint_shore_edges(canvas,group,tile,x,y,tw,th)
                forest_img=self.terrain_art.get_forest(tile.get('type'),tw,th)
                if forest_img is not None:
                    canvas.create_image(x,y,image=forest_img,tags=(group,))
                    self.terrain_art_refs.append(forest_img)
                resources, improvements = self.tile_item_summary(tile)
                # Use the game's actual plowed artwork, not hand-drawn diagonals.
                if any(self.readable(imp.get('type')).lower() == 'plow' for imp in improvements):
                    plowed=self.terrain_art.get_plowed(tw,th)
                    if plowed is not None:
                        canvas.create_image(x,y,image=plowed,tags=(group,))
                        self.terrain_art_refs.append(plowed)
                    else:
                        canvas.create_text(x,y+th*.14,text='Plowed',fill='#f1d9a2',font=('Segoe UI',9,'bold'),tags=(group,))
                # Road and river styles are directional; a fixed decorative line
                # is incorrect and produced apparent breaks at tile boundaries.
                for imp in improvements:
                    kind=self.readable(imp.get('type')).lower()
                    style=imp.get('style','')
                    if kind=='road':
                        self.paint_directional_road(canvas,group,x,y,tw,th,style)
                    elif kind=='river':
                        river_art=(self.terrain_art.get_composited_river(style,tw,th,imp.get('magnitude','2'))
                                   or self.terrain_art.get_river(style,tw,th))
                        if river_art is not None:
                            canvas.create_image(x,y,image=river_art,tags=(group,))
                            self.terrain_art_refs.append(river_art)
                        else:
                            self.paint_directional_river(canvas,group,x,y,tw,th,style)
                # Bonus resource icon and finite quantity.
                if resources:
                    resource = resources[0]
                    icon = self.terrain_art.get_bonus(resource.get('type'), max(22, int(th*0.33)))
                    if icon is not None:
                        canvas.create_image(x, y-th*0.04, image=icon, tags=(group,))
                        self.terrain_art_refs.append(icon)
                    qty = resource.get('quantity')
                    if qty and qty != '-1':
                        canvas.create_text(x+tw*0.20, y-th*0.14, text=qty, fill='white', font=('Segoe UI', 9, 'bold'), tags=(group,))
                # Small corner badge for saved improvements.
                badges=[]
                if any(self.readable(imp.get('type')).lower() == 'road' for imp in improvements): badges.append('Rd')
                if any(self.readable(imp.get('type')).lower() == 'plow' for imp in improvements): badges.append('Pl')
                if any(self.readable(imp.get('type')).lower() == 'river' for imp in improvements): badges.append('Rv')
                if badges:
                    canvas.create_text(x, y+th*0.26, text='/'.join(badges), fill='#111111', font=('Segoe UI', 9, 'bold'), tags=(group,))
            canvas.create_polygon(points,fill='',outline='#ff23ad' if direction==self.terrain_selected else '#465846',width=3 if direction==self.terrain_selected else 1,tags=(group,))
            # Selection is handled at canvas level from exact diamond geometry.
            # Empty-outline polygons do not reliably receive interior clicks in Tk.
        self.terrain_art_status.config(text=self.terrain_art.status + ' | Style-directed roads/rivers; provisional shore edges (read-only).')

    @staticmethod
    def is_water_tile(tile):
        return tile is not None and (tile.get('type') or '').split('.')[-1] in ('ocean','lake','highSeas','greatRiver')

    @staticmethod
    def direction_endpoint(direction,tw,th):
        return map_render.direction_endpoint(direction,tw,th)

    @staticmethod
    def _paint_primitives(canvas,tag,primitives):
        for kind,coords,options in primitives:
            if kind=='line':
                canvas.create_line(*coords,tags=(tag,),**options)
            elif kind=='oval':
                canvas.create_oval(*coords,tags=(tag,),**options)

    def paint_directional_road(self,canvas,tag,x,y,tw,th,style):
        self._paint_primitives(canvas,tag,map_render.road_primitives(x,y,tw,th,style))

    def paint_directional_river(self,canvas,tag,x,y,tw,th,style):
        self._paint_primitives(canvas,tag,map_render.river_primitives(x,y,tw,th,style))

    def paint_shore_edges(self,canvas,tag,tile,x,y,tw,th):
        # Read neighbouring tiles from the saved map. Coastline transparency
        # masks are the next refinement; this pass never draws a shore between
        # two water tiles, including adjoining lake tiles.
        tx=int(tile.get('x'));ty=int(tile.get('y'))
        cardinal=(('N',(0,-2),(-tw/2,0,0,-th/2)),
                  ('E',(1,0),(0,-th/2,tw/2,0)),
                  ('S',(0,2),(tw/2,0,0,th/2)),
                  ('W',(-1,0),(0,th/2,-tw/2,0)))
        for direction,(dx,dy),edge in cardinal:
            neighbor=self.terrain_by_xy.get((tx+dx,ty+dy))
            if neighbor is None or self.is_water_tile(neighbor):continue
            x1,y1,x2,y2=edge
            # A narrow shoreline cue, not a claim of FreeCol-exact masking.
            canvas.create_line(x+x1*.91,y+y1*.91,x+x2*.91,y+y2*.91,
                               fill='#d0c49e',width=max(2,int(th*.045)),tags=(tag,))

    @staticmethod
    def diamond_contains(px,py,cx,cy,width,height,tolerance=0.0):
        return map_render.diamond_contains(px,py,cx,cy,width,height,tolerance)

    def on_terrain_click(self, event):
        """Find the geometric diamond, independent of stacked PNG overlays."""
        regions=getattr(self,'terrain_hit_regions',{})
        candidates=[]
        for direction,(cx,cy,tw,th) in regions.items():
            if self.diamond_contains(event.x,event.y,cx,cy,tw,th):
                # Prefer the tile closest to the click at a shared boundary.
                distance=abs(event.x-cx)/(tw/2)+abs(event.y-cy)/(th/2)
                candidates.append((distance,direction))
        if candidates:
            _,direction=min(candidates)
            self.select_terrain_direction(direction)

    def inspect_terrain_tile(self,tile,dx,dy):
        out=self.terrain_info
        out.configure(state='normal');out.delete('1.0','end')
        if tile is None:out.insert('end','Outside map bounds.');out.configure(state='disabled');return
        description=[f'Selected tile: {self.terrain_selected} — {self.readable(tile.get("type"))}',f'Coordinates: ({tile.get("x")}, {tile.get("y")}) | offset ({dx:+d}, {dy:+d})',
                     f'Tile ID: {tile.get("id")}',f'Terrain: {tile.get("type")}',
                     f'Owner: {tile.get("owner","—")}',f'Owning settlement: {tile.get("owningSettlement","—")}',
                     '', 'Saved improvements and resources:']
        items = self.tile_items(tile)
        for child in items:
            kind = 'Resource' if child.tag == 'resource' else 'Improvement'
            properties = [f'type={self.readable(child.get("type"))}']
            for attr in ('quantity', 'turns', 'magnitude', 'style'):
                if attr in child.attrib:
                    properties.append(f'{attr}={child.get(attr)}')
            description.append('  ' + kind + ': ' + ', '.join(properties))
        if not items:
            description.append('  None saved')
        description += ['', 'Neighbour offsets account for the centre row parity (even/odd Y).',
                        'Terrain editing remains disabled pending map-renderer validation.']
        out.insert('end','\n'.join(description));out.configure(state='disabled')

    def insert_detail_unit(self,u):
        uid=u.get('id');key=(uid,'experience')
        xp=self.edits[key][1] if key in self.edits else u.get('experience','')
        table=self.detail_tables['Units']
        if not table.exists(uid):
            table.insert('','end',iid=uid,values=(self.readable(u.get('unitType')),self.readable(u.get('workType') or u.get('role')),self.experience_towards(u.attrib),xp,self.loc_name(u.get('location'))),tags=('changed',) if key in self.edits else ('editable',))

    def unit_for_equipment(self):
        if not self.current_path:return None
        # Detailed unit selection takes priority on player/colony/settlement pages.
        if self.active != 'Units':
            if self.detail_tabs.select() != str(self.detail_frames['Units']):
                return None
            if not self.tables[self.active].selection():
                return None
            selected=self.detail_tables['Units'].selection()
            if selected:
                return next((u for u in self.records['Units'] if u.get('id')==selected[0]),None)
            return None
        selected=self.tables['Units'].selection()
        if selected:
            return self.records['Units'][int(selected[0])]
        return None

    def update_context_actions(self):
        """Show destructive controls only for a compatible, visible selection.

        Unit action visibility follows the same unit-resolution path as the
        existing deletion method; no deletion implementation is changed.
        """
        if not hasattr(self, 'delete_native_btn'):
            return
        group=self.active
        main_selected=bool(self.tables[group].selection()) if group in self.tables else False
        detail_unit_active=(self.detail_tabs.select()==str(self.detail_frames['Units']))
        unit_selected=False
        if self.current_path:
            if group=='Units':
                unit_selected=main_selected
            elif group in ('Players','Colonies','Native settlements') and main_selected and detail_unit_active:
                unit_selected=bool(self.detail_tables['Units'].selection())
        settlement_selected=(group=='Native settlements' and main_selected and bool(self.current_path))

        def show(widget, visible, options):
            if visible:
                if not widget.winfo_manager():
                    widget.pack(**options)
            elif widget.winfo_manager():
                widget.pack_forget()

        show(self.equip_panel,unit_selected,{'fill':'x','padx':8,'pady':(2,4)})
        show(self.delete_native_btn,unit_selected,{'anchor':'e','padx':8,'pady':(0,3)})
        show(self.delete_settlement_btn,settlement_selected,{'anchor':'e','padx':8,'pady':(0,3)})

    def update_inline_equipment(self):
        self.update_context_actions()
        unit=self.unit_for_equipment()
        self.equip_current_unit=unit
        if unit is None:
            self.equip_unit.configure(text='Select a unit in a unit list')
            self.equip_select.configure(values=[])
            self.equip_apply.configure(state='disabled')
            return
        uid=unit.get('id')
        self.equip_unit.configure(text=uid+' — '+self.short(unit.get('unitType')))
        supported=[]
        for role in ROLES:
            try:validate_equipment(self.root,unit,role,1)
            except (ValueError,UnknownMovement):continue
            supported.append(role)
        staged=self.edits.get((uid,'equipment'))
        role,amount=staged[1] if staged else (unit.get('role','model.role.default'),int(unit.get('roleCount','1')))
        self.equip_select.configure(values=supported)
        suggested=('model.role.pioneer' if not staged and role=='model.role.default' and self.short(unit.get('unitType'))=='hardyPioneer' and 'model.role.pioneer' in supported else role)
        self.equip_choice.set(suggested if suggested in supported else (supported[0] if supported else ''))
        self.equip_sets.set(f'{amount*20} tools')
        self.equip_apply.configure(state='normal' if supported else 'disabled')
        self.toggle_equipment_sets()

    def toggle_equipment_sets(self):
        pioneer=self.equip_choice.get()=='model.role.pioneer'
        self.equip_sets_entry.configure(state='readonly' if pioneer else 'disabled')
        if not pioneer:self.equip_sets.set('20 tools')

    def stage_inline_equipment(self):
        unit=self.equip_current_unit
        if unit is None:return
        uid=unit.get('id')
        try:
            role=self.equip_choice.get()
            amount=int(self.equip_sets.get().split()[0])//20 if role=='model.role.pioneer' else 1
            self.edit_session.stage_equipment(self.root,unit,role,amount)
            self.refresh()
            self.status.set(f'{len(self.edits)} staged changes — {uid}: {self.short(role)} x{amount}; no warehouse goods consumed')
        except (ValueError,UnknownMovement) as exc:
            messagebox.showerror('Invalid equipment',str(exc))

    def delete_selected_unit(self):
        if not self.current_path:return
        tab=self.active
        if tab=='Units':
            selection=self.tables['Units'].selection()
            if not selection:return
            unit=self.records['Units'][int(selection[0])]
        else:
            if tab not in ('Players','Colonies','Native settlements'):return
            selected=self.detail_tables['Units'].selection()
            if not selected:
                messagebox.showinfo('Select unit','Open the Units detail tab and select a unit.');return
            unit=next((u for u in self.records['Units'] if u.get('id')==selected[0]),None)
            if unit is None:return
        uid=unit.get('id')
        if tab=='Native settlements':
            selected_home=unit.get('indianSettlement')
            sel=self.tables[tab].selection()
            if sel and selected_home and selected_home!=self.records[tab][int(sel[0])].get('id'):
                self.status.set(f'{uid} belongs to {self.locations.get(selected_home,selected_home)}; deletion will clean its actual home settlement references.')
        key=(uid,'deleteUnit')
        if not messagebox.askyesno('Confirm staged unit deletion',f'Stage deletion of {uid} ({self.short(unit.get("unitType"))})?\n\nHome: {self.locations.get(unit.get("indianSettlement"),unit.get("indianSettlement") or "not native")}.\nOnly safely resolvable units can be deleted. Save As will verify dependencies.'):
            return
        self.edit_session.stage_unit_deletion(uid)
        self.status.set(f'{len(self.edits)} staged changes. Unit {uid} marked for deletion; original untouched.')

    def delete_selected_settlement(self):
        if self.active!='Native settlements' or not self.xml_bytes:return
        selection=self.tables['Native settlements'].selection()
        if not selection:return
        village=self.records['Native settlements'][int(selection[0])]
        sid=village.get('id')
        try:plan=self.edit_session.plan_settlement_deletion(self.xml_bytes,sid)
        except (UnsafeDeletion,ValueError) as exc:
            messagebox.showwarning('Deletion blocked',f'{sid} cannot currently be safely deleted:\n\n{exc}')
            return
        label=f'{plan["name"]} ({sid})\n{len(plan["units"])} units; {plan["cached_copies"]} cached views; {plan["claimed_tiles"]} linked tiles'
        if not messagebox.askyesno('Confirm entire settlement deletion',f'Stage removal of:\n\n{label}\n\nAll connected native units will be removed. No combat consequences are simulated.\n\nOriginal save remains untouched.'):
            return
        self.edit_session.stage_settlement_deletion(sid)
        self.status.set(f'{len(self.edits)} staged changes. Settlement deletion pending Save As.')

    def edit_colony_unit(self,event):
        """Edit a colony worker by its persistent game ID, not its list position."""
        if self.active not in ('Colonies','Players','Native settlements'):return
        table=self.detail_tables['Units']
        if table.identify_column(event.x)!='#4':return
        row=table.identify_row(event.y)
        if not row:return
        units=[u for u in self.records['Units'] if u.get('id')==row]
        if len(units)!=1:return
        if 'experience' not in self.edit_session.editable_fields('Units',units[0]):return
        raw=units[0].get('experience')
        if raw is None or not raw.isdecimal():
            self.status.set('This unit has no editable experience attribute.');return
        self.start_numeric_edit(table,row,'Experience',(row,'experience'),int(raw))

    def sync_unit_views(self, unit_id):
        """Refresh both live presentations of one game unit without losing selection."""
        unit=next((u for u in self.records.get('Units',[]) if u.get('id')==unit_id),None)
        if unit is None:return
        main=self.tables['Units']
        for row in main.get_children():
            if self.records['Units'][int(row)].get('id')==unit_id:
                main.item(row, values=self.row_values('Units',unit))
                break
        sub=self.detail_tables['Units']
        if sub.exists(unit_id):
            key=(unit_id,'experience')
            value=self.edits[key][1] if key in self.edits else unit.get('experience','')
            sub.set(unit_id,'Experience',value)
            sub.item(unit_id,tags=('changed',) if key in self.edits or (unit_id,'movesLeft') in self.edits else ('editable',))
        overview=self.detail_tables['Overview']
        if self.active=='Units' and overview.exists('experience'):
            sel=main.selection()
            if sel and self.records['Units'][int(sel[0])].get('id')==unit_id:
                key=(unit_id,'experience')
                overview.set('experience','Value',self.edits[key][1] if key in self.edits else unit.get('experience',''))
                overview.item('experience',tags=('changed',) if key in self.edits else ('editable',))
                mv_key=(unit_id,'movesLeft')
                if overview.exists('movesLeft'):
                    overview.set('movesLeft','Value',self.edits[mv_key][1] if mv_key in self.edits else unit.get('movesLeft',''))
                    overview.item('movesLeft',tags=('changed',) if mv_key in self.edits else ('editable',))

    def selected_colony(self):
        tv=self.tables['Colonies']
        selection=tv.selection()
        if self.active!='Colonies' or not selection:return None
        return self.records['Colonies'][int(selection[0])]

    def cancel_cell_edit(self):
        """Discard an unfinished inline edit, if any."""
        widget=self.cell_editor
        self.cell_editor=None
        self.editing_cell=None
        if widget is not None:
            try: widget.destroy()
            except tk.TclError: pass

    def edit_overview(self,event):
        group=self.active
        if group not in ('Players','Units','Colonies','Native settlements'):return
        tv=self.tables[group]
        sel=tv.selection()
        if not sel:return
        obj=self.records[group][int(sel[0])]
        table=self.detail_tables['Overview']
        field=table.identify_row(event.y)
        if table.identify_column(event.x)!='#2' or not field:return
        if group=='Native settlements' and field=='learnableSkill' and field in self.edit_session.editable_fields(group,obj):
            self.start_choice_edit(table,field,'Value',(obj.get('id'),'learnableSkill'),obj.get(field),self.professions);return
        if field not in self.edit_session.editable_fields(group,obj):return
        if group=='Units' and field=='movesLeft':
            try: movement_cap(self.root,obj)
            except UnknownMovement as exc:
                self.status.set('Movement edit unavailable: '+str(exc));return
        old_raw=obj.get(field)
        if old_raw is None or not old_raw.isdecimal():return
        self.start_numeric_edit(table,field,'Value',(obj.get('id'),'sonsOfLibertyTarget' if group=='Colonies' else field),int(old_raw))

    def start_numeric_edit(self,table,row,column,key,original):
        if self.cell_editor is not None and not self.commit_cell_edit():return
        bounds=table.bbox(row,column)
        if not bounds:return
        x,y,w,h=bounds
        current=self.edits.get(key,(original,original))[1]
        editor=ttk.Entry(table,justify='right')
        editor.insert(0,str(current)); editor.place(x=x,y=y,width=w,height=h)
        self.cell_editor=editor
        self.editing_cell=(table,row,key,original,column)
        editor.focus_set();editor.select_range(0,'end')
        editor.bind('<Return>',lambda _:self.commit_cell_edit())
        editor.bind('<Escape>',lambda _:self.cancel_cell_edit())
        editor.bind('<FocusOut>',lambda _:self.commit_cell_edit())

    def edit_goods(self, event):
        """Place a small editable Entry over the quantity cell (no popup)."""
        colony=self.selected_colony()
        if colony is None:return
        table=self.detail_tables['Goods']
        row=table.identify_row(event.y)
        col=table.identify_column(event.x)
        if not row or col!='#2':return
        if self.cell_editor is not None:
            self.commit_cell_edit()
            if self.cell_editor is not None:return
        store=colony.find('./goodsContainer/storedGoods')
        if store is None:return
        goods=next((g for g in store.findall('goods') if g.get('type')==row),None)
        original=int(goods.get('amount','0')) if goods is not None else 0
        key=(colony.get('id'),row)
        self.start_numeric_edit(table,row,'Quantity',key,original)

    def commit_cell_edit(self):
        editor=self.cell_editor
        context=self.editing_cell
        if editor is None or context is None:return True
        table,row,key,original,column=context
        try: raw=editor.get().strip()
        except tk.TclError:return False
        try:
            new=self.edit_session.validate(
                key, raw, original=original, root=self.root,
                units=self.records['Units'], professions=self.professions)
        except EditValidationError as exc:
            self.status.set(str(exc))
            if str(exc).startswith('Invalid quantity:') or str(exc).startswith('Invalid value:'):
                editor.focus_set()
            return False
        self.edit_session.stage(key, original, new)
        self.cancel_cell_edit()
        if table.exists(row):
            table.set(row,column,new)
            table.item(row,tags=('changed',) if new!=original else ('editable',))
        # Keep the main list and the detail display consistent after inline edits.
        if self.active in ('Players','Units','Colonies','Native settlements') and table is self.tables[self.active]:
            self.show_details(self.active)
        elif self.active in ('Players','Units','Colonies','Native settlements') and table is self.detail_tables['Overview']:
            list_table=self.tables[self.active]
            for rid in list_table.get_children():
                obj=self.records[self.active][int(rid)]
                if obj.get('id')==key[0]:
                    list_table.item(rid,values=self.row_values(self.active,obj))
                    break
        if key[1] in ('experience','movesLeft'):self.sync_unit_views(key[0])
        if '|' in key[1] or key[1]=='learnableSkill':
            self.show_details(self.active)
        self.status.set(f'{len(self.edits)} staged change(s) — green rows changed; original save untouched')
        return True

    def render_diplomacy(self,group,obj):
        tree=self.detail_tables['Diplomacy']
        owner=obj if group=='Players' else self.players.get(obj.get('owner'))
        if owner is None:return
        if group=='Players':
            for other_id,other in self.players.items():
                if other_id==owner.get('id'):continue
                for kind in ('stance','tension'):
                    entry=next((c for c in owner.findall(kind) if c.get('player')==other_id),None)
                    if entry is None:continue
                    key=(owner.get('id'),f'{kind}|{other_id}')
                    value=self.edits.get(key,(None,entry.get('value')))[1]
                    tree.insert('','end',iid=f'{kind}|{other_id}',values=(other.get('username'),kind,value),tags=('changed',) if key in self.edits else ('editable',))
        else:
            for other_id,other in self.players.items():
                if other.get('playerType')!='colonial':continue
                entry=next((c for c in obj.findall('alarm') if c.get('player')==other_id),None)
                key=(obj.get('id'),f'alarm|{other_id}')
                value=self.edits[key][1] if key in self.edits else (entry.get('value') if entry is not None else '(absent)')
                tree.insert('','end',iid=f'alarm|{other_id}',values=(other.get('username'),'alarm',value),tags=('changed',) if key in self.edits else ('editable',))

    def edit_diplomacy(self,event):
        if self.active not in ('Players','Native settlements'):return
        tree=self.detail_tables['Diplomacy'];row=tree.identify_row(event.y)
        if not row or tree.identify_column(event.x)!='#3':return
        selection=self.tables[self.active].selection()
        if not selection:return
        obj=self.records[self.active][int(selection[0])]
        kind,other=row.split('|',1)
        entry=next((x for x in obj.findall(kind) if x.get('player')==other),None)
        original=entry.get('value') if entry is not None else None
        key=(obj.get('id'),row)
        if kind=='stance':
            self.start_choice_edit(tree,row,'Value',key,original,['peace','war','cease_fire','alliance'])
        else:
            self.start_numeric_edit(tree,row,'Value',key,int(original) if original is not None else 0)

    def start_choice_edit(self,table,row,column,key,original,options):
        if self.cell_editor is not None and not self.commit_cell_edit():return
        bounds=table.bbox(row,column)
        if not bounds:return
        x,y,w,h=bounds
        cur=self.edits.get(key,(original,original))[1]
        widget=ttk.Combobox(table,values=options,state='readonly')
        widget.set(cur or options[0]);widget.place(x=x,y=y,width=w,height=h)
        self.cell_editor=widget
        self.editing_cell=(table,row,key,original,column)
        widget.focus_set()
        widget.bind('<<ComboboxSelected>>',lambda _:self.commit_cell_edit())
        widget.bind('<Return>',lambda _:self.commit_cell_edit())
        widget.bind('<Escape>',lambda _:self.cancel_cell_edit())

    def delete_selected_native_unit(self):
        if self.active!='Native settlements':
            messagebox.showinfo('Select a settlement','Select a native settlement first.');return
        selection=self.tables['Native settlements'].selection()
        if not selection:return
        village=self.records['Native settlements'][int(selection[0])]
        vid=village.get('id')
        units=[u for u in self.records['Units'] if u.get('owner')==village.get('owner') and
               (u.get('indianSettlement')==vid or u.get('id') in {x.get('id') for x in village.findall('ownedUnits')})]
        if not units:
            messagebox.showinfo('No affiliated units','No units affiliated with this settlement were identified.');return
        win=tk.Toplevel(self);win.title('Native unit deletion — '+village.get('name',''));win.geometry('760x420')
        ttk.Label(win,text='Select one unit by unique ID. Deletion is staged and verified at Save As.',padding=8).pack(anchor='w')
        columns=('ID','Type','Location','Home settlement')
        table=ttk.Treeview(win,columns=columns,show='headings',selectmode='browse')
        for c in columns:table.heading(c,text=c);table.column(c,width=170)
        for u in units:table.insert('','end',iid=u.get('id'),values=(u.get('id'),self.short(u.get('unitType')),self.loc_name(u.get('location')),self.loc_name(u.get('indianSettlement'))))
        table.pack(fill='both',expand=True,padx=8,pady=8)
        def stage():
            selected=table.selection()
            if not selected:return
            uid=selected[0];key=(uid+'|'+vid,'deleteNativeUnit')
            if not messagebox.askyesno('Confirm deletion',f'Delete {uid} affiliated with {village.get("name")}?\n\nThis will remove its unit record, AI controller, and home-settlement reference. External dependencies cause Save As to fail safely.',parent=win):return
            self.edit_session.stage_native_unit_deletion(uid,vid)
            self.status.set(f'{len(self.edits)} staged changes — includes deletion of {uid}; original untouched')
            win.destroy()
        ttk.Button(win,text='Stage deletion',command=stage).pack(pady=8)

    def save_as(self):
        if self.cell_editor is not None and not self.commit_cell_edit():return
        if not self.current_path:
            messagebox.showinfo('Open save first','Please open a save file first.');return
        if not self.edits:
            messagebox.showinfo('No changes','Double-click an editable quantity in the Goods or Overview pane to stage an edit.');return
        source=pathlib.Path(self.current_path)
        filename=source.stem+'_edited.fsg'
        destination=filedialog.asksaveasfilename(initialdir=str(source.parent),initialfile=filename,
                         defaultextension='.fsg',filetypes=[('FreeCol saves','*.fsg')])
        if not destination:return
        target=pathlib.Path(destination)
        if target.resolve()==source.resolve():
            messagebox.showerror('Original protected','You cannot overwrite the opened save. Choose another filename.');return
        if target.exists():
            messagebox.showerror('Already exists','For safety, this editor never overwrites an existing file. Choose a new filename.');return
        try:
            report=self.edit_session.save_as(source,target)
        except Exception as exc:
            messagebox.showerror('Save failed',str(exc));return
        self.status.set(f"Saved {len(self.edits)} changes to {target.name} | Original unchanged")
        messagebox.showinfo('Save created',f"Wrote: {target}\n\n{report['changes']} attributes changed.\nAll other archive members checked unchanged.\n\nPlease load this file in FreeCol to verify game compatibility.")

    @staticmethod
    def building_tier(name):
        return presentation.building_tier(name)

if __name__=='__main__':
    Explorer().mainloop()
