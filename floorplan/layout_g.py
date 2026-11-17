"""LAYOUT G (17-11-2026) - the clients' blue-pen sketch placed on the real
building geometry taken from the builder's DWG.

Source of the geometry: floorplan/source/solaris_typical_5_7_10.dxf (mm),
east wing = builder units x05 + x06 + x07 plus the dead-end common passage
and the strip behind the lifts that only these three units use.

Coordinates (same convention as plan_model.py), in FEET:
  x from the OUTER face of the east wall, increasing westward
  y from the OUTER face of the south wall, increasing northward
  DWG -> model:  x = (X - 6002130) / 304.8,  y = (-206361 - Y) / 304.8
The inner plastered wall faces are therefore at x = y = 0.39 (120 mm).

This module must not import plan_model at import time (plan_model imports
it); everything that needs Room is created lazily.
"""
import math
from functools import wraps

from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union

T = 0.375                    # internal partition, 4.5"
E0 = S0 = 0.39               # inner plaster face of east / south walls
N0 = 91.83                   # inner plaster face of north wall
WEST_SLOPE = 0.1444          # ft of x lost per ft of y along the west facade
DATE = "17-11-2026"
TITLE = "LAYOUT G - blue-pen sketch on DWG geometry"


def xw(y):
    """Inner plaster face of the west (glass) facade at height y."""
    return 47.58 - WEST_SLOPE * y


def xw_out(y):
    """Outer structural face of the west facade wall."""
    return 47.98 - WEST_SLOPE * y


def _arc(cx, cy, r, a0, a1, n=10):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


# ------------------------------------------------------------ real envelope
ARC_C = (30.40, 87.30)       # centre of the rounded NW corner (DWG 6011396,-232971)
INNER = Polygon([(E0, S0), (xw(S0), S0)] + _arc(*ARC_C, 4.53, 8.2, 90.0)
                + [(E0, N0)])
OUTER = Polygon([(0.0, 0.0), (47.98, 0.0)] + _arc(*ARC_C, 4.92, 8.2, 90.0)
                + [(0.0, 92.22)])
# cut-out / service void at the waist (DWG hatch boundary)
CUTOUT_G = Polygon([(24.64, 40.09), (41.90, 40.09), (40.75, 48.10), (24.64, 48.10)])
MD_DOOR_G = (0.0, 43.0, 48.0)          # 5'-0" door in the 8'-0" passage mouth
PASSAGE_MOUTH = (40.09, 48.10)         # existing common passage, clear 8'-0"

GLASS_WEST_G = [((47.98, 0.0), (xw_out(40.09), 40.09)),
                ((xw_out(48.10), 48.10), (35.27, 88.0))]
_a = _arc(*ARC_C, 4.92, 8.2, 90.0, 6)
GLASS_WEST_G += list(zip(_a[:-1], _a[1:]))
GLASS_NORTH_G = [((30.40, 92.22), (4.90, 92.22))]

# RCC columns (plaster outline, read off the DWG plaster line / wall-hatch gaps)
COLUMNS = {
    "C1": box(20.28, 0.33, 22.87, 1.54),
    "C2": box(45.17, 0.33, 47.80, 1.54),
    "C3": box(20.28, 19.82, 22.87, 22.41),
    "C4": box(42.30, 19.82, 44.95, 21.42),
    "C5": box(20.28, 38.55, 22.87, 40.16),
    "C6": Polygon([(40.69, 39.76), (41.02, 37.40), (42.20, 37.57), (41.90, 39.76)]),
    "C7": box(20.28, 48.10, 22.38, 50.46),
    "C8": Polygon([(39.49, 48.43), (39.15, 50.37), (40.74, 50.60), (41.00, 48.43)]),
    "C9": box(0.0, 48.10, 1.71, 50.46),
    "C10": box(0.33, 68.54, 2.30, 71.62),
    "C11": box(0.33, 89.70, 1.54, 91.90),
    "C12": box(20.28, 89.70, 22.38, 91.90),
    "C13": Polygon([(35.63, 71.30), (36.07, 68.25), (38.15, 68.55), (37.71, 71.60)]),
    "C14": Polygon([(34.89, 79.85), (35.19, 77.77), (36.78, 78.00), (36.48, 80.08)]),
}
COLS = unary_union([c.intersection(OUTER) for c in COLUMNS.values()])
GRID_X = {"A": 0.17, "B": 21.57}
GRID_Y = {"1": 0.9, "2": 21.1, "3": 39.3, "4": 49.3, "5": 70.1, "6": 90.8}

# existing builder features (context / demolition), feet
EXIST_SUNK = [("ex. toilet x07", box(0.33, 0.33, 4.33, 6.33)),
              ("ex. toilet x06", box(35.90, 35.76, 42.48, 39.76)),
              ("ex. toilet x05", box(0.33, 51.71, 4.33, 59.68))]
EXIST_DUCT = box(0.33, 48.43, 4.33, 51.38)
EXIST_WALLS_REMOVED = [            # centre lines of 100 mm walls to take down
    ((27.25, 20.02), (32.25, 20.02)),                                    # x07 | x06 at the OPD passage
    ((8.50, 30.8), (8.50, 35.83)),                                       # x06 east wall (X-ray part)
    ((14.66, 39.92), (20.28, 39.92)),                                    # x06 north wall (lobby mouth)
    ((4.33, 0.33), (4.33, 6.50)), ((0.33, 6.50), (4.33, 6.50)),          # x07 toilet
    ((4.50, 51.5), (4.50, 60.0)), ((0.33, 59.85), (4.50, 59.85)),        # x05 toilet
    ((14.28, 48.27), (20.34, 48.27)),                                    # x05 south wall (part)
]
# lift / stair core east of the unit (context only)
LIFTS = [box(-9.62, 8.10, -0.39, 15.98), box(-9.62, 16.60, -0.39, 22.97),
         box(-9.62, 23.59, -0.39, 29.95), box(-9.62, 30.58, -0.39, 36.94)]
CORE_DUCT = box(-9.84, 37.76, -1.15, 39.76)
REFUGE = box(-26.6, -1.6, -0.1, 5.3)


def fi(v, half=False):
    """Feet-inches string, rounded to the nearest inch (or half inch)."""
    step = 24 if half else 12
    n = round(v * step)
    ft, rem = divmod(n, step)
    if half:
        inch, h = divmod(rem, 2)
        return f"{ft}'-{inch}{'½' if h else ''}\""
    return f"{ft}'-{rem}\""


# ------------------------------------------------------------------- doors
def D(cx, cy, w, axis, swing, hinge="lo", kind="single"):
    """axis 'v': the wall runs north-south, the door spans y.  'h': spans x.
    swing +1 / -1: the leaf opens toward +axis / -axis of the other direction.
    kind: single | double | open (cased opening / curtain) | hatch (counter)."""
    return dict(cx=cx, cy=cy, w=w, axis=axis, swing=swing, hinge=hinge, kind=kind)


def _legacy_door(d):
    letter = ({1: "E", -1: "W"} if d["axis"] == "v" else {1: "N", -1: "S"})[d["swing"]]
    return (d["cx"], d["cy"], d["w"], letter)


_GRoom = None


def _room_cls():
    global _GRoom
    if _GRoom is None:
        from plan_model import Room

        class GRoom(Room):
            """Room clipped to the real inner wall faces, cut-out and columns."""
            @property
            def poly(self):
                x, y, w, h = self.rect
                p = box(x, y, x + w, y + h).intersection(INNER)
                p = p.difference(CUTOUT_G)
                if self.zone != "circ":
                    p = p.difference(COLS)
                for hx, hy, hw, hh in self.holes:
                    p = p.difference(box(hx, hy, hx + hw, hy + hh))
                return p
        _GRoom = GRoom
    return _GRoom


