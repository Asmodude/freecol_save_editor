"""Better Colony Graphics: state resolution and local artwork lookup.

Original, nation-neutral artwork can be supplied in assets/colonies/.
The resolver never changes a FreeCol savegame.
"""
from dataclasses import dataclass
from pathlib import Path

SIZES=("small","medium","large")
TIERS=("colony","stockade","fort","fortress")
FORT_RANK={"model.building.stockade":1,"model.building.fort":2,"model.building.fortress":3}


@dataclass(frozen=True)
class ColonyGraphic:
    key: str
    population: int
    size: str
    fortification: str
    image_path: Path | None


def population_size(count):
    if count < 0:
        raise ValueError("Negative colony population")
    return "small" if count <= 3 else "medium" if count <= 7 else "large"


def resolve_colony_graphic(colony, asset_dir=None, population=None):
    """Return one of the twelve graphic keys, independent of nationality.

    `population` may be supplied from a validated colony population count.
    Otherwise nested colony worker units are counted. This is provisional
    until compared with FreeCol's getApparentUnitCount() on representative saves.
    """
    if population is None:
        population=sum(1 for unit in colony.iter("unit") if unit.get("id"))
    size=population_size(population)
    rank=0
    for element in colony.iter("building"):
        rank=max(rank,FORT_RANK.get(element.get("type"),0))
    tier=TIERS[rank]
    key=f"{tier}_{size}"
    directory=Path(asset_dir) if asset_dir is not None else Path(__file__).resolve().parent/"assets"/"colonies"
    image=directory/f"{key}.png"
    return ColonyGraphic(key,population,size,tier,image if image.is_file() else None)


def draw_colony_placeholder(canvas, px, py, width, height, graphic):
    """High-contrast visual placeholder; not part of final 12-artwork set."""
    w=max(15,width*.38);h=max(12,height*.50)
    top=py-h*.7
    # Outlined raised label allows settlement identification against any terrain.
    canvas.create_rectangle(px-w/2-3,top-3,px+w/2+3,top+h+3,
                            fill="#fff1b0",outline="#1b2230",width=2)
    roof=[px-w/2,top+h*.37,px,top,px+w/2,top+h*.37]
    canvas.create_polygon(roof,fill="#9d3b25",outline="#20232a",width=1)
    canvas.create_rectangle(px-w*.35,top+h*.37,px+w*.35,top+h,
                            fill="#f8e3a5",outline="#20232a",width=1)
    if graphic.fortification!="colony":
        canvas.create_rectangle(px-w*.55,top+h*.32,px+w*.55,top+h*.92,
                                outline="#262b31",width=2)
    if graphic.fortification in ("fort","fortress"):
        canvas.create_line(px-w*.55,top+h*.38,px-w*.55,top+h,
                           fill="#333333",width=3)
    if graphic.fortification=="fortress":
        canvas.create_rectangle(px-w*.56,top+h*.17,px-w*.34,top+h*.48,
                                fill="#7a818c",outline="#20232a")
        canvas.create_rectangle(px+w*.34,top+h*.17,px+w*.56,top+h*.48,
                                fill="#7a818c",outline="#20232a")
    canvas.create_text(px,top+h*1.18,text=graphic.key.replace("_"," "),
                       fill="#131b21",font=("Segoe UI",max(7,int(height*.14)),"bold"))
