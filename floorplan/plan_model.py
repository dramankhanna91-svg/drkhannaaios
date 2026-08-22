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
# REVISION C (22-08-2026): envelope from a calibrated pixel survey of the
# architect's sheet, cross-checked against the builder's CAD PDF
# (19'-6.5" + 19'-6.5" + 8'-0" passage + 43'-9.5" + walls = 92'-0").
# East edge straight; west facade tapers; curved NW corner. 48'-6" x 92'-0".
PLATE_PTS = [
    (0.0, 0.0),        # SE corner (sheet top-left)
    (48.5, 0.0),       # SW corner
    (47.3, 10.0),      # west facade, tapering east as it runs north
    (45.8, 20.0),
    (44.3, 30.0),
    (43.6, 45.0),
    (41.5, 50.0),
    (39.9, 60.0),
    (38.5, 70.0),
    (37.1, 80.0),
    (36.2, 85.0),
    (35.0, 89.5),      # curve begins
    (33.5, 91.0),
    (31.0, 92.0),      # curve meets north wall
    (0.0, 92.0),       # NE corner
]
PLATE = Polygon(PLATE_PTS)

# Cut-out / service void against the west facade, at the waist
CUTOUT = Polygon([(25.6, 40.0), (44.0, 40.0), (42.7, 48.0), (25.6, 48.0)])

# Openable-glass bands (drawn outside the plate edge)
GLASS_WEST = [(PLATE_PTS[i], PLATE_PTS[i + 1]) for i in range(1, 13)]
GLASS_NORTH = [((31.0, 92.0), (10.0, 92.0))]

MD_DOOR = (0.0, 43.0, 48.0)   # main door on east facade, y-span (5'-0")


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
                        ("wc", 38.2, 62.0, 1.6, 2.2, 0), ("sink", 36.4, 64.6, 1.5, 1.2, 0)]),
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