def _mk(key, name, rect, zone, doors=(), furniture=(), holes=(), notes="",
        dims=None, label=None):
    R = _room_cls()
    r = R(key, name, "", rect, zone,
          doors=[_legacy_door(d) for d in doors if d["kind"] in ("single", "double")],
          furniture=list(furniture), holes=list(holes), notes=notes)
    r.gdoors = list(doors)
    r.label = label
    if dims is None and zone != "circ":
        p = r.poly
        x, y, w, h = rect
        if abs(p.area - w * h) < 0.03 * w * h:
            dims = f"{fi(w)} x {fi(h)}"
        else:
            minx, miny, maxx, maxy = p.bounds
            hh = maxy - miny
            dims = f"≈{fi(p.area / hh)} x {fi(hh)}"
    r.dims = dims or ""
    return r


def _ward_wc(key, x, y, door, wc, sink, shower, label, acc=False):
    """Ensuite 5'-5" deep: WC + basin + shower, 3'-0" door opening outward."""
    return _mk(key, "Toilet (Acc.)" if acc else "Toilet", (x, y, 9.0, 5.4), "wet",
               doors=[door], label=label,
               furniture=[("wc",) + wc, ("sink",) + sink + (1.3, 1.2, 0),
                          ("shower",) + shower + (0,)])


