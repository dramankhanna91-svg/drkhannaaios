"""LAYOUT H (17-11-2026) - Ar. Bankim Dave's proposal (09-01-2026) improved,
drawn on the builder's DWG geometry.

Geometry source: floorplan/source/solaris_typical_5_7_10.dxf (mm, from the
client's DWG "SOLARIS SHINE TYPICAL FLOOR LAYOUT PLAN 19-12-25").  East wing =
units x05 (north) + x06 + x07 (south) + the dead-end lobby in front of
x06/x07 + the common passage up to the cut-out.

Repo coordinates (feet):
    x = (X_mm - 6002110) / 304.8     0 = OUTER plaster face of the east wall
    y = (-206341 - Y_mm) / 304.8     0 = OUTER plaster face of the south wall
x grows westward on the sheet, y grows northward (same as plan_model.py).

Everything here is self-contained so that the Rev C constants in
plan_model.py (used by layouts A-F) stay untouched.  plan_model.py imports
this module with one line; registration in LAYOUTS happens at the bottom.
"""
import math
from contextlib import contextmanager

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

import plan_model
from plan_model import Room

T = 0.375            # internal partition, 4.5" (115 mm block + plaster)
EXT = 0.46           # external wall / facade zone, 140 mm plaster to plaster
_X0, _Y0 = 6002110.0, -206341.0


def ft(X, Y):
    """DWG millimetres -> repo feet."""
    return ((X - _X0) / 304.8, (_Y0 - Y) / 304.8)


