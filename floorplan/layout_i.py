"""LAYOUT I (18-11-2026) - the clients' PENCIL sketch with blue-pen sizes,
drawn on the builder's DWG geometry.  New feature: a LARGE WAITING HALL AT
THE ENTRY (seat rows across the hall south of the 8'-0" entry passage).

Geometry, columns, room class, door / furniture drawing and the whole north
(IPD) block are imported from layout_g.py; nothing there is edited.  South
block (clients' sizes in feet, blue pen):

    east column   CSSD / autoclave row 7'-0"  |  OT 20'-0" x 20'-0"  |
                  recovery 7'-0"  |  waiting hall (to the 8'-0" passage)
    middle        staff band 6'-1" (change, scrub, store, dirty utility)
                  + OPD passage 4'-6"
    west glass    Lounge 6'-8" | OPD 2 8'-1" | OPD 1 8'-1" |
                  Emergency 9'-3" | X-ray 5'-9"   (sum = the DWG depth)

    cd floorplan && python3 layout_i.py build

Brief: deliverables/LAYOUT_I_BRIEF_AND_FEASIBILITY.md
"""
import math
import os
from contextlib import contextmanager
from itertools import combinations

from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

import layout_g as G
from layout_g import D, E0, S0, T, fi, xw

DATE = "18-11-2026"
TITLE = "LAYOUT I - pencil sketch, large entry waiting"

# ------------------------------------------------------------ set-out (feet)
CS_D = 7.0                       # CSSD / autoclave row, client "7"
OT_S = S0 + CS_D + T             # 7.765  south face of the OT
OT_N = OT_S + 20.0               # 27.765 north face of the OT
REC_S = OT_N + T                 # 28.14
REC_D = 7.0                      # recovery, client "7"
REC_N = REC_S + REC_D            # 35.14
HALL_S = REC_N + T               # 35.515 south face of the waiting hall
HALL_N = 48.10                   # north face of the 8'-0" entry passage
OT_WF = E0 + 20.0                # 20.39  west face of the OT (grid-B column line)
OTW_C = OT_WF + T / 2            # centre of the OT west wall
CS_C = S0 + CS_D + T / 2         # centre of the CSSD | OT wall
REC_C = OT_N + T / 2             # centre of the OT | recovery wall
BAND0, BAND1 = OT_WF + T, 26.87  # staff band, 6'-1" clear
PAS0 = BAND1 + T                 # 27.245 east face of the OPD passage
PAS_W = 4.5                      # client "4.5"
PAS1 = PAS0 + PAS_W              # 31.745
WX = PAS1 + T                    # 32.12  east face of the west (glass) rooms
WXC = PAS1 + T / 2
# west column, south -> north: clear depths (client "8.1", "9.3 / 5.9")
W_OPD, W_EM, W_XR = 8.0 + 1 / 12, 9.25, 5.75
W_LG = 39.76 - S0 - 2 * W_OPD - W_EM - W_XR - 4 * T      # lounge = the remainder
Y_OPD2 = S0 + W_LG + T
Y_OPD1 = Y_OPD2 + W_OPD + T
Y_EM = Y_OPD1 + W_OPD + T
Y_XR = Y_EM + W_EM + T
LOBBY_GAP = (33.55, 38.55)       # 5'-0" opening hall <-> OPD lobby (south of column C5)
NOTCH = (15.1, REC_N - 1.965, 5.8, 2.1)       # recovery door recess (keeps the 5'-0" gap)

SEAT_W, SEAT_D = 1.0 + 10 / 12, 1.0 + 8 / 12  # 1'-10" x 1'-8"
AISLE = 4.0
ROW_X0, ROW_N = 0.45, 8
LANE = (ROW_X0 + ROW_N * SEAT_W, 20.28)       # trolley / OPD lane, clear of seats
ENTRY_STRIP = (HALL_N - 5.0, HALL_N)          # 5'-0" circulation in front of the main door
DY = OT_S - S0                                # shift of G's OT equipment (G's OT starts at S0)

# existing x06 north wall kept between column C5 and the cut-out
EXTRA_WALLS = [box(22.87, 39.76, 24.4, 40.16)]

NORTH_KEYS = ("duct", "pharm", "obs", "change", "ns", "store", "duty", "bath5", "pantry",
              "room1", "wcR1", "room2", "wcR2", "room3", "wcR3", "room4", "wcR4", "suite",
              "wardcorr")

# ------------------------------------------------- clients' blue-pen sizes
# (mark, where it is written, room it was applied to, built clear size,
#  nearest DWG line / fit)
CLIENT_SIZES = [
    ("20", "inside the OT and on its east wall", "Operation theatre",
     "20'-0\" x 20'-0\"", "west face on the grid-B column line (C3 is 1 3/8\" proud); exact"),
    ("7 (first read as X)", "east wall, beside AUTOCLAVE", "CSSD / autoclave row depth",
     "7'-0\"", "builder's x07 toilet block ends 6'-6\" from the south wall: 6\" off, exact as built"),
    ("7 (first read as X)", "east wall, beside RECOVERY", "Recovery depth",
     "7'-0\"", "no DWG wall; its north wall lands 8\" south of the end of the x06 east wall"),
    ("8", "at the ENTRY, twice", "Entry passage (north part of the hall)",
     "8'-0\"", "the builder's common passage is 8'-0\" clear: exact"),
    ("4.5 with arrows", "in the OPD passage", "OPD passage width",
     "4'-6\"", "free-standing partitions; exact as built"),
    ("8.1", "glass side, beside ticks 3 / 4", "OPD 2 and OPD 1 depth (N-S)",
     "8'-1\" each", "no DWG wall on these lines; exact as built"),
    ("9.3", "glass side, beside ticks 2 / 1", "Emergency / dressing depth (N-S)",
     "9'-3\"", "exact as built"),
    ("5.9", "glass side, under 9.3", "X-ray room depth (N-S), at the cut-out end",
     "5'-9\"", "north face = the existing x06 north wall: exact"),
    ("1, 2, 3, 4 with ticks", "glass side, one per room", "room order from the cut-out: "
     "1 Emergency / X-ray, 2 OPD 1, 3 OPD 2, 4 Lounge", "-", "order kept"),
]


# ------------------------------------------------------------------- rooms
def _seats(x0, y0, n):
    return [("chair", x0 + i * SEAT_W, y0, SEAT_W - 0.08, SEAT_D, 0) for i in range(n)]


ROW_A_Y = HALL_S + 0.02                       # backs on the recovery wall, faces north
ROW_B_Y = ROW_A_Y + SEAT_D + AISLE            # faces south, back to the entry strip
SUBWAIT = (21.0, REC_S + 0.05, 3)             # 3 seats on the dirty-utility wall, face north


