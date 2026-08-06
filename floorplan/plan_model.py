"""Parametric model of the 7th-floor hospital plan, Solaris Shine, Althan, Surat.

Coordinate system (matches Ar. Bankim Dave's sheet orientation):
  x : feet from the EAST facade, increasing WESTWARD  (sheet left -> right)
  y : feet from the SOUTH wall, increasing NORTHWARD  (sheet top  -> bottom)
Rendering inverts the y axis so the sheet reads exactly like the architect's
drawing (South at top, North at bottom, East left, West right).
"""
from dataclasses import dataclass, field
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

WALL = 0.375          # internal wall thickness (4.5")
CEIL_H = 9.5          # slab-to-ceiling, for the 3D view

# ---------------------------------------------------------------- floor plate
# Traced from the dimensioned JPG (DWG not convertible in this environment).
# East edge straight; west facade angled inward toward north; curved NW corner.
PLATE_PTS = [
    (0.0, 0.0),        # SE corner (sheet top-left)
    (48.5, 0.0),       # SW corner
    (44.5, 40.0),      # west facade, angling east as it runs north
    (43.0, 55.0),
    (41.5, 70.0),
    (39.5, 88.0),
    (38.8, 92.0),
    (36.5, 97.5),      # start of curved corner
    (33.0, 100.2),
    (29.0, 101.0),     # curve meets north edge
    (0.0, 101.0),      # NE corner
]
PLATE = Polygon(PLATE_PTS)

# Cut-out void (open shaft) against the west facade, mid-plan
CUTOUT = Polygon([(27.5, 48.0), (43.9, 48.0), (42.6, 60.5), (27.5, 60.5)])

# Openable-glass bands (drawn outside the plate edge)
GLASS_WEST = [((48.5, 0.0), (44.5, 40.0)), ((44.5, 40.0), (43.0, 55.0)),
              ((43.0, 55.0), (41.5, 70.0)), ((41.5, 70.0), (38.8, 92.0))]
GLASS_NORTH = [((29.0, 101.0), (10.0, 101.0))]

MD_DOOR = (0.0, 49.5, 53.5)   # main double door on east facade, y-span


@dataclass
class Room:
    key: str
    name: str
    dims: str                 # printed dimension string
    rect: tuple               # (x, y, w, h) feet
    zone: str
    doors: list = field(default_factory=list)   # (cx, cy, width, wall NSEW)
    furniture: list = field(default_factory=list)  # (kind, x, y, w, h, rot)
    holes: list = field(default_factory=list)   # (x, y, w, h) nested rooms to subtract
    notes: str = ""

    @property
    def poly(self) -> Polygon:
        x, y, w, h = self.rect
        p = box(x, y, x + w, y + h).intersection(PLATE)
        if p.intersects(CUTOUT):
            p = p.difference(CUTOUT)
        for hx, hy, hw, hh in self.holes:
            p = p.difference(box(hx, hy, hx + hw, hy + hh))
        return p

    @property
    def area(self) -> float:
        return self.poly.area


ZONES = {
    "surgical":  ("#d9ead3", "Surgical / sterile"),
    "consult":   ("#d0e0f0", "Consult / OPD"),
    "public":    ("#fdf3d8", "Public / reception"),
    "inpatient": ("#e6e0f0", "Inpatient wing"),
    "support":   ("#e8e8e4", "Support / stores"),
    "wet":       ("#d8eef0", "Toilets / wet"),
    "circ":      ("#f7f6f2", "Circulation"),
}