def layout_g_rooms():
    """North (IPD) block: the blue-pen sketch (same as Layout F) on the DWG
    outline and column grid.  South block: the clients' 3rd sketch, drawn in
    blue pen over the DWG print, which takes precedence there."""
    wait = ([("chair", 33.2 + 1.8 * i, 30.9, 1.4, 1.4, 0) for i in range(5)]
            + [("chair", 31.3 + 1.8 * i, 34.0, 1.4, 1.4, 0) for i in range(6)]
            + [("chair", 28.2 + 1.8 * i, 38.2, 1.4, 1.4, 0) for i in range(3)]
            + [("chair", 28.2 + 1.8 * i, 36.4, 1.4, 1.4, 0) for i in range(2)]
            + [("chair", 21.0 + 1.8 * i, 31.2, 1.4, 1.4, 0) for i in range(3)])
    rooms = [
        # ---------- SOUTH BLOCK: zoning of the 3rd sketch (blue pen over the DWG print)
        # OT = whole east part of unit x07, west wall on the west face of grid-B columns,
        # north wall = the existing x07 | x06 party wall (kept).
        _mk("ot", "OPERATION THEATRE", (E0, S0, 22.48, 19.43), "surgical",
            furniture=[("ottable", 10.4, 6.4, 2.6, 6.5, 15), ("light", 11.2, 4.6, 1.5, 1.5, 0),
                       ("counter", 6.0, 0.6, 7.0, 1.5, 0), ("cart", 17.6, 3.0, 1.8, 2.6, 0),
                       ("cart", 2.0, 9.0, 1.8, 2.6, 0), ("cart", 2.0, 13.0, 1.8, 2.6, 0)],
            dims="22'-6\" x 19'-5\"", label=(9.6, 16.4),
            notes="Patient in/out only through Recovery; staff through Scrub"),
        _mk("otstore", "OT Store", (E0, 20.21, 7.94, 10.39), "support",
            doors=[D(2.4, 20.01, 3.0, "h", 1)],
            furniture=[("shelf", 0.6, 24.0, 1.2, 6.4, 0), ("shelf", 6.9, 20.5, 1.2, 9.8, 0),
                       ("shelf", 2.2, 29.2, 4.4, 1.2, 0)],
            label=(4.4, 25.6), notes="Strip behind the lifts; uses the builder's x07 door opening"),
        _mk("recovery", "RECOVERY / PRE-OP", (8.705, 20.21, 14.165, 10.39), "surgical",
            doors=[D(17.6, 20.01, 5.0, "h", -1, kind="double"),
                   D(17.6, 30.79, 5.0, "h", -1, kind="double")],
            furniture=[("bed", 9.3, 20.5, 3.2, 6.8, 180), ("bed", 13.0, 20.5, 3.2, 6.8, 180),
                       ("side", 12.55, 20.5, 0.4, 1.4, 0), ("desk", 9.0, 28.6, 3.4, 1.7, 0)],
            label=(13.0, 28.2),
            notes="5'-0\" double doors in line: lobby -> recovery -> OT"),
        _mk("xray", "X-RAY / DRESSING / EMERGENCY", (E0, 30.975, 13.89, 8.785), "consult",
            doors=[D(14.47, 36.6, 4.0, "v", -1)],
            furniture=[("exam", 3.4, 35.9, 6.4, 2.5, 0), ("counter", 5.6, 31.2, 6.0, 1.4, 0),
                       ("cart", 1.0, 31.4, 1.6, 2.2, 0)],
            label=(8.8, 33.7),
            notes="Lead-lined; mobile / portable X-ray only at this size"),
        # staff strip between the OT and the OPD passage (3'-7½" clear, as sketched)
        _mk("autoclave", "Autoclave / CSSD", (23.245, S0, 9.0, 5.11), "surgical",
            doors=[D(29.7, 5.69, 2.75, "h", -1)],
            furniture=[("counter", 23.5, 0.6, 5.6, 1.5, 0)], label=(27.4, 3.5)),
        _mk("scrub", "Scrub", (23.245, 5.875, 3.625, 3.725), "surgical",
            doors=[D(23.06, 7.7, 3.0, "v", -1),
                   D(25.06, 9.79, 2.6, "h", 1, kind="open")],
            furniture=[("sink", 25.5, 6.1, 1.2, 1.1, 0), ("sink", 25.5, 7.4, 1.2, 1.1, 0)],
            label=(24.5, 8.6)),
        _mk("otchange", "OT Change", (23.245, 9.975, 3.625, 6.725), "surgical",
            doors=[D(25.06, 16.89, 2.5, "h", -1)],
            furniture=[("shelf", 23.4, 10.2, 1.1, 4.2, 0)],
            label=(25.7, 13.3),
            notes="Staff-only way in: OPD passage -> air-lock -> change -> scrub -> OT"),
        _mk("otlobby", "OT air-lock", (23.245, 17.075, 3.625, 2.745), "surgical",
            doors=[D(27.06, 18.45, 2.5, "v", -1)], label=(24.4, 18.6)),
        _mk("opd2", "OPD 2 · Plaster bay", (23.245, 20.21, 3.625, 10.39), "consult",
            doors=[D(25.06, 30.79, 3.4, "h", -1, kind="open")],
            furniture=[("exam", 23.45, 20.5, 2.25, 6.0, 0), ("cart", 23.5, 27.2, 1.6, 2.0, 0)],
            label=(26.25, 25.4),
            notes="As sketched it is a 3'-7½\" bay, not a consulting room"),
        # west rooms off the OPD passage
        _mk("lounge", "DRS' LOUNGE", (32.62, S0, 5.38, 9.71), "consult",
            doors=[D(32.43, 7.9, 2.75, "v", 1)],
            furniture=[("sofa", 32.9, 0.6, 4.8, 2.2, 180), ("chair", 36.2, 8.2, 1.4, 1.4, 0)],
            label=(35.3, 5.0)),
        _mk("wcLg", "Toilet", (41.5, S0, 7.0, 4.2), "wet",
            doors=[D(42.9, 4.78, 2.25, "h", 1)],
            furniture=[("wc", 43.6, 0.6, 1.5, 2.0, 180), ("sink", 41.8, 0.6, 1.3, 1.2, 0)],
            label=(42.6, 3.3)),
        _mk("drrest", "Drs' Rest + WC", (38.375, S0, 10.0, 9.71), "consult",
            holes=[(41.125, S0, 8.0, 4.575)],
            doors=[D(38.19, 7.9, 2.5, "v", 1)],
            furniture=[("bed", 39.4, 7.0, 6.2, 2.8, 0), ("side", 38.6, 0.6, 1.3, 1.4, 0)],
            dims="≈8'-1\" x 9'-9\" incl. WC", label=(43.2, 5.9),
            notes="Reached through the lounge"),
        _mk("opd3", "OPD 3 · Psychiatry", (32.62, 10.475, 14.0, 9.345), "consult",
            doors=[D(32.43, 17.9, 3.0, "v", 1, hinge="hi")],
            furniture=[("desk", 35.6, 12.3, 4.6, 2.0, 0), ("chair", 37.2, 10.7, 1.4, 1.4, 0),
                       ("chair", 35.9, 14.6, 1.4, 1.4, 0), ("chair", 38.1, 14.6, 1.4, 1.4, 0),
                       ("sofa", 41.6, 11.4, 2.3, 5.2, 0), ("plant", 42.2, 17.6, 1.3, 1.3, 0)],
            label=(38.8, 17.9),
            notes="Dr. Heena; acoustic partitions + solid door"),
        _mk("opd1", "OPD 1 · Ortho", (32.62, 20.21, 13.0, 9.89), "consult",
            doors=[D(32.43, 28.3, 3.0, "v", 1, hinge="hi")],
            furniture=[("exam", 40.2, 22.6, 2.25, 6.0, 0), ("desk", 34.6, 22.0, 4.6, 2.0, 0),
                       ("chair", 36.2, 20.5, 1.4, 1.4, 0), ("chair", 34.8, 24.3, 1.4, 1.4, 0),
                       ("chair", 37.0, 24.3, 1.4, 1.4, 0)],
            label=(37.2, 27.8), notes="Dr. Aman"),
        _mk("recep", "RECEPTION", (20.655, 36.275, 6.215, 3.485), "public",
            doors=[D(24.0, 36.09, 4.6, "h", -1, kind="hatch"),
                   D(20.47, 37.4, 2.2, "v", 1)],
            furniture=[("counter", 21.7, 36.5, 4.6, 1.2, 0)],
            label=(24.9, 38.7), dims="6'-3\" x 3'-6\""),
        _mk("wcP", "Patient WC (existing)", (35.90, 35.76, 7.0, 4.0), "wet",
            doors=[D(35.71, 37.0, 2.45, "v", 1)],
            furniture=[("wc", 39.0, 37.5, 1.5, 2.0, 0), ("sink", 39.6, 36.0, 1.2, 1.1, 0)],
            label=(37.3, 38.2),
            notes="Builder's x06 toilet kept on its sunk slab and shaft"),
        # --------------------------------------- east service band (north of entry)
        _mk("duct", "Duct", (E0, 48.49, 3.94, 2.89), "support", dims=""),
        _mk("bp", "BP / ECG", (E0, 48.49, 7.51, 10.71), "consult",
            holes=[(E0, 48.49, 4.315, 3.265), (6.525, 55.2, 1.6, 4.2)],
            doors=[D(6.4, 48.30, 3.0, "h", 1)],
            furniture=[("exam", 0.6, 56.5, 5.7, 2.25, 0), ("desk", 0.7, 52.0, 3.0, 1.7, 0),
                       ("chair", 1.5, 53.8, 1.3, 1.2, 0)],
            dims="7'-6\" wide, L-shape", label=(5.5, 53.9)),
        _mk("pharm", "PHARMACY", (8.275, 48.49, 5.63, 6.71), "public",
            doors=[D(14.09, 53.6, 2.75, "v", -1),
                   D(11.3, 48.30, 3.6, "h", 1, kind="hatch")],
            furniture=[("counter", 9.5, 48.7, 3.6, 1.2, 0), ("shelf", 8.45, 50.6, 1.1, 4.4, 0)],
            label=(11.4, 51.6), notes="Dispensing hatch faces the entry passage"),
        _mk("obs", "Obs. Bed", (6.9, 55.575, 7.005, 3.625), "inpatient",
            doors=[D(14.09, 57.39, 3.2, "v", -1, kind="open")],
            furniture=[("bed", 7.1, 55.9, 6.5, 2.9, 180)], label=(10.6, 58.75),
            notes="Curtained day-care / observation bed beside the nursing station"),
        _mk("change", "Staff Change", (E0, 59.575, 5.81, 6.425), "support",
            doors=[D(6.39, 64.2, 2.5, "v", -1)],
            furniture=[("shelf", 0.6, 59.8, 1.2, 5.9, 0)], label=(3.6, 62.0)),
        _mk("ns", "NURSING STN.", (6.575, 59.575, 7.33, 6.425), "inpatient",
            doors=[D(14.09, 62.8, 5.0, "v", -1, kind="open")],
            furniture=[("counter", 12.3, 60.3, 1.4, 5.0, 0), ("chair", 10.4, 62.0, 1.4, 1.4, 0),
                       ("shelf", 6.8, 59.8, 4.4, 1.1, 0)], label=(9.6, 64.6)),
        _mk("store", "Store", (E0, 66.375, 5.01, 6.625), "support",
            doors=[D(3.9, 66.19, 2.5, "h", 1)],
            furniture=[("shelf", 0.6, 71.8, 4.6, 1.0, 0), ("shelf", 4.2, 69.2, 1.0, 2.5, 0)],
            label=(2.7, 67.7)),
        _mk("duty", "Duty Dr / Staff Rest", (5.775, 66.375, 8.13, 6.625), "support",
            doors=[D(14.09, 68.4, 2.75, "v", -1)],
            furniture=[("bed", 6.0, 70.1, 6.5, 2.7, 180), ("shelf", 6.0, 66.6, 3.6, 1.0, 0)],
            label=(8.9, 68.7),
            notes="Bunk (2 berths)"),
        _mk("bath5", "Suite Bath", (E0, 73.375, 5.81, 5.425), "wet",
            doors=[D(3.0, 78.99, 2.75, "h", 1)],
            furniture=[("shower", 0.6, 73.6, 1.7, 2.4, 0), ("sink", 2.7, 73.6, 1.3, 1.2, 0),
                       ("wc", 4.4, 73.7, 1.5, 2.0, 180)]),
        _mk("pantry", "Pantry", (6.575, 73.375, 7.33, 5.425), "support",
            doors=[D(14.09, 76.6, 2.75, "v", -1)],
            furniture=[("counter", 6.8, 73.6, 6.0, 1.5, 0), ("cart", 6.8, 76.5, 1.8, 2.0, 0)],
            label=(10.3, 76.6)),
        # --------------------------- wards on the west glass, toilets paired at the glass
        _mk("room1", "ROOM 1", (20.655, 48.49, 22.0, 10.41), "inpatient",
            holes=[(31.625, 53.125, 10.5, 5.9)],
            doors=[D(20.47, 56.4, 3.5, "v", 1, hinge="hi")],
            furniture=[("bed", 25.0, 48.7, 3.3, 6.8, 180), ("side", 28.5, 48.7, 1.4, 1.5, 0),
                       ("wardrobe", 20.9, 50.7, 2.0, 3.6, 0), ("sofa", 33.0, 48.7, 5.4, 2.3, 180),
                       ("tv", 25.0, 58.2, 3.4, 0.5, 0)], label=(28.1, 56.9),
            dims="≈19'-2\" x 10'-5\" incl. toilet"),
        _ward_wc("wcR1", 32.0, 53.5, D(31.81, 56.6, 3.0, "v", -1, hinge="hi"),
                 (35.3, 56.7, 1.5, 2.0, 0), (33.0, 57.5), (37.1, 53.7, 2.2, 2.4), (34.2, 54.9),
                 acc=True),
        _mk("room2", "ROOM 2", (20.655, 59.275, 22.0, 10.425), "inpatient",
            holes=[(31.625, 59.2, 10.5, 5.85)],
            doors=[D(20.47, 61.8, 3.5, "v", 1)],
            furniture=[("bed", 25.0, 62.7, 3.3, 6.8, 0), ("side", 28.5, 68.0, 1.4, 1.5, 0),
                       ("wardrobe", 20.9, 64.6, 2.0, 4.6, 0), ("sofa", 30.8, 67.2, 4.4, 2.3, 0),
                       ("tv", 25.0, 59.5, 3.4, 0.5, 0)], label=(28.6, 61.2),
            dims="≈17'-7\" x 10'-5\" incl. toilet"),
        _ward_wc("wcR2", 32.0, 59.275, D(31.81, 61.6, 3.0, "v", -1),
                 (35.3, 59.5, 1.5, 2.0, 180), (33.0, 59.5), (36.3, 62.0, 2.0, 2.4), (34.2, 63.3)),
        _mk("room3", "ROOM 3", (20.655, 70.075, 20.0, 10.225), "inpatient",
            holes=[(29.625, 74.525, 10.5, 5.9)],
            doors=[D(20.47, 77.6, 3.5, "v", 1, hinge="hi")],
            furniture=[("bed", 24.7, 70.3, 3.3, 6.8, 180), ("side", 28.2, 70.3, 1.3, 1.5, 0),
                       ("wardrobe", 20.9, 70.4, 2.0, 4.4, 0), ("sofa", 30.2, 70.3, 5.0, 2.3, 180),
                       ("tv", 24.7, 79.6, 3.4, 0.5, 0)], label=(26.0, 78.4),
            dims="≈16'-1\" x 10'-3\" incl. toilet"),
        _ward_wc("wcR3", 30.0, 74.9, D(31.7, 74.71, 3.0, "h", -1),
                 (30.4, 78.1, 1.5, 2.0, 0), (32.5, 78.9), (34.0, 75.1, 2.2, 2.3), (32.2, 76.6)),
        _mk("room4", "ROOM 4", (20.655, 80.675, 20.0, 11.155), "inpatient",
            holes=[(29.625, 80.6, 10.5, 5.85)],
            doors=[D(20.47, 82.7, 3.5, "v", 1)],
            furniture=[("bed", 24.7, 80.9, 3.3, 6.8, 180), ("side", 28.2, 80.9, 1.3, 1.5, 0),
                       ("wardrobe", 20.9, 85.2, 2.0, 4.3, 0), ("sofa", 23.6, 89.3, 5.4, 2.3, 0),
                       ("tv", 29.0, 86.9, 0.5, 3.2, 0)], label=(31.6, 88.9),
            dims="≈14'-6\" x 11'-2\" incl. toilet"),
        _ward_wc("wcR4", 30.0, 80.675, D(31.7, 86.26, 3.0, "h", 1),
                 (30.4, 80.9, 1.5, 2.0, 180), (32.5, 80.9), (33.0, 83.5, 2.0, 2.3), (31.4, 84.0)),
        _mk("suite", "SUITE ROOM 5", (E0, 79.175, 19.89, 12.655), "inpatient",
            holes=[(13.905, 79.175, 6.5, 5.8)],
            doors=[D(17.28, 84.79, 3.5, "h", 1)],
            furniture=[("bed", 7.0, 79.4, 3.5, 7.0, 180), ("side", 10.6, 79.4, 1.4, 1.5, 0),
                       ("side", 5.5, 79.4, 1.4, 1.5, 0),
                       ("wardrobe", 0.6, 83.0, 2.0, 5.0, 0), ("sofa", 8.4, 89.3, 6.0, 2.3, 0),
                       ("chair", 6.4, 89.6, 1.4, 1.4, 0), ("sofa", 17.8, 86.6, 2.3, 4.6, 0),
                       ("desk", 2.6, 89.6, 3.0, 1.8, 0)],
            dims="≈19'-11\" x 12'-8\" (L) + bath", label=(11.0, 87.4),
            notes="Private bath entered from the suite; sit-out on the north glass"),
        # ------------------------------------------- open-plan / circulation anchors
        _mk("wait", "WAITING AREA (19 seats)", (30.4, 32.45, 11.0, 1.4), "circ",
            furniture=wait + [("water", 28.0, 31.0, 1.2, 1.2, 0),
                              ("plant", 41.2, 33.6, 1.3, 1.3, 0)]),
        _mk("lobby2", "LOBBY", (14.655, 32.2, 5.6, 6.0), "circ"),
        _mk("opdlobby", "OPD PASSAGE 5'-0\"", (27.245, 6.5, 5.0, 12.0), "circ",
            notes="One passage feeds OPD 1, OPD 3, the lounge and the staff door to the OT"),
        _mk("lobby", "ENTRY PASSAGE 8'-0\"", (1.0, 41.4, 12.0, 1.4), "circ"),
        _mk("bay", "trolley /\nwheelchair bay", (20.6, 43.2, 3.6, 2.0), "circ"),
        _mk("wardcorr", "WARD PASSAGE 6'-0\"", (14.28, 50.0, 6.0, 32.0), "circ"),
    ]
    return rooms


