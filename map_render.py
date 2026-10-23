"""Renderer-neutral geometry and directional-path instructions.

Phase 0: reproduces accepted Tk canvas paths without modifying their appearance.
Instructions are (kind, args, options); neither Tk nor Qt is imported here.
"""


def terrain_offsets(y):
    shift=int(y)&1
    return {'N':(0,-2),'NE':(shift,-1),'E':(1,0),'SE':(shift,1),
            'S':(0,2),'SW':(shift-1,1),'W':(-1,0),
            'NW':(shift-1,-1),'C':(0,0)}


def direction_endpoint(direction,tw,th):
    endpoints=((0,-th/2),(tw/4,-th/4),(tw/2,0),(tw/4,th/4),
               (0,th/2),(-tw/4,th/4),(-tw/2,0),(-tw/4,-th/4))
    return endpoints[direction]


def diamond_contains(px,py,cx,cy,width,height,tolerance=0.0):
    if width<=0 or height<=0:
        return False
    return abs(px-cx)/(width/2)+abs(py-cy)/(height/2) <= 1.0+tolerance


def road_primitives(x,y,tw,th,style):
    if len(style)!=8 or any(c not in '01' for c in style):
        return []
    active=[i for i,c in enumerate(style) if c=='1']
    result=[]
    for d in active:
        dx,dy=direction_endpoint(d,tw,th)
        path=(x,y,x+dx*.56,y+dy*.58,x+dx,y+dy)
        result.append(('line',path,{'fill':'#714d2e','width':max(3,round(th*.067)),'smooth':1}))
        result.append(('line',path,{'fill':'#c99b61','width':max(1,round(th*.035)),'smooth':1}))
    if active:
        radius=max(2,round(th*.045))
        result.append(('oval',(x-radius,y-radius,x+radius,y+radius),{'fill':'#c99b61','outline':''}))
    return result


def river_primitives(x,y,tw,th,style):
    if len(style)!=4 or any(c not in '012' for c in style):
        return []
    result=[]
    for pos,c in enumerate(style):
        if c=='0':
            continue
        dx,dy=direction_endpoint(1+pos*2,tw,th)
        breadth=max(3,round(th*(.09 if c=='2' else .055)))
        path=(x,y,x+dx*.53,y+dy*.45,x+dx,y+dy)
        result.append(('line',path,{'fill':'#3d7189','width':breadth+2,'smooth':1}))
        result.append(('line',path,{'fill':'#8dc4da','width':breadth,'smooth':1}))
    return result