def _south_block():
    """South consult/surgical block - shared by architect plan and Layout A."""
    return [
        Room("wc_dr", "Toilet", "3'-10½\" x 6'-4\"", (0.4, 0.4, 3.9, 6.3), "wet",
             doors=[(4.3, 5.2, 2.2, "E")],
             furniture=[("wc", 1.4, 1.6, 1.6, 2.2, 0), ("sink", 1.2, 4.8, 1.5, 1.2, 0),
                        ("shower", 3.0, 0.6, 0.9, 0.9, 0)]),
        Room("autoclave", "Autoclave + Scrub", "10'-8\" x 5'-0\"", (4.7, 0.4, 10.7, 5.0), "surgical",
             doors=[(10.0, 5.4, 2.5, "N")],
             furniture=[("counter", 5.0, 0.6, 10.0, 1.9, 0)]),
        Room("doctor", "Doctor Room 1", "15'-0\" x 13'-1\" (attached WC)", (0.4, 5.8, 15.0, 7.7), "consult",
             holes=[(0.4, 0.4, 3.9, 6.3)],
             doors=[(13.0, 13.5, 2.8, "N")],
             furniture=[("desk", 6.2, 8.6, 4.0, 2.3, 0), ("chair", 5.0, 9.4, 1.4, 1.4, 0),
                        ("chair", 10.6, 8.0, 1.4, 1.4, 0), ("chair", 10.6, 10.4, 1.4, 1.4, 0),
                        ("exam", 1.2, 6.4, 2.25, 5.5, 0)]),
        Room("store", "Store Room", "4'-9\" x 9'-9½\"", (15.8, 0.4, 4.75, 9.8), "support",
             doors=[(18.2, 10.2, 2.5, "N")],
             furniture=[("shelf", 16.0, 0.6, 1.2, 9.2, 0), ("shelf", 19.3, 0.6, 1.2, 9.2, 0)]),
        Room("opd1", "OPD 1 (Doctor Rm 2)", "12'-0\" x 9'-9½\"", (20.9, 0.4, 12.0, 9.8), "consult",
             doors=[(30.5, 10.2, 2.8, "N")],
             furniture=[("desk", 23.5, 4.8, 6.0, 2.3, 0), ("chair", 25.6, 2.9, 1.4, 1.4, 0),
                        ("chair", 23.6, 7.6, 1.4, 1.4, 0), ("chair", 26.2, 7.6, 1.4, 1.4, 0),
                        ("exam", 21.3, 0.7, 2.25, 5.5, 0)]),
        Room("opd2", "OPD 2 (Doctor Rm 3)", "12'-3\" x 9'-9½\"", (35.4, 0.4, 12.25, 9.8), "consult",
             doors=[(36.6, 10.2, 2.8, "N")],
             furniture=[("desk", 38.0, 4.8, 6.0, 2.3, 0), ("chair", 40.2, 2.9, 1.4, 1.4, 0),
                        ("chair", 38.2, 7.6, 1.4, 1.4, 0), ("chair", 40.8, 7.6, 1.4, 1.4, 0),
                        ("exam", 35.7, 0.7, 2.25, 5.5, 0)]),
        Room("exam_mid", "Exam", "2'-3\" x 5'-6\"", (33.0, 0.4, 2.0, 9.8), "consult",
             furniture=[("exam", 33.2, 1.2, 1.9, 5.5, 0)]),
        Room("ot", "OPERATION THEATRE", "20'-0\" x 17'-0\"", (0.4, 16.3, 20.6, 17.0), "surgical",
             doors=[(21.4, 24.5, 4.0, "E")],
             furniture=[("ottable", 8.5, 22.0, 2.6, 6.5, 15), ("counter", 1.0, 16.6, 6.0, 1.5, 0),
                        ("cart", 16.5, 19.0, 1.8, 2.6, 0), ("cart", 16.5, 28.0, 1.8, 2.6, 0),
                        ("light", 10.2, 20.0, 1.5, 1.5, 0)]),
    ]


