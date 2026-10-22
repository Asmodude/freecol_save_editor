"""FreeCol staggered-row grid geometry for a compact isometric map."""

def neighbor(x,y,direction):
    shift=y&1
    offsets={"NE":(shift,-1),"SE":(shift,1),"SW":(shift-1,1),"NW":(shift-1,-1)}
    dx,dy=offsets[direction]
    return x+dx,y+dy

def map_grid(cx,cy,radius=4):
    """Yield a 9x9 region along the NE and SE axes, centred at (cx,cy)."""
    for r in range(-radius,radius+1):
        for c in range(-radius,radius+1):
            x,y=cx,cy
            for _ in range(abs(r)):
                x,y=neighbor(x,y,'SE' if r>0 else 'NW')
            for _ in range(abs(c)):
                x,y=neighbor(x,y,'NE' if c>0 else 'SW')
            yield r,c,x,y