# -------------------------------------------------------------------- walls
def _solids(rooms):
    return [r for r in rooms if r.zone != "circ"]


def wall_bands_g(rooms):
    """True-thickness walls: 4.5" partitions around every room, the real
    external walls (outer face - inner face), cut-out surround and columns,
    with door / hatch / cased openings and the main entrance punched out."""
    polys = [r.poly for r in _solids(rooms)]
    solid = unary_union(polys)
    grown = unary_union([p.buffer(T, join_style=2) for p in polys])
    walls = grown.difference(solid).intersection(INNER)
    walls = walls.difference(CUTOUT_G)
    ring = CUTOUT_G.buffer(0.33, join_style=2).difference(CUTOUT_G).intersection(OUTER)
    perimeter = OUTER.difference(INNER)
    walls = unary_union([walls, ring, perimeter, COLS])
    for r in rooms:
        for d in getattr(r, "gdoors", []):
            w = d["w"]
            if d["axis"] == "h":
                op = box(d["cx"] - w / 2, d["cy"] - 0.45, d["cx"] + w / 2, d["cy"] + 0.45)
            else:
                op = box(d["cx"] - 0.45, d["cy"] - w / 2, d["cx"] + 0.45, d["cy"] + w / 2)
            walls = walls.difference(op.difference(COLS))
    _, y1, y2 = MD_DOOR_G
    walls = walls.difference(box(-0.5, y1, 0.8, y2))
    if walls.geom_type != "Polygon":      # drop slivers / stray lines
        from shapely.geometry import MultiPolygon
        walls = MultiPolygon([g for g in walls.geoms
                              if g.geom_type == "Polygon" and g.area > 1e-3])
    return walls


def free_space(rooms):
    """Clear circulation: inside the walls, outside every room and wall band."""
    grown = unary_union([r.poly.buffer(T, join_style=2) for r in _solids(rooms)])
    return (INNER.difference(grown).difference(CUTOUT_G.buffer(0.33, join_style=2))
            .difference(COLS))


# ----------------------------------------------------------- legacy bridge
def with_geometry(fn):
    """Decorator for the shared renderers (blueprint_svg, dxf_export,
    render3d): while drawing layout 'G' the DWG geometry replaces Rev C."""
    @wraps(fn)
    def wrapper(key, *a, **k):
        if key != "G":
            return fn(key, *a, **k)
        import plan_model as pm
        new = dict(PLATE=OUTER, CUTOUT=CUTOUT_G, GLASS_WEST=GLASS_WEST_G,
                   GLASS_NORTH=GLASS_NORTH_G, MD_DOOR=MD_DOOR_G, wall_bands=wall_bands_g)
        targets = [vars(pm), fn.__globals__]
        saved = [{n: t[n] for n in new if n in t} for t in targets]
        try:
            for t, s in zip(targets, saved):
                for n in s:
                    t[n] = new[n]
            return fn(key, *a, **k)
        finally:
            for t, s in zip(targets, saved):
                t.update(s)
    return wrapper