def _north_wing():
    """Inpatient wing - unchanged from the architect's plan (A and B)."""
    return [
        Room("duct", "Duct / V", "", (0.4, 55.2, 4.0, 5.6), "support"),
        Room("wc_c1", "Toilet (Acc.)", "3'-10½\" x 7'-10\"", (0.4, 61.2, 3.9, 7.8), "wet",
             doors=[(4.4, 66.8, 2.4, "E")],
             furniture=[("wc", 1.3, 62.4, 1.6, 2.2, 0), ("sink", 1.2, 67.4, 1.5, 1.2, 0)]),
        Room("nursing", "NURSING STATION", "7'-6\" x 8'-10½\"", (6.5, 60.3, 7.5, 8.9), "inpatient",
             doors=[(14.1, 64.5, 2.8, "E")],
             furniture=[("counter", 6.8, 60.6, 7.0, 1.8, 0), ("counter", 12.2, 62.3, 1.7, 6.0, 0),
                        ("chair", 8.6, 63.4, 1.4, 1.4, 0), ("chair", 10.6, 64.8, 1.4, 1.4, 0)]),
        Room("single1", "Single Room 1", "11'-10\" x 8'-0\"", (4.4, 69.8, 11.8, 8.0), "inpatient",
             doors=[(14.0, 78.0, 2.8, "N")],
             furniture=[("bed", 5.0, 70.6, 3.2, 6.6, 0), ("side", 8.6, 70.4, 1.4, 1.6, 0)]),
        Room("single2", "Single Room 2", "11'-10\" x 9'-0\"", (0.4, 78.4, 11.8, 9.0), "inpatient",
             doors=[(10.0, 87.6, 2.8, "N")],
             furniture=[("bed", 1.2, 79.4, 3.2, 6.6, 0), ("side", 4.8, 79.2, 1.4, 1.6, 0)]),
        Room("wc_p1", "Toilet", "5'-9½\" x 5'-0\"", (4.6, 87.8, 5.8, 5.0), "wet",
             doors=[(10.6, 89.4, 2.2, "E")],
             furniture=[("wc", 5.4, 88.6, 1.6, 2.2, 0), ("sink", 8.6, 88.4, 1.5, 1.2, 0)]),
        Room("wc_p2", "Toilet", "5'-9½\" x 5'-0\"", (10.8, 90.4, 5.8, 5.0), "wet",
             doors=[(16.8, 92.2, 2.2, "E")],
             furniture=[("wc", 11.6, 91.2, 1.6, 2.2, 0), ("sink", 14.8, 91.0, 1.5, 1.2, 0)]),
        Room("single3", "Single Room 3", "11'-10\" x 9'-0\"", (0.4, 91.6, 11.8, 9.0), "inpatient",
             holes=[(4.6, 87.8, 5.8, 5.0), (10.8, 90.4, 5.8, 5.0)],
             doors=[(9.6, 91.5, 2.8, "N")],
             furniture=[("bed", 1.2, 92.8, 3.2, 6.6, 0), ("side", 4.8, 92.6, 1.4, 1.6, 0)]),
        Room("twin1", "Twin Sharing 1", "21'-4¼\" x 9'-2\"", (21.6, 58.3, 21.35, 9.2), "inpatient",
             doors=[(21.7, 63.0, 2.8, "W")],
             furniture=[("bed", 23.0, 59.2, 3.2, 6.6, 0), ("side", 26.6, 59.0, 1.4, 1.6, 0),
                        ("bed", 29.4, 59.2, 3.2, 6.6, 0), ("side", 33.0, 59.0, 1.4, 1.6, 0),
                        ("wc", 39.0, 59.4, 1.6, 2.2, 0), ("sink", 37.4, 62.0, 1.5, 1.2, 0)]),
        Room("twin2", "Twin Sharing 2", "18'-4\" x 9'-0\"", (21.6, 68.6, 18.3, 9.0), "inpatient",
             doors=[(21.7, 73.0, 2.8, "W")],
             furniture=[("bed", 23.0, 69.6, 3.2, 6.6, 0), ("side", 26.6, 69.4, 1.4, 1.6, 0),
                        ("bed", 29.4, 69.6, 3.2, 6.6, 0), ("side", 33.0, 69.4, 1.4, 1.6, 0),
                        ("wc", 36.6, 69.8, 1.6, 2.2, 0), ("sink", 35.2, 72.4, 1.5, 1.2, 0)]),
        Room("single4", "Single Room 4", "16'-0\" x 9'-0\"", (21.3, 78.2, 16.0, 9.0), "inpatient",
             doors=[(21.4, 83.0, 2.8, "W")],
             furniture=[("bed", 22.6, 79.2, 3.2, 6.6, 0), ("side", 26.2, 79.0, 1.4, 1.6, 0),
                        ("wc", 33.4, 79.0, 1.6, 2.2, 0), ("sink", 32.0, 81.8, 1.5, 1.2, 0)]),
        Room("single5", "Single Room 5", "14'-8\" x 10'-1½\"", (20.4, 87.8, 14.7, 10.1), "inpatient",
             doors=[(20.5, 92.6, 2.8, "W")],
             furniture=[("bed", 21.8, 88.8, 3.2, 6.6, 0), ("side", 25.4, 88.6, 1.4, 1.6, 0),
                        ("wc", 30.6, 88.8, 1.6, 2.2, 0), ("sink", 29.2, 91.4, 1.5, 1.2, 0)]),
        Room("pantry", "Pantry", "7'-9½\" x 5'-6½\"", (12.4, 95.0, 7.8, 5.6), "support",
             doors=[(13.4, 94.9, 2.4, "S")],
             furniture=[("counter", 12.7, 98.8, 7.2, 1.5, 0)]),
    ]