def layout_i_rooms():
    """Layout I.  North block = Layout G's (pencil sketch, true-size IPD), with
    the BP / ECG room turned into the accessible patient WC.  South block = the
    pencil sketch with the clients' blue sizes."""
    mk = G._mk
    north = [r for r in G.layout_g_rooms() if r.key in NORTH_KEYS]
    south = [
        # ------------------------------------------------ CSSD / autoclave row (7'-0")
        mk("wash", "CSSD wash (dirty)", (E0, S0, 6.0, CS_D), "support",
           doors=[D(3.4, CS_C, 2.0, "h", 1, kind="hatch"),
                  D(6.5775, 3.1, 2.4, "v", 1, kind="hatch"),
                  D(6.5775, 5.95, 2.5, "v", -1)],
           furniture=[("counter", 0.6, 0.5, 4.6, 1.5, 0), ("sink", 0.9, 0.65, 1.2, 1.1, 0),
                      ("sink", 2.7, 0.65, 1.2, 1.1, 0), ("cart", 0.6, 4.6, 1.5, 2.2, 0)],
           label=(3.1, 4.7),
           notes="On the builder's x07 toilet slab (drain point); used sets arrive by the OT hatch"),
        mk("cssd", "CSSD clean / pack + AUTOCLAVE", (6.765, S0, 7.5, CS_D), "surgical",
           doors=[D(10.5, CS_C, 2.0, "h", 1, kind="hatch"),
                  D(14.4525, 5.7, 2.5, "v", -1)],
           furniture=[("counter", 9.2, 0.5, 4.9, 1.5, 0), ("cart", 12.3, 3.2, 1.6, 2.0, 0)],
           label=(10.6, 5.0),
           notes="Pass-through autoclave in the wash wall; pass box to the OT"),
        mk("sstore", "Sterile store", (14.64, S0, 5.75, CS_D), "surgical",
           doors=[D(17.6, CS_C, 3.0, "h", -1),
                  D(OTW_C, 4.6, 2.75, "v", 1, hinge="hi")],
           furniture=[("shelf", 14.8, 0.5, 5.4, 1.1, 0), ("shelf", 14.8, 1.9, 1.1, 2.2, 0)],
           label=(17.3, 3.6),
           notes="Opens to the OT; staff reach the CSSD through it from the change room"),
        # ------------------------------------------------ OT 20' x 20'
        mk("ot", "OPERATION THEATRE", (E0, OT_S, 20.0, 20.0), "surgical",
           furniture=[("ottable", 9.39, 7.0 + DY, 2.0, 6.75, 0),
                      ("counter", 5.0, OT_S + 0.02, 4.2, 1.33, 0),
                      ("counter", 11.9, OT_S + 0.02, 3.9, 1.33, 0),
                      ("cart", 5.9, 7.6 + DY, 1.5, 3.0, 0), ("cart", 5.9, 11.0 + DY, 1.5, 3.0, 0)],
           dims="20'-0\" x 20'-0\"", label=(6.0, 25.3),
           notes="Patient through the pre-op room (5'-0\" sliding door); staff through scrub; "
                 "soiled out through the dirty hatch and Dirty utility"),
        # ------------------------------------------------ recovery row (7'-0")
        mk("recB", "RECOVERY BAY", (E0, REC_S, 8.31 - E0, REC_D), "surgical",
           doors=[D(8.4975, 32.9, 3.75, "v", -1, kind="open")],
           furniture=[("bed", 0.6, REC_S + 0.25, 6.5, 3.2, 180), ("side", 0.6, 32.0, 1.4, 1.2, 0)],
           label=(4.5, 34.05),
           notes="East of the kept x06 east wall line (the blue wall of the sketch)"),
        mk("recovery", "PRE-OP / HOLDING", (8.685, REC_S, OT_WF - 8.685, REC_D), "surgical",
           holes=[NOTCH],
           doors=[D(17.8, REC_C, 5.0, "h", -1, kind="slide"),
                  D(17.9, NOTCH[1] + T / 2, 4.0, "h", -1, kind="double")],
           furniture=[("bed", 8.85, REC_S + 0.25, 6.5, 3.2, 180),
                      ("side", 8.85, 32.0, 1.4, 1.2, 0)],
           dims="11'-8\" x 7'-0\"", label=(12.3, 34.05),
           notes="1 holding bay + trolley transfer zone in line with the OT door"),
        # ------------------------------------------------ staff band (6'-1")
        mk("stchange", "OT staff change M / F", (BAND0, S0, BAND1 - BAND0, CS_D), "surgical",
           doors=[D(BAND1 + T / 2, 3.6, 2.75, "v", -1),
                  D(24.6, CS_C, 2.75, "h", 1)],
           furniture=[("shelf", 23.1, 0.5, 3.6, 1.1, 0), ("side", 21.0, 6.15, 2.0, 1.1, 0)],
           dims="6'-1\" x 7'-0\"", label=(23.9, 3.3),
           notes="Only staff way in: OPD passage > staff lobby > change > scrub > OT"),
        mk("scrub", "SCRUB", (BAND0, OT_S, BAND1 - BAND0, 8.0), "surgical",
           doors=[D(OTW_C, 12.0, 3.5, "v", -1)],
           furniture=[("counter", 25.27, 11.0, 1.6, 4.4, 0), ("sink", 25.45, 11.2, 1.2, 1.1, 0),
                      ("sink", 25.45, 12.65, 1.2, 1.1, 0), ("sink", 25.45, 14.1, 1.2, 1.1, 0)],
           label=(22.9, 14.9), notes="3-tap scrub trough outside the OT staff door"),
        mk("anst", "Anaes. / consumable store", (BAND0, 16.14, BAND1 - BAND0, 3.3), "support",
           doors=[D(OTW_C, 17.8, 2.75, "v", 1)],
           furniture=[("shelf", 25.6, 16.3, 1.1, 3.0, 0)], label=(23.4, 18.9),
           notes="Opens to the OT only"),
        mk("du", "Dirty utility", (BAND0, 19.815, BAND1 - BAND0, OT_N - 19.815), "support",
           doors=[D(OTW_C, 25.3, 3.0, "v", 1, hinge="hi"),
                  D(BAND1 + T / 2, 24.0, 3.0, "v", -1)],
           furniture=[("sink", 23.2, 20.0, 1.3, 1.2, 0), ("counter", 24.7, 20.0, 2.0, 1.5, 0),
                      ("cart", 25.3, 26.1, 1.4, 1.5, 0)],
           dims="6'-1\" x 7'-11\"", label=(24.6, 22.6),
           notes="Sluice + waste hold; soiled exit to the OPD passage; column C3 in its SE corner"),
        mk("stlobby", "Staff lobby", (PAS0, S0, PAS_W, W_LG), "surgical",
           doors=[D(29.5, S0 + W_LG + T / 2, 3.5, "h", -1),
                  D(WXC, 3.4, 2.75, "v", 1)],
           label=(28.45, 5.9), notes="Door across the passage: the south end is staff-only"),
        # ------------------------------------------------ west glass column
        mk("lounge", "DRS' LOUNGE", (WX, S0, 16.0, W_LG), "consult",
           holes=[(41.125, S0, 8.0, 4.575)],
           furniture=[("sofa", 35.3, 0.6, 5.5, 2.2, 180), ("chair", 33.0, 5.2, 1.4, 1.4, 0),
                      ("desk", 35.4, 4.6, 3.0, 1.7, 0)],
           label=(38.2, 3.9)),
        mk("wcLg", "Toilet", (41.5, S0, 7.0, 4.2), "wet",
           doors=[D(42.9, 4.78, 2.25, "h", 1)],
           furniture=[("wc", 43.6, 0.6, 1.5, 2.0, 180), ("sink", 41.8, 0.6, 1.3, 1.2, 0)],
           label=(42.6, 3.3)),
        mk("opd2", "OPD 2 · Psychiatry", (WX, Y_OPD2, 16.0, W_OPD), "consult",
           doors=[D(WXC, 13.6, 3.0, "v", 1, hinge="hi")],
           furniture=[("desk", 35.1, 9.3, 4.6, 2.0, 0), ("chair", 36.7, 7.7, 1.4, 1.4, 0),
                      ("chair", 35.4, 11.6, 1.4, 1.4, 0), ("chair", 37.6, 11.6, 1.4, 1.4, 0),
                      ("sofa", 41.1, 8.4, 2.3, 5.2, 0), ("plant", 41.7, 13.9, 1.3, 1.3, 0)],
           label=(37.6, 14.2), notes="Dr. Heena; acoustic partitions + solid door"),
        mk("opd1", "OPD 1 · Ortho", (WX, Y_OPD1, 16.0, W_OPD), "consult",
           doors=[D(WXC, 22.3, 3.0, "v", 1, hinge="hi")],
           furniture=[("exam", 39.7, 17.3, 2.25, 6.0, 0), ("desk", 34.1, 17.7, 4.6, 2.0, 0),
                      ("chair", 35.7, 16.2, 1.4, 1.4, 0), ("chair", 34.3, 20.0, 1.4, 1.4, 0),
                      ("chair", 36.5, 20.0, 1.4, 1.4, 0)],
           label=(37.0, 22.7), notes="Dr. Aman"),
        mk("emer", "EMERGENCY / DRESSING", (WX, Y_EM, 16.0, W_EM), "consult",
           doors=[D(WXC, 31.0, 4.0, "v", 1, kind="double"),
                  D(34.2, Y_XR - T / 2, 3.5, "h", 1, kind="open")],
           furniture=[("exam", 38.6, 25.2, 2.5, 6.4, 0), ("counter", 32.5, 24.6, 4.6, 1.4, 0),
                      ("sink", 32.7, 24.7, 1.2, 1.1, 0), ("cart", 40.6, 31.6, 1.6, 1.8, 0)],
           label=(36.0, 28.4),
           notes="Trolley door straight off the OPD lobby; plaster / dressing / emergency couch"),
        mk("xray", "X-RAY (mobile)", (WX, Y_XR, 16.0, W_XR), "consult",
           doors=[D(WXC, 37.2, 3.5, "v", 1, hinge="hi")],
           furniture=[("exam", 36.3, 34.25, 5.8, 2.25, 0), ("counter", 37.2, 38.3, 2.6, 1.3, 0)],
           label=(38.3, 37.3),
           notes="Lead-lined; on the builder's x06 toilet slab (fill and level); mobile unit only"),
        # ------------------------------------------------ patient WC on the builder's x05 toilet
        mk("wcP", "Patient WC (Acc.)", (E0, 48.49, 7.51, 10.71), "wet",
           holes=[(E0, 48.49, 4.315, 3.265), (6.525, 55.2, 1.6, 4.2)],
           doors=[D(6.4, 48.30, 3.0, "h", 1)],
           furniture=[("wc", 0.6, 56.7, 1.6, 2.2, 0), ("sink", 0.6, 52.1, 1.3, 1.2, 0),
                      ("sink", 5.0, 52.3, 1.3, 1.2, 0)],
           dims="6'-2\" x 7'-5\" + lobby", label=(4.4, 57.6),
           notes="Builder's x05 toilet slab and duct; door on the waiting hall"),
        # ------------------------------------------------ open-plan anchors (circulation)
        mk("hall", f"ENTRY WAITING HALL · {2 * ROW_N} seats", (1.0, ROW_A_Y + SEAT_D + 1.2, 13.0, 1.6),
           "circ",
           furniture=_seats(ROW_X0, ROW_A_Y, ROW_N) + _seats(ROW_X0, ROW_B_Y, ROW_N)),
        mk("lane", "TROLLEY + OPD LANE", (16.3, 37.2, 1.6, 5.4), "circ"),
        mk("entry", "ENTRY PASSAGE 8'-0\"", (8.4, 46.3, 6.0, 1.2), "circ"),
        mk("recep", "RECEPTION", (22.1, 44.4, 2.0, 3.0), "circ",
           furniture=[("counter", 20.45, 41.2, 1.5, 5.6, 0), ("chair", 22.5, 42.4, 1.4, 1.4, 0)]),
        mk("lobby", "OPD LOBBY", (23.5, 35.4, 7.0, 1.4), "circ",
           furniture=_seats(*SUBWAIT) + [("water", 23.2, 38.4, 1.2, 1.2, 0),
                                         ("plant", 30.2, 38.2, 1.3, 1.3, 0)]),
        mk("opdpass", "OPD PASSAGE 4'-6\"", (PAS0 + 0.1, 10.0, 1.6, 15.0), "circ"),
    ]
    return south + north


# -------------------------------------------------------------------- walls
def walls_i(rooms):
    return unary_union([G.wall_bands_g(rooms)] + EXTRA_WALLS)


def free_i(rooms):
    return G.free_space(rooms).difference(unary_union(EXTRA_WALLS))


