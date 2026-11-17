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

# ---- OT suite set-out (feet).  See deliverables/OT_G_BRIEF.md
OT_W = OT_D = 20.0           # OT clear, masonry face to masonry face
OT_N = S0 + OT_D             # north face of the OT (party wall rebuilt 7" north)
OT_WF = E0 + OT_W            # west face of the OT (on the grid-B column line)
PW_C = OT_N + 0.19           # centre line of the rebuilt party wall
OTW_C = OT_WF + 0.19         # centre line of the OT west wall
BAND0 = OT_WF + 0.375        # east face of the staff / clean band
BAND_W = 26.87 - BAND0       # 6'-1" clear (was 3'-7 1/2" as sketched)
ROWA0 = OT_N + 0.375         # south face of the row north of the OT
ROWA1 = ROWA0 + 10.0         # north face of that row


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
    ((4.33, 20.02), (32.25, 20.02)),                                     # x07 | x06 party wall (rebuilt 7" north)
    ((8.50, 20.3), (8.50, 35.83)),                                       # x06 east wall
    ((13.1, 39.92), (20.28, 39.92)),                                     # x06 north wall (lobby mouth)
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
    kind: single | double | slide (double sliding, hermetic) | open (cased
    opening / curtain) | hatch (counter / pass box)."""
    return dict(cx=cx, cy=cy, w=w, axis=axis, swing=swing, hinge=hinge, kind=kind)


_LEAF = ("single", "double", "slide")      # kinds that are real door leaves


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
          doors=[_legacy_door(d) for d in doors if d["kind"] in _LEAF],
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


def _ward_wc(key, x, y, door, fixtures, label):
    """Ward ensuite at the glass: 5'-0" deep (N-S), at least 6'-0" clear E-W,
    WC + basin + shower, 2'-9" door opening outward into the room."""
    return _mk(key, "Toilet", (x, y, 9.0, 5.0), "wet", doors=[door], label=label,
               furniture=list(fixtures))


def _bed(x, y, head):          # 3'-3" x 7'-0" bed; head on the 'N' or 'S' wall
    return ("bed", x, y, 3.25, 7.0, 180 if head == "S" else 0)


def _lk(x, y):                 # bedside locker 1'-6" x 1'-6"
    return ("side", x, y, 1.5, 1.5, 0)