def _arc(cx, cy, r, a0, a1, n=10):
    return [ft(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
               cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


# ------------------------------------------------------------ envelope (DWG)
# outer plaster line, layer "DR - PLASTER LINE"
PLATE_H_PTS = ([ft(6002110, -206341), ft(6016776, -206341), ft(6016686, -206964),
                ft(6016666, -207106), ft(6015898, -212424), ft(6015116, -217842),
                ft(6015009, -218584), ft(6012900, -233188)]
               + _arc(6011396, -232971, 1520, 352, 270)[1:]
               + [ft(6002110, -234491)])
PLATE_H = Polygon(PLATE_H_PTS)
INNER_H = PLATE_H.buffer(-EXT, join_style=2)

# cut-out (open to sky): x from the east face of its wall to the facade line
_cx, _cy0 = ft(6009660, -218601)
_, _cy1 = ft(6009660, -221001)
CUTOUT_H = box(_cx, _cy0, 60.0, _cy1).intersection(PLATE_H.buffer(0.05))

# glass line, layer "DR-GLASS" (150 mm outside the plaster line)
GLASS_WEST_H = [(ft(6016926, -206427), ft(6015173, -218570)),
                (ft(6014810, -221084), ft(6013059, -233211)),
                (ft(6013059, -233211), ft(6012479, -234255)),
                (ft(6012479, -234255), ft(6011396, -234651))]
GLASS_NORTH_H = [(ft(6011396, -234651), ft(6003626, -234651))]

MD_DOOR_H = (0.0, 41.16, 47.16)      # 6'-0" pair in the 7'-10½" common passage


def _rect(x1, y1, x2, y2):
    (ax, ay), (bx, by) = ft(x1, y1), ft(x2, y2)
    return box(min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))


def _quad(*pts):
    return Polygon([ft(*p) for p in pts])


# RCC columns (plaster outline) inside / on the edge of the wing
COLUMNS_H = {
    "C1": _rect(6008310, -206481, 6009100, -206831),
    "C2": _rect(6015897, -206481, 6016706, -206831),
    "C3": _rect(6008310, -212541, 6009100, -213191),
    "C4": _rect(6015022, -212541, 6015831, -212891),
    "C5": _rect(6008310, -218111, 6009100, -218461),
    "C6": _quad((6014532, -218461), (6014634, -217752), (6014980, -217802), (6014902, -218481)),
    "C7": _rect(6008310, -221141, 6008950, -221741),
    "C8": _quad((6014062, -221716), (6014145, -221141), (6014637, -221021), (6014547, -221786)),
    "C9": _rect(6002250, -227251, 6002830, -228191),
    "C10": _quad((6012989, -228093), (6013124, -227163), (6013757, -227254), (6013623, -228185)),
    "C11": _quad((6012765, -230699), (6012856, -230065), (6013341, -230135), (6013250, -230769)),
    "C12": _rect(6002250, -233701, 6002600, -234351),
    "C13": _rect(6008310, -233701, 6008950, -234351),
    "C14": _rect(6002250, -221141, 6002650, -221741),
}

# lift / stair core east of the wing (context only, outside the plate)
CORE_H = {
    "lifts": [_rect(5999200, y0, 6002010, y1) for y0, y1 in
              ((-208831, -211231), (-211421, -213361), (-213551, -215491), (-215681, -217621))],
    "duct": _rect(5999160, -217871, 6002250, -218601),
    "lobby": _rect(5996500, -208300, 5999000, -218601),       # lift lobby
    "stair_b": _rect(5991050, -211300, 5996200, -218000),     # stair around the 5th lift
    "stair_a": _rect(5991050, -208000, 5996200, -211200),     # fire stair (FD)
    "refuge": _rect(5994000, -206000, 6002000, -208000),      # refuge area @ 5/7/10
}

# builder's toilet (150 mm raised slab) and duct positions = plumbing points
PLUMBING_H = {
    "T507": _rect(6002250, -206481, 6003430, -208271),
    "T505": _rect(6002250, -222141, 6003430, -224531),
    "D505": _rect(6002250, -221141, 6003430, -222001),
    "T506": _quad((6013092, -217281), (6015056, -217281), (6014902, -218461), (6013092, -218461)),
}

# explicit walls where circulation meets circulation (existing walls kept)
EXTRA_WALLS_H = [
    box(EXT, 39.80, 14.275, 40.22),      # x06 north wall, east part (new)
    box(20.34, 39.76, 24.77, 40.22),     # x06 north wall, C5 to the cut-out
    box(EXT, 48.10, 24.77, 48.56),       # x05 south wall (existing)
    box(24.31, 40.22, 24.77, 48.10),     # cut-out east wall (existing)
]

# counter hatches / pass boxes: (cx, cy, width, 'h' horizontal wall | 'v')
HATCHES_H = [
    (7.9, 48.33, 3.6, "h", "pharmacy hatch"),
    (20.65, 8.3, 2.4, "v", "pass box"),
]

ACCESSIBLE_H = {"wc_acc", "wcW1", "wcW2", "wcW3"}     # 5'-0" turning circle drawn
_COLS_H = unary_union(list(COLUMNS_H.values()))
# single-leaf doors hinged at the high-coordinate jamb: (cx, cy)
HINGE_HI = set()


def fi(v):
    """feet -> 12'-6\" (nearest inch)."""
    n = int(round(v * 12))
    return f"{n // 12}'-{n % 12}\""


class RoomH(Room):
    """Room clipped to the DWG inner face; nested rooms get a 4.5" wall."""

    @property
    def poly(self):
        x, y, w, h = self.rect
        p = box(x, y, x + w, y + h).intersection(INNER_H)
        p = p.difference(CUTOUT_H.buffer(EXT, join_style=2))
        for hx, hy, hw, hh in self.holes:
            p = p.difference(box(hx, hy, hx + hw, hy + hh).buffer(T, join_style=2))
        if self.zone == "inpatient" or self.key.startswith(("wcW", "wcN")):
            p = p.difference(_COLS_H)        # IPD: clear floor excludes RCC columns
        return p


def R(key, name, x1, y1, x2, y2, zone, doors=(), furniture=(), holes=(), notes="", dims=None):
    """Room from clear corner coordinates; dimension string computed (E-W x N-S)."""
    b = box(x1, y1, x2, y2).intersection(INNER_H)
    h = y2 - y1
    if dims is None:
        if zone == "circ":
            dims = ""
        elif abs(b.area - (x2 - x1) * h) < 0.5:
            dims = f"{fi(x2 - x1)} x {fi(h)}"
        else:
            dims = f"{fi(b.area / h)} avg x {fi(h)}"
    return RoomH(key, name, dims, (x1, y1, x2 - x1, h), zone, doors=list(doors),
                 furniture=list(furniture), holes=[(a, b_, c - a, d - b_) for a, b_, c, d in holes],
                 notes=notes)


X1 = 18.375          # east clear face of the west ward rooms (6'-6" passage)
TW, TD = 6.0, 7.0    # ensuite: 6'-0" (E-W) x 7'-0" (N-S) = wheelchair size


def _twin(n, y1, y2, head, door_cy, hinge_hi, furn, door_w=3.75):
    """Twin-sharing room on the west glass, drawn with true-size furniture.

    head 'S' / 'N' = the solid wall the two bed heads stand on.  The 6' x 7'
    ensuite sits in the passage-side corner on the head side, so its 7' depth
    lines up with the 7' beds; the other side is a 6'-2" to 8'-0" deep zone
    (entry + foot aisle + attendant sofa) that runs clear to the window."""
    ty1, ty2 = (y1, y1 + TD) if head == "S" else (y2 - TD, y2)
    side = "south" if head == "S" else "north"
    room = R(f"twin{n}", f"TWIN SHARING {n}", X1, y1, 49.0, y2, "inpatient",
             doors=[(X1 - T / 2, door_cy, door_w, "E")], furniture=furn,
             holes=[(X1, ty1, X1 + TW, ty2)],
             notes=f"2 beds 3'-3\" x 7'-0\", heads on the solid {side} wall; "
                   "lockers, wardrobe, attendant sofa; ensuite 6' x 7'")
    if hinge_hi:
        HINGE_HI.add((X1 - T / 2, door_cy))
    tx = X1 + 0.5
    if head == "S":      # fixtures on the toilet's south wall, door in its north wall
        tdoor = (X1 + 4.425, ty2 + T / 2, 3.0, "N")
        fx = [("wc", tx, ty1 + 0.1, 1.6, 2.2, 180), ("sink", tx + 2.6, ty1 + 0.1, 1.3, 1.3, 0),
              ("shower", X1 + 0.15, ty2 - 2.65, 2.5, 2.5, 0)]
    else:
        tdoor = (X1 + 4.425, ty1 - T / 2, 3.0, "S")
        fx = [("wc", tx, ty2 - 2.3, 1.6, 2.2, 0), ("sink", tx + 2.6, ty2 - 1.4, 1.3, 1.3, 0),
              ("shower", X1 + 0.15, ty1 + 0.15, 2.5, 2.5, 0)]
    HINGE_HI.add(tdoor[:2])
    toilet = R(f"wcW{n}", "T (Acc.)", X1, ty1, X1 + TW, ty2, "wet", doors=[tdoor], furniture=fx)
    return [room, toilet]


def _bed(x, y, head):          # N-S bed 3'-3" x 7'-0"; head 'S' or 'N'
    return ("bed", x, y, 3.25, 7.0, 180 if head == "S" else 0)


def _lk(x, y):                 # bedside locker 1'-6" x 1'-6"
    return ("side", x, y, 1.5, 1.5, 0)


# IPD dimension strings: room -> ((x, y) of the E-W string, (x, y) of the N-S string)
IPD_PTS = {
    "twin1": ((30.0, 54.55), (26.95, 56.0)),
    "twin2": ((30.0, 73.65), (35.42, 70.0)),
    "twin3": ((28.0, 88.3), (24.97, 85.0)),
    "twin4": ((5.0, 87.4), (7.9, 80.0)),
}


def layout_h_rooms():
    """LAYOUT H - the architect's parti kept (OT 20'x17', twin-sharing rooms on
    the west glass, a 12' public hall), re-planned on the DWG geometry:

    * OT in the SE corner; patients reach it only through Recovery / Pre-op,
      staff only through Change -> Scrub; CSSD beside the OT with a pass box;
      soiled goods leave through Dirty Utility and a 3'-6" service passage
      that opens beside the main door (never through the public hall).
    * The 12' passage is turned east-west as a waiting concourse that ends on
      the west glass; X-ray / dressing / plaster sits at its mouth.
    * OPD wing on the west glass; psychiatry at the dead end behind its own
      sub-wait door.
    * Ward: 6'-6" passage, four twin rooms (8 beds) drawn with true-size
      furniture, every room with a window and an ensuite (three are 6'-0" x
      7'-0" wheelchair size); nursing station at the ward door.  Rev. of
      17-11-2026 (IPD fix): the earlier five-room / 10-bed version only worked
      with under-size bed, locker and wardrobe symbols.
    """
    rooms = [
        # ------------------------------------------------ OT complex (south-east)
        R("ot", "OPERATION THEATRE", 0.46, 0.46, 20.46, 17.46, "surgical",
          doors=[(16.6, 17.65, 5.0, "S"), (3.2, 17.65, 3.0, "N"), (20.65, 14.5, 3.5, "W")],
          furniture=[("ottable", 9.2, 5.6, 2.6, 6.5, 0), ("light", 9.75, 7.6, 1.5, 1.5, 0),
                     ("cart", 5.6, 4.6, 1.8, 2.6, 0), ("cart", 13.4, 7.4, 1.8, 2.6, 0),
                     ("counter", 0.7, 3.0, 1.6, 8.0, 0),
                     ("shelf", 12.0, 0.7, 6.0, 1.2, 0)],
          notes="Patients only via Recovery; staff only via Scrub; soiled out via Dirty Utility"),
        R("otstore", "Sterile Store", 20.835, 0.46, 26.835, 4.6, "support",
          doors=[(24.9, 4.79, 2.5, "S")],
          furniture=[("shelf", 25.4, 0.7, 1.2, 2.2, 0), ("shelf", 23.1, 0.65, 2.2, 1.2, 0)]),
        R("cssd", "CSSD / Autoclave", 20.835, 4.975, 26.835, 11.6, "surgical",
          doors=[(24.4, 11.79, 2.6, "S")],
          furniture=[("counter", 25.3, 5.2, 1.4, 3.6, 0), ("cart", 21.1, 5.2, 2.0, 2.0, 0),
                     ("sink", 21.2, 9.9, 1.3, 1.3, 0)],
          notes="Beside the OT; used sets in / sterile sets out through the pass box"),
        R("scrub", "Scrub", 20.835, 11.975, 26.835, 17.46, "surgical",
          doors=[(25.0, 17.65, 2.8, "S")],
          furniture=[("sink", 25.3, 12.4, 1.3, 1.3, 0), ("sink", 25.3, 14.2, 1.3, 1.3, 0)]),
        R("change", "Staff Change", 20.835, 17.835, 26.835, 27.4, "surgical",
          doors=[(27.02, 25.3, 2.8, "W"), (20.65, 25.3, 2.8, "W")],
          furniture=[("shelf", 25.5, 18.1, 1.2, 5.0, 0), ("shelf", 21.0, 18.0, 1.2, 2.2, 0)],
          notes="Only staff way in: OPD passage -> change -> scrub -> OT"),
        R("recovery", "RECOVERY / PRE-OP", 6.375, 17.835, 20.46, 27.4, "surgical",
          doors=[(16.9, 27.59, 5.0, "S")],
          furniture=[("bed", 6.5, 18.0, 6.6, 3.25, 180), ("bed", 6.5, 24.0, 6.6, 3.25, 180),
                     ("side", 6.6, 21.4, 1.4, 1.2, 0), ("side", 6.6, 22.7, 1.4, 1.2, 0),
                     ("desk", 19.0, 18.2, 1.3, 3.0, 0)],
          notes="2 beds; 5'-0\" double doors in line: hall -> recovery -> OT"),
        R("dirty", "Dirty Utility", 0.46, 17.835, 6.0, 27.4, "support",
          doors=[(2.2, 27.59, 2.8, "N")],
          furniture=[("sink", 0.8, 18.4, 1.4, 1.4, 0), ("counter", 0.7, 20.6, 1.6, 4.0, 0),
                     ("cart", 0.7, 25.0, 2.0, 1.5, 0)],
          notes="Sluice + bio-medical waste hold; exit to the service passage"),
        R("xray", "X-RAY (mobile) /\nDRESSING / PLASTER", 4.375, 27.775, 13.9, 39.8, "consult",
          doors=[(14.09, 33.5, 4.0, "W")],
          furniture=[("exam", 5.0, 28.6, 2.6, 6.6, 0), ("counter", 4.7, 38.1, 5.0, 1.4, 0),
                     ("desk", 11.2, 37.6, 2.4, 1.6, 0), ("cart", 8.2, 35.6, 1.8, 2.2, 0)],
          notes="Lead-lined; sized for a mobile DR unit, not a fixed AERB room"),
        # ------------------------------------------------ OPD wing (south-west)
        R("psywait", "Psy. Sub-wait", 27.21, 0.46, 33.21, 9.46, "public",
          doors=[(30.2, 9.65, 3.0, "S")],
          furniture=[("chair", 27.5, 1.0, 1.5, 1.5, 0), ("chair", 27.5, 2.7, 1.5, 1.5, 0),
                     ("chair", 27.5, 4.4, 1.5, 1.5, 0), ("plant", 27.5, 7.6, 1.4, 1.4, 0)],
          notes="Closed lobby: no through traffic, acoustic door"),
        R("psy", "OPD 3 · PSYCHIATRY", 33.585, 0.46, 49.0, 9.46, "consult",
          doors=[(33.4, 7.7, 3.0, "E")],
          furniture=[("sofa", 34.2, 0.7, 5.0, 2.3, 0), ("chair", 39.8, 3.6, 1.5, 1.5, 0), ("chair", 41.8, 3.6, 1.5, 1.5, 0),
                     ("desk", 39.6, 5.4, 4.0, 2.0, 0), ("chair", 40.8, 7.7, 1.5, 1.5, 0),
                     ("plant", 43.2, 1.0, 1.4, 1.4, 0)],
          notes="Dr. Heena; quiet end, SW glass, sofa seating, no couch"),
        R("opd2", "OPD 2", 33.585, 9.835, 49.0, 18.2, "consult",
          doors=[(33.4, 16.5, 3.0, "E")],
          furniture=[("exam", 34.0, 10.100, 6.0, 2.25, 0), ("chair", 39.6, 12.600, 1.5, 1.4, 0),
                     ("chair", 41.4, 12.600, 1.5, 1.4, 0), ("desk", 39.4, 14.200, 4.0, 1.9, 0),
                     ("chair", 40.6, 16.400, 1.5, 1.4, 0)],
          notes="Visiting consultant; buffer between ortho and psychiatry"),
        R("opd1", "OPD 1 · ORTHO", 33.585, 18.575, 49.0, 27.4, "consult",
          doors=[(33.4, 25.7, 3.0, "E")],
          furniture=[("exam", 34.0, 18.840, 6.0, 2.25, 0), ("chair", 39.6, 21.575, 1.5, 1.5, 0),
                     ("chair", 41.4, 21.575, 1.5, 1.5, 0), ("desk", 39.4, 23.275, 4.0, 2.0, 0),
                     ("chair", 40.6, 25.575, 1.5, 1.5, 0)],
          notes="Dr. Aman; first door off the hall, 35' from X-ray"),
        R("wc_acc", "T (Acc.)", 35.6, 32.5, 49.0, 39.76, "wet",
          doors=[(35.41, 36.3, 3.0, "W")],
          furniture=[("wc", 38.3, 37.3, 1.6, 2.2, 0), ("sink", 36.0, 33.0, 1.3, 1.3, 0)],
          notes="Public wheelchair WC on the builder's toilet position"),
        # ------------------------------------------------ entry
        R("pharm", "PHARMACY", 4.705, 48.56, 11.125, 54.5, "public",
          doors=[(11.31, 52.6, 2.6, "W")],
          furniture=[("counter", 5.0, 48.8, 5.8, 1.5, 0), ("shelf", 4.9, 53.0, 4.2, 1.2, 0)],
          notes="Hatch to the entrance lobby, on the way out"),
        R("duct", "Duct", 0.46, 48.56, 4.33, 51.38, "support", dims=""),
        R("wc_staff", "T", 0.46, 51.84, 4.33, 59.68, "wet",
          doors=[(4.52, 57.6, 2.5, "W")],
          furniture=[("wc", 1.6, 52.2, 1.6, 2.2, 0), ("sink", 0.9, 55.2, 1.3, 1.3, 0),
                     ("shower", 0.7, 57.6, 1.9, 1.9, 0)],
          notes="Staff WC + shower on the builder's toilet position"),
        # ------------------------------------------------ ward support (east band)
        R("clean", "Clean Utility", 0.46, 60.055, 4.33, 68.6, "support",
          doors=[(4.52, 61.6, 2.5, "W")],
          furniture=[("shelf", 0.7, 63.2, 1.2, 5.0, 0)]),
        R("pantry", "Pantry", 4.705, 62.875, 11.125, 68.6, "support",
          doors=[(11.31, 64.6, 2.6, "W")],
          furniture=[("counter", 5.0, 66.9, 5.8, 1.5, 0), ("sink", 5.2, 63.2, 1.3, 1.3, 0)]),
        # ------------------------------------------------ wards
        R("twin4", "TWIN SHARING 4", 0.46, 68.975, 11.125, 91.9, "inpatient",
          doors=[(11.31, 71.9, 3.75, "W")],
          holes=[(0.46, 68.975, 6.46, 77.0)],
          furniture=[("bed", 0.56, 77.45, 7.0, 3.25, 180), ("bed", 0.56, 83.7, 7.0, 3.25, 180),
                     _lk(0.56, 80.7), _lk(0.56, 82.2),
                     ("sofa", 1.7, 89.8, 5.5, 2.0, 0), ("wardrobe", 9.025, 87.8, 2.0, 4.0, 0)],
          notes="North window; 2 beds, heads on the solid east party wall; attendant sofa under the window"),
        # column C9 stands in the SE corner: the toilet is 8'-0" deep so that a
        # clear 6'-0" x 5'-3" remains north of the column
        R("wcN4", "T", 0.46, 68.975, 6.46, 77.0, "wet",
          doors=[(6.65, 75.0, 2.75, "W")],
          furniture=[("wc", 2.7, 69.1, 1.6, 2.2, 180), ("sink", 4.8, 69.1, 1.3, 1.3, 0),
                     ("shower", 0.6, 74.4, 2.5, 2.5, 0)]),
    ]
    # twin rooms on the west glass (south -> north)
    #   1: heads on the solid north wall (ensuite back-to-back with room 2)
    #   2, 3: heads on the solid south wall
    rooms += _twin(1, 48.56, 62.56, "N", 52.475, False,
                   [_bed(27.4, 55.46, "N"), _bed(34.15, 55.46, "N"),
                    _lk(30.75, 60.96), _lk(32.55, 60.96),
                    ("wardrobe", 22.6, 48.66, 4.0, 2.0, 0),
                    ("sofa", 27.3, 48.66, 5.5, 2.0, 180), ("sofa", 33.1, 48.66, 5.5, 2.0, 180)])
    rooms += _twin(2, 62.935, 76.535, "S", 73.725, True,
                   [_bed(25.4, 63.035, "S"), _bed(31.65, 63.035, "S"),
                    _lk(28.65, 63.035), _lk(30.15, 63.035),
                    ("wardrobe", 25.0, 74.435, 4.0, 2.0, 0), ("sofa", 29.6, 74.435, 5.5, 2.0, 0),
                    ("chair", 35.2, 72.0, 1.5, 1.5, 0)])
    rooms += _twin(3, 76.91, 91.9, "S", 86.875, True,
                   [_bed(24.95, 77.01, "S"), _bed(31.2, 77.01, "S"),
                    _lk(28.2, 77.01), _lk(29.7, 77.01),
                    ("wardrobe", 22.7, 89.8, 4.0, 2.0, 0), ("sofa", 26.9, 89.35, 5.5, 2.0, 0),
                    ("chair", 33.2, 85.2, 1.5, 1.5, 0)])
    # ---------------------------------------------------- circulation anchors
    seats = ([("chair", 21.1 + 1.6 * i, 28.0, 1.5, 1.5, 0) for i in range(3)]
             + [("chair", 33.9 + 1.6 * i, 28.0, 1.5, 1.5, 0) for i in range(5)]
             + [("chair", 23.2 + 1.6 * i, 38.1, 1.5, 1.5, 0) for i in range(7)])
    rooms += [
        R("wait", "12'-0\" w. WAITING CONCOURSE", 20.84, 31.6, 35.0, 35.6, "circ",
          furniture=seats + [("water", 34.0, 30.4, 1.2, 1.2, 0), ("plant", 41.0, 30.2, 1.4, 1.4, 0)]),
        R("gate", "gate 6'-1\"", 14.3, 36.0, 20.3, 39.0, "circ"),
        R("opdpass", "6'-0\" w. OPD passage", 27.21, 11.0, 33.21, 24.0, "circ"),
        R("svc", "3'-6\" dirty exit", 0.46, 29.0, 4.0, 38.0, "circ"),
        R("lobby", "ENTRANCE LOBBY", 4.0, 41.2, 19.0, 47.0, "circ"),
        R("recep", "RECEPTION", 20.2, 42.6, 24.3, 46.2, "circ",
          furniture=[("counter", 20.3, 41.1, 1.7, 6.2, 0), ("chair", 22.5, 42.0, 1.5, 1.5, 0),
                     ("chair", 22.5, 45.0, 1.5, 1.5, 0)]),
        R("ns", "NURSING STN.", 4.705, 55.0, 9.4, 60.4, "circ",
          furniture=[("counter", 9.6, 55.2, 1.6, 4.9, 0), ("chair", 7.4, 56.2, 1.5, 1.5, 0),
                     ("chair", 7.4, 58.4, 1.5, 1.5, 0), ("shelf", 5.0, 61.0, 3.8, 1.2, 0)]),
        R("wardcorr", "6'-6\" w. WARD PASSAGE", 11.5, 60.0, 18.0, 88.0, "circ",
          doors=[(14.75, 48.33, 5.0, "N"), (2.2, 40.01, 2.8, "N")],
          furniture=[("chair", 12.0, 90.0, 1.5, 1.5, 0), ("plant", 16.2, 90.1, 1.4, 1.4, 0)]),
    ]
    import ipd
    for r in rooms:                      # schedule sizes = the measured clear strings
        if r.key in IPD_PTS:
            (wx, wy), (dx, dy) = IPD_PTS[r.key]
            a, b = ipd.span(r.poly, wx, wy, "x")
            c, d = ipd.span(r.poly, dx, dy, "y")
            r.dims = f"{fi(b - a)} x {fi(d - c)}"
        elif r.key.startswith(("wcW", "wcN")):
            tw, td, _ = ipd.toilet_size(r.poly)
            r.dims = f"{fi(tw)} x {fi(td)}"
    return rooms


TITLE_H = "LAYOUT H - architect plan improved, DWG geometry"


# ------------------------------------------------------------------ geometry
def walls_h(rooms):
    """True-thickness wall bands for Layout H."""
    solids = [r.poly for r in rooms if r.zone != "circ"]
    grown = unary_union([p.buffer(T, join_style=2) for p in solids])
    walls = grown.difference(unary_union(solids))
    perimeter = PLATE_H.difference(INNER_H)
    cut_ring = CUTOUT_H.buffer(EXT, join_style=2).difference(CUTOUT_H)
    walls = unary_union([walls, perimeter, cut_ring] + EXTRA_WALLS_H + list(COLUMNS_H.values()))
    walls = walls.intersection(PLATE_H).difference(CUTOUT_H)
    cols = unary_union(list(COLUMNS_H.values()))
    openings = []
    for r in rooms:
        for (cx, cy, w, side) in r.doors:
            openings.append(box(cx - w / 2, cy - 0.6, cx + w / 2, cy + 0.6) if side in ("N", "S")
                            else box(cx - 0.6, cy - w / 2, cx + 0.6, cy + w / 2))
    for (cx, cy, w, o, _) in HATCHES_H:
        openings.append(box(cx - w / 2, cy - 0.3, cx + w / 2, cy + 0.3) if o == "h"
                        else box(cx - 0.3, cy - w / 2, cx + 0.3, cy + w / 2))
    walls = walls.difference(unary_union(openings).difference(cols))
    _, y1, y2 = MD_DOOR_H
    return walls.difference(box(-1.0, y1, 1.0, y2))


def circulation_h(rooms):
    solids = unary_union([r.poly for r in rooms if r.zone != "circ"])
    return INNER_H.difference(solids).difference(walls_h(rooms)).difference(CUTOUT_H)


@contextmanager
def h_geometry():
    """Temporarily point the generic tools (render, blueprint_svg, dxf_export,
    render3d) at the DWG geometry so they can draw Layout H unchanged."""
    import importlib
    names = dict(PLATE=PLATE_H, CUTOUT=CUTOUT_H, GLASS_WEST=GLASS_WEST_H,
                 GLASS_NORTH=GLASS_NORTH_H, MD_DOOR=MD_DOOR_H, wall_bands=walls_h,
                 circulation_poly=circulation_h)
    saved = []
    for modname in ("plan_model", "render", "blueprint_svg", "dxf_export", "render3d"):
        try:
            mod = importlib.import_module(modname)
        except Exception:
            continue
        for k, v in names.items():
            if hasattr(mod, k):
                saved.append((mod, k, getattr(mod, k)))
                setattr(mod, k, v)
    try:
        yield
    finally:
        for mod, k, v in saved:
            setattr(mod, k, v)


plan_model.LAYOUTS["H"] = (TITLE_H, layout_h_rooms)