@contextmanager
def i_geometry():
    """Point the shared tools (blueprint_svg, dxf_export) at the DWG geometry."""
    import importlib
    new = dict(PLATE=G.OUTER, CUTOUT=G.CUTOUT_G, GLASS_WEST=G.GLASS_WEST_G,
               GLASS_NORTH=G.GLASS_NORTH_G, MD_DOOR=G.MD_DOOR_G, wall_bands=walls_i)
    saved = []
    for name in ("plan_model", "dxf_export", "blueprint_svg"):
        mod = importlib.import_module(name)
        for k, v in new.items():
            if hasattr(mod, k):
                saved.append((mod, k, getattr(mod, k)))
                setattr(mod, k, v)
    try:
        yield
    finally:
        for mod, k, v in saved:
            setattr(mod, k, v)


# -------------------------------------------------------- OT equipment, flows
def _shift(e):
    s, x, y, w, h, t, n = e
    return (s, x, y + DY, w, h, t, n)


OT_EQUIP_I = [_shift(e) for e in G.OT_EQUIP if e[5] not in ("PB", "AC", "GAS")] + [
    ("rect", 9.5, OT_S - 0.3, 2.0, 0.55, "PB", "Pass box (sterile hatch) from CSSD clean"),
    ("rect", 2.4, OT_S - 0.3, 2.0, 0.55, "DH", "Dirty return hatch to CSSD wash"),
    ("rect", 5.45, 1.9, 2.3, 2.4, "AC", "Double-door autoclave (pass-through, loads from wash)"),
    ("rect", 10.4, OT_N + 0.39, 1.7, 0.3, "GAS", "Medical gas valve + alarm panel (AVSU)"),
]
OT_CURTAINS_I = [((8.8, 31.8), (15.3, 31.8)), ((0.5, 31.8), (6.4, 31.8))]
OT_TABLE_I = (9.39, 7.0 + DY, 2.0, 6.75)

FLOWS_I = {
    "patient": ("#1565c0", "Patient (trolley)", [
        [(0.9, 45.6), (17.9, 45.6), (17.9, 33.9), (17.8, 30.6), (17.8, 26.0), (12.6, 21.6)],
        [(16.6, 32.75), (9.6, 32.75), (6.0, 32.75)],
        [(17.0, 46.6), (17.0, 50.2)]]),
    "staff": ("#2e7d32", "Staff", [
        [(29.5, 33.0), (29.5, 8.6), (29.5, 5.2)],
        [(29.0, 3.6), (25.2, 3.6), (24.6, 5.6), (24.6, 9.4)],
        [(24.0, 10.2), (22.6, 12.0), (18.4, 12.0)],
        [(30.2, 3.4), (34.4, 3.4)]]),
    "clean": ("#00838f", "Clean / sterile supply", [
        [(4.4, 3.1), (9.0, 3.1)],
        [(10.5, 5.2), (10.5, 10.0)],
        [(13.0, 5.7), (16.0, 5.7)],
        [(17.6, 6.0), (17.6, 10.0)],
        [(22.6, 17.8), (18.4, 17.8)]]),
    "dirty": ("#c62828", "Dirty / soiled", [
        [(3.4, 10.2), (3.4, 6.5)],
        [(18.4, 25.3), (23.0, 25.0), (25.5, 24.0), (28.6, 24.0), (28.6, 31.0), (24.0, 36.6),
         (19.2, 36.6), (19.2, 44.2), (0.9, 44.2)]]),
}
OT_FIRE_PATH = [(0.6, OT_S + 0.2), (17.8, OT_N - 0.2), (17.8, 33.8), (17.9, 45.5), (0.2, 45.5)]
EMER_PATH = [(0.2, 45.5), (18.0, 45.5), (18.0, 36.4), (30.0, 36.0), (30.0, 31.0), (33.0, 31.0)]
SOUTH_KEYS = ("wash", "cssd", "sstore", "ot", "recB", "recovery", "stchange", "scrub", "anst", "du",
              "stlobby", "lounge", "wcLg", "opd2", "opd1", "emer", "xray")
OT_SUITE = ("ot", "recB", "recovery", "scrub", "stchange", "stlobby", "cssd", "wash", "sstore",
            "anst", "du")


@contextmanager
def _g_equipment():
    """Let layout_g's OT-equipment / DXF-extras helpers draw Layout I's lists."""
    saved = (G.OT_EQUIP, G.OT_CURTAINS, G.FLOWS)
    G.OT_EQUIP, G.OT_CURTAINS, G.FLOWS = OT_EQUIP_I, OT_CURTAINS_I, FLOWS_I
    try:
        yield
    finally:
        G.OT_EQUIP, G.OT_CURTAINS, G.FLOWS = saved


# ------------------------------------------------------------------- checks
def _by(rooms):
    return {r.key: r for r in rooms}


def _clear(poly):
    """Largest clear rectangle (E-W, N-S, area); column nibs under 2" are
    ignored (they disappear in the wall lining)."""
    import ipd
    w, d, _ = ipd.toilet_size(poly.buffer(0.17, join_style=2).buffer(-0.17, join_style=2), step=1 / 24)
    return w, d, poly.area


# rooms whose rectangle is only clipped by a 1 3/8" column nib or holds a nested WC / recess
CLEAR_AS_BUILT = {"ot": "20'-0\" x 20'-0\"", "sstore": "5'-9\" x 7'-0\"", "stchange": "6'-1\" x 7'-0\"",
                  "recovery": "11'-8\" x 7'-0\"", "lounge": "14'-7\" x 6'-8\" less WC",
                  "du": "6'-1\" x 7'-11\" less C3"}


def _seat_boxes(rooms):
    return [box(x, y, x + w, y + h) for r in rooms if r.zone == "circ"
            for (k, x, y, w, h, _) in r.furniture if k == "chair" and r.key in ("hall", "lobby")]