def layout_g_rooms():
    """North (IPD) block: the blue-pen sketch (same as Layout F) on the DWG
    outline and column grid.  South block: the clients' 3rd sketch, drawn in
    blue pen over the DWG print, which takes precedence there."""
    wait = ([("chair", 33.2 + 1.8 * i, 30.9, 1.4, 1.4, 0) for i in range(5)]
            + [("chair", 31.3 + 1.8 * i, 34.0, 1.4, 1.4, 0) for i in range(6)]
            + [("chair", 28.2 + 1.8 * i, 38.2, 1.4, 1.4, 0) for i in range(3)]
            + [("chair", 28.2 + 1.8 * i, 36.4, 1.4, 1.4, 0) for i in range(2)]
            + [("chair", 21.6 + 1.8 * i, 31.35, 1.4, 1.4, 0) for i in range(3)])
    rooms = [
        # ---------- SOUTH BLOCK: zoning of the 3rd sketch (blue pen over the DWG print),
        # reworked 17-11-2026 as a modular-OT suite (see deliverables/OT_G_BRIEF.md).
        # OT = 20'-0" x 20'-0" clear: west wall on the grid-B column line (2'-6" east of
        # the sketched line), north wall = the x07 | x06 party wall rebuilt 7" north.
        _mk("ot", "OPERATION THEATRE", (E0, S0, OT_W, OT_D), "surgical",
            furniture=[("ottable", 9.39, 7.0, 2.0, 6.75, 0),
                       ("counter", 5.0, S0 + 0.02, 12.0, 1.33, 0),
                       ("cart", 5.9, 7.6, 1.5, 3.0, 0), ("cart", 5.9, 11.0, 1.5, 3.0, 0)],
            dims="20'-0\" x 20'-0\"", label=(6.0, 17.75),
            notes="Patient in/out through Recovery (5'-0\" sliding door); staff through Scrub; "
                  "soiled out through Dirty utility"),
        _mk("otstore", "Anaes. / consumable store", (E0, ROWA0, 4.61, 10.0), "support",
            doors=[D(2.7, PW_C, 3.0, "h", 1)],
            furniture=[("shelf", 0.6, 24.4, 1.2, 6.2, 0), ("shelf", 3.7, 21.0, 1.2, 9.6, 0)],
            label=(2.55, 22.6),
            notes="Strip behind the lifts; opens to the OT only (builder's x07 door position)"),
        _mk("recovery", "PRE-OP / RECOVERY", (5.375, ROWA0, 12.125, 10.0), "surgical",
            doors=[D(14.9, PW_C, 5.0, "h", -1, kind="slide"),
                   D(15.3, ROWA1 + 0.19, 4.0, "h", -1, kind="double")],
            furniture=[("bed", 5.6, 21.55, 6.8, 3.2, 180), ("bed", 5.6, 26.8, 6.8, 3.2, 180),
                       ("counter", 16.35, 23.3, 1.1, 3.6, 0)],
            label=(10.3, 25.75),
            notes="Bay 1 = pre-op / holding + patient change (curtained); bay 2 = recovery"),
        _mk("opd2", "OPD 2 · Plaster / procedure", (17.875, ROWA0, 8.995, 10.0), "consult",
            doors=[D(27.06, 28.6, 3.5, "v", -1)],
            furniture=[("exam", 18.1, 23.6, 2.25, 6.0, 0), ("cart", 18.2, 21.1, 1.6, 2.0, 0),
                       ("counter", 23.1, 20.95, 3.6, 1.4, 0), ("sink", 25.3, 21.05, 1.2, 1.1, 0),
                       ("desk", 23.7, 23.6, 3.0, 1.7, 0), ("chair", 24.5, 25.5, 1.3, 1.3, 0)],
            dims="9'-0\" x 10'-0\"", label=(22.4, 27.6),
            notes="9'-0\" x 10'-0\"; grid-B column C3 stands 1'-8\" proud on its south wall"),
        _mk("xray", "X-RAY / DRESSING / EMERGENCY", (E0, ROWA1 + 0.375, 12.335, 39.76 - ROWA1 - 0.375),
            "consult",
            doors=[D(12.91, 36.9, 4.0, "v", -1)],
            furniture=[("exam", 2.0, 36.9, 6.4, 2.5, 0), ("counter", 4.6, 31.4, 6.0, 1.4, 0),
                       ("cart", 1.0, 31.5, 1.6, 2.2, 0)],
            label=(6.6, 34.6),
            notes="Lead-lined; mobile / portable X-ray only at this size"),
        # staff / clean band between the OT and the OPD passage, 6'-1" clear
        _mk("cssdC", "CSSD clean + sterile store", (BAND0, S0, BAND_W, 5.11), "surgical",
            doors=[D(OTW_C, 3.4, 2.0, "v", -1, kind="hatch"),
                   D(23.3, 5.69, 2.75, "h", -1, hinge="hi")],
            furniture=[("shelf", 23.0, 0.5, 2.8, 1.1, 0)],
            dims="6'-1\" x 5'-1\"", label=(23.2, 3.45)),
        _mk("cssdD", "CSSD wash (dirty)", (27.245, S0, 5.0, 5.11), "surgical",
            doors=[D(30.7, 5.69, 2.75, "h", -1, hinge="hi")],
            furniture=[("counter", 28.3, 0.6, 3.8, 1.5, 0), ("sink", 28.7, 0.75, 1.2, 1.1, 0),
                       ("sink", 30.4, 0.75, 1.2, 1.1, 0)],
            label=(30.2, 3.6)),
        _mk("scrub", "SCRUB", (BAND0, 5.875, BAND_W, 8.0), "surgical",
            doors=[D(OTW_C, 11.6, 3.5, "v", -1),
                   D(27.06, 7.5, 3.0, "v", -1)],
            furniture=[("counter", 25.27, 9.3, 1.6, 4.4, 0), ("sink", 25.45, 9.5, 1.2, 1.1, 0),
                       ("sink", 25.45, 10.95, 1.2, 1.1, 0), ("sink", 25.45, 12.4, 1.2, 1.1, 0),
                       ("shelf", 20.9, 6.3, 1.0, 3.0, 0)],
            label=(23.1, 13.25),
            notes="3-tap scrub trough outside the OT staff door; doubles as the clean lobby"),
        _mk("du", "Dirty utility", (BAND0, 14.25, BAND_W, OT_N - 14.25), "support",
            doors=[D(OTW_C, 16.3, 3.0, "v", 1, hinge="hi"),
                   D(27.06, 15.9, 3.0, "v", -1)],
            furniture=[("sink", 21.0, 18.45, 1.3, 1.2, 0), ("counter", 22.95, 18.3, 2.0, 1.5, 0),
                       ("cart", 25.3, 18.3, 1.4, 1.5, 0)],
            dims="6'-1\" x 6'-2\"", label=(23.7, 17.8),
            notes="Soiled exit to the OPD passage, separate from the clean route"),
        _mk("stlobby", "Staff lobby (air-lock)", (27.245, 5.875, 5.0, 4.225), "surgical",
            doors=[D(29.745, 10.29, 3.5, "h", -1)], label=(29.75, 6.5),
            notes="Door across the passage: the south end is staff-only"),
        # west rooms off the OPD passage
        _mk("lounge", "DRS' LOUNGE", (32.62, S0, 5.38, 9.71), "consult",
            doors=[D(32.43, 7.9, 2.75, "v", 1)],
            furniture=[("sofa", 32.9, 0.6, 4.8, 2.2, 180), ("chair", 36.2, 8.2, 1.4, 1.4, 0)],
            label=(35.3, 5.0)),
        _mk("wcLg", "Toilet", (41.5, S0, 7.0, 4.2), "wet",
            doors=[D(42.9, 4.78, 2.25, "h", 1)],
            furniture=[("wc", 43.6, 0.6, 1.5, 2.0, 180), ("sink", 41.8, 0.6, 1.3, 1.2, 0)],
            label=(42.6, 3.3)),
        _mk("stchange", "OT staff change M/F + WC", (38.375, S0, 10.0, 9.71), "surgical",
            holes=[(41.125, S0, 8.0, 4.575)],
            doors=[D(38.19, 7.9, 2.5, "v", 1)],
            furniture=[("shelf", 38.55, 0.6, 1.1, 4.4, 0), ("shelf", 41.7, 8.85, 4.0, 1.05, 0),
                       ("side", 42.3, 5.3, 2.6, 1.1, 0)],
            dims="≈8'-1\" x 9'-9\" incl. WC", label=(42.6, 7.2),
            notes="Two curtained cubicles + two locker banks; reached through the lounge"),
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
        _mk("store", "Store", (E0, 66.375, 5.01, 6.05), "support",
            doors=[D(3.9, 66.19, 2.5, "h", 1)],
            furniture=[("shelf", 2.5, 71.3, 2.8, 1.0, 0), ("shelf", 4.2, 68.6, 1.0, 2.5, 0)],
            label=(2.7, 67.7)),
        _mk("duty", "Duty Dr / Staff Rest", (5.775, 66.375, 8.13, 6.05), "support",
            doors=[D(14.09, 68.4, 2.75, "v", -1)],
            furniture=[("bed", 6.0, 69.55, 6.5, 2.7, 180), ("shelf", 6.0, 66.6, 3.6, 1.0, 0)],
            label=(8.9, 68.5),
            notes="Bunk (2 berths)"),
        # wheelchair-size bath 7'-0" x 6'-0" (5'-0" turning circle), 3'-0" door
        _mk("bath5", "Suite Bath (Acc.)", (E0, 72.8, 7.0, 6.0), "wet",
            doors=[D(3.4, 78.99, 3.0, "h", 1)],
            furniture=[("shower", 0.55, 72.95, 2.5, 2.5, 0), ("sink", 3.6, 72.95, 1.3, 1.2, 0),
                       ("wc", 5.5, 72.95, 1.6, 2.2, 180)], label=(2.0, 76.4)),
        _mk("pantry", "Pantry", (7.765, 72.8, 6.14, 6.0), "support",
            doors=[D(14.09, 76.6, 2.75, "v", -1)],
            furniture=[("counter", 7.95, 73.0, 5.7, 1.5, 0), ("cart", 7.95, 76.4, 1.8, 2.0, 0)],
            label=(11.3, 76.3)),
        # --------------------------- wards on the west glass, toilets paired at the glass
        # Single rooms, true-size furniture.  The paired ensuites stay at the glass
        # (clients' sketch) but are 5'-0" deep instead of 5'-5" x 9'-0" long, and sit
        # on the bed-head side, so the foot side of every room runs clear to the window.
        _mk("room1", "ROOM 1", (20.655, 48.49, 22.0, 10.41), "inpatient",
            holes=[(31.925, 53.525, 10.5, 5.6)],
            doors=[D(20.47, 56.4, 3.5, "v", 1)],
            furniture=[_bed(27.0, 51.8, "N"), _lk(30.25, 57.3),
                       ("wardrobe", 22.5, 48.6, 4.0, 2.0, 0),
                       ("sofa", 33.5, 48.6, 5.5, 2.0, 180)]),
        _ward_wc("wcR1", 32.3, 53.9, D(33.9, 53.71, 2.75, "h", -1),
                 [("sink", 32.5, 57.6, 1.3, 1.2, 0), ("wc", 34.3, 56.6, 1.6, 2.2, 0),
                  ("shower", 36.4, 56.3, 2.5, 2.5, 0)], (35.3, 55.3)),
        _mk("room2", "ROOM 2", (20.655, 59.275, 22.0, 10.425), "inpatient",
            holes=[(31.925, 59.2, 10.5, 5.45)],
            doors=[D(20.47, 61.8, 3.5, "v", 1, hinge="hi")],
            furniture=[_bed(26.0, 59.375, "S"), _lk(29.25, 59.375),
                       ("wardrobe", 20.75, 67.6, 4.0, 2.0, 0),
                       ("sofa", 30.1, 67.6, 5.5, 2.0, 0)]),
        _ward_wc("wcR2", 32.3, 59.275, D(33.9, 64.46, 2.75, "h", 1),
                 [("sink", 32.5, 59.4, 1.3, 1.2, 0), ("wc", 34.3, 59.4, 1.6, 2.2, 180),
                  ("shower", 36.0, 59.4, 2.5, 2.5, 0)], (35.3, 62.9)),
        _mk("room3", "ROOM 3", (20.655, 70.075, 20.0, 10.225), "inpatient",
            holes=[(28.525, 74.925, 10.5, 5.6)],
            doors=[D(20.47, 72.2, 3.5, "v", 1)],
            furniture=[_bed(25.0, 73.2, "N"), _lk(23.5, 78.7),
                       ("wardrobe", 20.75, 76.2, 2.0, 4.0, 0),
                       ("sofa", 30.1, 70.2, 5.5, 2.0, 180)]),
        _ward_wc("wcR3", 28.9, 75.3, D(30.5, 75.11, 2.75, "h", -1),
                 [("sink", 29.1, 79.0, 1.3, 1.2, 0), ("wc", 30.9, 78.0, 1.6, 2.2, 0),
                  ("shower", 32.3, 75.5, 2.5, 2.5, 0)], (31.9, 76.6)),
        # Room 4 is 14'-6" wide: 5'-0" attendant couch and a 2'-6" wardrobe only
        _mk("room4", "ROOM 4", (20.655, 80.675, 20.0, 11.155), "inpatient",
            holes=[(28.525, 80.6, 10.5, 5.45)],
            doors=[D(20.47, 82.7, 3.5, "v", 1, hinge="hi")],
            furniture=[_bed(25.0, 80.775, "S"), _lk(23.5, 80.775),
                       ("sofa", 20.75, 84.6, 2.0, 5.0, 270),
                       ("wardrobe", 23.5, 89.73, 2.5, 2.0, 0)]),
        _ward_wc("wcR4", 28.9, 80.675, D(30.5, 85.86, 2.75, "h", 1),
                 [("sink", 29.1, 80.8, 1.3, 1.2, 0), ("wc", 30.9, 80.8, 1.6, 2.2, 180),
                  ("shower", 32.6, 80.8, 2.5, 2.5, 0)], (31.9, 84.3)),
        _mk("suite", "SUITE ROOM 5", (E0, 79.175, 19.89, 12.655), "inpatient",
            holes=[(13.905, 79.175, 6.5, 5.8)],
            doors=[D(17.28, 84.79, 3.5, "h", 1)],
            furniture=[_bed(7.0, 79.275, "S"), _lk(5.5, 79.275), _lk(10.25, 79.275),
                       ("wardrobe", 0.5, 83.2, 2.0, 4.0, 0), ("sofa", 6.4, 89.73, 5.5, 2.0, 0),
                       ("chair", 13.6, 89.9, 1.8, 1.8, 0), ("chair", 16.0, 89.9, 1.8, 1.8, 0),
                       ("desk", 2.4, 89.9, 3.0, 1.8, 0)],
            notes="Private wheelchair-size bath entered from the suite; sit-out on the north glass"),
        # ------------------------------------------- open-plan / circulation anchors
        _mk("wait", "WAITING AREA (19 seats)", (30.4, 32.45, 11.0, 1.4), "circ",
            furniture=wait + [("water", 28.0, 31.0, 1.2, 1.2, 0),
                              ("plant", 41.2, 33.6, 1.3, 1.3, 0)]),
        _mk("lobby2", "LOBBY", (13.3, 32.6, 6.8, 5.6), "circ"),
        _mk("opdlobby", "OPD PASSAGE 5'-0\"", (27.245, 17.6, 5.0, 12.0), "circ",
            notes="One passage feeds OPD 1, OPD 3, the lounge and the staff door to the OT"),
        _mk("lobby", "ENTRY PASSAGE 8'-0\"", (1.0, 41.4, 12.0, 1.4), "circ"),
        _mk("bay", "trolley /\nwheelchair bay", (20.6, 43.2, 3.6, 2.0), "circ"),
        _mk("wardcorr", "WARD PASSAGE 6'-0\"", (14.28, 50.0, 6.0, 32.0), "circ"),
    ]
    import ipd
    for r in rooms:                      # schedule sizes = the measured clear strings
        if r.key in IPD_G:
            o = IPD_G[r.key]
            a, b = ipd.span(r.poly, o["w"][0], o["w"][1], "x")
            c, d = ipd.span(r.poly, o["d"][0], o["d"][1], "y")
            r.dims = f"{fi(b - a)} x {fi(d - c)}"
        elif r.key.startswith("wcR") or r.key == "bath5":
            tw, td, _ = ipd.toilet_size(r.poly)
            r.dims = f"{fi(tw)} x {fi(td)}"
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
                                          for y in [10.7 + 0.25 * i for i in range(78)]), 2)
    out["south_lobby_min_ft"] = round(min(_scan_width(free, "x", y, 12.5, 20.6)
                                          for y in [31.4 + 0.25 * i for i in range(33)]), 2)
    out["staff_band_ft"] = round(BAND_W, 2)
    out["ot_suite"] = ot_checks(rooms, walls=None)
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