# ------------------------------------------------------------------- checks
FIRE_PATH = [(2.0, 91.0), (17.28, 86.2), (17.28, 45.5), (0.2, 45.5)]
STAIR_PATH = [(0.2, 45.5), (-16.0, 45.5), (-16.0, 20.0), (-22.7, 20.0)]   # approx., from DWG core


def _scan_width(free, axis, fixed, lo, hi):
    """Clear width of the free space along a scan line."""
    if axis == "x":
        line = LineString([(lo, fixed), (hi, fixed)])
    else:
        line = LineString([(fixed, lo), (fixed, hi)])
    seg = line.intersection(free)
    if seg.is_empty:
        return 0.0
    geoms = seg.geoms if seg.geom_type.startswith("Multi") else [seg]
    return max(g.length for g in geoms)


def checks():
    """Numbers quoted in the brief; run `python3 layout_g.py`."""
    from itertools import combinations
    import plan_model as pm
    rooms = layout_g_rooms()
    sol = _solids(rooms)
    out = {}
    out["overlaps_gt_0.5sf"] = [(a.key, b.key, round(a.poly.intersection(b.poly).area, 2))
                                for a, b in combinations(sol, 2)
                                if a.poly.intersection(b.poly).area > 0.5]
    free = free_space(rooms)
    out["ward_passage_min_ft"] = round(min(_scan_width(free, "x", y, 13.0, 21.5)
                                           for y in [49.0 + 0.25 * i for i in range(140)]), 2)
    out["opd_passage_min_ft"] = round(min(_scan_width(free, "x", y, 26.6, 33.0)
                                          for y in [6.2 + 0.25 * i for i in range(95)]), 2)
    out["south_lobby_min_ft"] = round(min(_scan_width(free, "x", y, 14.0, 20.6)
                                          for y in [31.2 + 0.25 * i for i in range(34)]), 2)
    out["staff_strip_ft"] = 3.625
    out["entry_passage_min_ft"] = round(min(_scan_width(free, "y", x, 39.0, 49.0)
                                            for x in [0.6 + 0.25 * i for i in range(54)]), 2)
    walls = wall_bands_g(rooms)
    path = LineString(FIRE_PATH)
    suite = next(r for r in rooms if r.key == "suite").poly
    blocked = path.intersection(walls).length
    others = unary_union([r.poly for r in sol if r.key != "suite"])
    out["fire_path_unit_ft"] = round(path.length, 1)
    out["fire_path_blocked_ft"] = round(blocked + path.intersection(others).length, 2)
    out["fire_path_to_stair_ft"] = round(path.length + LineString(STAIR_PATH).length, 1)
    out["beds"] = {r.key: sum(1 for f in r.furniture if f[0] == "bed") for r in rooms
                   if any(f[0] == "bed" for f in r.furniture)}
    doors = []
    for r in rooms:
        for d in getattr(r, "gdoors", []):
            pt = Point(d["cx"], d["cy"])
            inside = [s.key for s in sol if s.poly.contains(pt)]
            doors.append((r.key, d["kind"], fi(d["w"]), round(r.poly.distance(pt), 2), inside))
    out["doors_off_wall"] = [d for d in doors if d[3] > 0.3 or d[4]]
    out["door_widths"] = {f"{r.key}.{i}": fi(d["w"]) for r in rooms
                          for i, d in enumerate(getattr(r, "gdoors", []))}
    out["room_area_sf"] = round(sum(r.area for r in sol), 0)
    out["clear_floor_sf"] = round(INNER.area - CUTOUT_G.intersection(INNER).area, 0)
    out["gross_outer_sf"] = round(OUTER.area - CUTOUT_G.area, 0)
    # --- Rev C envelope against the DWG (inches; + = Rev C larger)
    dev = {}
    pts = pm.PLATE_PTS
    west = LineString(pts[1:14])
    for y in (0, 10, 20, 30, 39, 50, 60, 70, 80, 85):
        hit = LineString([(20, y + 0.001), (60, y + 0.001)]).intersection(west)
        if not hit.is_empty:
            dev[f"west facade @ y={y}'"] = round((hit.x - xw_out(y)) * 12, 1)
    dev["south width (Rev C 48'-6\" vs wall face 47'-11.7\")"] = round((48.5 - 47.98) * 12, 1)
    dev["east length (Rev C 92'-0\" vs wall face 92'-2.7\")"] = round((92.0 - 92.22) * 12, 1)
    dev["cut-out east edge (Rev C 25.6' vs 24.64')"] = round((25.6 - 24.64) * 12, 1)
    dev["cut-out south edge"] = round((40.0 - 40.09) * 12, 1)
    dev["cut-out north edge"] = round((48.0 - 48.10) * 12, 1)
    out["revC_minus_DWG_inches"] = dev
    return out


# ------------------------------------------------------------ CAD sheet (PNG/SVG)
LABEL_FS = {"ot": 10, "scrub": 5.2, "otchange": 5.2, "otlobby": 5.0, "opd2": 5.4,
            "recep": 5.6, "lounge": 6.4, "drrest": 6.4, "recovery": 7.6, "xray": 7.4, "suite": 8.6, "room1": 8, "room2": 8,
            "room3": 8, "room4": 8, "opd1": 7.6, "opd3": 7.6}
SMALL = {"autoclave", "otlobby", "recep", "scrub", "otchange", "otstore", "opd2", "bp", "pharm", "obs",
         "change", "ns", "store", "duty", "pantry"}


def _door_tag(w):
    for lim, tag in ((4.9, "D1"), (3.9, "D2"), (3.4, "D3"), (2.9, "D4"), (2.7, "D5")):
        if w >= lim:
            return tag
    return "D6"


DOOR_LEGEND = [("D1", "5'-0\" double, OT / recovery"), ("D2", "4'-0\" X-ray / emergency"),
               ("D3", "3'-6\" trolley door (ward rooms, scrub-OT)"),
               ("D4", "3'-0\" consult / toilet"), ("D5", "2'-9\" service"),
               ("D6", "2'-6\" and under")]