def _circulation_common():
    return [
        Room("pass3", "3'-0\" w. Passage", "", (15.8, 10.6, 17.2, 3.0), "circ"),
        Room("spine", "12'-1½\" w. Passage", "", (21.5, 13.9, 12.1, 32.4), "circ"),
        Room("lobby", "ENTRANCE LOBBY", "", (0.4, 46.6, 21.1, 8.2), "circ"),
        Room("conn", "", "", (17.5, 34.3, 4.0, 12.3), "circ"),
        Room("pass5", "5'-0\" w. Passage", "", (16.6, 55.2, 4.9, 23.0), "circ"),
        Room("pass79", "7'-9½\" w. Passage", "", (13.0, 78.2, 7.9, 16.6), "circ"),
    ]


# --------------------------------------------------------- architect original
def architect_rooms():
    rooms = _south_block() + _north_wing() + _circulation_common()
    rooms += [
        Room("opd3", "OPD 3", "11'-9½\" x 9'-0\"", (34.5, 11.0, 11.8, 9.0), "consult",
             doors=[(34.4, 15.0, 2.8, "W")]),
        Room("recovery", "Recovery Room", "10'-5½\" x 6'-1\"", (36.4, 26.9, 10.5, 6.1), "surgical",
             doors=[(36.3, 29.8, 2.8, "W")]),
        Room("xray", "X-ray / Dressing", "9'-6½\" x 6'-1\"", (36.9, 33.9, 9.55, 6.1), "consult",
             doors=[(36.8, 36.8, 2.8, "W")]),
        Room("pharm", "Pharmacy", "6'-9½\" x 4'-1\"", (27.4, 41.0, 6.8, 4.1), "public",
             doors=[(27.3, 43.0, 2.4, "W")]),
        Room("wc_w", "Toilet", "5'-6\" x 3'-10½\"", (40.2, 41.0, 4.0, 4.2), "wet",
             doors=[(40.1, 43.0, 2.2, "W")]),
        Room("recep", "Reception", "", (20.0, 46.8, 7.4, 6.2), "public",
             furniture=[("counter", 20.4, 48.0, 2.0, 5.0, 0)]),
        Room("wait", "Waiting Area", "17'-3½\" x 12'-0\"", (0.4, 34.3, 17.0, 12.0), "public"),
    ]
    return rooms