# ------------------------------------------------------------ OT suite (17-11-2026)
# OT equipment at true size, feet: (shape, x, y, w, h, short tag, full name).
# shape: rect | dash (parking / zone outline) | circ (x, y = centre, w = radius)
OT_TABLE = (9.39, 7.0, 2.0, 6.75)            # 2'-0" x 6'-9", head to the south
OT_EQUIP = [
    ("dash", 5.39, 3.0, 10.0, 14.75, "", "4'-0\" clear zone round the table"),
    ("circ", 10.39, 8.9, 1.15, 0, "", "OT light (twin dome)"),
    ("circ", 10.39, 11.9, 1.15, 0, "", ""),
    ("pend", 7.9, 5.3, 0.9, 0, "P1", "Anaesthesia pendant (ceiling)"),
    ("pend", 8.2, 15.4, 0.9, 0, "P2", "Surgical pendant (ceiling)"),
    ("rect", 11.9, 3.9, 2.2, 2.4, "AM", "Anaesthesia machine"),
    ("rect", 11.8, 10.4, 1.3, 1.7, "MS", "Mayo stand"),
    ("rect", 14.5, 6.6, 1.5, 1.8, "DS", "Diathermy / suction cart"),
    ("dash", 0.6, 8.0, 2.8, 6.0, "C-ARM", "C-arm parking bay 2'-10\" x 6'-0\""),
    ("rect", 0.4, 15.2, 0.35, 3.4, "CP", "Control panel + X-ray viewer (wall)"),
    ("rect", 20.3, 2.4, 0.55, 2.0, "PB", "Pass box (sterile hatch) from CSSD"),
    ("rect", 25.95, 1.9, 2.3, 2.4, "AC", "Double-door autoclave (pass-through)"),
    ("rect", 10.4, 20.78, 1.7, 0.3, "GAS", "Medical gas valve + alarm panel (AVSU)"),
]
OT_CURTAINS = [((5.5, 25.75), (12.7, 25.75)), ((12.7, 20.9), (12.7, 30.6)),      # recovery bays
               ((41.3, 5.1), (41.3, 10.0)), ((44.0, 5.1), (44.0, 8.7))]            # change cubicles
INSTRUMENT_TROLLEYS = [(5.9, 7.6, 1.5, 3.0), (5.9, 11.0, 1.5, 3.0)]
WALL_CABINETS = (5.0, S0 + 0.02, 12.0, 1.33)

# flow routes (polylines, feet) for the OT-zone sheet
FLOWS = {
    "patient": ("#1565c0", "Patient", [
        [(0.9, 45.3), (16.2, 45.3), (16.2, 33.6), (15.0, 32.0), (15.0, 30.0), (13.9, 28.6),
         (13.9, 21.6), (14.6, 19.6), (12.7, 14.2)],
        [(13.9, 23.2), (12.75, 23.2)], [(13.9, 28.4), (12.75, 28.4)],
        [(16.9, 46.4), (16.9, 49.0)]]),
    "staff": ("#2e7d32", "Staff", [
        [(30.6, 33.2), (30.6, 11.8), (29.9, 10.4), (29.9, 8.9)],
        [(30.3, 8.4), (35.0, 8.4), (40.6, 8.4)],
        [(29.4, 7.7), (24.3, 7.7), (22.7, 9.6), (22.7, 11.9), (18.2, 11.9)]]),
    "clean": ("#00838f", "Clean / sterile supply", [
        [(30.0, 2.6), (24.3, 2.6)],
        [(24.0, 3.4), (18.3, 3.4)],
        [(23.3, 4.5), (23.3, 7.0), (21.9, 9.2), (21.9, 10.6), (18.4, 10.6)],
        [(2.7, 23.6), (2.7, 18.0)]]),
    "dirty": ("#c62828", "Dirty / soiled", [
        [(18.4, 16.3), (23.9, 16.3), (25.4, 15.9), (28.4, 15.9), (28.4, 32.6), (18.6, 34.9),
         (18.6, 44.0), (0.9, 44.0)],
        [(28.4, 15.9), (28.4, 11.6), (28.6, 10.4), (30.9, 8.9), (30.9, 4.4)]]),
}
OT_FIRE_PATH = [(0.6, 0.6), (14.9, 19.6), (14.9, 21.4), (15.3, 30.5), (16.5, 33.2), (16.5, 45.5),
                (0.2, 45.5)]
OT_ZONE_KEYS = ("ot", "otstore", "recovery", "opd2", "xray", "cssdC", "cssdD", "scrub", "du",
                "stlobby", "lounge", "stchange", "wcLg")