def checks(rooms=None):
    """Every number quoted in LAYOUT_I_BRIEF_AND_FEASIBILITY.md."""
    import ipd
    rooms = rooms or layout_i_rooms()
    by = _by(rooms)
    sol = [r for r in rooms if r.zone != "circ"]
    walls = walls_i(rooms)
    free = free_i(rooms)
    out = {}
    out["overlaps_gt_0.5sf"] = [(a.key, b.key, round(a.poly.intersection(b.poly).area, 2))
                                for a, b in combinations(sol, 2)
                                if a.poly.intersection(b.poly).area > 0.5]
    # furniture: inside its room / free floor, clear of walls, columns and each other
    issues = []
    solid_u = unary_union([r.poly for r in sol])
    for r in rooms:
        zone = r.poly if r.zone != "circ" else free
        bs = []
        for (k, x, y, w, h, _) in r.furniture:
            b = box(x, y, x + w, y + h)
            if b.difference(zone.buffer(0.03)).area > 0.05:
                issues.append(f"{r.key}: {k}@({x:.2f},{y:.2f}) outside by "
                              f"{b.difference(zone).area:.2f} sf")
            if b.intersection(walls).area > 0.05:
                issues.append(f"{r.key}: {k}@({x:.2f},{y:.2f}) in a wall / column")
            bs.append((k, b))
        for (ka, a), (kb, b) in combinations(bs, 2):
            if a.intersection(b).area > 0.05 and {ka, kb} != {"counter", "sink"}:
                issues.append(f"{r.key}: {ka} overlaps {kb}")
    out["furniture_issues"] = issues
    doors = []
    for r in rooms:
        for d in r.gdoors:
            pt = Point(d["cx"], d["cy"])
            inside = [s.key for s in sol if s.poly.contains(pt)]
            if r.poly.distance(pt) > 0.3 or inside:
                doors.append((r.key, d["kind"], round(r.poly.distance(pt), 2), inside))
            if d["kind"] in G._LEAF and d["kind"] != "slide":
                op = (box(d["cx"] - d["w"] / 2, d["cy"] - 0.2, d["cx"] + d["w"] / 2, d["cy"] + 0.2)
                      if d["axis"] == "h" else
                      box(d["cx"] - 0.2, d["cy"] - d["w"] / 2, d["cx"] + 0.2, d["cy"] + d["w"] / 2))
                if op.intersection(G.COLS).area > 0.01:
                    doors.append((r.key, "door in a column"))
    out["doors_off_wall"] = doors

    # ---- waiting
    seats = _seat_boxes(rooms)
    hall = [s for s in seats if s.bounds[0] < LANE[0] + 0.01]
    strip = box(E0, ENTRY_STRIP[0], 20.28, ENTRY_STRIP[1])
    lane = box(LANE[0], LOBBY_GAP[0], LANE[1], ENTRY_STRIP[0])
    link = box(20.28, LOBBY_GAP[0], PAS1, LOBBY_GAP[1])
    hall_poly = box(E0, HALL_S, 20.28, HALL_N)
    out["waiting"] = dict(
        seats_hall=len(hall), seats_opd_subwait=len(seats) - len(hall), seats_total=len(seats),
        seat_size=f"{fi(SEAT_W)} x {fi(SEAT_D)}",
        aisle_between_rows_ft=round(ROW_B_Y - ROW_A_Y - SEAT_D, 2),
        hall_clear=f"{fi(20.28 - E0)} x {fi(HALL_N - HALL_S)}",
        hall_area_sf=round(hall_poly.area, 0),
        hall_sf_per_seat=round(hall_poly.area / len(hall), 1),
        seating_zone_sf_per_seat=round((LANE[0] - E0) * (ENTRY_STRIP[0] - HALL_S) / len(hall), 1),
        entry_strip_clear_ft=round(ENTRY_STRIP[1] - (ROW_B_Y + SEAT_D), 2),
        lane_clear_ft=round(LANE[1] - LANE[0], 2),
        seats_in_5ft_strip=sum(1 for s in seats if s.intersection(strip).area > 0.01),
        seats_in_lane=sum(1 for s in seats if s.intersection(lane).area > 0.01),
        seats_in_lobby_link=sum(1 for s in seats if s.intersection(link).area > 0.01),
        third_row_needs_ft=round(SEAT_D * 3 + AISLE + 5.0 - (HALL_N - HALL_S), 2))
    seat_u = unary_union(seats)
    trolley = LineString(FLOWS_I["patient"][2][0])
    out["trolley_route"] = dict(
        main_door_to_ot_door_ft=round(LineString(FLOWS_I["patient"][2][0][:5]).length, 1),
        min_gap_to_a_seat_ft=round(trolley.distance(seat_u), 2),
        crosses_seat_rows=bool(trolley.buffer(1.25).intersection(seat_u).area > 0.01),
        blocked_by_walls_ft=round(trolley.intersection(walls).length, 2))
    out["flow_blocked_ft"] = {
        n: round(sum(LineString(l).intersection(walls).length
                     + LineString(l).intersection(seat_u).length for l in ls), 2)
        for n, (_, _, ls) in FLOWS_I.items()}

    # ---- widths (clear, scanned on the free floor)
    sw = G._scan_width
    out["widths_ft"] = dict(
        opd_passage=round(min(sw(free, "x", y, 26.9, 32.2) for y in
                              [Y_OPD2 + 0.3 + 0.25 * i for i in range(78)]), 2),
        ward_passage=round(min(sw(free, "x", y, 13.0, 21.5) for y in
                               [49.0 + 0.25 * i for i in range(140)]), 2),
        hall_to_lobby_gap=round(sw(free, "y", 20.5, 30.0, 40.0), 2),
        lane=round(min(sw(free.difference(seat_u), "x", y, LANE[0] - 0.5, 20.5)
                       for y in [HALL_S + 0.3 + 0.25 * i for i in range(28)]), 2),
        entry_strip=round(min(sw(free.difference(seat_u), "y", x, ROW_B_Y + SEAT_D - 0.2, 48.3)
                              for x in [0.6 + 0.25 * i for i in range(76)]), 2),
        lobby_ns=round(sw(free, "y", 29.0, REC_S - 1, 40.2), 2),
        lobby_clear_north_of_subwait=round(39.76 - (REC_S + 0.05 + SEAT_D + AISLE), 2))

    # ---- OT
    ot = by["ot"].poly
    a, b = ipd.span(ot, 10.0, 17.0, "x")
    c, d_ = ipd.span(ot, 10.0, 17.0, "y")
    sq = box(E0, OT_S, OT_WF, OT_N)
    tx, ty, tw, th = OT_TABLE_I
    ring = box(tx - 4, ty - 4, tx + tw + 4, ty + th + 4)
    fixed = [box(x, y, x + w, y + h) for (k, x, y, w, h, _) in by["ot"].furniture if k == "counter"]
    fixed += [box(x, y, x + w, y + h) for s_, x, y, w, h, t, _ in OT_EQUIP_I
              if t in ("C-ARM", "CP", "PB", "DH")]
    eq = [(t or n, box(x, y, x + w, y + h)) for s_, x, y, w, h, t, n in OT_EQUIP_I if s_ == "rect"]
    eq += [(t, Point(x, y).buffer(w)) for s_, x, y, w, h, t, n in OT_EQUIP_I if s_ == "pend"]
    eq += [("table", box(tx, ty, tx + tw, ty + th))]
    eq += [(f"ot-{k}", box(x, y, x + w, y + h)) for (k, x, y, w, h, _) in by["ot"].furniture
           if k != "ottable"]
    out["ot"] = dict(
        clear_ft=(round(b - a, 2), round(d_ - c, 2)), area_sf=round(ot.area, 1),
        area_m2=round(ot.area * 0.092903, 1),
        columns_in_20x20={n: dict(proud_in=round((OT_WF - col.bounds[0]) * 12, 1),
                                  long_in=round((col.bounds[3] - col.bounds[1]) * 12, 1))
                          for n, col in G.COLUMNS.items() if col.intersection(sq).area > 1e-4},
        table_to_walls=dict(east=fi(tx - a), west=fi(b - tx - tw), south=fi(ty - c),
                            north=fi(d_ - ty - th)),
        fixed_items_in_4ft_ring_sf=round(sum(f.intersection(ring).area for f in fixed), 2),
        equipment_clashes=[(na, nb) for (na, ga), (nb, gb) in combinations(eq, 2)
                           if ga.intersection(gb).area > 0.02],
        doors={f"{r.key}.{i}": f"{fi(d['w'])} {d['kind']}" for r in rooms if r.key in OT_SUITE
               for i, d in enumerate(r.gdoors)},
        suite_area_sf=round(sum(by[k].area for k in OT_SUITE), 0))
    out["rooms"] = {}
    for r in sol:
        if r.key in SOUTH_KEYS or r.key == "wcP":
            w_, d2, _ = _clear(r.poly)
            out["rooms"][r.key] = dict(clear=CLEAR_AS_BUILT.get(r.key, f"{fi(w_)} x {fi(d2)}"), area_sf=round(r.area, 1),
                                       area_m2=round(r.area * 0.092903, 1))
    # ---- X-ray against AERB (figures from memory: to verify)
    em, xr = by["emer"].poly, by["xray"].poly
    xw_, xd_, _ = _clear(xr)
    ew_, ed_, _ = _clear(em)
    out["xray_aerb"] = dict(
        xray_clear=f"{fi(xw_)} x {fi(xd_)}", xray_m2=round(xr.area * 0.092903, 1),
        emergency_clear=f"{fi(ew_)} x {fi(ed_)}", emergency_m2=round(em.area * 0.092903, 1),
        combined_m2=round((em.area + xr.area) * 0.092903, 1),
        largest_side_m=round(max(ew_, ed_) * 0.3048, 2), shortest_side_m=round(min(xw_, xd_) * 0.3048, 2),
        fixed_unit_18m2_4m_side="FAILS (area and width)",
        xray_ew_width_at_cutout_end=fi(xw(39.76) - WX))
    # ---- travel
    stair = LineString(G.STAIR_PATH).length
    p_ot, p_ward, p_em = LineString(OT_FIRE_PATH), LineString(G.FIRE_PATH), LineString(EMER_PATH)
    out["travel_ft"] = dict(
        ot_far_corner_to_main_door=round(p_ot.length, 1),
        ot_far_corner_to_stair=round(p_ot.length + stair, 1),
        suite_far_corner_to_main_door=round(p_ward.length, 1),
        suite_far_corner_to_stair=round(p_ward.length + stair, 1),
        main_door_to_emergency_door=round(p_em.length, 1),
        main_door_to_stair_approx=round(stair, 1),
        blocked_ft=round(sum(p.intersection(walls).length + p.intersection(seat_u).length
                             for p in (p_ot, p_ward, p_em)), 2))
    # ---- beds, IPD audit, columns in rooms, areas
    glass = unary_union([LineString(s) for s in G.GLASS_WEST_G + G.GLASS_NORTH_G]).buffer(1.2)
    iss, nb, nh = ipd.audit(rooms, walls, glass)
    out["ipd_audit"] = dict(beds=nb, heads_on_solid_walls=nh, issues=iss)
    out["beds"] = {r.key: sum(1 for f in r.furniture if f[0] == "bed") for r in rooms
                   if any(f[0] == "bed" for f in r.furniture)}
    out["columns_in_rooms"] = {}
    for n, col in G.COLUMNS.items():
        for r in sol:
            x, y, w, h = r.rect
            full = box(x, y, x + w, y + h).intersection(G.INNER)
            for hx, hy, hw, hh in r.holes:
                full = full.difference(box(hx, hy, hx + hw, hy + hh))
            ar = full.intersection(col).area
            if ar > 0.3:
                out["columns_in_rooms"].setdefault(r.key, []).append(f"{n} {ar:.1f} sf")
    clear = G.INNER.area - G.CUTOUT_G.intersection(G.INNER).area
    out["areas_sf"] = dict(rooms=round(sum(r.area for r in sol), 0), clear_floor=round(clear, 0),
                           circulation_open=round(free.area, 0),
                           walls_columns=round(clear - sum(r.area for r in sol) - free.area, 0),
                           waiting_hall=round(hall_poly.area, 0),
                           opd_lobby=round(box(BAND0, REC_S, PAS1, 39.76).area, 0))
    return out


def schedule_rows(rooms=None):
    rooms = rooms or layout_i_rooms()
    from plan_model import ZONES
    return [(r.key, r.name.replace("\n", " "), r.dims, r.area, ZONES[r.zone][1])
            for r in rooms if r.zone != "circ" and r.key != "duct"]


# ------------------------------------------------------------------ drawing
def _draw_base(ax, rooms, walls, R, tag_fs=4.6, equip_labels=False):
    """layout_g's plan drawing with Layout I's OT equipment; the two G-only
    '3rd sketch' lines are taken off again."""
    with _g_equipment():
        G._draw_base(ax, rooms, walls, R, tag_fs=tag_fs, equip_labels=equip_labels)
    for ln in list(ax.lines):
        if ln.get_color() == "#3b4cc0":
            ln.remove()
    for t in list(ax.texts):
        if t.get_text().startswith("screen (as sketched)"):
            t.remove()
    # seats read as seats: a back line on every waiting chair
    for r in rooms:
        if r.key in ("hall", "lobby"):
            for (k, x, y, w, h, _) in r.furniture:
                if k == "chair":
                    back = y + 0.22 if (r.key == "lobby" or abs(y - ROW_A_Y) < 0.01) else y + h - 0.22
                    ax.plot([x + 0.12, x + w - 0.12], [back, back], color="#4a4a4a", lw=0.6, zorder=6.2)
    # reception counter opening + existing wall kept in the recovery
    ax.plot([8.4975, 8.4975], [REC_S, REC_N], color="#1f3fbf", lw=0.5, ls=(0, (2, 2)), zorder=7.6)


