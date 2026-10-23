"""Standalone read-only terrain atlas, using FreeCol's staggered-row map coordinates."""
import tkinter as tk
from tkinter import ttk, messagebox
from colony_graphics import resolve_colony_graphic, draw_colony_placeholder
try:
    from PIL import Image, ImageTk
except ImportError:
    Image=ImageTk=None

class MapEditorWindow(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app)
        self.app=app
        self.title('FreeCol Save Editor Colony Graphics Prototype — Map Editor (READ ONLY)')
        self.geometry('1120x780')
        self.minsize(760,480)
        self.center_x=tk.StringVar(value=str(getattr(app,'terrain_center',(67,110))[0]))
        self.center_y=tk.StringVar(value=str(getattr(app,'terrain_center',(67,110))[1]))
        self.selected=None
        self.regions=[]
        self.images=[]
        self.colonies_by_tile={c.get('tile'):c for c in app.records.get('Colonies',[])}
        self.show_selection_outline=tk.BooleanVar(value=False)
        top=ttk.Frame(self,padding=8);top.pack(fill='x')
        ttk.Label(top,text='Map centre X:').pack(side='left')
        ttk.Entry(top,textvariable=self.center_x,width=8).pack(side='left',padx=(4,14))
        ttk.Label(top,text='Y:').pack(side='left')
        ttk.Entry(top,textvariable=self.center_y,width=8).pack(side='left',padx=(4,14))
        ttk.Button(top,text='Show 9 × 9 tiles',command=self.jump).pack(side='left',padx=4)
        ttk.Button(top,text='Lake test (67,110)',command=lambda:self.goto(67,110)).pack(side='left',padx=4)
        ttk.Checkbutton(top,text='Show selected tile outline',
                        variable=self.show_selection_outline,command=self.paint).pack(side='left',padx=(8,4))
        ttk.Label(self,text='Read-only map survey · select a tile for details · colony tiles can be opened in the main editor',foreground='#286d44').pack(anchor='w',padx=12)
        area=ttk.PanedWindow(self,orient='horizontal');area.pack(fill='both',expand=True,padx=8,pady=8)
        left=ttk.Frame(area);right=ttk.Frame(area)
        area.add(left,weight=4);area.add(right,weight=1)
        self.canvas=tk.Canvas(left,bg='#637969',highlightthickness=0)
        self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Configure>',lambda e:self.paint())
        self.canvas.bind('<Button-1>',self.on_click)
        ttk.Label(right,text='Selected tile',font=('Segoe UI',12,'bold')).pack(anchor='w',pady=(3,8))
        self.info=tk.Text(right,height=20,width=29,wrap='word',font=('Consolas',10))
        self.info.pack(fill='both',expand=True)
        self.colony_button=ttk.Button(right,text='Go to colony',command=self.go_to_colony)
        self.colony_button.pack(fill='x',pady=8)
        self.colony_button.configure(state='disabled')
        self.colony=None
        self.goto(int(self.center_x.get()),int(self.center_y.get()))

    def goto(self,x,y):
        self.center_x.set(str(x));self.center_y.set(str(y))
        self.jump()

    def jump(self):
        try:x=int(self.center_x.get());y=int(self.center_y.get())
        except ValueError:
            messagebox.showerror('Invalid coordinates','X and Y must be integers.',parent=self);return
        if (x,y) not in self.app.terrain_by_xy:
            messagebox.showerror('Unknown tile',f'No tile at ({x}, {y}).',parent=self);return
        self.cx=x;self.cy=y
        self.selected=(x,y)
        self.paint();self.inspect(x,y)

    def paint(self):
        self.canvas.delete('all');self.regions=[];self.images=[]
        colony_layers=[]
        selected_outline=None
        if not hasattr(self,'cx'):return
        width=max(self.canvas.winfo_width(),100);height=max(self.canvas.winfo_height(),100)
        # Project a 9x9 neighborhood along the two isometric diagonal axes.
        # Screen basis: SE=(W/2,H/2), NE=(W/2,-H/2).
        tw=max(4,min((width-40)/9.05, (height-40)*2/9.05))
        th=tw/2
        mx=width/2;my=height/2
        from map_geometry import map_grid
        for r,c,x,y in map_grid(self.cx,self.cy):
                tile=self.app.terrain_by_xy.get((x,y))
                if tile is None:continue
                px=mx+(r+c)*tw/2
                py=my+(r-c)*th/2
                polygon=[px,py-th/2,px+tw/2,py,px,py+th/2,px-tw/2,py]
                self.canvas.create_polygon(polygon,fill='#7f8f78',outline='#526856',width=1)
                img=self.app.terrain_art.get(tile.get('type'),int(tw),int(th))
                if img:
                    self.images.append(img);self.canvas.create_image(px,py,image=img)
                forest=self.app.terrain_art.get_forest(tile.get('type'),int(tw),int(th))
                if forest:
                    self.images.append(forest);self.canvas.create_image(px,py,image=forest)
                resources,improvements=self.app.tile_item_summary(tile)
                for imp in improvements:
                    kind=self.app.readable(imp.get('type')).lower()
                    style=imp.get('style','')
                    if kind=='road':self.app.paint_directional_road(self.canvas,'',px,py,tw,th,style)
                    elif kind=='river':self.app.paint_directional_river(self.canvas,'',px,py,tw,th,style)
                    elif kind=='plow':
                        art=self.app.terrain_art.get_plowed(int(tw),int(th))
                        if art:self.images.append(art);self.canvas.create_image(px,py,image=art)
                if resources:
                    art=self.app.terrain_art.get_bonus(resources[0].get('type'),max(12,int(th*.3)))
                    if art:self.images.append(art);self.canvas.create_image(px,py,image=art)
                colony=self.colonies_by_tile.get(tile.get('id'))
                if colony is not None:
                    colony_layers.append((px,py,tw,th,resolve_colony_graphic(colony)))
                if (x,y)==self.selected:
                    selected_outline=polygon
                self.regions.append((x,y,px,py,tw,th))

        # Compositing order matters: terrain and tile features can otherwise
        # paint over earlier colony sprites, resembling a clipped PNG.
        for px,py,tw,th,graphic in colony_layers:
            rendered=False
            if graphic.image_path and Image is not None:
                try:
                    with Image.open(graphic.image_path) as original:
                        sprite=original.convert('RGBA')
                    # Artwork-only scaling experiment: 40% larger than the pilot.
                    factor=min(tw*.952/sprite.width, th*1.792/sprite.height)
                    target=(max(1,round(sprite.width*factor)),max(1,round(sprite.height*factor)))
                    sprite=sprite.resize(target,Image.Resampling.LANCZOS)
                    tk_image=ImageTk.PhotoImage(sprite,master=self)
                    self.images.append(tk_image)
                    # Raise the centre slightly while leaving terrain/tile geometry intact.
                    self.canvas.create_image(px,py-th*.08,image=tk_image)
                    rendered=True
                except (OSError,ValueError):
                    pass
            if not rendered:
                draw_colony_placeholder(self.canvas,px,py,tw,th,graphic)
        if self.show_selection_outline.get() and selected_outline is not None:
            self.canvas.create_polygon(selected_outline,fill='',outline='#ff23ad',width=3)

    def on_click(self,event):
        candidates=[]
        for x,y,px,py,tw,th in self.regions:
            if self.app.diamond_contains(event.x,event.y,px,py,tw,th):
                distance=abs(event.x-px)/(tw/2)+abs(event.y-py)/(th/2)
                candidates.append((distance,x,y))
        if candidates:
            _,x,y=min(candidates)
            self.selected=(x,y)
            self.paint();self.inspect(x,y)

    def inspect(self,x,y):
        tile=self.app.terrain_by_xy[(x,y)]
        self.colony=self.colonies_by_tile.get(tile.get('id'))
        lines=[f'Coordinates: ({x}, {y})',f'Terrain: {self.app.readable(tile.get("type"))}',
               f'Tile ID: {tile.get("id")}',f'Owner: {tile.get("owner","—")}', '']
        resources,improvements=self.app.tile_item_summary(tile)
        for item in resources:
            lines.append('Resource: '+self.app.readable(item.get('type')))
            lines.append('Quantity: '+item.get('quantity','—'))
        for item in improvements:
            lines.append('Improvement: '+self.app.readable(item.get('type')))
            if item.get('style'):lines.append('Style: '+item.get('style'))
        if self.colony:
            graphic=resolve_colony_graphic(self.colony)
            lines.extend(['','Colony: '+self.colony.get('name',''),
                          'Graphic state: '+graphic.key,
                          'Artwork: '+('available' if graphic.image_path else 'placeholder')])
        self.info.configure(state='normal');self.info.delete('1.0','end')
        self.info.insert('1.0','\n'.join(lines));self.info.configure(state='disabled')
        self.colony_button.configure(state='normal' if self.colony else 'disabled')

    def go_to_colony(self):
        if self.colony:
            self.app.navigate_to_colony(self.colony)
            self.app.lift()