def draw_ot_equipment(ax, labels=False, z=8.3):
    """OT table surround, pendants, anaesthesia machine, C-arm bay, pass box,
    autoclave, gas panel and the curtain lines.  labels=True writes the tags."""
    from matplotlib.patches import Rectangle, Circle
    ink = "#333333"
    for shape, x, y, w, h, tag, _ in OT_EQUIP:
        if shape == "circ":
            ax.add_patch(Circle((x, y), w, fc="none", ec="#777", lw=0.5, ls=(0, (3, 2)), zorder=z))
            cx, cy = x, y
        elif shape == "pend":
            ax.add_patch(Circle((x, y), w, fc="#fff6d6", ec=ink, lw=0.8, zorder=z))
            ax.plot([x - w, x + w], [y, y], color=ink, lw=0.4, zorder=z)
            ax.plot([x, x], [y - w, y + w], color=ink, lw=0.4, zorder=z)
            cx, cy = x, y
        elif shape == "dash":
            ax.add_patch(Rectangle((x, y), w, h, fc="none", ec="#1565c0" if tag else "#888",
                                   lw=0.6, ls=(0, (5, 3)), zorder=z - 2.5))
            cx, cy = x + w / 2, y + h / 2
        else:
            ax.add_patch(Rectangle((x, y), w, h, fc="#e9eef5", ec=ink, lw=0.6, zorder=z))
            cx, cy = x + w / 2, y + h / 2
        if labels and tag:
            ax.text(cx, cy, tag, ha="center", va="center", fontsize=6.6 if len(tag) < 4 else 6.0,
                    color="#111", zorder=z + 0.2, weight="bold",
                    rotation=90 if (shape == "dash" and h > w) else 0)
    for (xa, ya), (xb, yb) in OT_CURTAINS:
        ax.plot([xa, xb], [ya, yb], color="#7a5", lw=0.7, ls=(0, (1, 2)), zorder=z)


def ot_checks(rooms=None, walls=None):
    """Numbers quoted in OT_G_BRIEF.md."""
    import ipd
    rooms = rooms or layout_g_rooms()
    by = {r.key: r for r in rooms}
    walls = walls if walls is not None else wall_bands_g(rooms)
    ot = by["ot"].poly
    sq = box(E0, S0, E0 + 20.0, S0 + 20.0)
    out = {}
    a, b = ipd.span(ot, 10.0, 10.0, "x")
    c, d = ipd.span(ot, 10.0, 10.0, "y")
    out["ot_clear_ft"] = (round(b - a, 2), round(d - c, 2))
    out["ot_area_sf"] = round(ot.area, 1)
    out["ot_area_m2"] = round(ot.area * 0.092903, 1)
    out["columns_in_20x20"] = {
        n: dict(area_sf=round(col.intersection(sq).area, 2),
                proud_in=round((sq.bounds[2] - col.intersection(sq).bounds[0]) * 12, 1),
                long_in=round((col.intersection(sq).bounds[3] - col.intersection(sq).bounds[1]) * 12, 1))
        for n, col in COLUMNS.items() if col.intersection(sq).area > 1e-4}
    tx, ty, tw, th = OT_TABLE
    out["table_clear_to_walls_ft"] = dict(east=round(tx - a, 2), west=round(b - tx - tw, 2),
                                          south=round(ty - c, 2), north=round(d - ty - th, 2))
    ring = box(tx - 4, ty - 4, tx + tw + 4, ty + th + 4)
    fixed = [box(*WALL_CABINETS[:2], WALL_CABINETS[0] + WALL_CABINETS[2],
                 WALL_CABINETS[1] + WALL_CABINETS[3])]
    fixed += [box(x, y, x + w, y + h) for s_, x, y, w, h, t, _ in OT_EQUIP if t in ("C-ARM", "CP", "PB")]
    out["fixed_items_inside_4ft_ring_sf"] = round(sum(f.intersection(ring).area for f in fixed), 2)
    for k in ("scrub", "opd2", "recovery", "otstore", "xray", "cssdC", "cssdD", "du", "stlobby",
              "lounge", "stchange"):
        r = by[k]
        tw_, td_, _ = ipd.toilet_size(r.poly)          # largest clear rectangle
        out[k] = dict(clear=f"{fi(tw_)} x {fi(td_)}", area_sf=round(r.area, 1),
                      area_m2=round(r.area * 0.092903, 1))
    path = LineString(OT_FIRE_PATH)
    others = unary_union([r.poly for r in _solids(rooms) if r.key not in ("ot", "recovery")])
    out["travel_ot_far_corner_to_main_door_ft"] = round(path.length, 1)
    out["travel_ot_far_corner_to_stair_ft"] = round(path.length + LineString(STAIR_PATH).length, 1)
    out["travel_m"] = (round(path.length * 0.3048, 1),
                       round((path.length + LineString(STAIR_PATH).length) * 0.3048, 1))
    out["travel_path_blocked_ft"] = round(path.intersection(walls).length
                                          + path.intersection(others).length, 2)
    out["flow_blocked_ft"] = {}
    solid = {r.key: r.poly for r in _solids(rooms)}
    for name, (_, _, lines) in FLOWS.items():
        out["flow_blocked_ft"][name] = round(sum(LineString(l).intersection(walls).length
                                                 for l in lines), 2)
    out["suite_doors"] = {f"{r.key}.{i}": f"{fi(d_['w'])} {d_['kind']}" for r in rooms
                          if r.key in OT_ZONE_KEYS for i, d_ in enumerate(r.gdoors)}
    # equipment against walls / each other
    eq = [(t or n, box(x, y, x + w, y + h)) for s_, x, y, w, h, t, n in OT_EQUIP if s_ == "rect"]
    eq += [(t, Point(x, y).buffer(w)) for s_, x, y, w, h, t, n in OT_EQUIP if s_ == "pend"]
    eq += [("table", box(tx, ty, tx + tw, ty + th))]
    eq += [(f"trolley{i}", box(x, y, x + w, y + h)) for i, (x, y, w, h) in enumerate(INSTRUMENT_TROLLEYS)]
    clash = []
    for i, (na, ga) in enumerate(eq):
        for nb, gb in eq[i + 1:]:
            if ga.intersection(gb).area > 0.02:
                clash.append((na, nb))
    out["equipment_clashes"] = clash
    return out


