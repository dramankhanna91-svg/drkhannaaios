"""Adjacency / travel-distance scoring.

Methodology adapted from LorenaPujante/HospitalEdgeWeigths: spaces form a
graph whose edge weights are walking distances in metres/feet; key clinical
flows are scored by summed path length. Here rooms connect through corridor
space, so we approximate walking distance as the L1 (corridor-following)
distance between room door points, which matches that repo's
corridor-mediated edge model.
"""
from plan_model import LAYOUTS, MD_DOOR


def _door_pts(rooms, key):
    r = rooms[key]
    if r.doors:
        return [(cx, cy) for cx, cy, _, _ in r.doors]
    c = r.poly.representative_point()
    return [(c.x, c.y)]


def _l1(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _dist(rooms, a_pts, b_pts, a_key=None, b_key=None):
    """Min corridor distance between door sets; a door of one room lying on
    the other room's boundary is a direct connection (wall-thickness only)."""
    if a_key and b_key:
        pa, pb = rooms[a_key].poly, rooms[b_key].poly
        for pt in a_pts:
            from shapely.geometry import Point
            if pb.buffer(1.2).contains(Point(pt)):
                return 2.0
        for pt in b_pts:
            from shapely.geometry import Point
            if pa.buffer(1.2).contains(Point(pt)):
                return 2.0
    return min(_l1(a, b) for a in a_pts for b in b_pts)


FLOWS = [
    ("OT -> Recovery (post-op trolley)", "ot", "recovery"),
    ("Main door -> Reception", "MD", "recep"),
    ("Reception -> Waiting", "recep", "wait"),
    ("Pharmacy -> Main door (exit collection)", "pharm", "MD"),
    ("Consult cluster -> X-ray/Dressing", "opd1", "xray"),
    ("Nursing station -> farthest bed (Single 3)", "nursing", "single3"),
    ("Waiting -> nearest WC", "wait", "wc_w"),
]


def score_layout(key):
    _, factory = LAYOUTS[key]
    rooms = {r.key: r for r in factory()}
    md = [(MD_DOOR[0], (MD_DOOR[1] + MD_DOOR[2]) / 2)]
    out = {}
    for label, a, b in FLOWS:
        pa = md if a == "MD" else _door_pts(rooms, a)
        pb = md if b == "MD" else _door_pts(rooms, b)
        ka = None if a == "MD" else a
        kb = None if b == "MD" else b
        out[label] = _dist(rooms, pa, pb, ka, kb)
    return out


def comparison_table():
    keys = ["architect", "A", "B"]
    scores = {k: score_layout(k) for k in keys}
    lines = ["| Flow | Architect | Layout A | Layout B |",
             "|---|---|---|---|"]
    for label, _, _ in FLOWS:
        row = [f"| {label} "]
        for k in keys:
            row.append(f"| {scores[k][label]:.0f} ft ")
        lines.append("".join(row) + "|")
    tot = {k: sum(scores[k].values()) for k in keys}
    lines.append(f"| **Total key-flow travel** | **{tot['architect']:.0f} ft** "
                 f"| **{tot['A']:.0f} ft** | **{tot['B']:.0f} ft** |")
    return "\n".join(lines), scores