def _flows(ax, lw=2.4, ms=14, alpha=0.85, z=15):
    from matplotlib.patches import FancyArrowPatch
    for name, (colr, _, lines) in FLOWS_I.items():
        ls = (0, (3.5, 1.2)) if name == "dirty" else "-"
        for pts in lines:
            if len(pts) > 2:
                ax.plot([p[0] for p in pts[:-1]], [p[1] for p in pts[:-1]], color=colr, lw=lw,
                        alpha=alpha, zorder=z, solid_capstyle="round", solid_joinstyle="round", ls=ls)
            ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=ms,
                                         lw=lw, color=colr, alpha=min(1, alpha + 0.05), zorder=z,
                                         shrinkA=0, shrinkB=0, ls=ls))


CLIENT_BLUE = "#1f3fbf"
# blue-pen sizes shown on the sheets: (x, y, text, rotation)
CLIENT_TAGS = [(-2.6, S0 + CS_D / 2, "7", 0), (-2.6, REC_S + REC_D / 2, "7", 0),
               (-2.6, OT_S + 3.0, "20", 0), (-2.6, 44.6, "8", 0), (30.6, 26.6, "4.5", 0),
               (46.9, Y_OPD2 + W_OPD / 2, "8.1", 0), (45.7, Y_OPD1 + W_OPD / 2, "8.1", 0),
               (44.6, Y_EM + W_EM / 2, "9.3", 0), (43.6, Y_XR + W_XR / 2, "5.9", 0)]


def _client_tags(ax, fs=6.4, z=14):
    for x, y, t, rot in CLIENT_TAGS:
        ax.text(x, y, t, ha="center", va="center", fontsize=fs, color=CLIENT_BLUE, zorder=z,
                style="italic", weight="bold", rotation=rot,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=CLIENT_BLUE, lw=0.6))


SHEET_LABELS = {      # key: (text template, fontsize, rotation)
    "ot": ("OPERATION THEATRE\n{d} · {a:.0f} sf", 8.4, 0),
    "wash": ("CSSD wash (dirty)\n{d} · {a:.0f} sf", 4.8, 0),
    "cssd": ("CSSD clean / pack\n+ AUTOCLAVE\n{d} · {a:.0f} sf", 4.8, 0),
    "sstore": ("Sterile store\n{d}\n{a:.0f} sf", 4.6, 0),
    "recB": ("RECOVERY BAY\n{d} · {a:.0f} sf", 5.2, 0),
    "recovery": ("PRE-OP / HOLDING\n{d} · {a:.0f} sf", 5.2, 0),
    "stchange": ("OT staff\nchange M / F\n{a:.0f} sf", 4.6, 0),
    "scrub": ("SCRUB · {d} · {a:.0f} sf", 4.4, 0),
    "anst": ("Anaes. store · {a:.0f} sf", 4.2, 0),
    "du": ("Dirty utility\n{a:.0f} sf", 4.6, 0),
    "stlobby": ("Staff\nlobby", 4.4, 0),
    "lounge": ("DRS' LOUNGE\n{d} · {a:.0f} sf", 6.0, 0),
    "opd2": ("OPD 2 · Psychiatry\n{d} · {a:.0f} sf", 6.6, 0),
    "opd1": ("OPD 1 · Ortho\n{d} · {a:.0f} sf", 6.6, 0),
    "emer": ("EMERGENCY /\nDRESSING\n{d} · {a:.0f} sf", 6.4, 0),
    "xray": ("X-RAY (mobile)\n{d} · {a:.0f} sf", 5.4, 0),
}