# ------------------------------------------------- Layout C ("Arrival Hub")
def layout_c_rooms():
    """Fresh design around the arrival experience: generous lobby at the
    main door, reception with sightlines to door/waiting/corridors, pharmacy
    beside the exit, OT pod entered through a scrub anteroom, recovery
    discharging via a staff link, L-shaped waiting+recreation on the glass."""
    rooms = [
        # --- south consult block
        Room("wc_dr", "Toilet", "3'-10½\" x 6'-4\"", (0.4, 0.4, 3.9, 6.3), "wet",
             doors=[(4.3, 5.2, 2.2, "E")],
             furniture=[("wc", 1.4, 1.6, 1.6, 2.2, 0), ("sink", 1.2, 4.8, 1.5, 1.2, 0),
                        ("shower", 3.0, 0.6, 0.9, 0.9, 0)]),
        Room("cssd", "CSSD / Dirty Utility", "10'-8\" x 5'-0\"", (4.7, 0.4, 10.7, 5.0), "support",
             doors=[(10.0, 5.4, 2.5, "N")],
             furniture=[("counter", 5.0, 0.6, 10.0, 1.9, 0)]),
        Room("doctor", "Doctor Room 1", "15'-0\" x 13'-1\"\n(attached WC)", (0.4, 5.8, 15.0, 7.7), "consult",
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
        Room("exam_mid", "Exam", "2'-3\" x 5'-6\"", (33.0, 0.4, 2.0, 9.8), "consult",
             furniture=[("exam", 33.2, 1.2, 1.9, 5.5, 0)]),
        Room("opd2", "OPD 2 (Doctor Rm 3)", "12'-3\" x 9'-9½\"", (35.4, 0.4, 12.25, 9.8), "consult",
             doors=[(36.6, 10.2, 2.8, "N")],
             furniture=[("desk", 38.0, 4.8, 6.0, 2.3, 0), ("chair", 40.2, 2.9, 1.4, 1.4, 0),
                        ("chair", 38.2, 7.6, 1.4, 1.4, 0), ("chair", 40.8, 7.6, 1.4, 1.4, 0),
                        ("exam", 35.7, 0.7, 2.25, 5.5, 0)]),
        # --- surgical pod: spine -> scrub -> OT; OT -> recovery direct
        Room("ot", "OPERATION THEATRE", "20'-0\" x 17'-0\"", (0.4, 16.3, 20.6, 17.0), "surgical",
             furniture=[("ottable", 8.5, 22.0, 2.6, 6.5, 15), ("counter", 1.0, 16.6, 6.0, 1.5, 0),
                        ("cart", 16.5, 19.0, 1.8, 2.6, 0), ("cart", 16.5, 28.0, 1.8, 2.6, 0),
                        ("light", 10.2, 20.0, 1.5, 1.5, 0)]),
        Room("scrub", "Scrub + Autoclave", "5'-5\" x 6'-5\"", (21.4, 16.6, 5.4, 6.4), "surgical",
             doors=[(26.9, 19.8, 2.6, "E"), (21.3, 19.8, 3.0, "W")],
             furniture=[("sink", 21.8, 16.9, 1.4, 1.2, 0), ("sink", 23.4, 16.9, 1.4, 1.2, 0),
                        ("counter", 21.8, 21.4, 4.6, 1.3, 0)],
             notes="Gown/scrub anteroom - the only way into the OT"),
        Room("xray", "X-RAY / DRESSING", "6'-9\" x 9'-4\"", (21.4, 24.0, 6.8, 9.3), "consult",
             doors=[(28.3, 28.5, 2.8, "E")],
             furniture=[("exam", 22.2, 24.6, 2.25, 5.5, 0), ("counter", 22.0, 31.8, 5.6, 1.2, 0)],
             notes="Inboard room - AERB shielding-ready, serves OPDs and OT"),
        Room("recovery", "RECOVERY (2 beds)", "10'-10\" x 9'-2\"", (0.4, 33.8, 10.8, 9.2), "surgical",
             doors=[(6.0, 33.7, 3.0, "S"), (11.3, 38.5, 3.0, "W")],
             furniture=[("bed", 1.2, 34.8, 3.2, 6.6, 0), ("side", 4.8, 34.6, 1.4, 1.6, 0),
                        ("bed", 6.6, 34.8, 3.2, 6.6, 0), ("cart", 1.0, 41.4, 1.8, 1.6, 0)],
             notes="Direct door from OT; discharges via staff link to wards"),
        # --- the waist: pharmacy at exit, triage, arrival lobby
        Room("pharm", "PHARMACY", "8'-0\" x 5'-1\"", (0.4, 43.4, 8.0, 5.1), "public",
             doors=[(4.4, 48.6, 3.0, "N"), (8.5, 45.9, 2.4, "W")],
             furniture=[("counter", 0.7, 47.2, 7.2, 1.3, 0), ("shelf", 0.7, 43.7, 7.2, 1.3, 0)],
             notes="Dispensing counter opens into the lobby beside the exit"),
        Room("triage", "Triage / Vitals", "5'-6\" x 5'-1\"", (15.0, 43.4, 5.5, 5.1), "consult",
             doors=[(17.7, 48.6, 2.6, "N")],
             furniture=[("desk", 15.4, 44.0, 3.0, 1.8, 0), ("chair", 18.8, 44.2, 1.4, 1.4, 0)]),
        Room("recep", "RECEPTION", "", (5.5, 51.5, 9.0, 5.5), "circ",
             furniture=[("counter", 6.0, 52.0, 7.0, 2.0, -28), ("chair", 7.6, 54.8, 1.4, 1.4, 0),
                        ("chair", 9.8, 55.2, 1.4, 1.4, 0)]),
        # --- waiting + recreation on the glass
        Room("subwait", "OPD sub-wait", "", (34.5, 11.0, 12.0, 7.0), "circ",
             furniture=[("chair", 42.4, 12.0, 1.4, 1.4, 0), ("chair", 42.4, 13.8, 1.4, 1.4, 0),
                        ("chair", 42.4, 15.6, 1.4, 1.4, 0)]),
        Room("wait", "WAITING + RECREATION", "≈13' x 27' (20+ seats)", (33.6, 20.3, 13.8, 27.2), "public",
             holes=[(40.0, 40.8, 4.5, 4.6)],
             doors=[(33.7, 31.0, 3.6, "E")],
             furniture=[("plant", 34.4, 21.2, 1.6, 1.6, 0), ("plant", 43.4, 21.2, 1.6, 1.6, 0),
                        ("tv", 34.0, 22.6, 0.8, 4.0, 0),
                        ("chair", 35.2, 27.4, 1.4, 1.4, 0), ("chair", 37.0, 27.4, 1.4, 1.4, 0),
                        ("chair", 38.8, 27.4, 1.4, 1.4, 0), ("chair", 40.6, 27.4, 1.4, 1.4, 0),
                        ("chair", 42.4, 27.4, 1.4, 1.4, 0),
                        ("chair", 35.2, 30.8, 1.4, 1.4, 0), ("chair", 37.0, 30.8, 1.4, 1.4, 0),
                        ("chair", 38.8, 30.8, 1.4, 1.4, 0), ("chair", 40.6, 30.8, 1.4, 1.4, 0),
                        ("chair", 42.4, 30.8, 1.4, 1.4, 0),
                        ("chair", 35.2, 34.2, 1.4, 1.4, 0), ("chair", 37.0, 34.2, 1.4, 1.4, 0),
                        ("chair", 38.8, 34.2, 1.4, 1.4, 0), ("chair", 40.6, 34.2, 1.4, 1.4, 0),
                        ("chair", 35.2, 37.6, 1.4, 1.4, 0), ("chair", 37.0, 37.6, 1.4, 1.4, 0),
                        ("chair", 38.8, 37.6, 1.4, 1.4, 0), ("chair", 40.4, 37.6, 1.4, 1.4, 0),
                        ("water", 34.2, 44.6, 1.4, 1.4, 0), ("plant", 36.4, 44.6, 1.6, 1.6, 0)],
             notes="Recreation corner (TV, plants, kids nook) at the quiet south end"),
        Room("wc_w", "Acc. WC", "5'-6\" x 3'-10½\"", (40.2, 41.0, 4.0, 4.2), "wet",
             doors=[(40.1, 43.0, 2.2, "W")],
             furniture=[("wc", 41.0, 41.6, 1.6, 2.2, 0), ("sink", 43.0, 41.4, 1.2, 1.2, 0)]),
        # --- north ward wing (bones kept; duct/WC nudged for the deeper lobby)
        Room("duct", "Duct / V", "", (0.4, 59.2, 4.0, 4.2), "support"),
        Room("wc_c1", "Toilet (Acc.)", "3'-10½\" x 5'-4\"", (0.4, 64.0, 3.9, 5.4), "wet",
             doors=[(4.4, 66.6, 2.4, "E")],
             furniture=[("wc", 1.3, 64.8, 1.6, 2.2, 0), ("sink", 1.2, 67.8, 1.5, 1.2, 0)]),
        Room("nursing", "NURSING STATION", "7'-6\" x 8'-10½\"", (6.5, 60.3, 7.5, 8.9), "inpatient",
             doors=[(14.1, 64.5, 2.8, "E")],
             furniture=[("counter", 6.8, 60.6, 7.0, 1.8, 0), ("counter", 12.2, 62.3, 1.7, 6.0, 0),
                        ("chair", 8.6, 63.4, 1.4, 1.4, 0), ("chair", 10.6, 64.8, 1.4, 1.4, 0)]),
    ]
    # unchanged ward rooms from the architect's wing
    keep = {"single1", "single2", "single3", "single4", "single5",
            "twin1", "twin2", "wc_p1", "wc_p2", "pantry"}
    rooms += [r for r in _north_wing() if r.key in keep]
    # circulation label anchors
    rooms += [
        Room("pass3", "3'-0\" w. Passage", "", (15.8, 10.6, 17.2, 3.0), "circ"),
        Room("spine", "spine  ≥6'-4\" w.", "", (28.8, 13.9, 4.8, 30.0), "circ"),
        Room("stafflink", "staff link", "", (11.6, 33.8, 9.5, 14.7), "circ"),
        Room("lobby", "ARRIVAL LOBBY", "", (0.4, 48.9, 20.7, 9.6), "circ"),
        Room("pass5", "5'-0\" w. Passage", "", (16.6, 58.5, 5.0, 19.7), "circ"),
        Room("pass79", "7'-9½\" w. Passage", "", (13.0, 78.2, 7.9, 16.6), "circ"),
    ]
    return rooms


# --------------------------- Layout D (Dr. Khanna's own sketch, interpreted)
def layout_d_rooms():
    """Line-diagram interpretation of Dr. Khanna's notebook sketch:
    OT at the SE corner with Recovery and X-ray/Dressing stacked below it,
    autoclave/bath/doctors' lounge across the south, store below autoclave,
    OPD 1+2 mid-plan, waiting on the west glass beside the cut-out (wash
    attached), reception at the entry, pharmacy + common washroom at the
    nursing/ward gate, ward wing of 4 singles + General Ward."""
    rooms = [
        # --- east clinical stack (per sketch: OT at the corner, then down)
        Room("ot", "OPERATION THEATRE", "20'-0\" x 17'-0\"", (0.4, 0.4, 20.6, 17.0), "surgical",
             furniture=[("ottable", 8.5, 6.5, 2.6, 6.5, 15), ("counter", 1.0, 0.7, 6.0, 1.5, 0),
                        ("cart", 16.5, 3.0, 1.8, 2.6, 0), ("cart", 16.5, 12.0, 1.8, 2.6, 0)]),
        Room("recovery", "RECOVERY (2 beds)", "11'-0\" x 9'-0\"", (0.4, 17.9, 11.0, 9.0), "surgical",
             doors=[(6.0, 17.8, 3.0, "S"), (11.5, 22.4, 3.0, "W")],
             furniture=[("bed", 1.2, 18.8, 3.2, 6.6, 0), ("bed", 6.4, 18.8, 3.2, 6.6, 0)],
             notes="Direct door from the OT above it, exactly as sketched"),
        Room("xray", "X-RAY / DRESSING", "11'-0\" x 9'-7\"", (0.4, 28.4, 11.0, 9.6), "consult",
             doors=[(11.5, 33.0, 2.8, "W")],
             furniture=[("exam", 1.2, 29.2, 2.25, 5.5, 0), ("counter", 1.0, 36.0, 6.0, 1.3, 0)]),
        # --- south band west of the OT
        Room("autoclave", "Autoclave + Scrub", "6'-7\" x 5'-5\"", (21.4, 0.4, 6.6, 5.4), "surgical",
             doors=[(21.4, 3.0, 2.6, "E"), (24.6, 5.9, 2.4, "N")],
             furniture=[("sink", 22.0, 0.7, 1.4, 1.2, 0), ("counter", 24.4, 0.7, 3.2, 1.4, 0)]),
        Room("bath_st", "Staff Bath", "3'-0\" x 5'-5\"", (28.4, 0.4, 3.0, 5.4), "wet",
             doors=[(31.5, 2.8, 2.0, "W")],
             furniture=[("wc", 28.9, 0.9, 1.5, 2.0, 0), ("shower", 29.9, 3.8, 1.2, 1.2, 0)]),
        Room("lounge", "DOCTORS' LOUNGE", "≈15' x 9'-7\" (w/ bath)", (31.8, 0.4, 15.8, 9.6), "consult",
             doors=[(36.0, 10.1, 2.8, "N")],
             furniture=[("desk", 33.0, 5.6, 4.5, 2.2, 0), ("chair", 34.2, 3.6, 1.4, 1.4, 0),
                        ("chair", 36.6, 3.6, 1.4, 1.4, 0), ("bed", 42.0, 0.8, 3.0, 6.4, 0)],
             notes="Rest room for on-duty doctors, from the sketch's top corner"),
        Room("store", "Store Room", "6'-7\" x 6'-7\"", (21.4, 6.2, 6.6, 6.6), "support",
             doors=[(24.6, 12.9, 2.5, "N")],
             furniture=[("shelf", 21.7, 6.5, 1.2, 6.0, 0), ("shelf", 26.6, 6.5, 1.2, 6.0, 0)]),
        # --- OPD pair mid-plan (sketch: OPD 2 then OPD 1 toward the glass)
        Room("opd2", "OPD 2", "9'-2\" x 9'-0\"", (28.6, 11.4, 9.2, 9.0), "consult",
             doors=[(33.0, 20.5, 2.8, "N")],
             furniture=[("desk", 29.6, 15.4, 5.0, 2.2, 0), ("chair", 31.4, 13.6, 1.4, 1.4, 0),
                        ("exam", 35.0, 11.7, 2.25, 5.5, 0)]),
        Room("opd1", "OPD 1", "9'-0\" x 9'-0\"", (38.4, 11.4, 9.0, 9.0), "consult",
             doors=[(42.0, 20.5, 2.8, "N")],
             furniture=[("desk", 39.4, 15.4, 5.0, 2.2, 0), ("chair", 41.2, 13.6, 1.4, 1.4, 0),
                        ("exam", 44.2, 11.7, 2.25, 5.5, 0)]),
        # --- waiting on the west glass, wash beside the cut-out (as sketched)
        Room("wait", "WAITING", "≈17' x 26' (20+ seats)", (30.4, 21.8, 17.0, 25.7), "public",
             holes=[(40.0, 40.8, 4.5, 4.6)],
             doors=[(33.0, 47.6, 3.4, "N"), (30.3, 25.0, 3.0, "E")],
             furniture=[("chair", 32.0, 23.4, 1.4, 1.4, 0), ("chair", 33.8, 23.4, 1.4, 1.4, 0),
                        ("chair", 35.6, 23.4, 1.4, 1.4, 0), ("chair", 37.4, 23.4, 1.4, 1.4, 0),
                        ("chair", 39.2, 23.4, 1.4, 1.4, 0), ("chair", 41.0, 23.4, 1.4, 1.4, 0),
                        ("chair", 32.0, 26.8, 1.4, 1.4, 0), ("chair", 33.8, 26.8, 1.4, 1.4, 0),
                        ("chair", 35.6, 26.8, 1.4, 1.4, 0), ("chair", 37.4, 26.8, 1.4, 1.4, 0),
                        ("chair", 39.2, 26.8, 1.4, 1.4, 0), ("chair", 41.0, 26.8, 1.4, 1.4, 0),
                        ("chair", 32.0, 30.2, 1.4, 1.4, 0), ("chair", 33.8, 30.2, 1.4, 1.4, 0),
                        ("chair", 35.6, 30.2, 1.4, 1.4, 0), ("chair", 37.4, 30.2, 1.4, 1.4, 0),
                        ("chair", 32.0, 33.6, 1.4, 1.4, 0), ("chair", 33.8, 33.6, 1.4, 1.4, 0),
                        ("chair", 35.6, 33.6, 1.4, 1.4, 0), ("chair", 37.4, 33.6, 1.4, 1.4, 0),
                        ("tv", 30.8, 37.4, 0.8, 4.0, 0), ("water", 31.2, 44.4, 1.4, 1.4, 0),
                        ("plant", 45.2, 22.6, 1.6, 1.6, 0), ("plant", 33.6, 44.4, 1.6, 1.6, 0)]),
        Room("wc_w", "Wash (Acc.)", "5'-6\" x 3'-10½\"", (40.2, 41.0, 4.0, 4.2), "wet",
             doors=[(40.1, 43.0, 2.2, "W")],
             furniture=[("wc", 41.0, 41.6, 1.6, 2.2, 0), ("sink", 43.0, 41.4, 1.2, 1.2, 0)]),
        # --- entry waist: lobby + reception (arrows in the sketch)
        Room("recep", "RECEPTION", "", (5.5, 51.5, 9.0, 5.5), "circ",
             furniture=[("counter", 6.0, 52.0, 7.0, 2.0, -28), ("chair", 7.6, 54.8, 1.4, 1.4, 0)]),
        # --- ward gate: pharmacy + common washroom + pantry + linen
        Room("pharm", "PHARMACY", "8'-0\" x 5'-7\"", (21.6, 58.4, 8.0, 5.6), "public",
             doors=[(21.5, 61.0, 2.6, "E")],
             furniture=[("counter", 21.9, 58.7, 1.4, 5.0, 0), ("shelf", 27.9, 58.7, 1.4, 5.0, 0)],
             notes="At the nursing/ward junction, per the sketch"),
        Room("washC", "Washroom", "8'-0\" x 3'-9\"", (21.6, 64.4, 8.0, 3.8), "wet",
             doors=[(21.5, 66.2, 2.2, "E")],
             furniture=[("wc", 22.4, 64.8, 1.5, 2.0, 0), ("sink", 27.6, 64.8, 1.3, 1.2, 0)]),
        Room("pantry", "Pantry", "6'-7\" x 5'-5\"", (30.0, 61.0, 6.6, 5.4), "support",
             doors=[(33.2, 66.5, 2.4, "N")],
             furniture=[("counter", 30.3, 61.3, 6.0, 1.4, 0)]),
        Room("linen", "Linen / Util.", "≈5' x 5'-5\"", (37.2, 61.0, 5.0, 5.4), "support",
             doors=[(39.6, 66.5, 2.2, "N")]),
        Room("duct", "Duct / V", "", (0.4, 59.2, 4.0, 4.2), "support"),
        Room("wc_c1", "Toilet (Acc.)", "3'-10½\" x 5'-4\"", (0.4, 64.0, 3.9, 5.4), "wet",
             doors=[(4.4, 66.6, 2.4, "E")],
             furniture=[("wc", 1.3, 64.8, 1.6, 2.2, 0), ("sink", 1.2, 67.8, 1.5, 1.2, 0)]),
        Room("nursing", "NURSING STN.", "7'-6\" x 8'-10½\"", (6.5, 60.3, 7.5, 8.9), "inpatient",
             doors=[(14.1, 64.5, 2.8, "E")],
             furniture=[("counter", 6.8, 60.6, 7.0, 1.8, 0), ("chair", 8.6, 63.4, 1.4, 1.4, 0)]),
        # --- ward wing: Room 1 (deluxe) + Rooms 2-4 (singles) + General Ward
        Room("room1", "ROOM 1 (Deluxe)", "18'-4\" x 9'-0\"", (21.6, 68.6, 18.3, 9.0), "inpatient",
             doors=[(21.5, 73.0, 2.8, "E")],
             furniture=[("bed", 23.0, 69.6, 3.2, 6.6, 0), ("side", 26.6, 69.4, 1.4, 1.6, 0),
                        ("chair", 29.4, 70.0, 1.4, 1.4, 0),
                        ("wc", 36.6, 69.8, 1.6, 2.2, 0), ("sink", 35.2, 72.4, 1.5, 1.2, 0)]),
        Room("room2", "Room 2", "11'-10\" x 8'-0\"", (4.4, 69.8, 11.8, 8.0), "inpatient",
             doors=[(14.0, 78.0, 2.8, "N")],
             furniture=[("bed", 5.0, 70.6, 3.2, 6.6, 0), ("side", 8.6, 70.4, 1.4, 1.6, 0)]),
        Room("room3", "Room 3", "11'-10\" x 9'-0\"", (0.4, 78.4, 11.8, 9.0), "inpatient",
             doors=[(10.0, 87.6, 2.8, "N")],
             furniture=[("bed", 1.2, 79.4, 3.2, 6.6, 0), ("side", 4.8, 79.2, 1.4, 1.6, 0)]),
        Room("wc_p1", "Toilet", "5'-9½\" x 5'-0\"", (4.6, 87.8, 5.8, 5.0), "wet",
             doors=[(10.6, 89.4, 2.2, "E")],
             furniture=[("wc", 5.4, 88.6, 1.6, 2.2, 0), ("sink", 8.6, 88.4, 1.5, 1.2, 0)]),
        Room("wc_p2", "Toilet", "5'-9½\" x 5'-0\"", (10.8, 90.4, 5.8, 5.0), "wet",
             doors=[(16.8, 92.2, 2.2, "E")],
             furniture=[("wc", 11.6, 91.2, 1.6, 2.2, 0), ("sink", 14.8, 91.0, 1.5, 1.2, 0)]),
        Room("room4", "Room 4", "11'-10\" x 9'-0\"", (0.4, 91.6, 11.8, 9.0), "inpatient",
             holes=[(4.6, 87.8, 5.8, 5.0), (10.8, 90.4, 5.8, 5.0)],
             doors=[(9.6, 91.5, 2.8, "N")],
             furniture=[("bed", 1.2, 92.8, 3.2, 6.6, 0), ("side", 4.8, 92.6, 1.4, 1.6, 0)]),
        Room("gw", "GENERAL WARD", "≈17' x 19'-8\" (4 beds, curtains)", (20.4, 78.2, 16.9, 19.7), "inpatient",
             holes=[(31.0, 78.4, 5.2, 4.2), (30.0, 90.0, 3.2, 6.3)],
             doors=[(20.3, 83.0, 3.4, "E"), (20.3, 92.5, 3.0, "E")],
             furniture=[("bed", 21.6, 79.2, 3.2, 6.6, 0), ("side", 25.2, 79.0, 1.4, 1.6, 0),
                        ("bed", 26.8, 79.2, 3.2, 6.6, 0),
                        ("bed", 21.6, 90.4, 3.2, 6.6, 0), ("side", 25.2, 90.2, 1.4, 1.6, 0),
                        ("bed", 26.0, 90.4, 3.2, 6.6, 0)],
             notes="Replaces twins + singles 4-5: 4 curtained beds, 2 attached toilets"),
        Room("wc_g1", "Toilet", "5'-2½\" x 4'-0\"", (31.0, 78.4, 5.2, 4.2), "wet",
             doors=[(31.0, 80.4, 2.0, "E")],
             furniture=[("wc", 31.8, 78.8, 1.5, 2.0, 0), ("sink", 34.6, 78.8, 1.2, 1.2, 0)]),
        Room("wc_g2", "Toilet", "2'-11½\" x 6'-3\"", (30.0, 90.0, 3.2, 6.3), "wet",
             doors=[(30.0, 91.6, 2.0, "E")],
             furniture=[("wc", 30.6, 90.6, 1.5, 2.0, 0), ("sink", 30.6, 94.6, 1.3, 1.2, 0)]),
        # --- circulation label anchors
        Room("spine", "9'-0\" w. spine", "", (11.8, 18.0, 9.2, 40.0), "circ"),
        Room("link", "link", "", (21.4, 13.2, 7.0, 7.6), "circ"),
        Room("lobby", "ENTRY / RECEPTION", "", (0.4, 48.9, 20.7, 9.6), "circ"),
        Room("pass5", "5'-0\" w. Passage", "", (16.6, 58.5, 5.0, 19.7), "circ"),
        Room("pass79", "7'-9½\" w. Passage", "", (13.0, 78.2, 7.9, 16.6), "circ"),
    ]
    return rooms


# -------- Layout E: Dr. Khanna's FINAL sketch (v2), on the Rev C envelope
def layout_e_rooms():
    """Digitization of the doctor's second sketch on the confirmed 92'-0"
    plate: OT 20'x20' pod at the SE with scrub + autoclave, recovery and
    X-ray/dressing/emergency stacked to the entry; OPD 1-3 + doctors'
    lounge mid-south; waiting on the west glass above the cut-out;
    entry lobby with reception + pharmacy; service band on the east;
    Rooms 1-4 (ensuite) on the glass + Suite 5 at the north."""
    rooms = [
        # --- OT pod (south-east)
        Room("autoclave", "Autoclave", "9'-10\" x 5'-2\"", (0.4, 0.4, 9.8, 5.2), "surgical",
             doors=[(5.0, 5.8, 2.4, "N")],
             furniture=[("counter", 0.7, 0.7, 9.0, 1.6, 0)],
             notes="Sterile supply direct to OT"),
        Room("sterile", "Sterile Store / Change", "9'-6\" x 5'-2\"", (10.6, 0.4, 9.8, 5.2), "surgical",
             doors=[(16.5, 5.8, 2.4, "N")],
             furniture=[("shelf", 10.9, 0.7, 1.2, 4.4, 0), ("shelf", 18.9, 0.7, 1.2, 4.4, 0)]),
        Room("ot", "OPERATION THEATRE", "20'-0\" x 20'-0\"", (0.4, 6.0, 20.0, 20.0), "surgical",
             furniture=[("ottable", 8.6, 13.0, 2.6, 6.5, 15), ("counter", 1.0, 6.3, 6.0, 1.5, 0),
                        ("cart", 16.6, 9.0, 1.8, 2.6, 0), ("cart", 16.6, 20.0, 1.8, 2.6, 0),
                        ("light", 10.4, 11.0, 1.5, 1.5, 0)]),
        Room("scrub", "Scrub", "5'-2\" x 7'-0\"", (20.9, 2.0, 5.2, 7.0), "surgical",
             doors=[(20.8, 7.2, 2.6, "W"), (23.5, 9.1, 2.4, "N")],
             furniture=[("sink", 21.3, 2.3, 1.4, 1.2, 0), ("sink", 23.0, 2.3, 1.4, 1.2, 0)]),
        Room("recovery", "RECOVERY / Stretcher", "12'-0\" x 8'-0\"", (0.4, 26.4, 12.0, 8.0), "surgical",
             doors=[(6.0, 26.3, 3.0, "S"), (12.5, 30.4, 2.8, "W")],
             furniture=[("bed", 1.2, 27.2, 3.2, 6.6, 0), ("cart", 9.8, 27.0, 1.8, 2.2, 0)],
             notes="Direct door from OT; discharges via spine, never the lobby"),
        Room("xray", "X-RAY / DRESSING / EMERGENCY", "12'-0\" x 7'-7\"", (0.4, 34.8, 12.0, 7.6), "consult",
             doors=[(6.5, 42.5, 3.0, "N"), (12.5, 38.5, 2.6, "W")],
             furniture=[("exam", 1.2, 35.4, 2.25, 5.5, 0), ("counter", 7.2, 35.2, 4.4, 1.3, 0)],
             notes="Walk-in emergencies come straight off the entry lobby"),
        # --- consult band (mid-south) + lounge
        Room("bath_lg", "Bath", "3'-0\" x 5'-0\"", (26.5, 0.4, 3.0, 5.0), "wet",
             doors=[(29.6, 2.8, 2.0, "W")],
             furniture=[("wc", 27.0, 0.8, 1.4, 1.9, 0), ("shower", 27.0, 3.2, 1.2, 1.2, 0)]),
        Room("lounge", "DOCTORS' LOUNGE", "≈17' x 9'-0\" (w/ bath)", (29.9, 0.4, 17.4, 9.0), "consult",
             doors=[(33.5, 9.5, 2.6, "N")],
             furniture=[("desk", 31.0, 4.6, 4.2, 2.2, 0), ("chair", 32.2, 2.8, 1.4, 1.4, 0),
                        ("bed", 41.0, 0.8, 3.0, 6.2, 0)]),
        Room("opd2", "OPD 2", "10'-2\" x 9'-0\"", (20.9, 13.0, 10.2, 9.0), "consult",
             doors=[(20.8, 17.5, 2.8, "W")],
             furniture=[("desk", 22.0, 17.0, 4.6, 2.2, 0), ("chair", 23.4, 15.2, 1.4, 1.4, 0),
                        ("exam", 28.4, 13.3, 2.25, 5.5, 0)]),
        Room("opd1", "OPD 1", "10'-2\" x 9'-0\"", (20.9, 22.4, 10.2, 9.0), "consult",
             doors=[(20.8, 26.9, 2.8, "W")],
             furniture=[("desk", 22.0, 26.4, 4.6, 2.2, 0), ("chair", 23.4, 24.6, 1.4, 1.4, 0),
                        ("exam", 28.4, 22.7, 2.25, 5.5, 0)]),
        Room("opd3", "OPD 3", "≈12' x 9'-2\"", (31.6, 12.9, 12.6, 9.2), "consult",
             doors=[(31.5, 17.5, 2.8, "E")],
             furniture=[("desk", 33.0, 17.0, 4.6, 2.2, 0), ("chair", 34.4, 15.2, 1.4, 1.4, 0),
                        ("exam", 39.6, 13.2, 2.25, 5.5, 0)]),
        # --- waiting on the west glass (his v2 addition)
        Room("wait", "WAITING AREA", "≈12' x 17' (16 seats)", (31.6, 22.5, 12.8, 17.1), "public",
             doors=[(31.7, 35.5, 3.2, "E")],
             furniture=[("chair", 33.0, 23.6, 1.4, 1.4, 0), ("chair", 34.8, 23.6, 1.4, 1.4, 0),
                        ("chair", 36.6, 23.6, 1.4, 1.4, 0), ("chair", 38.4, 23.6, 1.4, 1.4, 0),
                        ("chair", 33.0, 27.0, 1.4, 1.4, 0), ("chair", 34.8, 27.0, 1.4, 1.4, 0),
                        ("chair", 36.6, 27.0, 1.4, 1.4, 0), ("chair", 38.4, 27.0, 1.4, 1.4, 0),
                        ("chair", 33.0, 30.4, 1.4, 1.4, 0), ("chair", 34.8, 30.4, 1.4, 1.4, 0),
                        ("chair", 36.6, 30.4, 1.4, 1.4, 0), ("chair", 38.4, 30.4, 1.4, 1.4, 0),
                        ("chair", 33.0, 33.8, 1.4, 1.4, 0), ("chair", 34.8, 33.8, 1.4, 1.4, 0),
                        ("chair", 36.6, 33.8, 1.4, 1.4, 0), ("chair", 38.2, 33.8, 1.4, 1.4, 0),
                        ("tv", 32.0, 37.6, 0.8, 3.6, 0), ("water", 35.0, 38.0, 1.4, 1.4, 0),
                        ("plant", 41.8, 23.0, 1.6, 1.6, 0)],
             notes="West openable glass; fed from the OPD lobby"),
        # --- entry waist
        Room("recep", "RECEPTION", "", (13.0, 44.0, 6.5, 4.0), "circ",
             furniture=[("counter", 13.4, 44.6, 5.6, 1.9, -18)]),
        # --- east service band (north of entry)
        Room("pharm", "PHARMACY", "7'-5\" x 6'-0\"", (5.0, 48.8, 7.4, 6.0), "public",
             doors=[(8.6, 48.7, 2.6, "S")],
             furniture=[("counter", 5.3, 49.0, 6.6, 1.4, 0), ("shelf", 5.3, 53.2, 6.6, 1.3, 0)],
             notes="Counter faces the entry lobby - registration + dispensing"),
        Room("bp", "BP / Exam Room", "11'-10\" x 5'-7\"", (0.4, 55.4, 11.8, 5.6), "consult",
             doors=[(12.3, 58.2, 2.6, "W")],
             furniture=[("desk", 0.8, 55.8, 3.6, 1.9, 0), ("exam", 8.6, 55.7, 2.25, 5.2, 0)]),
        Room("ns", "NURSING STN. + Obs Bed", "11'-10\" x 7'-7\"", (0.4, 61.4, 11.8, 7.6), "inpatient",
             doors=[(12.3, 65.2, 2.8, "W")],
             furniture=[("counter", 0.8, 61.7, 8.0, 1.7, 0), ("chair", 2.6, 63.9, 1.4, 1.4, 0),
                        ("bed", 8.2, 63.9, 3.0, 4.6, 0)]),
        Room("washC", "Wash + Bath (2)", "11'-10\" x 5'-0\"", (0.4, 69.4, 11.8, 5.0), "wet",
             doors=[(12.3, 71.9, 2.4, "W")],
             furniture=[("wc", 1.2, 70.0, 1.5, 2.0, 0), ("shower", 4.4, 70.0, 1.3, 1.3, 0),
                        ("sink", 8.8, 70.0, 1.4, 1.2, 0)]),
        Room("store", "Stores", "11'-10\" x 5'-5\"", (0.4, 74.8, 11.8, 5.4), "support",
             doors=[(12.3, 77.5, 2.4, "W")],
             furniture=[("shelf", 0.8, 75.1, 1.2, 4.6, 0), ("shelf", 10.8, 75.1, 1.2, 4.6, 0)]),
        Room("pantry", "Pantry", "4'-6\" x 5'-2\"", (13.0, 84.0, 4.5, 5.2), "support",
             doors=[(15.2, 83.9, 2.2, "S")],
             furniture=[("counter", 13.3, 87.6, 3.9, 1.3, 0)]),
        # --- wards on the glass (ensuite, per v2 sketch) + suite
        Room("room1", "ROOM 1", "≈23' x 10'-2\" (ensuite)", (18.2, 48.8, 25.0, 10.2), "inpatient",
             holes=[(18.4, 49.0, 4.2, 5.2)],
             doors=[(17.9, 55.5, 2.8, "E")],
             furniture=[("bed", 24.0, 49.6, 3.2, 6.6, 0), ("side", 27.6, 49.4, 1.4, 1.6, 0),
                        ("chair", 30.4, 50.0, 1.4, 1.4, 0)]),
        Room("wcR1", "T", "", (18.4, 49.0, 4.2, 5.2), "wet",
             doors=[(20.4, 54.3, 2.0, "N")],
             furniture=[("wc", 19.0, 49.6, 1.5, 2.0, 0), ("sink", 21.4, 49.4, 1.2, 1.2, 0)]),
        Room("room2", "ROOM 2", "≈22' x 10'-0\" (ensuite)", (18.2, 59.4, 24.0, 10.0), "inpatient",
             holes=[(18.4, 59.6, 4.2, 5.2)],
             doors=[(17.9, 66.0, 2.8, "E")],
             furniture=[("bed", 24.0, 60.2, 3.2, 6.6, 0), ("side", 27.6, 60.0, 1.4, 1.6, 0),
                        ("chair", 30.4, 60.6, 1.4, 1.4, 0)]),
        Room("wcR2", "T", "", (18.4, 59.6, 4.2, 5.2), "wet",
             doors=[(20.4, 64.9, 2.0, "N")],
             furniture=[("wc", 19.0, 60.2, 1.5, 2.0, 0), ("sink", 21.4, 60.0, 1.2, 1.2, 0)]),
        Room("room3", "ROOM 3", "≈21' x 9'-6\" (ensuite)", (18.2, 69.8, 22.5, 9.6), "inpatient",
             holes=[(18.4, 70.0, 4.2, 5.2)],
             doors=[(17.9, 76.0, 2.8, "E")],
             furniture=[("bed", 24.0, 70.6, 3.2, 6.6, 0), ("side", 27.6, 70.4, 1.4, 1.6, 0),
                        ("chair", 30.4, 71.0, 1.4, 1.4, 0)]),
        Room("wcR3", "T", "", (18.4, 70.0, 4.2, 5.2), "wet",
             doors=[(20.4, 75.3, 2.0, "N")],
             furniture=[("wc", 19.0, 70.6, 1.5, 2.0, 0), ("sink", 21.4, 70.4, 1.2, 1.2, 0)]),
        Room("room4", "ROOM 4", "≈17' x 11'-10\" (ensuite)", (18.0, 79.8, 18.0, 11.8), "inpatient",
             holes=[(18.2, 80.0, 4.2, 5.2)],
             doors=[(17.8, 80.8, 2.6, "E")],
             furniture=[("bed", 24.0, 80.8, 3.2, 6.6, 0), ("side", 27.6, 80.6, 1.4, 1.6, 0),
                        ("chair", 30.2, 81.2, 1.4, 1.4, 0)]),
        Room("wcR4", "T", "", (18.2, 80.0, 4.2, 5.2), "wet",
             doors=[(20.2, 85.3, 2.0, "N")],
             furniture=[("wc", 18.8, 80.6, 1.5, 2.0, 0), ("sink", 21.2, 80.4, 1.2, 1.2, 0)]),
        Room("suite", "SUITE ROOM 5", "12'-2\" x 8'-7\" (ensuite)", (0.4, 83.4, 12.2, 8.6), "inpatient",
             holes=[(8.6, 86.8, 3.8, 5.0)],
             doors=[(6.0, 83.3, 3.0, "S")],
             furniture=[("bed", 1.2, 84.6, 3.2, 6.6, 0), ("side", 4.8, 84.4, 1.4, 1.6, 0)]),
        Room("wcS5", "T", "", (8.6, 86.8, 3.8, 5.0), "wet",
             doors=[(8.5, 88.9, 2.0, "E")],
             furniture=[("wc", 9.2, 87.4, 1.5, 2.0, 0), ("sink", 11.2, 87.2, 1.2, 1.2, 0)]),
        # --- circulation label anchors
        Room("link", "link", "", (20.9, 9.4, 20.0, 3.2), "circ"),
        Room("spine", "7'-8\" w. spine", "", (12.8, 26.2, 7.7, 16.6), "circ"),
        Room("sublobby", "OPD LOBBY", "", (20.9, 31.8, 10.4, 7.9), "circ"),
        Room("lobby", "ENTRY LOBBY", "", (0.4, 42.8, 25.0, 5.6), "circ"),
        Room("wardcorr", "5'-0\" w. Passage", "", (12.6, 48.8, 5.0, 34.4), "circ"),
    ]
    return rooms


LAYOUTS = {
    "architect": ("Architect's Proposal (as received)", architect_rooms),
    "A": ("LAYOUT A — Targeted Revision", layout_a_rooms),
    "B": ("LAYOUT B — Fresh Alternative", layout_b_rooms),
    "C": ("LAYOUT C — \"Arrival Hub\" (fresh design)", layout_c_rooms),
    "D": ("LAYOUT D — Dr. Khanna's Sketch (interpreted)", layout_d_rooms),
    "E": ("LAYOUT E — Dr. Khanna's Final Plan", layout_e_rooms),
}


# ------------------------------------------------------- CAD-style geometry
def solid_rooms(rooms):
    return [r for r in rooms if r.zone != "circ"]


def circulation_poly(rooms):
    """Everything inside the plate that is not a room or the cut-out."""
    solids = unary_union([r.poly for r in solid_rooms(rooms)])
    return PLATE.buffer(-0.75).difference(solids).difference(CUTOUT)


def wall_bands(rooms):
    """Filled wall geometry: grown room outlines minus room interiors,
    plus the plate perimeter and cut-out surround, with door openings and
    the main entrance punched out."""
    solids = [r.poly for r in solid_rooms(rooms)]
    grown = unary_union([p.buffer(0.55, join_style=2) for p in solids]
                        + [CUTOUT.buffer(0.55, join_style=2)])
    walls = grown.difference(unary_union(solids)).difference(CUTOUT)
    perimeter = PLATE.difference(PLATE.buffer(-0.75))
    walls = unary_union([walls, perimeter]).intersection(PLATE)

    for r in rooms:
        for (cx, cy, w, side) in r.doors:
            if side in ("N", "S"):
                opening = box(cx - w / 2, cy - 1.1, cx + w / 2, cy + 1.1)
            else:
                opening = box(cx - 1.1, cy - w / 2, cx + 1.1, cy + w / 2)
            walls = walls.difference(opening)

    _, y1, y2 = MD_DOOR
    walls = walls.difference(box(-1.5, y1, 1.5, y2))
    return walls