# ------------------------------------------------------------------- Layout A
def layout_a_rooms():
    """Targeted revision: fixes the three flagged flaws, everything else kept."""
    rooms = _south_block() + _north_wing() + _circulation_common()
    rooms += [
        Room("opd3", "OPD 3", "11'-9½\" x 9'-0\"", (34.5, 11.0, 11.8, 9.0), "consult",
             doors=[(34.4, 15.0, 2.8, "W")],
             furniture=[("desk", 36.6, 15.8, 5.5, 2.2, 0), ("chair", 38.6, 14.0, 1.4, 1.4, 0),
                        ("exam", 42.0, 11.4, 2.25, 5.5, 0)]),
        # FIX 1 - Recovery moved against the OT's north wall, direct door
        Room("recovery", "RECOVERY (2 beds)", "10'-6\" x 12'-0\"", (0.4, 34.3, 10.5, 12.0), "surgical",
             doors=[(6.0, 34.2, 3.0, "S"),        # direct door from OT
                    (8.5, 46.4, 3.0, "N")],       # discharge door to lobby
             furniture=[("bed", 1.2, 35.6, 3.2, 6.6, 0), ("side", 4.8, 35.4, 1.4, 1.6, 0),
                        ("bed", 1.2, 43.0, 3.2, 6.6, 90), ("cart", 8.6, 40.0, 1.8, 2.6, 0)],
             notes="East-facade windows; post-op patients never cross the corridor"),
        Room("xray", "X-Ray / Dressing", "6'-0\" x 12'-0\"", (11.3, 34.3, 6.0, 12.0), "consult",
             doors=[(17.4, 40.0, 2.8, "E")],
             furniture=[("exam", 12.0, 35.0, 2.25, 5.5, 0), ("counter", 11.6, 44.4, 5.2, 1.4, 0)],
             notes="Fronts the connector by the spine; lead-lined partition to Recovery"),
        # FIX 2 - Pharmacy on the exit path at the lobby / spine junction
        Room("pharm", "PHARMACY", "7'-6\" x 6'-6\"", (20.0, 46.6, 7.5, 6.5), "public",
             doors=[(24.0, 53.2, 3.0, "N")],
             furniture=[("counter", 20.4, 46.9, 6.6, 1.6, 0), ("shelf", 20.3, 51.4, 6.9, 1.3, 0)],
             notes="Dispensing counter faces the exit path 8 ft from the main door"),
        Room("recep", "RECEPTION", "9'-0\" x 6'-0\"", (2.0, 47.4, 9.0, 6.0), "public",
             furniture=[("counter", 3.0, 48.2, 6.5, 2.0, 0), ("chair", 4.4, 50.8, 1.4, 1.4, 0),
                        ("chair", 6.6, 50.8, 1.4, 1.4, 0)],
             notes="Desk faces the main door; clear sightline to the waiting area"),
        # FIX 3 - Waiting on the west openable-glass facade
        Room("subwait", "OPD sub-wait", "", (33.6, 20.3, 13.4, 6.3), "circ",
             furniture=[("chair", 42.2, 21.2, 1.4, 1.4, 0), ("chair", 42.2, 23.0, 1.4, 1.4, 0),
                        ("chair", 42.2, 24.8, 1.4, 1.4, 0)]),
        Room("wait", "WAITING / LOUNGE", "≈13' x 20' (18 seats)", (33.6, 27.0, 13.5, 20.5), "public",
             holes=[(40.0, 40.8, 4.5, 4.6)],
             doors=[(33.5, 31.0, 3.2, "W")],
             furniture=[("chair", 35.0, 28.2, 1.4, 1.4, 0), ("chair", 36.8, 28.2, 1.4, 1.4, 0),
                        ("chair", 38.6, 28.2, 1.4, 1.4, 0), ("chair", 40.4, 28.2, 1.4, 1.4, 0),
                        ("chair", 42.2, 28.2, 1.4, 1.4, 0),
                        ("chair", 35.0, 31.4, 1.4, 1.4, 0), ("chair", 36.8, 31.4, 1.4, 1.4, 0),
                        ("chair", 38.6, 31.4, 1.4, 1.4, 0), ("chair", 40.4, 31.4, 1.4, 1.4, 0),
                        ("chair", 35.0, 34.8, 1.4, 1.4, 0), ("chair", 36.8, 34.8, 1.4, 1.4, 0),
                        ("chair", 38.6, 34.8, 1.4, 1.4, 0), ("chair", 40.4, 34.8, 1.4, 1.4, 0),
                        ("chair", 42.0, 34.8, 1.4, 1.4, 0),
                        ("chair", 35.0, 38.2, 1.4, 1.4, 0), ("chair", 36.8, 38.2, 1.4, 1.4, 0),
                        ("chair", 38.6, 38.2, 1.4, 1.4, 0), ("chair", 40.2, 38.2, 1.4, 1.4, 0),
                        ("plant", 34.4, 43.6, 1.6, 1.6, 0), ("plant", 43.0, 28.0, 1.6, 1.6, 0),
                        ("tv", 34.0, 41.0, 0.8, 4.0, 0), ("water", 38.8, 43.6, 1.4, 1.4, 0)],
             notes="Full-height openable glass on the west; TV, plants, water dispenser"),
        Room("wc_w", "Acc. WC", "5'-6\" x 3'-10½\"", (40.2, 41.0, 4.0, 4.2), "wet",
             doors=[(40.1, 43.0, 2.2, "W")],
             furniture=[("wc", 41.0, 41.6, 1.6, 2.2, 0), ("sink", 43.0, 41.4, 1.2, 1.2, 0)]),
    ]
    return rooms


