"""DXF export (AutoCAD-openable, R2018) for the hospital layouts."""
import ezdxf
from ezdxf.enums import TextEntityAlignment

from plan_model import PLATE, CUTOUT, GLASS_WEST, GLASS_NORTH, LAYOUTS

LAYERS = {
    "PLATE":     {"color": 7, "lineweight": 50},
    "WALLS":     {"color": 7, "lineweight": 35},
    "GLASS":     {"color": 5, "lineweight": 25},
    "DOORS":     {"color": 1, "lineweight": 18},
    "TEXT":      {"color": 7},
    "FURNITURE": {"color": 8, "lineweight": 13},
    "VOID":      {"color": 6},
}


def export_dxf(key, out_path):
    _, factory = LAYOUTS[key]
    rooms = factory()

    doc = ezdxf.new("R2018", setup=True)
    doc.header["$INSUNITS"] = 2            # feet... INSUNITS 2 = feet
    msp = doc.modelspace()
    for name, attribs in LAYERS.items():
        doc.layers.add(name, color=attribs.get("color", 7))

    msp.add_lwpolyline(list(PLATE.exterior.coords), close=True,
                       dxfattribs={"layer": "PLATE"})
    msp.add_lwpolyline(list(CUTOUT.exterior.coords), close=True,
                       dxfattribs={"layer": "VOID"})

    for (x1, y1), (x2, y2) in GLASS_WEST + GLASS_NORTH:
        msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "GLASS"})

    for r in rooms:
        p = r.poly
        if p.is_empty:
            continue
        geoms = p.geoms if p.geom_type.startswith("Multi") else [p]
        for g in geoms:
            if g.geom_type != "Polygon" or g.area < 0.5:
                continue
            msp.add_lwpolyline(list(g.exterior.coords), close=True,
                               dxfattribs={"layer": "WALLS"})
        c = p.representative_point()
        if r.name:
            label = r.name + (" " + r.dims if r.dims else "")
            h = 1.1 if p.area > 60 else 0.7
            msp.add_text(label, height=h, dxfattribs={"layer": "TEXT"}).set_placement(
                (c.x, c.y), align=TextEntityAlignment.MIDDLE_CENTER)
        for (cx, cy, w, wall) in r.doors:
            if wall in ("N", "S"):
                msp.add_line((cx - w / 2, cy), (cx + w / 2, cy), dxfattribs={"layer": "DOORS"})
            else:
                msp.add_line((cx, cy - w / 2), (cx, cy + w / 2), dxfattribs={"layer": "DOORS"})
        for (kind, x, y, w, h, rot) in r.furniture:
            msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True,
                               dxfattribs={"layer": "FURNITURE"})

    doc.saveas(out_path)
    auditor = doc.audit()
    return len(auditor.errors)