def render_sheet(out_base):
    """Dimensioned CAD sheet (PNG + SVG + JPG).  South at the top."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, FancyArrow
    from matplotlib.lines import Line2D
    import render as R
    import ipd
    from plan_model import ZONES

    INK = R.INK
    rooms = layout_i_rooms()
    walls = walls_i(rooms)
    chk = checks(rooms)
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
            big = r.key == "hall"
            ax.text(x0 + w0 / 2, y0 + h0 / 2, r.name, ha="center", va="center",
                    fontsize=8.6 if big else (5.2 if r.key in ("lane", "recep") else 6.6),
                    color="#222" if big else "#444", style="italic", weight="bold", zorder=9,
                    rotation=90 if r.key == "recep" else rot)
            continue
        if r.key == "duct":
            ax.text(lx + 0.5, ly + 0.3, "DUCT", fontsize=5, ha="center", va="center", zorder=9)
            continue
        if r.key in G.IPD_G:
            o = G.IPD_G[r.key]
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
                        f"{fi(tw)} × {fi(td)}", ha="center", va="center", fontsize=4.6, color=INK,
                        zorder=11, bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.85))
            for key, c in (("bath5", (3.4, 75.75)), ("wcP", (3.4, 55.0))):
                if r.key == key:
                    ax.add_patch(Circle(c, 2.5, fc="none", ec="#2c6fbb", lw=0.6, ls=(0, (4, 3)),
                                        zorder=9))
            ax.add_patch(Circle((lx, ly), 0.85, fc="white", ec=INK, lw=0.7, zorder=10))
            ax.text(lx, ly, "T", ha="center", va="center", fontsize=6.5, weight="bold", color=INK,
                    zorder=11)
            tag = {"bath5": "Suite bath", "wcP": f"PATIENT WC (Acc.)\n{r.area:.0f} sf"}.get(r.key)
            if tag:
                ax.text(lx, ly + (1.45 if r.key == "bath5" else -2.1), tag, ha="center", va="center",
                        fontsize=5.2, color=INK, zorder=11, weight="bold" if r.key == "wcP" else None,
                        bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.8))
            continue
        if r.key in SHEET_LABELS:
            tpl, fs, rot = SHEET_LABELS[r.key]
            d = chk["rooms"][r.key]["clear"].replace(" x ", " × ").split(" less")[0]
            txt = tpl.format(d=d, a=r.area)
        else:
            fs = G.LABEL_FS.get(r.key, 6.2 if r.key in G.SMALL else 7.4)
            rot = 0
            txt = f"{r.name}\n{r.dims.split(' incl')[0]}\n{r.area:.0f} sf"
            if r.key == "obs":
                txt, fs = f"Obs. Bed {r.dims} · {r.area:.0f} sf", 5.2
        ax.text(lx, ly, txt, ha="center", va="center", fontsize=fs, color="#111",
                weight="bold" if (r.name.isupper() or r.key in ("opd1", "opd2")) else "normal",
                zorder=9, linespacing=1.25, rotation=rot,
                bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.72))
    ax.text(27.0, 30.4, "sub-wait · 3 seats", ha="center", va="center", fontsize=5.0, color="#444",
            style="italic", zorder=9)
    ax.text(7.5, HALL_S + SEAT_D + 3.35, f"2 rows × {ROW_N} seats 1'-10\" × 1'-8\" · 4'-0\" aisle",
            ha="center", va="center", fontsize=5.6, color="#444", style="italic", zorder=9)

    # ---- column grid
    for name, gx in G.GRID_X.items():
        ax.plot([gx, gx], [-7.2, 95.5], color="#b04a2f", lw=0.5, ls=(0, (10, 3, 2, 3)), zorder=4)
        ax.add_patch(Circle((gx, -8.2), 1.0, fc="white", ec="#b04a2f", lw=0.9, zorder=12))
        ax.text(gx, -8.2, name, ha="center", va="center", fontsize=8, color="#b04a2f",
                weight="bold", zorder=13)
    for name, gy in G.GRID_Y.items():
        ax.plot([-11.2, 52.6], [gy, gy], color="#b04a2f", lw=0.5, ls=(0, (10, 3, 2, 3)), zorder=4)
        ax.add_patch(Circle((53.6, gy), 1.0, fc="white", ec="#b04a2f", lw=0.9, zorder=12))
        ax.text(53.6, gy, name, ha="center", va="center", fontsize=8, color="#b04a2f",
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

    def chain_v(ys, x, fs=6.3, side=-1, labels=None):
        ax.plot([x, x], [ys[0], ys[-1]], color=INK, lw=0.6, zorder=12)
        for y in ys:
            tick(x, y)
            ax.plot([x - 0.5, x + 0.5], [y, y], color=INK, lw=0.35, zorder=12)
        labels = labels or [fi(b - a) if b - a > 1 else "" for a, b in zip(ys[:-1], ys[1:])]
        for (ya, yb), lab in zip(zip(ys[:-1], ys[1:]), labels):
            if lab:
                ax.text(x + side * 0.8, (ya + yb) / 2, lab, ha="center", va="center", fontsize=fs,
                        color=INK, rotation=90, zorder=12)

    xs = [E0, OT_WF, BAND0, BAND1, PAS0, PAS1, WX, xw(S0)]
    chain_h(xs, -3.6, ["20'-0\"", "", fi(BAND1 - BAND0), "", "4'-6\"", "", fi(xw(S0) - WX)])
    chain_h([0.0, 47.98], -5.9, ["47'-11¾\" over walls"], fs=7)
    chain_v([S0, S0 + CS_D, OT_S, OT_N, REC_S, REC_N, HALL_S, 40.09, 48.10, 48.49, 55.2, 55.575,
             59.2, 59.575, 66.0, 66.375, 72.425, 72.8, 78.8, 79.175, G.N0], -12.2)
    chain_v([0.0, 92.22], -14.6, fs=7, labels=["92'-2¾\" over walls"])
    chain_v([48.49, 58.9, 59.275, 69.7, 70.075, 80.3, 80.675, G.N0], 45.4, side=1)
    chain_v([S0, S0 + W_LG, Y_OPD2, Y_OPD2 + W_OPD, Y_OPD1, Y_OPD1 + W_OPD, Y_EM, Y_EM + W_EM,
             Y_XR, 39.76], 50.4, side=1)
    for (xa, xb, y, lab) in [(14.28, 20.28, 73.6, "6'-0\""),
                             (LANE[0], LANE[1], 36.5, fi(LANE[1] - LANE[0]))]:
        ax.annotate("", xy=(xb, y), xytext=(xa, y),
                    arrowprops=dict(arrowstyle="<->", lw=0.8, color="#a33"), zorder=12)
        ax.text((xa + xb) / 2, y - 0.6, lab, ha="center", va="center", fontsize=6.5, color="#a33",
                zorder=12)
    for (x, ya, yb, lab, lx) in [(3.0, ROW_B_Y + SEAT_D, HALL_N, fi(HALL_N - ROW_B_Y - SEAT_D), 3.7),
                                 (20.52, LOBBY_GAP[0], LOBBY_GAP[1], "5'-0\"", 21.3)]:
        ax.annotate("", xy=(x, yb), xytext=(x, ya),
                    arrowprops=dict(arrowstyle="<->", lw=0.8, color="#a33"), zorder=12)
        ax.text(lx, (ya + yb) / 2, lab, ha="center", va="center", fontsize=6.5, color="#a33",
                rotation=90, zorder=12)
    _client_tags(ax)
    _flows(ax, lw=1.1, ms=8, alpha=0.75, z=9.5)

    # ---- compass, north arrow, title
    for x, y, s in [(24, -11.0, "SOUTH SIDE"), (20, 97.2, "NORTH SIDE")]:
        ax.text(x, y, s, ha="center", va="center", fontsize=10, weight="bold",
                bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(-17.2, 64, "EAST SIDE (lift / stair core)", rotation=90, ha="center", va="center",
            fontsize=10, weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(55.6, 60, "WEST SIDE", rotation=-90, ha="center", va="center", fontsize=10,
            weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.add_patch(FancyArrow(55.6, 86.5, 0, 4.2, width=0.5, head_width=1.8, head_length=1.6,
                            fc=INK, ec=INK))
    ax.text(55.6, 85.0, "N", ha="center", fontsize=12, weight="bold", color=INK)
    w = chk["waiting"]
    clear = chk["areas_sf"]["clear_floor"]
    ax.set_title("LAYOUT I — clients' pencil sketch with blue-pen sizes on the builder's DWG geometry "
                 "· LARGE WAITING HALL AT THE ENTRY\n"
                 "Hospital of Dr. Aman Khanna & Dr. Heena — 7th Floor, Solaris Shine, Althan, Surat\n"
                 f"Waiting {w['seats_total']} seats ({w['seats_hall']} in the hall + "
                 f"{w['seats_opd_subwait']} OPD sub-wait)  ·  OT 20'-0\" × 20'-0\"  ·  5 beds + 2 pre-op / "
                 f"recovery + 1 observation  ·  clear floor ≈ {clear:,.0f} sq ft", fontsize=12, pad=14)

    # ---- legend, notes
    handles = [Line2D([], [], marker="s", ls="", ms=10, mfc=R._tint(colr, 0.38), mec="#999",
                      label=lbl) for colr, lbl in ZONES.values() if lbl != "Circulation"]
    handles += [Line2D([], [], marker="s", ls="", ms=10, mfc=INK, mec=INK, label="Walls (4½\" partitions)"),
                Line2D([], [], marker="s", ls="", ms=10, mfc="#8c2f1b", mec="black",
                       label="RCC column (from DWG)"),
                Line2D([], [], color="#2c6fbb", lw=2.0, label="Openable glass facade"),
                Line2D([], [], color="#1f77b4", lw=1, ls=(0, (4, 2)),
                       label="Builder's toilet slab / duct (existing)"),
                Line2D([], [], color="#c0392b", lw=1, ls=(0, (5, 3)), label="Existing 100 mm wall removed"),
                Line2D([], [], color="#b04a2f", lw=0.8, ls=(0, (10, 3, 2, 3)), label="Column grid line"),
                Line2D([], [], marker="s", ls="", ms=9, mfc="white", mec=CLIENT_BLUE,
                       label="Clients' blue-pen size (feet)")]
    handles += [Line2D([], [], color=c, lw=1.4, ls=(0, (3.5, 1.2)) if n == "dirty" else "-", label=l)
                for n, (c, l, _) in FLOWS_I.items()]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(-19, 105.6),
              bbox_transform=ax.transData, ncol=4, fontsize=7.6, frameon=False)
    x_ = chk["xray_aerb"]
    notes = ("NOTES\n"
             "1. Geometry: builder DWG (typical 5th/7th/10th floor), units x05+x06+x07 + dead-end passage. Dimensions are "
             "clear, between finished wall faces.  Blue boxes = the clients' blue-pen sizes, all built exactly.\n"
             f"2. WAITING: {w['seats_hall']} seats in the entry hall (2 rows of {ROW_N}, 4'-0\" aisle between), "
             f"{w['seats_opd_subwait']} sub-wait seats in the OPD lobby = {w['seats_total']}.  No seat stands in the "
             f"{fi(w['entry_strip_clear_ft'])} entry strip, the {fi(w['lane_clear_ft'])} lane or the 5'-0\" opening to the "
             "OPD lobby.  A third row (24 seats) needs 1'-5\" taken from the 7' + 7' of the autoclave row and recovery.\n"
             "3. Trolley: main door > entry strip > lane > pre-op door > OT.  It never crosses a seat row; it shares the "
             "lane with OPD walkers.  OT 20'-0\" × 20'-0\" clear; OT suite detail and flows: ot_I_zone.jpg.\n"
             f"4. X-ray {x_['xray_clear']} ({x_['xray_m2']} m²) + Emergency {x_['emergency_clear']}: mobile / portable unit "
             "only (AERB fixed unit ≈ 18 m², no side < 4 m: figures from memory, to verify).\n"
             "5. Patient WC is on the builder's x05 toilet slab at the hall (was BP / ECG in Layout G).  New wet points "
             "(scrub, CSSD, sluice, lounge WC, ward toilets): raised floor + drain runs to be designed.\n"
             "6. IPD block as Layout G: 4 single rooms + suite, true-size furniture (bed 3'-3\" × 7'-0\").  Concept for "
             "review; structure, fire, AERB and HVAC to be verified by the project architect and consultants.")
    ax.text(-18, 113.3, notes, fontsize=6.6, color=INK, va="top", linespacing=1.5)
    ax.text(-18, 104.0, "DOORS  " + "   ".join(f"{t} = {d}" for t, d in G.DOOR_LEGEND), fontsize=6.2,
            color="#a33", va="top")

    ax.plot([0, 20], [100.5, 100.5], lw=3, color=INK)
    for i in range(0, 21, 5):
        ax.plot([i, i], [99.9, 101.1], lw=1.2, color=INK)
        ax.text(i, 102.5, f"{i}'", ha="center", fontsize=7, color=INK)

    # ---- room schedule (right margin)
    sched = schedule_rows(rooms)
    lines = ["ROOM SCHEDULE (clear sizes)", "─" * 49]
    for n, (key, name, dims, area, _) in enumerate(sched, 1):
        nm = (name[:26] + "…") if len(name) > 27 else name
        dm = chk["rooms"][key]["clear"] if key in chk["rooms"] and key != "wcP" else dims
        dm = dm.split(" + ")[0].split(" incl")[0]
        lines.append(f"{n:>2} {nm:<28s} {dm:<17s}{area:>4.0f}")
    a = chk["areas_sf"]
    lines += ["─" * 49, f"   rooms total {a['rooms']:>32.0f} sf",
              f"   waiting hall (open) {a['waiting_hall']:>24.0f} sf",
              f"   clear floor inside walls {a['clear_floor']:>19.0f} sf", "",
              f"WAITING  {w['seats_hall']} hall + {w['seats_opd_subwait']} OPD sub-wait = "
              f"{w['seats_total']} seats",
              "BEDS  5 in-patient (4 single rooms + suite)",
              "      2 pre-op / recovery, 1 observation", "      1 staff rest (duty bunk)"]
    ax.text(58.4, -6, "\n".join(lines), fontsize=6.4, color=INK, va="top", family="monospace",
            linespacing=1.42)

    tb0, tb1 = 125.0, 132.0
    ax.add_patch(Rectangle((-18, tb0), 104, tb1 - tb0, fc="white", ec=INK, lw=1.2, zorder=3))
    for fx in (16, 48, 68):
        ax.plot([fx, fx], [tb0, tb1], color=INK, lw=0.8, zorder=4)
    for x, head, body in [(-16.5, "PROJECT", "Hospital of Dr. Aman Khanna & Dr. Heena\n"
                                             "7th Floor, Solaris Shine, Althan, Surat"),
                          (17.5, "DRAWING", "LAYOUT I — pencil sketch, large entry waiting\n"
                                            "Dimensioned layout plan, feet-inches"),
                          (49.5, "SCALE / DATE", f"N.T.S. (use the scale bar)\n{DATE}"),
                          (69.5, "STATUS", "Concept for review — to be verified\n"
                                           "by the project architect")]:
        ax.text(x, tb0 + 1.5, head, fontsize=6, color="#777", zorder=5)
        ax.text(x, tb0 + 4.6, body, fontsize=7.5, color=INK, va="center", zorder=5)
    ax.set_xlim(-20, 88)
    ax.set_ylim(133.5, -13.5)
    ax.axis("off")
    ipd.save_sheet(fig, ax, out_base)
    plt.close(fig)


def render_ot_zone(out_jpg, px=2400):
    """OT-zone + waiting-hall close-up with the four flow routes."""
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyArrowPatch
    from PIL import Image
    import render as R
    import ipd

    INK = R.INK
    rooms = layout_i_rooms()
    by = _by(rooms)
    walls = walls_i(rooms)
    chk = checks(rooms)
    X0, X1, Y0, YP, Y1 = -12.5, 50.5, -7.5, 49.6, 74.6
    W_IN = 16.0
    FT = W_IN / (X1 - X0)
    fig = plt.figure(figsize=(W_IN, W_IN * (Y1 - Y0) / (X1 - X0)))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    _draw_base(ax, rooms, walls, R, tag_fs=6.4, equip_labels=True)
    ax.add_patch(Rectangle((X0, YP), X1 - X0, Y1 - YP, fc="white", ec="none", zorder=20))
    ax.plot([X0, X1], [YP, YP], color=INK, lw=0.9, zorder=21)
    ax.add_patch(Rectangle((X0, Y0), X1 - X0, 2.6, fc="white", ec="none", zorder=20))

    def lab(x, y, txt, fs=6.0, bold=False, rot=0, color="#111", alpha=0.86, z=13):
        ax.text(x, y, txt, ha="center", va="center", fontsize=fs * 1.3, color=color, zorder=z,
                weight="bold" if bold else "normal", rotation=rot, linespacing=1.25,
                bbox=dict(fc="white", ec="none", pad=0.4, alpha=alpha))

    a_ = {k: by[k].area for k in by}
    d_ = {k: v["clear"].replace(" x ", " × ").split(" less")[0] for k, v in chk["rooms"].items()}
    w = chk["waiting"]
    ax.text(X0 + 0.8, Y0 + 1.25, "OT ZONE + ENTRY WAITING — LAYOUT I    sizes, equipment and flow routes",
            fontsize=13.5, weight="bold", color=INK, va="center", zorder=22)
    ax.text(X1 - 0.8, Y0 + 1.25, "Solaris Shine, 7th floor · Dr. Aman Khanna & Dr. Heena · " + DATE
            + " · concept for review", fontsize=7.6, color="#444", va="center", ha="right", zorder=22)

    lab(5.9, 25.2, f"OPERATION THEATRE\n20'-0\" × 20'-0\" clear\n{a_['ot']:.0f} sf · "
        f"{a_['ot'] * 0.0929:.1f} m²", 9.0, True)
    lab(3.1, 4.8, f"CSSD WASH (dirty)\n{d_['wash']} · {a_['wash']:.0f} sf", 4.6, True)
    lab(10.9, 5.1, f"CSSD CLEAN / PACK\n{d_['cssd']} · {a_['cssd']:.0f} sf", 4.6, True)
    lab(17.6, 4.2, f"STERILE STORE\n{d_['sstore']}\n{a_['sstore']:.0f} sf", 4.6, True)
    lab(24.0, 3.3, f"STAFF CHANGE\nM / F\n{a_['stchange']:.0f} sf", 4.6, True)
    lab(22.9, 15.0, f"SCRUB · {a_['scrub']:.0f} sf", 4.8, True)
    lab(23.2, 18.95, f"ANAES. STORE · {a_['anst']:.0f} sf", 4.0, True)
    lab(24.6, 22.4, f"DIRTY\nUTILITY\n{a_['du']:.0f} sf", 4.6, True)
    lab(28.5, 1.8, "STAFF\nLOBBY", 4.2, True)
    lab(4.5, 34.1, f"RECOVERY BAY\n{d_['recB']} · {a_['recB']:.0f} sf", 4.8, True)
    lab(12.3, 34.1, f"PRE-OP / HOLDING\n{d_['recovery']} · {a_['recovery']:.0f} sf", 4.8, True)
    lab(38.3, 4.4, f"DRS' LOUNGE\n{d_['lounge']} · {a_['lounge']:.0f} sf", 5.4, True)
    lab(37.8, 14.2, f"OPD 2 · Psychiatry\n{d_['opd2']} · {a_['opd2']:.0f} sf", 5.4)
    lab(37.0, 22.7, f"OPD 1 · Ortho\n{d_['opd1']} · {a_['opd1']:.0f} sf", 5.4)
    lab(35.9, 28.5, f"EMERGENCY /\nDRESSING\n{d_['emer']} · {a_['emer']:.0f} sf", 5.4, True)
    lab(38.4, 37.4, f"X-RAY (mobile)\n{d_['xray']} · {a_['xray']:.0f} sf", 4.8, True)
    lab(7.6, 39.2, f"ENTRY WAITING HALL · {w['seats_hall']} seats\n{w['hall_clear'].replace(' x ', ' × ')} · "
        f"{w['hall_area_sf']:.0f} sf · 4'-0\" aisle", 6.4, True)
    lab(22.4, 45.2, "RECEPTION", 4.8, True, rot=90)
    lab(26.4, 38.6, "OPD LOBBY", 5.0, True)
    lab(24.0, 30.7, "sub-wait · 3 seats", 4.2)
    for x, y, t, rot in [(28.25, 19.0, "OPD PASSAGE 4'-6\"", 90), (11.6, 47.2, "ENTRY PASSAGE 8'-0\" · 5'-0\" kept clear", 0)]:
        ax.text(x, y, t, ha="center", va="center", fontsize=7.4, color="#444", style="italic",
                weight="bold", rotation=rot, zorder=13)
    ax.text(3.0, 2.9, "ex. x07 toilet slab = drain", ha="center", va="center", fontsize=5.4,
            color="#1f77b4", zorder=13)
    for nm, (cx, cy) in (("C1", (21.57, 0.95)), ("C3", (21.57, 21.1)), ("C5", (21.57, 39.35))):
        ax.text(cx, cy, nm, ha="center", va="center", fontsize=7.0, color="white", zorder=13,
                weight="bold")
    tx, ty, tw, th = OT_TABLE_I
    lab(tx + tw / 2, ty + th + 0.75, "OT TABLE 2'-0\" × 6'-9\"", 4.4, alpha=0.75)

    DIMS = [("ot", 3.0, 26.9, "x", 0.5), ("ot", 19.3, 17.0, "y", 0.72),
            ("scrub", 24.6, 12.5, "y", 0.4),
            ("opd2", 38.0, 8.3, "x", 0.6), ("opd2", 44.6, 11.5, "y", 0.5),
            ("opd1", 38.0, 16.6, "x", 0.6), ("opd1", 38.95, 20.0, "y", 0.5),
            ("emer", 37.0, 32.9, "x", 0.5), ("emer", 41.9, 28.0, "y", 0.4),
            ("xray", 37.0, 39.1, "x", 0.35), ("lounge", 36.0, 6.6, "x", 0.5)]
    for k, x, y, axis, at in DIMS:
        ipd.dim_string(ax, by[k].poly, x, y, axis, fs=6.6, at=at, z=14)
    free = free_i(rooms).difference(unary_union(
        [box(x, y, x + w_, y + h) for r in rooms if r.zone == "circ" for (_, x, y, w_, h, _) in r.furniture]))
    for (x, y, axis, at) in [(29.5, 9.3, "x", 0.5), (18.0, 41.9, "x", 0.5), (20.52, 36.0, "y", 0.5),
                             (2.6, 46.0, "y", 0.5), (14.4, 39.9, "y", 0.5)]:
        ipd.dim_string(ax, free, x, y, axis, fs=6.6, color="#a33", z=14, at=at)
    tc = chk["ot"]["table_to_walls"]
    for (xa, ya, xb, yb, txt, lx, ly, rot) in [
            (E0, ty + 0.3, tx, ty + 0.3, tc["east"], 4.4, ty - 0.1, 0),
            (tx + tw, ty + 2.4, OT_WF, ty + 2.4, tc["west"], 17.2, ty + 2.0, 0),
            (10.39, OT_S + 1.35, 10.39, ty, "5'-3\" to cabinets", 10.39, OT_S + 2.6, 0),
            (10.39, ty + th, 10.39, OT_N, tc["north"], 10.9, OT_N - 2.2, 90)]:
        ax.annotate("", xy=(xb, yb), xytext=(xa, ya),
                    arrowprops=dict(arrowstyle="<->", lw=0.55, color="#6a1b9a"), zorder=12)
        lab(lx, ly, txt, 4.8, rot=rot, color="#6a1b9a", alpha=0.8, z=14)
    _client_tags(ax, fs=8.0, z=19)
    _flows(ax)
    for x, y, t, colr, rot in [(8.0, 46.0, "PATIENT IN / OUT", "#1565c0", 0),
                               (8.0, 43.75, "SOILED OUT → service lift", "#c62828", 0),
                               (17.0, 48.9, "to wards", "#1565c0", 0),
                               (30.3, 12.5, "STAFF", "#2e7d32", 90),
                               (28.1, 27.6, "SOILED", "#c62828", 90),
                               (17.6, 9.0, "STERILE", "#00838f", 0),
                               (17.1, 37.6, "TROLLEY\nLANE", "#1565c0", 90)]:
        lab(x, y, t, 4.8, True, rot=rot, color=colr, z=16)

    def block(x, y, title, lines, fs=7.0, mono=False, color="#222", tcolor=None):
        ax.text(x, y, title, fontsize=8.6, weight="bold", color=tcolor or INK, va="top", zorder=22)
        lh = fs * 1.72 / 72 / FT
        ax.text(x, y + 1.15, "\n".join(lines), fontsize=fs, color=color, va="top", zorder=22,
                linespacing=1.5, family="monospace" if mono else None)
        return y + 1.15 + lh * len(lines) + 1.0

    c1, c2, c3 = X0 + 0.8, 6.0, 29.6
    y = YP + 0.9
    ax.text(c1, y, "FLOW ROUTES", fontsize=8.6, weight="bold", color=INK, va="top", zorder=22)
    notes = {"patient": ["main door → 5' entry strip → lane →", "pre-op door 4'-0\" → OT 5'-0\" sliding",
                         "door → recovery bay → lane → wards", "never through a seat row"],
             "staff": ["OPD lobby → 4'-6\" passage → staff", "lobby door → change → scrub → OT;",
                       "lounge off the staff lobby"],
             "clean": ["wash → pass-through autoclave →", "clean / pack → pass box → OT;",
                       "sterile store → OT; anaes. store → OT"],
             "dirty": ["instruments: OT → hatch → CSSD wash;", "waste / linen: OT → dirty utility →",
                       "passage → OPD lobby → lane → main door"]}
    y += 1.5
    for name, (colr, nm, _) in FLOWS_I.items():
        ax.add_patch(FancyArrowPatch((c1, y + 0.3), (c1 + 3.2, y + 0.3), arrowstyle="-|>",
                                     mutation_scale=13, lw=2.4, color=colr, zorder=22,
                                     ls=(0, (3.5, 1.2)) if name == "dirty" else "-"))
        ax.text(c1 + 3.8, y, nm, fontsize=8.0, weight="bold", color=colr, va="top", zorder=22)
        ax.text(c1 + 3.8, y + 1.0, "\n".join(notes[name]), fontsize=6.4, color="#333", va="top",
                zorder=22, linespacing=1.4)
        y += 4.9
    ax.plot([c1, c1 + 10], [y + 0.9, y + 0.9], lw=2.5, color=INK, zorder=22)
    for i in range(0, 11, 5):
        ax.plot([c1 + i] * 2, [y + 0.6, y + 1.2], lw=1, color=INK, zorder=22)
        ax.text(c1 + i, y + 0.3, f"{i}'", ha="center", fontsize=6.5, color=INK, zorder=22)

    rows = [("ot", "Operation theatre"), ("recovery", "Pre-op / holding + transfer"),
            ("recB", "Recovery bay"), ("scrub", "Scrub (3 taps)"),
            ("stchange", "OT staff change M / F"), ("stlobby", "Staff lobby"),
            ("cssd", "CSSD clean / pack + autoclave"), ("wash", "CSSD wash (dirty side)"),
            ("sstore", "Sterile store"), ("anst", "Anaes. / consumable store"),
            ("du", "Dirty utility"), ("emer", "Emergency / dressing"), ("xray", "X-ray (mobile)")]
    lines = [f"{nm:<30s}{chk['rooms'][k]['clear'] :<24s}"
             f"{a_[k]:>4.0f} sf {a_[k] * 0.0929:>5.1f} m²" for k, nm in rows]
    lines.append(f"{'OT suite, 11 rooms':<47s}{chk['ot']['suite_area_sf']:>4.0f} sf")
    y2 = block(c2, YP + 0.9, "ROOM SCHEDULE  (largest clear rectangle; area net of columns)", lines,
               fs=6.5, mono=True)
    eq = [f"{t:<6s}{n}" for _, _, _, _, _, t, n in OT_EQUIP_I if t]
    eq += ["      Instrument trolleys 1'-6\" x 3'-0\" (2); OT table 2'-0\" x 6'-9\"; dashed box: 4'-0\" zone"]
    block(c2, y2, "OT EQUIPMENT  (drawn at true size)", eq, fs=6.5, mono=True)

    cs = [f"{m:<5s} {room}: built {built}" for m, _, room, built, _ in CLIENT_SIZES[:8]]
    cs = [s.replace(" (first read as X)", "") for s in cs]
    y3 = block(c3, YP + 0.9, "CLIENTS' BLUE-PEN SIZES (feet) — all built exactly", cs, fs=6.5,
               tcolor=CLIENT_BLUE)
    cols = chk["ot"]["columns_in_20x20"]
    t_ = chk["travel_ft"]
    wd = chk["widths_ft"]
    ck = [f"OT {chk['ot']['area_sf']:.0f} sf = {chk['ot']['area_m2']} m²; asked 20' x 20' (≈ 36 m²): met",
          "Columns in the OT: " + (", ".join(f"{n} {v['proud_in']}\" proud" for n, v in cols.items())
                                    or "none") + " (in the west wall lining)",
          f"Table to walls: E {tc['east']}, W {tc['west']}, S {tc['south']}, N {tc['north']}",
          f"Waiting: {w['seats_total']} seats ({w['seats_hall']} hall + {w['seats_opd_subwait']} sub-wait); "
          f"hall {w['hall_sf_per_seat']} sf per seat",
          f"Trolley route {chk['trolley_route']['main_door_to_ot_door_ft']:.0f} ft door to OT door; nearest "
          f"seat {fi(chk['trolley_route']['min_gap_to_a_seat_ft'])} away; crosses no row",
          f"Clear widths: entry strip {fi(wd['entry_strip'])}, lane {fi(wd['lane'])}, hall-lobby opening "
          f"{fi(wd['hall_to_lobby_gap'])}, OPD passage {fi(wd['opd_passage'])}",
          f"Travel: OT far corner → main door {t_['ot_far_corner_to_main_door']:.0f} ft, → stair "
          f"≈ {t_['ot_far_corner_to_stair']:.0f} ft ({t_['ot_far_corner_to_stair'] * 0.3048:.0f} m)",
          "X-ray: mobile unit only (AERB fixed room ≈ 18 m², 4 m side: to verify)",
          "Recovery is 7'-0\" deep as marked: a 6'-6\" x 2'-2\" trolley only just turns (6'-10\" diagonal)",
          "HVAC plant for the OT is not designed.  Guideline figures: to verify"]
    block(c3, y3, "CHECKS", ck, fs=6.5)
    ax.text(X1 - 0.8, Y1 - 0.7, "SOUTH is at the top, EAST (lift core) on the left.  Blue strings = clear "
            "sizes.  Blue boxes = clients' sizes.  Columns red-brown.  Blue dashed = builder's toilet slab.",
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


# ------------------------------------------------------------------ outputs
def export_dxf_i(path):
    import ezdxf
    from dxf_export import export_dxf
    with i_geometry():
        export_dxf("I", path)
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    with _g_equipment():
        G.dxf_extras(doc, msp)
    for name, color in (("WAITING_SEATS", 4), ("CLIENT_SIZES", 5)):
        doc.layers.add(name, color=color)
    for s in _seat_boxes(layout_i_rooms()):
        msp.add_lwpolyline(list(s.exterior.coords), close=True, dxfattribs={"layer": "WAITING_SEATS"})
    for x, y, t, _ in CLIENT_TAGS:
        msp.add_text(f"client {t} ft", height=0.5, dxfattribs={"layer": "CLIENT_SIZES"}).set_placement((x, y))
    for w in EXTRA_WALLS:
        msp.add_lwpolyline(list(w.exterior.coords), close=True, dxfattribs={"layer": "WALLS"})
    doc.saveas(path)
    return len(doc.audit().errors)


BP_NAMES = {"wash": ("CSSD wash", ""), "cssd": ("CSSD clean", "+ autoclave"),
            "sstore": ("St. store", ""), "stchange": ("Change", ""), "anst": ("An. store", ""),
            "stlobby": ("", ""), "scrub": ("SCRUB", ""), "du": ("Dirty ut.", ""),
            "lounge": ("LOUNGE", "14'-7\" x 6'-8\""), "opd2": ("OPD 2 · Psy.", "13'-3\" x 8'-1\""),
            "opd1": ("OPD 1 · Ortho", "10'-2\" x 8'-1\""), "emer": ("EMERGENCY", "10'-7\" x 9'-3\""),
            "xray": ("X-RAY", "8'-7\" x 5'-9\""), "lane": ("", ""), "opdpass": ("", ""),
            "recB": ("RECOVERY", "7'-11\" x 7'-0\""), "recovery": ("PRE-OP", "11'-8\" x 7'-0\""),
            "obs": ("", ""), "store": ("", ""), "duct": ("", ""),
            "hall": (f"WAITING HALL · {2 * ROW_N} SEATS", ""), "wardcorr": ("WARD PASSAGE", "")}


def _bp_rooms():
    rooms = layout_i_rooms()
    for r in rooms:
        if r.key in BP_NAMES:
            r.name, r.dims = BP_NAMES[r.key]
    return rooms


def blueprint_i(out_dir):
    import blueprint_svg as B
    p = os.path.join(out_dir, "layout_I_blueprint.svg")
    B.ENVELOPE["I"] = B.ENVELOPE["G"]
    plan_model.LAYOUTS["I"] = (TITLE, _bp_rooms)
    try:
        with i_geometry():
            B.render_blueprint("I", "blueprint", p)
    finally:
        plan_model.LAYOUTS["I"] = (TITLE, layout_i_rooms)
        del B.ENVELOPE["I"]
    t = B.THEMES["blueprint"]
    cols = "".join(f'<polygon points="{B._poly_pts(c.intersection(G.OUTER))}" fill="{t["accent"]}" '
                   f'fill-opacity="0.55" stroke="{t["accent"]}" stroke-width="0.8"/>'
                   for c in G.COLUMNS.values())
    w = checks()["waiting"]
    s = open(p, encoding="utf-8").read()
    s = (s.replace("VISITOR WC: COMMON-AREA TOILETS OUTSIDE THE MAIN ENTRY (SEE BUILDER'S FLOOR PLAN)",
                   f"ENTRY WAITING HALL {w['seats_hall']} SEATS + {w['seats_opd_subwait']} OPD SUB-WAIT · "
                   "PATIENT WC AT THE HALL · COLUMNS FROM THE DWG")
          .replace("OT SUITE ENTERED ONLY VIA RECOVERY (PATIENTS) / SCRUB (STAFF)",
                   "OT 20'-0\" × 20'-0\" · ENTERED ONLY VIA PRE-OP (PATIENTS) / CHANGE + SCRUB (STAFF)")
          .replace("</svg>", cols + "</svg>"))
    open(p, "w", encoding="utf-8").write(s)
    return p


def build_outputs(out_dir=None):
    out_dir = out_dir or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                      "..", "deliverables"))
    base = os.path.join(out_dir, "layout_I_detailed")
    render_sheet(base)
    size = render_ot_zone(os.path.join(out_dir, "ot_I_zone.jpg"))
    errors = export_dxf_i(base + ".dxf")
    bp = blueprint_i(out_dir)
    return dict(dxf_audit_errors=errors, ot_zone_px=size, blueprint=os.path.basename(bp))


import plan_model  # noqa: E402

plan_model.LAYOUTS["I"] = (TITLE, layout_i_rooms)

if __name__ == "__main__":
    import json
    import sys
    print(json.dumps(checks(), indent=1, default=str))
    if "build" in sys.argv[1:]:
        print(build_outputs())