# ------------------------------------------------------------------- Layout B
def layout_b_rooms():
    """Fresh alternative: same plate + inpatient wing, re-zoned clinical core."""
    rooms = [r for r in _south_block() if r.key != "autoclave"]
    rooms += _north_wing() + _circulation_common()
    rooms += [
        Room("dirty", "Dirty Utility / CSSD", "10'-8\" x 5'-0\"", (4.7, 0.4, 10.7, 5.0), "support",
             doors=[(10.0, 5.4, 2.5, "N")],
             furniture=[("counter", 5.0, 0.6, 10.0, 1.9, 0)]),
        # Scrub + autoclave as a true anteroom on the OT's corridor wall
        Room("scrub", "Scrub + Autoclave", "5'-6\" x 6'-6\"", (21.9, 16.3, 5.5, 6.5), "surgical",
             doors=[(21.8, 19.5, 2.5, "W"), (27.5, 19.5, 2.5, "E")],
             furniture=[("sink", 22.3, 16.6, 1.5, 1.2, 0), ("counter", 22.2, 21.0, 4.8, 1.4, 0)],
             notes="Staff gown/scrub before entering the OT; spine locally 6'-7\" wide"),
        # X-ray/Dressing in the old OPD-3 slot - serves the consult cluster
        Room("xray", "X-RAY / DRESSING", "11'-9½\" x 9'-0\"", (34.5, 11.0, 11.8, 9.0), "consult",
             doors=[(34.4, 15.0, 2.8, "W")],
             furniture=[("exam", 41.6, 11.6, 2.25, 5.5, 0), ("counter", 35.0, 11.3, 5.0, 1.4, 0)],
             notes="Adjacent to all three consult rooms and 20 ft from the OT"),
        Room("recovery", "RECOVERY (2 beds)", "10'-6\" x 12'-0\"", (0.4, 34.3, 10.5, 12.0), "surgical",
             doors=[(6.0, 34.2, 3.0, "S"), (8.5, 46.4, 3.0, "N")],
             furniture=[("bed", 1.2, 35.6, 3.2, 6.6, 0), ("side", 4.8, 35.4, 1.4, 1.6, 0),
                        ("bed", 1.2, 43.0, 3.2, 6.6, 90), ("cart", 8.6, 40.0, 1.8, 2.6, 0)],
             notes="Direct door from the OT; east-facade windows"),
        Room("nurses", "Nurses' Duty / Rest", "6'-0\" x 12'-0\"", (11.3, 34.3, 6.0, 12.0), "inpatient",
             doors=[(17.4, 40.0, 2.8, "E")],
             furniture=[("bed", 12.0, 35.0, 2.8, 6.2, 0), ("desk", 11.8, 43.2, 4.0, 2.0, 0),
                        ("chair", 13.0, 41.4, 1.4, 1.4, 0)],
             notes="Rest bunk + lockers; accessible WC 15 ft along the corridor"),
        Room("pharm", "PHARMACY", "7'-6\" x 6'-6\"", (20.0, 46.6, 7.5, 6.5), "public",
             doors=[(24.0, 53.2, 3.0, "N")],
             furniture=[("counter", 20.4, 46.9, 6.6, 1.6, 0), ("shelf", 20.3, 51.4, 6.9, 1.3, 0)],
             notes="On the exit path; consultation window at the counter"),
        Room("recep", "RECEPTION", "9'-0\" x 6'-0\"", (2.0, 47.4, 9.0, 6.0), "public",
             furniture=[("counter", 3.0, 48.2, 6.5, 2.0, 0), ("chair", 4.4, 50.8, 1.4, 1.4, 0),
                        ("chair", 6.6, 50.8, 1.4, 1.4, 0)]),
        # Larger L-shaped waiting + recreation band on the full west glass run
        Room("wait", "WAITING + RECREATION", "≈13' x 27' (20+ seats)", (33.6, 20.5, 13.8, 27.0), "public",
             holes=[(40.0, 40.8, 4.5, 4.6)],
             doors=[(33.5, 24.0, 3.2, "W")],
             furniture=[("chair", 35.0, 21.6, 1.4, 1.4, 0), ("chair", 36.8, 21.6, 1.4, 1.4, 0),
                        ("chair", 38.6, 21.6, 1.4, 1.4, 0), ("chair", 40.4, 21.6, 1.4, 1.4, 0),
                        ("chair", 42.2, 21.6, 1.4, 1.4, 0),
                        ("chair", 35.0, 25.0, 1.4, 1.4, 0), ("chair", 36.8, 25.0, 1.4, 1.4, 0),
                        ("chair", 38.6, 25.0, 1.4, 1.4, 0), ("chair", 40.4, 25.0, 1.4, 1.4, 0),
                        ("chair", 42.2, 25.0, 1.4, 1.4, 0),
                        ("chair", 35.0, 28.4, 1.4, 1.4, 0), ("chair", 36.8, 28.4, 1.4, 1.4, 0),
                        ("chair", 38.6, 28.4, 1.4, 1.4, 0), ("chair", 40.4, 28.4, 1.4, 1.4, 0),
                        ("chair", 35.0, 31.8, 1.4, 1.4, 0), ("chair", 36.8, 31.8, 1.4, 1.4, 0),
                        ("chair", 38.6, 31.8, 1.4, 1.4, 0), ("chair", 40.2, 31.8, 1.4, 1.4, 0),
                        ("chair", 35.0, 35.2, 1.4, 1.4, 0), ("chair", 36.8, 35.2, 1.4, 1.4, 0),
                        ("tv", 34.0, 38.6, 0.8, 4.0, 0), ("water", 39.0, 43.0, 1.4, 1.4, 0),
                        ("plant", 34.4, 43.2, 1.6, 1.6, 0), ("plant", 43.2, 21.4, 1.6, 1.6, 0),
                        ("plant", 41.8, 43.0, 1.6, 1.6, 0)],
             notes="Recreation corner (TV, plants, kids nook) at the quiet south end"),
        Room("wc_w", "Acc. WC", "5'-6\" x 3'-10½\"", (40.2, 41.0, 4.0, 4.2), "wet",
             doors=[(40.1, 43.0, 2.2, "W")],
             furniture=[("wc", 41.0, 41.6, 1.6, 2.2, 0), ("sink", 43.0, 41.4, 1.2, 1.2, 0)]),
    ]
    return rooms


LAYOUTS = {
    "architect": ("Architect's Proposal (as received)", architect_rooms),
    "A": ("LAYOUT A — Targeted Revision", layout_a_rooms),
    "B": ("LAYOUT B — Fresh Alternative", layout_b_rooms),
}