def _draw_door(ax, d, ink, z=8):
    import numpy as np
    w, s = d["w"], d["swing"]
    if d["axis"] == "h":
        lo, hi = (d["cx"] - w / 2, d["cy"]), (d["cx"] + w / 2, d["cy"])
        perp = (0.0, float(s))
    else:
        lo, hi = (d["cx"], d["cy"] - w / 2), (d["cx"], d["cy"] + w / 2)
        perp = (float(s), 0.0)
    kind = d["kind"]
    if kind == "open":
        ax.plot([lo[0], hi[0]], [lo[1], hi[1]], color="#888", lw=0.8, ls=(0, (2, 2)), zorder=z)
        return
    if kind == "hatch":
        ax.plot([lo[0], hi[0]], [lo[1], hi[1]], color=ink, lw=2.2, zorder=z,
                solid_capstyle="butt")
        return
    leaves = [(lo, hi, w)] if d["hinge"] == "lo" else [(hi, lo, w)]
    if kind == "double":
        mid = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
        leaves = [(lo, mid, w / 2), (hi, mid, w / 2)]
    for hinge, jamb, r in leaves:
        a0 = math.atan2(jamb[1] - hinge[1], jamb[0] - hinge[0])
        a1 = math.atan2(perp[1], perp[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        th = np.linspace(a0, a0 + da, 16)
        ax.plot(hinge[0] + r * np.cos(th), hinge[1] + r * np.sin(th), color=ink, lw=0.55, zorder=z)
        ax.plot([hinge[0], hinge[0] + perp[0] * r], [hinge[1], hinge[1] + perp[1] * r],
                color=ink, lw=1.1, zorder=z)


def _draw_furniture(ax, item, R):
    from matplotlib.patches import Rectangle, Circle
    kind, x, y, w, h, rot = item
    if kind == "wc" and rot == 180:          # tank on the low-y wall
        ax.add_patch(Rectangle((x, y), w, h * 0.5, fc="white", lw=0.5, ec="#4a4a4a", zorder=6))
        ax.add_patch(Circle((x + w / 2, y + h * 0.72), w * 0.4, fc="white", lw=0.5,
                            ec="#4a4a4a", zorder=6))
    elif kind == "sofa" and rot == 180:      # back on the low-y side
        ax.add_patch(Rectangle((x, y), w, h, fc="white", lw=0.55, ec="#4a4a4a", zorder=6))
        ax.plot([x + 0.25, x + w - 0.25], [y + 0.55, y + 0.55], color="#4a4a4a", lw=0.45, zorder=6)
    else:
        R._furniture(ax, item)


def render_sheet(out_base):
    """Dimensioned CAD sheet for Layout G (PNG + SVG).  South at the top."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, Polygon as MplPoly, FancyArrow
    from matplotlib.lines import Line2D
    import render as R
    from plan_model import ZONES

    INK = R.INK
    rooms = layout_g_rooms()
    walls = wall_bands_g(rooms)
    fig, ax = plt.subplots(figsize=(19.5, 26.2))
    ax.set_aspect("equal")

    # ---- context: lift / stair core and common passage (not part of the unit)
    grey = "#9a9a9a"
    for lf in LIFTS:
        x0, y0, x1, y1 = lf.bounds
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#f1f1f1", ec=grey, lw=0.8, zorder=1))
        ax.plot([x0, x1], [y0, y1], color=grey, lw=0.4, zorder=1)
        ax.plot([x0, x1], [y1, y0], color=grey, lw=0.4, zorder=1)
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, "LIFT", fontsize=6.5, color="#666", ha="center",
                va="center", zorder=2, bbox=dict(fc="#f1f1f1", ec="none", pad=0.6))
    x0, y0, x1, y1 = CORE_DUCT.bounds
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="white", ec=grey, lw=0.8, hatch="///",
                           zorder=1))
    ax.text(-5.5, 38.76, "DUCT", fontsize=5.5, color="#666", ha="center", va="center",
            bbox=dict(fc="white", ec="none", pad=0.4), zorder=2)
    for yy in (40.09, 48.10):
        ax.plot([-10.4, 0], [yy, yy], color=grey, lw=1.4, zorder=1)
    ax.text(-5.4, 41.6, "COMMON PASSAGE 8'-0\"\nto lift lobby + 2 stairs", fontsize=6.3,
            color="#555", ha="center", va="center", style="italic")
    ax.text(-5.0, 4.2, "refuge area /\nlift lobby beyond", fontsize=6, color="#777", ha="center",
            va="center", style="italic")
    ax.text(-5.0, 52.5, "unit x04\n(not in scope)", fontsize=6, color="#777", ha="center",
            va="center", style="italic")

    # ---- floor, service ledge, cut-out
    R._fill(ax, INNER, 1, fc=R.CORRIDOR, ec="none")
    ax.add_patch(Rectangle((0.33, -1.97), 47.65, 1.97, fc="white", ec=INK, lw=0.7, hatch="xxx",
                           zorder=1))
    ax.text(24, -0.98, "SERVICE LEDGE (parapet)", ha="center", va="center", fontsize=6.5,
            color=INK, bbox=dict(fc="white", ec="none", pad=0.5))
    R._fill(ax, CUTOUT_G, 2, fc="white", ec="none", hatch="///", lw=0)
    c = CUTOUT_G.centroid
    ax.text(c.x, c.y, "CUT-OUT (void)\n17'-3\" x 8'-0\"", ha="center", va="center", fontsize=8,
            color=INK, zorder=4, bbox=dict(fc="white", ec="none", pad=1.5))

    # ---- rooms
    for r in rooms:
        if r.zone == "circ":
            continue
        p = r.poly
        R._fill(ax, p, 2, fc=R._tint(ZONES[r.zone][0], 0.38), ec="none")
        for g in R._iter_polys(p):
            if r.zone == "wet":
                R._tile_hatch(ax, g, 3)
            elif g.area > 30:
                R._tile_hatch2(ax, g, 2.5)

    # ---- existing builder items: sunk toilet slabs (dashed blue), walls removed (dashed red)
    for name, b in EXIST_SUNK + [("ex. duct", EXIST_DUCT)]:
        x0, y0, x1, y1 = b.bounds
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec="#1f77b4", lw=0.9,
                               ls=(0, (4, 2)), zorder=6.5))
    for (xa, ya), (xb, yb) in EXIST_WALLS_REMOVED:
        ax.plot([xa, xb], [ya, yb], color="#c0392b", lw=0.7, ls=(0, (5, 3)), alpha=0.75,
                zorder=6.6)

    # ---- lines of the 3rd sketch that are not built as walls (see the brief)
    ax.plot([20.28, 20.28], [40.25, 47.95], color="#3b4cc0", lw=0.8, ls=(0, (3, 3)), zorder=6.6)
    ax.plot([0.5, 8.3], [34.6, 34.6], color="#3b4cc0", lw=0.8, ls=(0, (3, 3)), zorder=6.6)
    ax.text(2.6, 34.95, "screen (as sketched)", fontsize=4.6, color="#3b4cc0",
            ha="center", va="center", zorder=9)

    # ---- walls + columns
    R._fill(ax, walls, 7, fc=INK, ec="none")
    for name, col in COLUMNS.items():
        cc = col.intersection(OUTER)
        R._fill(ax, cc, 7.5, fc="#8c2f1b", ec="black", lw=0.6)

    # ---- furniture + doors
    for r in rooms:
        for f in r.furniture:
            _draw_furniture(ax, f, R)
        for d in r.gdoors:
            _draw_door(ax, d, INK)
            if d["kind"] in ("single", "double"):
                off = 0.95
                tx, ty = d["cx"], d["cy"]
                if d["axis"] == "h":
                    ty -= d["swing"] * off
                else:
                    tx -= d["swing"] * off
                ax.text(tx, ty, _door_tag(d["w"]), fontsize=4.6, color="#a33", zorder=11,
                        ha="center", va="center",
                        bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.85))

    # ---- labels
    for r in rooms:
        p = r.poly
        if p.is_empty or not r.name:
            continue
        cpt = p.representative_point()
        lx, ly = r.label if r.label else (cpt.x, cpt.y)
        if r.zone == "circ":
            x0, y0, w0, h0 = r.rect
            rot = 90 if h0 > w0 * 1.4 else 0
            ax.text(x0 + w0 / 2, y0 + h0 / 2, r.name, ha="center", va="center",
                    fontsize=5.6 if r.key == "bay" else 7.6,
                    color="#444", style="italic", weight="bold", zorder=9, rotation=rot)
            continue
        if r.key == "duct":
            ax.text(lx + 0.5, ly + 0.3, "DUCT", fontsize=5, ha="center", va="center", zorder=9)
            continue
        if r.zone == "wet":
            ax.add_patch(Circle((lx, ly), 0.85, fc="white", ec=INK, lw=0.7, zorder=10))
            ax.text(lx, ly, "T", ha="center", va="center", fontsize=6.5, weight="bold",
                    color=INK, zorder=11)
            if "Acc" in r.name or "existing" in r.name or r.key == "bath5":
                tag = ("Acc." if "Acc" in r.name else
                       "Patient WC (existing)" if "existing" in r.name else "Suite bath")
                ax.text(lx - (2.2 if "existing" in r.name else 0),
                        ly + (-1.9 if "existing" in r.name else 1.45), tag, ha="center", va="center", fontsize=5.2, color=INK,
                        zorder=11, bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.8))
            continue
        fs = LABEL_FS.get(r.key, 6.2 if r.key in SMALL else 7.4)
        txt = f"{r.name}\n{r.dims.split(' incl')[0]}\n{r.area:.0f} sf"
        if r.key == "obs":
            txt, fs = f"Obs. Bed {r.dims} · {r.area:.0f} sf", 5.2
        rot = 90 if r.key in ("scrub", "otchange", "opd2") else 0
        if r.key in ("otchange", "opd2"):
            txt = f"{r.name} {r.dims} · {r.area:.0f} sf"
        elif r.key in ("scrub", "otlobby"):
            txt, rot = f"{r.name}\n{r.area:.0f} sf", 0
        elif r.key == "recep":
            txt = f"{r.name}\n{r.dims}"
        ax.text(lx, ly, txt, ha="center", va="center", fontsize=fs, color="#111",
                weight="bold" if r.name.isupper() else "normal", zorder=9, linespacing=1.25,
                rotation=rot, bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.72))

    # ---- glass
    for (xa, ya), (xb, yb) in GLASS_WEST_G + GLASS_NORTH_G:
        dx, dy = xb - xa, yb - ya
        n = math.hypot(dx, dy)
        ox, oy = dy / n * 0.55, -dx / n * 0.55
        ax.plot([xa + ox, xb + ox], [ya + oy, yb + oy], color="#2c6fbb", lw=1.8, zorder=5)
        ax.plot([xa + ox * 1.9, xb + ox * 1.9], [ya + oy * 1.9, yb + oy * 1.9], color="#2c6fbb",
                lw=0.6, zorder=5)
    ax.text(46.6, 26, "OPENABLE GLASS", rotation=-81.8, fontsize=7.5, color="#2c6fbb",
            ha="center", va="center")
    ax.text(39.8, 70, "OPENABLE GLASS", rotation=-81.8, fontsize=7.5, color="#2c6fbb",
            ha="center", va="center")
    ax.text(15, 93.8, "OPENABLE GLASS", fontsize=7.5, color="#2c6fbb", ha="center", va="center")

    # ---- main door
    _, y1, y2 = MD_DOOR_G
    _draw_door(ax, D(0.2, (y1 + y2) / 2, 5.0, "v", 1, kind="double"), INK)
    ax.annotate("MAIN ENTRY\n5'-0\" double door", xy=(-0.4, 45.5), xytext=(-6.2, 46.2),
                fontsize=7, weight="bold", ha="center", va="center", color=INK,
                arrowprops=dict(arrowstyle="->", lw=1.0, color=INK))

    # ---- column grid
    for name, gx in GRID_X.items():
        ax.plot([gx, gx], [-7.2, 95.5], color="#b04a2f", lw=0.5, ls=(0, (10, 3, 2, 3)), zorder=4)
        ax.add_patch(Circle((gx, -8.2), 1.0, fc="white", ec="#b04a2f", lw=0.9, zorder=12))
        ax.text(gx, -8.2, name, ha="center", va="center", fontsize=8, color="#b04a2f",
                weight="bold", zorder=13)
    for name, gy in GRID_Y.items():
        ax.plot([-11.2, 50.5], [gy, gy], color="#b04a2f", lw=0.5, ls=(0, (10, 3, 2, 3)), zorder=4)
        ax.add_patch(Circle((51.5, gy), 1.0, fc="white", ec="#b04a2f", lw=0.9, zorder=12))
        ax.text(51.5, gy, name, ha="center", va="center", fontsize=8, color="#b04a2f",
                weight="bold", zorder=13)

    # ---- dimension chains (clear, wall face to wall face)
    def tick(x, y):
        ax.plot([x - 0.35, x + 0.35], [y + 0.35, y - 0.35], color=INK, lw=0.8, zorder=12)

    def chain_h(xs, y, labels, fs=6.3):
        ax.plot([xs[0], xs[-1]], [y, y], color=INK, lw=0.6, zorder=12)
        for x in xs:
            tick(x, y)
            ax.plot([x, x], [y - 0.5, y + 0.9], color=INK, lw=0.35, zorder=12)
        for (xa, xb), lab in zip(zip(xs[:-1], xs[1:]), labels):
            if lab:
                ax.text((xa + xb) / 2, y - 0.75, lab, ha="center", va="center", fontsize=fs,
                        color=INK, zorder=12)

    def chain_v(ys, x, labels, fs=6.3, side=-1):
        ax.plot([x, x], [ys[0], ys[-1]], color=INK, lw=0.6, zorder=12)
        for y in ys:
            tick(x, y)
            ax.plot([x - 0.5, x + 0.5], [y, y], color=INK, lw=0.35, zorder=12)
        for (ya, yb), lab in zip(zip(ys[:-1], ys[1:]), labels):
            if lab:
                ax.text(x + side * 0.8, (ya + yb) / 2, lab, ha="center", va="center", fontsize=fs,
                        color=INK, rotation=90, zorder=12)

    chain_h([E0, 22.87, 23.245, 26.87, 27.245, 32.245, 32.62, 38.0, 38.375, xw(S0)], -3.6,
            ["22'-6\"", "", "3'-7½\"", "", "5'-0\"", "", "5'-5\"", "", fi(xw(S0) - 38.375)])
    chain_h([0.0, 47.98], -5.9, ["47'-11¾\" over walls (Rev C: 48'-6\" to glass line)"], fs=7)
    ys = [S0, 19.82, 20.21, 30.6, 30.975, 39.76, 40.09, 48.10, 48.49, 55.2, 55.575, 59.2,
          59.575, 66.0, 66.375, 73.0, 73.375, 78.8, 79.175, N0]
    chain_v(ys, -12.2, [fi(b - a) if b - a > 1 else "" for a, b in zip(ys[:-1], ys[1:])])
    chain_v([0.0, 92.22], -14.6, ["92'-2¾\" over walls (Rev C: 92'-0\")"], fs=7)
    wys = [48.49, 58.9, 59.275, 69.7, 70.075, 80.3, 80.675, N0]
    chain_v(wys, 45.4, [fi(b - a) if b - a > 1 else "" for a, b in zip(wys[:-1], wys[1:])],
            side=1)
    sys_ = [S0, 10.1, 10.475, 19.82, 20.21, 30.1]
    chain_v(sys_, 49.4, [fi(b - a) if b - a > 1 else "" for a, b in zip(sys_[:-1], sys_[1:])],
            side=1)
    # passage-width callouts
    for (xa, xb, y, lab) in [(14.28, 20.28, 73.6, "6'-0\""), (27.245, 32.245, 24.6, "5'-0\"")]:
        ax.annotate("", xy=(xb, y), xytext=(xa, y),
                    arrowprops=dict(arrowstyle="<->", lw=0.8, color="#a33"), zorder=12)
        ax.text((xa + xb) / 2, y - 0.6, lab, ha="center", va="center", fontsize=6.5,
                color="#a33", zorder=12)
    ax.annotate("", xy=(3.0, 48.10), xytext=(3.0, 40.09),
                arrowprops=dict(arrowstyle="<->", lw=0.8, color="#a33"), zorder=12)
    ax.text(2.3, 42.0, "8'-0\"", ha="center", va="center", fontsize=6.5, color="#a33",
            rotation=90, zorder=12)

    # ---- flow arrows
    for (xa, ya, xb, yb) in [(2.0, 45.5, 12.5, 45.5), (17.3, 47.0, 17.3, 52.5),
                             (17.4, 41.5, 17.4, 37.0), (21.0, 33.9, 26.6, 33.9),
                             (29.7, 32.6, 29.7, 28.0), (17.6, 33.4, 17.6, 31.3)]:
        ax.annotate("", xy=(xb, yb), xytext=(xa, ya),
                    arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#3a7d44"), zorder=9)

    # ---- compass, north arrow, title
    for x, y, s in [(24, -11.0, "SOUTH SIDE"), (20, 97.2, "NORTH SIDE")]:
        ax.text(x, y, s, ha="center", va="center", fontsize=10, weight="bold",
                bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(-17.2, 64, "EAST SIDE (lift / stair core)", rotation=90, ha="center", va="center",
            fontsize=10, weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(55.0, 44, "WEST SIDE", rotation=-90, ha="center", va="center", fontsize=10,
            weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.add_patch(FancyArrow(55.0, 86.5, 0, 4.2, width=0.5, head_width=1.8, head_length=1.6,
                            fc=INK, ec=INK))
    ax.text(55.0, 85.0, "N", ha="center", fontsize=12, weight="bold", color=INK)

    clear = INNER.area - CUTOUT_G.intersection(INNER).area
    ax.set_title("LAYOUT G — clients' blue-pen sketch on the builder's DWG geometry\n"
                 "Hospital of Dr. Aman Khanna & Dr. Heena — 7th Floor, Solaris Shine, Althan, Surat\n"
                 f"Clear floor ≈ {clear:,.0f} sq ft inside walls  ·  ward passage 6'-0\"  ·  "
                 "OPD passage 5'-0\"  ·  entry passage 8'-0\"", fontsize=12, pad=14)

    # ---- legend, keynotes
    handles = [Line2D([], [], marker="s", ls="", ms=10, mfc=R._tint(colr, 0.38), mec="#999",
                      label=lbl) for colr, lbl in ZONES.values() if lbl != "Circulation"]
    handles += [Line2D([], [], marker="s", ls="", ms=10, mfc=INK, mec=INK, label="Walls (4½\" partitions)"),
                Line2D([], [], marker="s", ls="", ms=10, mfc="#8c2f1b", mec="black",
                       label="RCC column (from DWG)"),
                Line2D([], [], color="#2c6fbb", lw=2.0, label="Openable glass facade"),
                Line2D([], [], color="#1f77b4", lw=1, ls=(0, (4, 2)),
                       label="Builder's toilet slab / duct (existing)"),
                Line2D([], [], color="#c0392b", lw=1, ls=(0, (5, 3)),
                       label="Existing 100 mm wall removed"),
                Line2D([], [], color="#b04a2f", lw=0.8, ls=(0, (10, 3, 2, 3)),
                       label="Column grid line"),
                Line2D([], [], color="#3b4cc0", lw=0.8, ls=(0, (3, 3)),
                       label="3rd-sketch line not built as a wall")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(-19, 105.6),
              bbox_transform=ax.transData, ncol=4, fontsize=7.6, frameon=False)
    notes = ("NOTES\n"
             "1. Geometry: builder DWG (typical 5th/7th/10th floor), units x05+x06+x07 + dead-end passage. "
             "Dimensions are clear, between finished wall faces.\n"
             "2. South block = clients' 3rd sketch (over the DWG print): OT 22'-6\" x 19'-5\", x07|x06 party wall kept; OPD passage widened from ≈3'-3\" as drawn to 5'-0\".  "
             "3. Trolley doors 3'-6\" (D3); OT / recovery doors 5'-0\" double (D1).\n"
             "4. X-ray room ≈ 11 m²: mobile / portable unit only (AERB fixed unit needs ≈ 18 m², no side < 4 m).  "
             "5. New ward toilets are away from the builder's shafts: raised floor + drain runs to be designed.\n"
             "6. (T) toilet — tiled, floor trap.  Bed heads on solid walls.  Concept for review; "
             "structure, fire and AERB to be verified by the project architect.")
    ax.text(-18, 112.6, notes, fontsize=6.6, color=INK, va="top", linespacing=1.5)
    ax.text(-18, 104.0, "DOORS  " + "   ".join(f"{t} = {d}" for t, d in DOOR_LEGEND), fontsize=6.2,
            color="#a33", va="top")

    # ---- scale bar
    ax.plot([0, 20], [100.5, 100.5], lw=3, color=INK)
    for i in range(0, 21, 5):
        ax.plot([i, i], [99.9, 101.1], lw=1.2, color=INK)
        ax.text(i, 102.5, f"{i}'", ha="center", fontsize=7, color=INK)

    # ---- room schedule (right margin)
    sched = [(r.name, r.dims, r.area) for r in rooms if r.zone != "circ" and r.key != "duct"]
    lines = ["ROOM SCHEDULE (clear sizes)", "─" * 46]
    n = 0
    for name, dims, area in sched:
        n += 1
        nm = name.replace("X-RAY / DRESSING / EMERGENCY", "X-RAY / DRESSING / EMERG.")
        nm = (nm[:24] + "…") if len(nm) > 25 else nm
        dm = dims.split(" + ")[0].split(" incl")[0].replace(" (L)", "")
        lines.append(f"{n:>2} {nm:<25s} {dm:<19s}{area:>4.0f}")
    lines += ["─" * 46, f"   rooms total {sum(a for _, _, a in sched):>29.0f} sf",
              f"   clear floor inside walls {clear:>16.0f} sf",
              "", "BEDS  5 in-patient (4 rooms + suite)",
              "      2 recovery / pre-op, 1 observation", "      2 staff rest (duty bunk, Drs' rest)"]
    ax.text(57.0, -6, "\n".join(lines), fontsize=6.6, color=INK, va="top", family="monospace",
            linespacing=1.42)

    # ---- title block
    tb0, tb1 = 120.5, 127.5
    ax.add_patch(Rectangle((-18, tb0), 102, tb1 - tb0, fc="white", ec=INK, lw=1.2, zorder=3))
    for fx in (16, 46, 66):
        ax.plot([fx, fx], [tb0, tb1], color=INK, lw=0.8, zorder=4)
    for x, head, body in [(-16.5, "PROJECT", "Hospital of Dr. Aman Khanna & Dr. Heena\n"
                                             "7th Floor, Solaris Shine, Althan, Surat"),
                          (17.5, "DRAWING", "LAYOUT G — blue-pen sketch on DWG geometry\n"
                                            "Dimensioned layout plan, feet-inches"),
                          (47.5, "SCALE / DATE", f"N.T.S. (use the scale bar)\n{DATE}"),
                          (67.5, "STATUS", "Concept for review — to be verified\n"
                                           "by the project architect")]:
        ax.text(x, tb0 + 1.5, head, fontsize=6, color="#777", zorder=5)
        ax.text(x, tb0 + 4.6, body, fontsize=7.5, color=INK, va="center", zorder=5)

    ax.set_xlim(-20, 86)
    ax.set_ylim(129, -13.5)
    ax.axis("off")
    fig.savefig(out_base + ".png", dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return clear


def dxf_extras(doc, msp):
    """Extra DXF layers for Layout G: columns, column grid, real inner wall
    face, lift core and the builder's toilet slabs."""
    for name, color in (("COLUMNS", 1), ("GRID", 30), ("INNER_FACE", 3), ("CORE", 8),
                        ("EXISTING", 5)):
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    for col in COLUMNS.values():
        cc = col.intersection(OUTER)
        msp.add_lwpolyline(list(cc.exterior.coords), close=True, dxfattribs={"layer": "COLUMNS"})
    msp.add_lwpolyline(list(INNER.exterior.coords), close=True, dxfattribs={"layer": "INNER_FACE"})
    for gx in GRID_X.values():
        msp.add_line((gx, -6), (gx, 96), dxfattribs={"layer": "GRID"})
    for gy in GRID_Y.values():
        msp.add_line((-11, gy), (51, gy), dxfattribs={"layer": "GRID"})
    for b in LIFTS + [CORE_DUCT]:
        msp.add_lwpolyline(list(b.exterior.coords), close=True, dxfattribs={"layer": "CORE"})
    for _, b in EXIST_SUNK + [("duct", EXIST_DUCT)]:
        msp.add_lwpolyline(list(b.exterior.coords), close=True, dxfattribs={"layer": "EXISTING"})


if __name__ == "__main__":
    import json
    import plan_model  # noqa: F401  (registers the layout)
    print(json.dumps(checks(), indent=1, default=str))