def render_ot_zone(out_jpg, px=2400):
    """Dedicated OT-zone sheet: close-up of the south block with clear
    dimensions, true-size OT equipment and the four flow routes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
    from matplotlib.lines import Line2D
    import io
    from PIL import Image
    import render as R
    import ipd

    INK = R.INK
    rooms = layout_g_rooms()
    by = {r.key: r for r in rooms}
    walls = wall_bands_g(rooms)
    chk = ot_checks(rooms, walls)
    X0, X1, Y0, YP, Y1 = -12.5, 50.5, -7.5, 49.3, 72.6
    W_IN = 16.0
    FT = W_IN / (X1 - X0)                       # inches per foot on the sheet
    fig = plt.figure(figsize=(W_IN, W_IN * (Y1 - Y0) / (X1 - X0)))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    _draw_base(ax, rooms, walls, R, tag_fs=6.4, equip_labels=True)
    # white panel under the plan for the legend, schedule and checks
    ax.add_patch(Rectangle((X0, YP), X1 - X0, Y1 - YP, fc="white", ec="none", zorder=20))
    ax.plot([X0, X1], [YP, YP], color=INK, lw=0.9, zorder=21)
    ax.add_patch(Rectangle((X0, Y0), X1 - X0, 2.6, fc="white", ec="none", zorder=20))

    def lab(x, y, txt, fs=6.0, bold=False, rot=0, color="#111", alpha=0.86, z=13):
        ax.text(x, y, txt, ha="center", va="center", fontsize=fs * 1.3, color=color, zorder=z,
                weight="bold" if bold else "normal", rotation=rot, linespacing=1.25,
                bbox=dict(fc="white", ec="none", pad=0.4, alpha=alpha))

    def leader(x, y, tx, ty):
        ax.plot([x, tx], [y, ty], color="#555", lw=0.5, zorder=12.5)
        ax.add_patch(Circle((x, y), 0.12, fc="#555", ec="none", zorder=12.5))

    a_ = {k: by[k].area for k in by}
    d_ = {k: by[k].dims.split(" incl")[0] for k in by}
    ax.text(X0 + 0.8, Y0 + 1.25, "OT ZONE — LAYOUT G    operation theatre suite: sizes, equipment and "
            "flow routes", fontsize=13.5, weight="bold", color=INK, va="center", zorder=22)
    ax.text(X1 - 0.8, Y0 + 1.25, "Solaris Shine, 7th floor · Dr. Aman Khanna & Dr. Heena · " + DATE
            + " · concept for review", fontsize=7.6, color="#444", va="center", ha="right", zorder=22)

    # ---- room labels
    lab(5.7, 17.75, f"OPERATION THEATRE\n20'-0\" × 20'-0\" clear\n{a_['ot']:.0f} sf · "
        f"{a_['ot'] * 0.0929:.1f} m²", 9.2, True)
    lab(2.25, 26.6, f"ANAES. / CONSUMABLE STORE\n{d_['otstore']} · {a_['otstore']:.0f} sf", 5.2,
        True, rot=90)
    lab(15.75, 22.35, f"PRE-OP /\nRECOVERY\n{d_['recovery']}\n{a_['recovery']:.0f} sf", 5.6, True)
    lab(9.0, 23.15, "Bay 1 · PRE-OP / HOLDING\n(curtained: patient change)", 5.0)
    lab(9.0, 28.4, "Bay 2 · RECOVERY", 5.0)
    lab(22.3, 28.0, f"OPD 2 · PLASTER /\nPROCEDURE\n{d_['opd2']} · {a_['opd2']:.0f} sf", 6.4, True)
    lab(6.3, 35.0, f"X-RAY / DRESSING / EMERGENCY\n{d_['xray']} · {a_['xray']:.0f} sf\n"
        "mobile X-ray only", 6.0, True)
    lab(23.0, 13.25, f"SCRUB · {d_['scrub']} · {a_['scrub']:.0f} sf", 5.0, True)
    lab(23.6, 17.9, f"DIRTY UTILITY · {a_['du']:.0f} sf", 4.8, True)
    lab(29.75, 6.4, "STAFF LOBBY (air-lock)", 4.5, True)
    lab(35.3, 4.6, f"DRS' LOUNGE\n{d_['lounge']}\n{a_['lounge']:.0f} sf", 5.6, True)
    lab(43.0, 7.0, f"OT STAFF CHANGE\nM / F cubicles + WC\n{a_['stchange'] + a_['wcLg']:.0f} sf",
        5.0, True)
    lab(38.6, 17.9, f"OPD 3 · Psychiatry\n{d_['opd3']} · {a_['opd3']:.0f} sf", 5.6)
    lab(37.4, 27.9, f"OPD 1 · Ortho\n{d_['opd1']} · {a_['opd1']:.0f} sf", 5.6)
    lab(24.9, 38.7, "RECEPTION", 5.0)
    lab(22.5, 44.3, "TROLLEY /\nWHEELCHAIR BAY", 4.6)
    # the two CSSD rooms are too small for a label: leaders to the service ledge
    for (x, y, tx, txt) in [(23.9, 4.75, 21.0, f"CSSD CLEAN + STERILE STORE\n{d_['cssdC']} · "
                             f"{a_['cssdC']:.0f} sf"),
                            (31.2, 4.6, 32.6, f"CSSD WASH (dirty side)\n{d_['cssdD']} · "
                             f"{a_['cssdD']:.0f} sf")]:
        leader(x, y, tx, -2.6)
        lab(tx, -3.35, txt, 5.4, True, z=23)
    for x, y, t, rot in [(29.65, 23.0, "OPD PASSAGE 5'-0\"", 90), (17.2, 37.4, "LOBBY", 0),
                         (9.0, 41.6, "ENTRY PASSAGE 8'-0\"", 0), (36.5, 32.9, "WAITING AREA", 0)]:
        ax.text(x, y, t, ha="center", va="center", fontsize=7.6, color="#444", style="italic",
                weight="bold", rotation=rot, zorder=13)
    ax.text(2.35, 3.4, "ex. x07 toilet slab\n(level it, cap drains)", ha="center", va="center",
            fontsize=5.6, color="#1f77b4", zorder=13)
    for nm, (cx, cy) in (("C1", (21.57, 0.95)), ("C3", (21.57, 21.4)), ("C5", (21.57, 39.3))):
        ax.text(cx, cy, nm, ha="center", va="center", fontsize=7.0, color="white", zorder=13,
                weight="bold")
    lab(26.0, 11.5, "3-tap\nscrub\ntrough", 4.0, alpha=0.7)
    ax.text(11.0, 1.07, "WALL CABINETS 12'-0\" x 1'-4\" (recessed in the panel lining)", ha="center",
            va="center", fontsize=5.8, color="#111", zorder=13)
    lab(10.39, 14.55, "OT TABLE 2'-0\" x 6'-9\"\nhead to the south", 4.6, alpha=0.75)
    ax.text(5.35, 10.8, "instrument trolleys", ha="center", va="center", fontsize=5.6,
            color="#111", zorder=13, rotation=90)

    # ---- clear dimensions (blue strings, measured on the room polygons)
    DIMS = [("ot", 3.0, 19.65, "x", 0.62), ("ot", 17.0, 9.0, "y", 0.82),
            ("scrub", 24.75, 9.0, "y", 0.3),
            ("opd2", 22.0, 30.35, "x", 0.5), ("opd2", 19.5, 25.0, "y", 0.5),
            ("recovery", 9.0, 30.45, "x", 0.25), ("recovery", 13.05, 26.0, "y", 0.5),
            ("otstore", 2.7, 30.35, "x", 0.5), ("xray", 6.0, 33.3, "x", 0.5),
            ("xray", 11.9, 35.0, "y", 0.5),
            ("lounge", 35.3, 9.35, "x", 0.5), ("opd3", 39.0, 19.3, "x", 0.5),
            ("opd3", 44.0, 15.0, "y", 0.5), ("opd1", 39.0, 21.0, "x", 0.5),
            ("opd1", 43.3, 25.0, "y", 0.5)]
    for k, x, y, axis, at in DIMS:
        ipd.dim_string(ax, by[k].poly, x, y, axis, fs=6.8, at=at, z=14)
    free = free_space(rooms)
    for (x, y, axis) in [(29.7, 13.3, "x"), (16.5, 38.6, "x")]:
        ipd.dim_string(ax, free, x, y, axis, fs=6.8, color="#a33", z=14)
    tc = chk["table_clear_to_walls_ft"]
    tx, ty, tw, th = OT_TABLE
    for (xa, ya, xb, yb, txt, lx, ly, rot) in [
            (E0, 7.2, tx, 7.2, fi(tc["east"]), 4.3, 6.85, 0),
            (tx + tw, 9.2, OT_WF, 9.2, fi(tc["west"]), 16.6, 8.85, 0),
            (10.39, S0 + 1.35, 10.39, ty, "5'-3\" to cabinets", 10.39, 2.5, 0),
            (10.39, ty + th, 10.39, OT_N, fi(tc["north"]), 10.85, 16.9, 90)]:
        ax.annotate("", xy=(xb, yb), xytext=(xa, ya),
                    arrowprops=dict(arrowstyle="<->", lw=0.55, color="#6a1b9a"), zorder=12)
        lab(lx, ly, txt, 5.0, rot=rot, color="#6a1b9a", alpha=0.8, z=14)

    # ---- flow routes
    for name, (colr, _, lines) in FLOWS.items():
        ls = (0, (3.5, 1.2)) if name == "dirty" else "-"
        for pts in lines:
            ax.plot([p[0] for p in pts[:-1]], [p[1] for p in pts[:-1]], color=colr, lw=2.4,
                    alpha=0.85, zorder=15, solid_capstyle="round", solid_joinstyle="round", ls=ls)
            ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=14,
                                         lw=2.4, color=colr, alpha=0.9, zorder=15,
                                         shrinkA=0, shrinkB=0, ls=ls))
    for x, y, t, colr, rot in [(8.5, 46.35, "PATIENT IN / OUT", "#1565c0", 0),
                               (8.5, 43.0, "SOILED OUT → service lift", "#c62828", 0),
                               (19.3, 48.3, "to wards", "#1565c0", 0),
                               (30.75, 18.0, "STAFF", "#2e7d32", 90),
                               (28.25, 20.6, "SOILED", "#c62828", 90),
                               (19.4, 4.35, "STERILE", "#00838f", 0),
                               (13.75, 26.0, "PATIENT", "#1565c0", 90)]:
        lab(x, y, t, 5.0, True, rot=rot, color=colr, z=16)

    # ---- deviation markers (the sketched lines, dash-dot magenta)
    mg = "#ad1457"
    for (xa, ya), (xb, yb) in [((23.06, 1.6), (23.06, 19.8)), ((0.5, 20.02), (26.8, 20.02)),
                               ((8.52, 20.9), (8.52, 30.7)), ((14.47, 31.3), (14.47, 39.6)),
                               ((23.06, 22.5), (23.06, 30.7))]:
        ax.plot([xa, xb], [ya, yb], color=mg, lw=0.9, ls=(0, (6, 2, 1, 2)), zorder=11)
    for n, (x, y) in enumerate([(23.06, 14.06), (6.6, 20.02), (8.52, 25.75), (14.47, 35.3),
                                (23.06, 24.4), (45.2, 9.0), (31.4, 11.2)], 1):
        ax.add_patch(Circle((x, y), 0.55, fc="white", ec=mg, lw=0.9, zorder=17))
        ax.text(x, y + 0.03, str(n), ha="center", va="center", fontsize=7.0, color=mg,
                weight="bold", zorder=18)

    # ---- panel under the plan: three columns
    def block(x, y, title, lines, fs=7.2, mono=False, color="#222", tcolor=None):
        ax.text(x, y, title, fontsize=8.6, weight="bold", color=tcolor or INK, va="top", zorder=22)
        lh = fs * 1.72 / 72 / FT
        ax.text(x, y + 1.15, "\n".join(lines), fontsize=fs, color=color, va="top", zorder=22,
                linespacing=1.5, family="monospace" if mono else None)
        return y + 1.15 + lh * len(lines) + 1.0

    c1, c2, c3 = X0 + 0.8, 6.6, 29.3
    y = YP + 0.9
    ax.text(c1, y, "FLOW ROUTES", fontsize=8.6, weight="bold", color=INK, va="top", zorder=22)
    notes = {"patient": ["main door → lobby → pre-op bay →", "OT (5'-0\" sliding door) →",
                         "recovery bay → lobby → wards"],
             "staff": ["OPD passage → staff-lobby door →", "lounge → change → staff lobby →",
                       "scrub → OT"],
             "clean": ["CSSD wash → autoclave → clean side →", "pass box, or scrub, → OT;",
                       "anaes. / consumable store → OT"],
             "dirty": ["OT → dirty utility → OPD passage →", "lobby → main door → service lift;",
                       "instruments → CSSD wash (closed box)"]}
    y += 1.5
    for name, (colr, nm, _) in FLOWS.items():
        ax.add_patch(FancyArrowPatch((c1, y + 0.3), (c1 + 3.2, y + 0.3), arrowstyle="-|>",
                                     mutation_scale=13, lw=2.4, color=colr, zorder=22,
                                     ls=(0, (3.5, 1.2)) if name == "dirty" else "-"))
        ax.text(c1 + 3.8, y, nm, fontsize=8.0, weight="bold", color=colr, va="top", zorder=22)
        ax.text(c1 + 3.8, y + 1.0, "\n".join(notes[name]), fontsize=6.6, color="#333", va="top",
                zorder=22, linespacing=1.4)
        y += 4.1
    y += 0.6
    ax.plot([c1, c1 + 10], [y + 0.9, y + 0.9], lw=2.5, color=INK, zorder=22)
    for i in range(0, 11, 5):
        ax.plot([c1 + i] * 2, [y + 0.6, y + 1.2], lw=1, color=INK, zorder=22)
        ax.text(c1 + i, y + 0.3, f"{i}'", ha="center", fontsize=6.5, color=INK, zorder=22)

    rows = [("ot", "Operation theatre"), ("scrub", "Scrub (3 taps) / clean lobby"),
            ("recovery", "Pre-op / recovery, 2 bays"), ("otstore", "Anaes. / consumable store"),
            ("cssdC", "CSSD clean + sterile store"), ("cssdD", "CSSD wash (dirty side)"),
            ("du", "Dirty utility"), ("stlobby", "Staff lobby (air-lock)"),
            ("stchange", "OT staff change M/F + WC"), ("lounge", "Drs' lounge"),
            ("opd2", "OPD 2 · plaster / procedure"), ("xray", "X-ray / dressing / emerg.")]
    lines = []
    for k, nm in rows:
        ar = a_[k] + (a_["wcLg"] if k == "stchange" else 0)
        lines.append(f"{nm:<29s}{d_[k]:<18s}{ar:>4.0f} sf {ar * 0.0929:>5.1f} m²")
    y2 = block(c2, YP + 0.9, "ROOM SCHEDULE  (clear, plaster face to plaster face; net of columns)",
               lines, fs=6.7, mono=True)
    eq = [f"{t:<6s}{n}" for _, _, _, _, _, t, n in OT_EQUIP if t]
    eq += ["      Instrument trolleys 1'-6\" x 3'-0\" (2); OT table 2'-0\" x 6'-9\"",
           "      Dashed circles: twin-dome OT light. Grey dashed box: 4'-0\" clear zone"]
    block(c2, y2, "OT EQUIPMENT  (drawn at true size)", eq, fs=6.7, mono=True)

    dv = ["1  OT west wall 2'-5¾\" (29¾\") east, onto the grid-B column line:",
          "   OT 22'-6\" → 20'-0\" wide; staff band 3'-7½\" → 6'-1\"",
          "2  x07 | x06 party wall rebuilt 7\" north: OT depth 19'-5\" → 20'-0\"",
          "3  OT-store wall 3'-4\" east: store 7'-11\" → 4'-7\" wide",
          f"4  X-ray west wall 1'-2\" (14\") east for the recovery door: 122 → {a_['xray']:.0f} sf",
          "5  OPD 2 moved out of the 3'-8\" strip to a 9'-0\" x 10'-0\" room",
          "6  Unnamed corner room: Drs' rest → OT staff change + WC",
          "7  New door across the OPD passage (south end = staff lobby)"]
    y3 = block(c3, YP + 0.9, "DEVIATIONS FROM THE 3rd SKETCH  (magenta dash-dot = sketched line)",
               dv, fs=6.8, tcolor=mg)
    cols = chk["columns_in_20x20"]
    ck = [f"OT {chk['ot_area_sf']:.0f} sf = {chk['ot_area_m2']} m²; asked: 20' x 20' (≈ 36 m²)",
          "Columns inside the 20' x 20': " + ", ".join(
              f"{n} {v['proud_in']}\" x {v['long_in']}\"" for n, v in cols.items()) + " (corner nibs)",
          f"Table to walls: E {fi(tc['east'])}, W {fi(tc['west'])}, S {fi(tc['south'])}, "
          f"N {fi(tc['north'])}",
          f"OPD 2 clear of column C3: {chk['opd2']['clear']} (C3 stands 1'-8\" proud)",
          f"OT far corner → main door {chk['travel_ot_far_corner_to_main_door_ft']:.0f} ft "
          f"({chk['travel_m'][0]} m); → stair ≈ {chk['travel_ot_far_corner_to_stair_ft']:.0f} ft "
          f"(≈ {chk['travel_m'][1]} m)",
          "X-ray: mobile unit only at this size",
          "HVAC: OT air-handling unit + condensers need a plant space on the",
          "   cut-out / service ledge (not designed)",
          "Guideline figures (NABH / HFG-India / AERB) are from memory: to verify"]
    y3 = block(c3, y3, "CHECKS", ck, fs=6.8)
    block(c3, y3, "DOORS", [f"{t}  {d}" for t, d in DOOR_LEGEND[:5]]
          + ["PB  pass box 2'-0\" (CSSD → OT)"], fs=6.4, color="#a33")
    ax.text(X1 - 0.8, Y1 - 0.7, "SOUTH is at the top, EAST (lift core) on the left.  Blue strings = "
            "clear sizes, feet-inches.  Columns red-brown.  Blue dashed = builder's toilet slab.",
            fontsize=6.2, color="#555", va="center", ha="right", zorder=22)
    ax.set_xlim(X0, X1)
    ax.set_ylim(Y1, Y0)
    ax.axis("off")
    buf = io.BytesIO()
    fig.savefig(buf, dpi=px / W_IN * 1.5, facecolor="white", format="png")
    plt.close(fig)
    buf.seek(0)
    im = Image.open(buf).convert("RGB")
    im = im.resize((px, round(im.height * px / im.width)), Image.LANCZOS)
    im.save(out_jpg, quality=92, optimize=True)
    return im.size


# ------------------------------------------------------------ CAD sheet (PNG/SVG)
# IPD rooms: label in the clear floor (never over the bed), W / D dimension
# strings as (x, y, text position along the string, text offset)
IPD_G = {
    "room1": dict(label=(29.9, 50.15), w=(27.0, 51.4, 0.1, 0), d=(26.75, 53.0, 0.52, 0)),
    "room2": dict(label=(27.55, 68.4), w=(27.0, 67.0, 0.93, 0), d=(25.05, 64.0, 0.62, 0)),
    "room3": dict(label=(26.9, 71.35), w=(27.0, 72.7, 0.93, 0), d=(23.15, 75.0, 0.5, 0)),
    "room4": dict(label=(28.9, 89.95), w=(27.0, 88.4, 0.47, 0), d=(23.1, 86.0, 0.55, 0)),
    "suite": dict(label=(8.6, 87.5), w=(10.0, 88.9, 0.82, 0), d=(12.5, 86.0, 0.35, 0)),
}
IPD_WINDOW = (-3.5, 49.0, 45.6, 96.0)      # close-up crop, plan feet (x0, x1, y0, y1)

LABEL_FS = {"ot": 8.4, "scrub": 4.6, "opd2": 6.4, "cssdC": 4.5, "cssdD": 4.5, "du": 4.4,
            "stlobby": 3.9, "otstore": 4.8, "stchange": 5.0,
            "recep": 5.6, "lounge": 6.4, "drrest": 6.4, "recovery": 7.6, "xray": 7.4, "suite": 8.6, "room1": 8, "room2": 8,
            "room3": 8, "room4": 8, "opd1": 7.6, "opd3": 7.6}
SMALL = {"recep", "scrub", "otstore", "bp", "pharm", "obs",
         "change", "ns", "store", "duty", "pantry"}


SHEET_NAME = {"cssdC": "CSSD clean +\nsterile store", "cssdD": "CSSD wash\n(dirty)",
              "du": "Dirty utility", "stlobby": "Staff lobby\n(air-lock)",
              "stchange": "OT staff change\nM / F + WC", "opd2": "OPD 2 · Plaster /\nprocedure",
              "ot": "OPERATION THEATRE", "recovery": "PRE-OP / RECOVERY", "scrub": "SCRUB",
              "xray": "X-RAY / DRESSING /\nEMERGENCY"}


def _door_tag(w):
    for lim, tag in ((4.9, "D1"), (3.9, "D2"), (3.4, "D3"), (2.9, "D4"), (2.7, "D5")):
        if w >= lim:
            return tag
    return "D6"


DOOR_LEGEND = [("D1", "5'-0\" double sliding, hermetic (OT patient door)"),
               ("D2", "4'-0\" recovery / X-ray"),
               ("D3", "3'-6\" trolley door (ward rooms, OPD 2, scrub-OT, staff lobby)"),
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
    if kind == "slide":          # double sliding: leaves parked on the wall face
        from matplotlib.patches import Rectangle
        al = (1.0, 0.0) if d["axis"] == "h" else (0.0, 1.0)
        ax.plot([lo[0], hi[0]], [lo[1], hi[1]], color=ink, lw=0.6, ls=(0, (3, 2)), zorder=z)
        for start in (-w / 2, w):
            x0 = lo[0] + al[0] * start + perp[0] * 0.5 - (0.13 if al[1] else 0)
            y0 = lo[1] + al[1] * start + perp[1] * 0.5 - (0.13 if al[0] else 0)
            ax.add_patch(Rectangle((x0, y0), al[0] * w / 2 + al[1] * 0.26,
                                   al[1] * w / 2 + al[0] * 0.26, fc="#cfe3ff", ec=ink, lw=0.8,
                                   zorder=z + 1))
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
    if kind == "ottable":                    # OT table, true size, head section marked
        ax.add_patch(Rectangle((x, y), w, h, fc="#dfe9df", lw=0.8, ec="#222", zorder=6.4))
        ax.plot([x, x + w], [y + 1.4, y + 1.4], color="#222", lw=0.5, zorder=6.5)
        ax.plot([x, x + w], [y + h - 2.0, y + h - 2.0], color="#222", lw=0.5, zorder=6.5)
        return
    if kind == "wc" and rot == 180:          # tank on the low-y wall
        ax.add_patch(Rectangle((x, y), w, h * 0.5, fc="white", lw=0.5, ec="#4a4a4a", zorder=6))
        ax.add_patch(Circle((x + w / 2, y + h * 0.72), w * 0.4, fc="white", lw=0.5,
                            ec="#4a4a4a", zorder=6))
    elif kind == "sofa" and rot == 180:      # back on the low-y side
        ax.add_patch(Rectangle((x, y), w, h, fc="white", lw=0.55, ec="#4a4a4a", zorder=6))
        ax.plot([x + 0.25, x + w - 0.25], [y + 0.55, y + 0.55], color="#4a4a4a", lw=0.45, zorder=6)
    else:
        R._furniture(ax, item)


def _draw_base(ax, rooms, walls, R, tag_fs=4.6, equip_labels=False):
    """Plan drawing shared by the full sheet and the OT-zone sheet: context,
    floor, rooms, existing builder items, walls, columns, furniture, doors,
    OT equipment, glass and the main door."""
    from matplotlib.patches import Rectangle, Circle
    from plan_model import ZONES
    INK = R.INK
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
            if d["kind"] in _LEAF:
                off = 0.95
                tx, ty = d["cx"], d["cy"]
                if d["axis"] == "h":
                    ty -= d["swing"] * off
                else:
                    tx -= d["swing"] * off
                ax.text(tx, ty, _door_tag(d["w"]), fontsize=tag_fs, color="#a33", zorder=11,
                        ha="center", va="center",
                        bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.85))

    draw_ot_equipment(ax, labels=equip_labels)

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



def render_sheet(out_base):
    """Dimensioned CAD sheet for Layout G (PNG + SVG).  South at the top."""
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, Polygon as MplPoly, FancyArrow
    from matplotlib.lines import Line2D
    import os
    import render as R
    import ipd
    from plan_model import ZONES

    INK = R.INK
    rooms = layout_g_rooms()
    walls = wall_bands_g(rooms)
    fig, ax = plt.subplots(figsize=(19.5, 26.2))
    ax.set_aspect("equal")

    _draw_base(ax, rooms, walls, R)

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
        if r.key in IPD_G:
            o = IPD_G[r.key]
            wl = ipd.dim_string(ax, p, o["w"][0], o["w"][1], "x", at=o["w"][2], off=o["w"][3], fs=5.2)
            dl = ipd.dim_string(ax, p, o["d"][0], o["d"][1], "y", at=o["d"][2], off=o["d"][3], fs=5.2)
            ax.text(o["label"][0], o["label"][1],
                    f"{r.name} · 1 bed\nclear {fi(wl)} × {fi(dl)}\n{r.area:.0f} sf net of toilet",
                    ha="center", va="center", fontsize=5.0, color="#111", zorder=9.2,
                    weight="bold", linespacing=1.3,
                    bbox=dict(fc="#f6f3fa", ec="none", pad=0.5, alpha=0.9))
            continue
        if r.zone == "wet":
            if r.key.startswith("wcR") or r.key == "bath5":
                tw, td, _ = ipd.toilet_size(p)
                ax.text(lx, ly + (1.25 if r.key in ("wcR2", "wcR4") else -1.25),
                        f"{fi(tw)} × {fi(td)}", ha="center", va="center",
                        fontsize=4.6, color=INK, zorder=11,
                        bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.85))
            if r.key == "bath5":
                ax.add_patch(Circle((3.4, 75.75), 2.5, fc="none", ec="#2c6fbb", lw=0.6,
                                    ls=(0, (4, 3)), zorder=9))
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
        rot = 90 if r.key == "otstore" else 0
        if r.key == "otstore":
            txt = f"{r.name}\n{r.dims} · {r.area:.0f} sf"
        elif r.key in ("cssdC", "cssdD"):
            txt = f"{SHEET_NAME[r.key].split(chr(10))[0].rstrip(' +')}\n{r.area:.0f} sf"
        elif r.key == "stlobby":
            txt = "Staff lobby (air-lock)"
        elif r.key in ("scrub", "du"):
            txt = f"{SHEET_NAME[r.key]} · {r.dims} · {r.area:.0f} sf"
        elif r.key in SHEET_NAME:
            txt = f"{SHEET_NAME[r.key]}\n{r.dims.split(' incl')[0]} · {r.area:.0f} sf"
        elif r.key == "recep":
            txt = f"{r.name}\n{r.dims}"
        ax.text(lx, ly, txt, ha="center", va="center", fontsize=fs, color="#111",
                weight="bold" if r.name.isupper() else "normal", zorder=9, linespacing=1.25,
                rotation=rot, bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.72))

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

    chain_h([E0, OT_WF, BAND0, 26.87, 27.245, 32.245, 32.62, 38.0, 38.375, xw(S0)], -3.6,
            ["20'-0\"", "", fi(BAND_W), "", "5'-0\"", "", "5'-5\"", "", fi(xw(S0) - 38.375)])
    chain_h([0.0, 47.98], -5.9, ["47'-11¾\" over walls (Rev C: 48'-6\" to glass line)"], fs=7)
    ys = [S0, OT_N, ROWA0, ROWA1, ROWA1 + 0.375, 39.76, 40.09, 48.10, 48.49, 55.2, 55.575, 59.2,
          59.575, 66.0, 66.375, 72.425, 72.8, 78.8, 79.175, N0]
    chain_v(ys, -12.2, [fi(b - a) if b - a > 1 else "" for a, b in zip(ys[:-1], ys[1:])])
    chain_v([0.0, 92.22], -14.6, ["92'-2¾\" over walls (Rev C: 92'-0\")"], fs=7)
    wys = [48.49, 58.9, 59.275, 69.7, 70.075, 80.3, 80.675, N0]
    chain_v(wys, 45.4, [fi(b - a) if b - a > 1 else "" for a, b in zip(wys[:-1], wys[1:])],
            side=1)
    sys_ = [S0, 10.1, 10.475, 19.82, 20.21, 30.1]
    chain_v(sys_, 49.4, [fi(b - a) if b - a > 1 else "" for a, b in zip(sys_[:-1], sys_[1:])],
            side=1)
    # passage-width callouts
    for (xa, xb, y, lab) in [(14.28, 20.28, 73.6, "6'-0\""), (27.245, 32.245, 13.2, "5'-0\"")]:
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
                             (29.7, 32.6, 29.7, 28.0), (15.3, 33.8, 15.3, 31.5)]:
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
             "2. South block = clients' 3rd sketch reworked as an OT suite (OT_G_BRIEF.md, ot_G_zone.jpg): OT 20'-0\" x 20'-0\" clear; OT west wall 2'-6\" east of the sketched line "
             "(on grid B), party wall rebuilt 7\" north; staff band 6'-1\"; OPD passage 5'-0\".\n"
             "3. Trolley doors 3'-6\" (D3); OT patient door 5'-0\" double sliding (D1); recovery / X-ray 4'-0\" (D2).  "
             "4. X-ray room ≈ 10 m²: mobile / portable unit only (AERB fixed unit ≈ 18 m², no side < 4 m: to verify).  "
             "5. New ward toilets are away from the builder's shafts: raised floor + drain runs to be designed.\n"
             "6. (T) toilet — tiled, floor trap.  Bed heads on solid walls.  Concept for review; "
             "structure, fire and AERB to be verified by the project architect.\n"
             "7. IPD furniture at true size: bed 3'-3\" x 7'-0\", locker 1'-6\" sq., wardrobe 2'-0\" x 4'-0\", attendant sofa 2'-0\" x 5'-6\" "
             "(Room 4: 5'-0\" couch, 2'-6\" wardrobe).  Blue strings = clear size between plaster faces, measured on the DWG geometry; "
             "room areas exclude the toilet.  Dashed blue circle = 5'-0\" wheelchair turning circle.")
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
        nm = nm.replace("OPD 2 · Plaster / procedure", "OPD 2 · Plaster / proc.")
        nm = (nm[:24] + "…") if len(nm) > 25 else nm
        dm = dims.split(" + ")[0].split(" incl")[0].replace(" (L)", "")
        lines.append(f"{n:>2} {nm:<25s} {dm:<19s}{area:>4.0f}")
    lines += ["─" * 46, f"   rooms total {sum(a for _, _, a in sched):>29.0f} sf",
              f"   clear floor inside walls {clear:>16.0f} sf",
              "", "BEDS  5 in-patient (4 single rooms + suite)",
              "      2 pre-op / recovery, 1 observation", "      1 staff rest (duty bunk)"]
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
    ipd.save_sheet(fig, ax, out_base, IPD_WINDOW,
                   os.path.join(os.path.dirname(os.path.abspath(out_base)), "ipd_G.jpg"))
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
    for name, color in (("OT_EQUIPMENT", 4), ("FLOW_PATIENT", 5), ("FLOW_STAFF", 3),
                        ("FLOW_CLEAN", 4), ("FLOW_DIRTY", 1)):
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    for shape, x, y, w, h, tag, _ in OT_EQUIP:
        if shape in ("circ", "pend"):
            msp.add_circle((x, y), w, dxfattribs={"layer": "OT_EQUIPMENT"})
        else:
            msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True,
                               dxfattribs={"layer": "OT_EQUIPMENT"})
        if tag:
            msp.add_text(tag, height=0.4, dxfattribs={"layer": "OT_EQUIPMENT"}).set_placement(
                (x, y - 0.5) if shape in ("circ", "pend") else (x + 0.1, y + 0.1))
    for name, (_, _, lines) in FLOWS.items():
        for pts in lines:
            msp.add_lwpolyline(pts, dxfattribs={"layer": "FLOW_" + name.upper()})


def build_outputs(out_dir="../deliverables"):
    """Regenerate every Layout G drawing (G only; Layout H is not touched)."""
    import os
    base = os.path.join(out_dir, "layout_G_detailed")
    render_sheet(base)                                   # PNG + SVG + JPG (+ ipd_G.jpg)
    from dxf_export import export_dxf
    errors = export_dxf("G", base + ".dxf")
    size = render_ot_zone(os.path.join(out_dir, "ot_G_zone.jpg"))
    import blueprint_svg as B
    for theme in ("blueprint", "clean"):
        B.render_blueprint("G", theme, os.path.join(out_dir, f"layout_G_{theme}.svg"))
    from render3d import render_3d
    render_3d("G", os.path.join(out_dir, "3d_layout_G.png"))
    return dict(dxf_audit_errors=errors, ot_zone_px=size)


if __name__ == "__main__":
    import json
    import sys
    import plan_model  # noqa: F401  (registers the layout)
    print(json.dumps(checks(), indent=1, default=str))
    if "build" in sys.argv[1:]:                          # python3 layout_g.py build
        print(build_outputs())
