"""Build every Layout H deliverable and run its checks.

    cd floorplan && python3 build_h.py

Outputs (../deliverables): layout_H_detailed.png/.svg/.dxf,
layout_H_blueprint.svg, layout_H_clean.svg, 3d_layout_H.png and
layout_H_schedule.md (room schedule + check results, pasted into the brief).
"""
import os
import sys
from itertools import combinations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, FancyArrow, Rectangle
from matplotlib.lines import Line2D
import numpy as np
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

import layout_h as H
from layout_h import fi
import ipd
from plan_model import ZONES
import render as RD

OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "deliverables"))
INK = "#2b2b2b"
DATE = "17-11-2026"

# label overrides: key -> dict(x, y, fs, rot, lines)
LABELS = {
    "ot": dict(x=10.5, y=14.4),
    "recovery": dict(x=11.7, y=22.65, fs=6.3),
    "xray": dict(x=10.6, y=29.7, fs=5.7),
    "dirty": dict(x=3.7, y=22.4, rot=90, fs=6.4),
    "otstore": dict(x=22.6, y=3.1, fs=5.4),
    "cssd": dict(x=22.9, y=8.3, fs=5.3),
    "scrub": dict(x=22.9, y=13.2, fs=6.0),
    "change": dict(x=24.55, y=21.8, rot=90, fs=5.8),
    "psywait": dict(x=31.3, y=5.0, rot=90, fs=6.4),
    "psy": dict(x=36.6, y=4.75, fs=5.8, name="OPD 3\nPSYCHIATRY"),
    "opd2": dict(x=36.6, y=13.75, fs=5.8),
    "opd1": dict(x=36.6, y=22.5, fs=5.8, name="OPD 1\nORTHO"),
    "pharm": dict(x=7.7, y=51.7, fs=6.2),
    "clean": dict(x=3.2, y=64.9, rot=90, fs=6.0),
    "pantry": dict(x=8.3, y=64.9, fs=6.2),
    "duct": dict(x=2.9, y=50.0, fs=5.5),
}
# IPD rooms: label in the clear floor (never over a bed), W / D dimension strings
# (x, y, text position along the string, text offset)
IPD_H = {     # label position; text position / offset on the W and D strings (points: H.IPD_PTS)
    "twin1": dict(label=(31.6, 52.25), w=(0.5, 0.42), d=(0.62, 0.42)),
    "twin2": dict(label=(31.0, 71.45), w=(0.55, 0.42), d=(0.22, -0.42)),
    "twin3": dict(label=(29.3, 85.6), w=(0.5, 0.42), d=(0.64, -0.42)),
    "twin4": dict(label=(9.75, 81.6), rot=90, w=(0.42, -0.42), d=(0.1, 0.42)),
}
IPD_WINDOW = (-3.5, 53.5, 46.2, 97.0)      # close-up crop, plan feet (x0, x1, y0, y1)
CIRC_LABELS = {
    "wait": dict(x=27.4, y=33.6, fs=8.2, bold=True),
    "gate": dict(x=17.3, y=38.6, fs=5.8),
    "opdpass": dict(x=30.2, y=18.0, rot=90, fs=6.6),
    "svc": dict(x=2.2, y=33.6, rot=90, fs=5.8),
    "lobby": dict(x=10.5, y=46.3, fs=8.2, bold=True),
    "recep": dict(x=23.4, y=44.0, rot=90, fs=6.2, bold=True),
    "ns": dict(x=7.0, y=60.3, fs=6.0, bold=True),
    "wardcorr": dict(x=14.75, y=70.0, rot=90, fs=7.2),
}


# ------------------------------------------------------------------- checks
def run_checks(rooms):
    out = []
    solids = [r for r in rooms if r.zone != "circ"]
    bad = [(a.key, b.key, round(a.poly.intersection(b.poly).area, 2))
           for a, b in combinations(solids, 2) if a.poly.intersection(b.poly).area > 0.5]
    out.append(f"solid-room overlaps > 0.5 sf: {bad or 'none'}")
    cols = unary_union(list(H.COLUMNS_H.values()))
    walls = H.walls_h(rooms)
    issues = []
    for r in rooms:
        zone_poly = r.poly if r.zone != "circ" else H.circulation_h(rooms)
        fb = []
        for (kind, x, y, w, h, rot) in r.furniture:
            b = box(x, y, x + w, y + h)
            if kind == "ottable":
                b = box(x, y, x + w, y + h + 2.0)
            if b.difference(zone_poly.buffer(0.02)).area > 0.05:
                issues.append(f"{r.key}:{kind}@({x},{y}) outside room by {b.difference(zone_poly).area:.2f} sf")
            if b.intersection(cols).area > 0.01:
                issues.append(f"{r.key}:{kind}@({x},{y}) hits a column")
            if b.intersection(walls).area > 0.05:
                issues.append(f"{r.key}:{kind}@({x},{y}) hits a wall")
            fb.append((kind, b))
        for (ka, a), (kb, b) in combinations(fb, 2):
            if a.intersection(b).area > 0.05 and {ka, kb} != {"ottable", "light"}:
                issues.append(f"{r.key}: {ka} overlaps {kb}")
        for (cx, cy, w, side) in r.doors:
            op = (box(cx - w / 2, cy - 0.3, cx + w / 2, cy + 0.3) if side in ("N", "S")
                  else box(cx - 0.3, cy - w / 2, cx + 0.3, cy + w / 2))
            if op.intersection(cols).area > 0.01:
                issues.append(f"{r.key}: door at ({cx},{cy}) hits a column")
            # the leaf must sweep over floor, not a wall or furniture of any room
            sw = _swing_box(cx, cy, w, side)
            hit = sw.intersection(walls).area
            if hit > 0.6:
                issues.append(f"{r.key}: door swing at ({cx},{cy}) crosses a wall ({hit:.1f} sf)")
    out.append(f"furniture / door issues: {issues or 'none'}")
    # bed heads on solid walls: head end must touch a wall band, not glass
    heads = []
    glass = unary_union([LineString(seg) for seg in H.GLASS_WEST_H + H.GLASS_NORTH_H]).buffer(1.2)
    for r in rooms:
        for (kind, x, y, w, h, rot) in r.furniture:
            if kind != "bed":
                continue
            if w > h:
                hd = box(x - 0.3, y, x + 0.1, y + h) if rot == 180 else box(x + w - 0.1, y, x + w + 0.3, y + h)
            else:
                hd = box(x, y - 0.3, x + w, y + 0.1) if rot == 180 else box(x, y + h - 0.1, x + w, y + h + 0.3)
            ok = hd.intersection(walls).area > 0.3 and hd.intersection(glass).area < 0.01
            heads.append((r.key, ok))
    iss, nb, nh = ipd.audit(rooms, walls, glass)
    out.append(f"IPD true-size audit ({nb} beds, {nh} heads on solid walls): {iss or 'none'}")
    for r in rooms:
        if r.key.startswith(("wcW", "wcN")):
            tw, td, ta = ipd.toilet_size(r.poly)
            out.append(f"toilet {r.key}: clear {fi(tw)} x {fi(td)}, {ta:.0f} sf"
                       + ("" if min(tw, td) >= 4.99 and max(tw, td) >= 5.99 else "  BELOW 5'x6'"))
    out.append(f"beds: {len(heads)} drawn, heads on solid wall: "
               f"{sum(1 for _, ok in heads if ok)}/{len(heads)}"
               + ("" if all(ok for _, ok in heads) else f"  FAIL {[k for k, ok in heads if not ok]}"))
    return out


def _swing_box(cx, cy, w, side):
    half = w / 2 if w >= 4.5 else w
    if side == "N":
        return box(cx - w / 2, cy + 0.35, cx + w / 2, cy + 0.2 + half)
    if side == "S":
        return box(cx - w / 2, cy - 0.2 - half, cx + w / 2, cy - 0.35)
    if side == "E":
        return box(cx + 0.35, cy - w / 2, cx + 0.2 + half, cy + w / 2)
    return box(cx - 0.2 - half, cy - w / 2, cx - 0.35, cy + w / 2)


# --------------------------------------------------------------- 2D drawing
def _door(ax, d, z=8):
    cx, cy, w, side = d
    leaves = [(-1, w / 2), (1, w / 2)] if w >= 4.5 else [(1 if (cx, cy) in H.HINGE_HI else -1, w)]
    for hs, r in leaves:
        if side in ("N", "S"):
            sg = 1 if side == "N" else -1
            hx = cx + hs * w / 2
            ax.plot([hx, hx], [cy, cy + sg * r], lw=1.0, color=INK, zorder=z)
            if hs < 0:
                t1, t2 = (0, 90) if sg > 0 else (270, 360)
            else:
                t1, t2 = (90, 180) if sg > 0 else (180, 270)
            ax.add_patch(Arc((hx, cy), 2 * r, 2 * r, theta1=t1, theta2=t2, lw=0.55, color=INK, zorder=z))
        else:
            sg = 1 if side == "E" else -1
            hy = cy + hs * w / 2
            ax.plot([cx, cx + sg * r], [hy, hy], lw=1.0, color=INK, zorder=z)
            if hs < 0:
                t1, t2 = (0, 90) if sg > 0 else (90, 180)
            else:
                t1, t2 = (270, 360) if sg > 0 else (180, 270)
            ax.add_patch(Arc((cx, hy), 2 * r, 2 * r, theta1=t1, theta2=t2, lw=0.55, color=INK, zorder=z))


def _dim_chain(ax, stations, const, axis, side=1, fs=6.4, color="#444"):
    """Running dimension chain with ticks. axis 'x': stations are x values at y=const."""
    for a, b in zip(stations[:-1], stations[1:]):
        if axis == "x":
            ax.plot([a, b], [const, const], lw=0.6, color=color, zorder=12)
            ax.text((a + b) / 2, const - 0.55 * side, fi(b - a), ha="center", va="center",
                    fontsize=fs, color=color, zorder=12)
        else:
            ax.plot([const, const], [a, b], lw=0.6, color=color, zorder=12)
            ax.text(const + 0.75 * side, (a + b) / 2, fi(b - a), ha="center", va="center",
                    fontsize=fs, color=color, rotation=90, zorder=12)
    for s in stations:
        if axis == "x":
            ax.plot([s - 0.3, s + 0.3], [const + 0.3, const - 0.3], lw=0.8, color=color, zorder=12)
            ax.plot([s, s], [const - 0.5, const + 0.5], lw=0.4, color=color, zorder=12)
        else:
            ax.plot([const - 0.3, const + 0.3], [s + 0.3, s - 0.3], lw=0.8, color=color, zorder=12)
            ax.plot([const - 0.5, const + 0.5], [s, s], lw=0.4, color=color, zorder=12)


def bed_count(rooms):
    ipd = sum(1 for r in rooms if r.zone == "inpatient" for f in r.furniture if f[0] == "bed")
    rec = sum(1 for r in rooms if r.key == "recovery" for f in r.furniture if f[0] == "bed")
    return ipd, rec


def render_detailed(out_base):
    rooms = H.layout_h_rooms()
    walls = H.walls_h(rooms)
    pal = RD.CAD_PALETTE
    fig, ax = plt.subplots(figsize=(13, 22))
    ax.set_aspect("equal")

    RD._fill(ax, H.PLATE_H, 1, fc=RD.CORRIDOR, ec="none")
    # service ledge south, cut-out
    ax.add_patch(Rectangle((0, -3.6), 48.12, 2.9, fc="white", ec=INK, lw=0.8, hatch="xxx", zorder=1))
    ax.text(30, -2.15, "SERVICE AREA (ledge)", ha="center", va="center", fontsize=7.5, color=INK,
            bbox=dict(fc="white", ec="none", pad=1.2), zorder=2)
    RD._fill(ax, H.CUTOUT_H, 2, fc="white", ec="none", hatch="///", lw=0)
    c = H.CUTOUT_H.centroid
    ax.text(c.x, c.y, "CUT-OUT\n(open to sky)", ha="center", va="center", fontsize=8.5, color=INK,
            zorder=4, bbox=dict(fc="white", ec="none", pad=1.5))

    # lift core (context, from the DWG)
    for lf in H.CORE_H["lifts"]:
        x0, y0, x1, y1 = lf.bounds
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="#efefef", ec="#777", lw=0.8, zorder=2))
        ax.plot([x0, x1], [y0, y1], color="#999", lw=0.4, zorder=2)
        ax.plot([x0, x1], [y1, y0], color="#999", lw=0.4, zorder=2)
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, "LIFT", ha="center", va="center", fontsize=6.5,
                color="#555", zorder=3, bbox=dict(fc="#efefef", ec="none", pad=0.8))
    x0, y0, x1, y1 = H.CORE_H["duct"].bounds
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="white", ec="#777", lw=0.8, hatch="//", zorder=2))
    ax.text(-5.0, 4.0, "lift core / refuge area\n(building, from DWG)", ha="center", va="center",
            fontsize=6, color="#666", style="italic")
    ax.text(-6.0, 66.0, "unit x04\n(party wall)", ha="center", va="center", fontsize=6, color="#666",
            style="italic")

    # rooms
    for r in rooms:
        if r.zone == "circ":
            continue
        p = r.poly
        RD._fill(ax, p, 2, fc=RD._tint(ZONES[r.zone][0], pal["tint_keep"]), ec="none")
        for g in RD._iter_polys(p):
            if r.zone == "wet":
                RD._tile_hatch(ax, g, 3)
            elif g.area > 30:
                RD._tile_hatch2(ax, g, 2.5)

    # builder's toilet / duct positions that are NOT reused as toilets
    x0, y0, x1, y1 = H.PLUMBING_H["T507"].bounds
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc="none", ec="#2c6fbb", lw=0.7, ls=(0, (3, 2)),
                           zorder=5))
    ax.text(x0 + 0.25, y1 + 0.45, "builder WC position:\nomit, keep slab flush", fontsize=4.6,
            color="#2c6fbb", va="top", zorder=9)

    RD._fill(ax, walls, 7, fc=INK, ec="none")
    for k, col in H.COLUMNS_H.items():
        RD._fill(ax, col, 7.5, fc="#000000", ec="#c0392b", lw=0.9)

    for r in rooms:
        for f in r.furniture:
            RD._furniture(ax, f, pal=pal)
        for d in r.doors:
            _door(ax, d)
    for (cx, cy, w, o, lbl) in H.HATCHES_H:
        if o == "h":
            for dy in (-0.12, 0.12):
                ax.plot([cx - w / 2, cx + w / 2], [cy + dy, cy + dy], color="#c0392b", lw=0.9, zorder=9)
        else:
            for dx in (-0.12, 0.12):
                ax.plot([cx + dx, cx + dx], [cy - w / 2, cy + w / 2], color="#c0392b", lw=0.9, zorder=9)
    ax.text(19.1, 8.3, "pass box", fontsize=5, color="#c0392b", rotation=90, ha="center", va="center", zorder=9)
    ax.text(7.9, 47.45, "pharmacy hatch", fontsize=5, color="#c0392b", ha="center", va="center", zorder=9)

    # ---------------------------------------------------------------- labels
    keynotes = []
    for r in rooms:
        p = r.poly
        if p.is_empty or not r.name:
            continue
        if r.zone == "circ":
            o = CIRC_LABELS.get(r.key, {})
            cp = p.representative_point()
            ax.text(o.get("x", cp.x), o.get("y", cp.y), r.name, ha="center", va="center",
                    fontsize=o.get("fs", 7), rotation=o.get("rot", 0), zorder=9,
                    color="#222" if o.get("bold") else "#77776f",
                    weight="bold" if o.get("bold") else "normal",
                    style="normal" if o.get("bold") else "italic")
            continue
        cp = p.representative_point()
        if r.zone == "wet":
            keynotes.append((r, cp))
            continue
        if r.key in IPD_H:
            o = IPD_H[r.key]
            (wx, wy), (dx, dy) = H.IPD_PTS[r.key]
            wl = ipd.dim_string(ax, p, wx, wy, "x", at=o["w"][0], off=o["w"][1])
            dl = ipd.dim_string(ax, p, dx, dy, "y", at=o["d"][0], off=o["d"][1])
            nb = sum(1 for f in r.furniture if f[0] == "bed")
            ax.text(o["label"][0], o["label"][1],
                    f"{r.name} · {nb} beds\nclear {fi(wl)} × {fi(dl)}\n"
                    f"{p.area:.0f} sf = {p.area / nb:.0f} sf per bed",
                    ha="center", va="center", fontsize=5.9, color="#111", zorder=9.2,
                    linespacing=1.3, rotation=o.get("rot", 0))
            continue
        o = LABELS.get(r.key, {})
        fs = o.get("fs", 10 if p.area > 200 else (8 if p.area > 90 else 6.5))
        txt = o.get("name", r.name) + ("\n" + r.dims if r.dims else "") + (f"\n{p.area:.0f} sf" if p.area > 45 else "")
        if r.key == "duct":
            txt = "Duct"
        ax.text(o.get("x", cp.x), o.get("y", cp.y), txt, ha="center", va="center", fontsize=fs,
                color="#111", weight="bold" if r.name.isupper() or "·" in r.name else "normal",
                rotation=o.get("rot", 0), zorder=9, linespacing=1.25)
    KN = {"wc_acc": (38.2, 34.8), "wc_staff": (2.8, 56.2), "wcN4": (3.6, 72.6), "wcW1": (22.0, 58.6),
          "wcW2": (22.0, 66.9), "wcW3": (22.0, 80.9)}
    for r, cp in keynotes:
        x, y = KN.get(r.key, (cp.x, cp.y))
        acc = r.key in H.ACCESSIBLE_H
        if acc:
            ax.add_patch(Circle((x, y), 2.5, fc="none", ec="#2c6fbb", lw=0.6, ls=(0, (4, 3)), zorder=9))
        ax.add_patch(Circle((x, y), 0.95, fc="white", ec=INK, lw=0.8, zorder=10))
        ax.text(x, y, "T", ha="center", va="center", fontsize=7, weight="bold", color=INK, zorder=11)
        if r.key.startswith(("wcW", "wcN")):
            tw, td, _ = ipd.toilet_size(r.poly)
            tdims = f"{fi(tw)}×{fi(td)}"
        else:
            tdims = r.dims.replace(" avg", "").replace(" x ", "×")
        ax.text(x, y + 1.55, ("Acc. " if acc else "") + tdims,
                ha="center", va="center", fontsize=4.6, color=INK, zorder=11,
                bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.8))

    # flow arrows: patient (blue), staff (green), soiled (brown)
    def flow(pts, col, ls="-"):
        xs, ys = zip(*pts)
        ax.plot(xs[:-1] + (xs[-1],), ys, color=col, lw=1.1, ls=ls, zorder=9.5, alpha=0.9)
        ax.annotate("", xy=pts[-1], xytext=pts[-2], zorder=9.5,
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.1))
    flow([(3.0, 43.4), (17.4, 43.4), (17.4, 30.0), (17.2, 24.5), (16.9, 15.4)], "#1f5fbf")
    flow([(30.2, 26.4), (28.0, 25.3), (25.0, 25.3), (25.0, 16.3), (21.6, 15.2), (19.4, 14.6)], "#2e7d32", "--")
    flow([(3.2, 16.4), (3.2, 19.0), (5.2, 20.2), (5.2, 25.4), (2.2, 27.0), (2.2, 42.0), (0.6, 43.0)], "#8d5524", ":")

    # glass
    for (x1, y1), (x2, y2) in H.GLASS_WEST_H + H.GLASS_NORTH_H:
        ax.plot([x1, x2], [y1, y2], color="#2c6fbb", lw=2.0, zorder=5)
        dx, dy = x2 - x1, y2 - y1
        n = np.hypot(dx, dy)
        ox, oy = dy / n * 0.45, -dx / n * 0.45
        ax.plot([x1 + ox, x2 + ox], [y1 + oy, y2 + oy], color="#2c6fbb", lw=0.6, zorder=5)
    ax.text(47.2, 22, "OPENABLE GLASS", rotation=-81.8, fontsize=7.5, color="#2c6fbb", ha="center", va="center")
    ax.text(41.2, 68, "OPENABLE GLASS", rotation=-81.8, fontsize=7.5, color="#2c6fbb", ha="center", va="center")
    ax.text(18, 93.9, "OPENABLE GLASS", fontsize=7.5, color="#2c6fbb", ha="center")

    # main door (pair, opening outwards = exit direction)
    _, y1, y2 = H.MD_DOOR_H
    for hy, t1, t2 in ((y1, 90, 180), (y2, 180, 270)):
        ax.add_patch(Arc((0.2, hy), 6, 6, theta1=t1, theta2=t2, lw=0.7, color=INK, zorder=8))
        ax.plot([0.2, -2.8], [hy, hy], lw=1.1, color=INK, zorder=8)
    ax.annotate("MD - MAIN ENTRY\n6'-0\" pair, opens out", xy=(-0.4, (y1 + y2) / 2), xytext=(-7.0, 51.0),
                fontsize=7.2, weight="bold", ha="center", va="center", color=INK,
                arrowprops=dict(arrowstyle="->", lw=1.0, color=INK))
    ax.text(-7.0, 53.6, "common passage to lift lobby;\nstairs ≈30' and ≈55' beyond", fontsize=5.6,
            ha="center", va="center", color="#555", style="italic")

    # compass
    for x, y, s in [(24, -11.0, "SOUTH SIDE"), (20, 98.2, "NORTH SIDE")]:
        ax.text(x, y, s, ha="center", va="center", fontsize=10, weight="bold",
                bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(-14.3, 62, "EAST SIDE", rotation=90, ha="center", va="center", fontsize=10, weight="bold",
            bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(58.5, 30, "WEST SIDE", rotation=-90, ha="center", va="center", fontsize=10, weight="bold",
            bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.add_patch(FancyArrow(57, 84, 0, 4.5, width=0.6, head_width=2.0, head_length=1.8, fc=INK, ec=INK))
    ax.text(57, 82.4, "N", ha="center", fontsize=13, weight="bold", color=INK)

    # dimensions (clear-space stations = wall centre lines, outer faces at the ends)
    _dim_chain(ax, [0, 20.65, 27.02, 33.4, 48.12], -5.4, "x", side=1)
    _dim_chain(ax, [0, 48.12], -7.6, "x", side=1, fs=8, color=INK)
    _dim_chain(ax, [0, 9.65, 18.39, 27.59, 40.0, 48.33, 62.75, 76.72, 92.36], 51.6, "y", side=1)
    _dim_chain(ax, [0, 17.65, 27.59, 40.0, 48.33, 68.79, 92.36], -11.4, "y", side=-1)
    _dim_chain(ax, [0, 92.36], -13.0, "y", side=-1, fs=8, color=INK)
    _dim_chain(ax, [0, 11.31, 18.19, 30.47], 95.6, "x", side=-1)

    # legend
    handles = [Line2D([], [], marker="s", ls="", ms=10, mfc=RD._tint(col, 0.35), mec="#999", label=lbl)
               for col, lbl in ZONES.values() if lbl != "Circulation"]
    handles += [Line2D([], [], marker="s", ls="", ms=10, mfc=INK, mec=INK, label="Walls (4½\" partitions)"),
                Line2D([], [], marker="s", ls="", ms=10, mfc="black", mec="#c0392b", label="RCC column (DWG)"),
                Line2D([], [], color="#2c6fbb", lw=2.0, label="Openable glass facade"),
                Line2D([], [], color="#1f5fbf", lw=1.2, label="Patient to OT"),
                Line2D([], [], color="#2e7d32", lw=1.2, ls="--", label="Staff to OT"),
                Line2D([], [], color="#8d5524", lw=1.2, ls=":", label="Soiled / waste out")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02, 0.118), ncol=4, fontsize=7.2,
              frameon=False, columnspacing=1.0, handletextpad=0.5)

    n_ipd, rec = bed_count(rooms)
    carpet = H.INNER_H.area - H.CUTOUT_H.intersection(H.INNER_H).area
    notes = ("NOTES\n"
             f"1. Geometry from the builder's DWG (typical floor 5/7/10): 48'-1½\" x 92'-4\" over plaster.\n"
             f"2. Beds: {n_ipd} in-patient (4 twin rooms, each with window + ensuite) + {rec} recovery.  IPD furniture is\n"
             "    drawn at true size: bed 3'-3\" x 7'-0\", locker 1'-6\" sq., wardrobe 2'-0\" x 4'-0\", attendant sofa 2'-0\" x 5'-6\".\n"
             "    Blue strings in the ward rooms = clear size, plaster face to plaster face, measured on the DWG geometry.\n"
             "3. OT is entered only through Recovery/Pre-op (patients) or Change > Scrub (staff).\n"
             "4. Soiled goods: OT > Dirty Utility > 3'-6\" service passage > door beside the main entry.\n"
             "5. X-ray room is 114 sf: mobile unit only. AERB fixed-unit room (≈194 sf) does NOT fit here.\n"
             "6. (T) toilets: floor raised 150 mm as in the builder's toilets; new drain runs to be designed.\n"
             "7. Dashed blue circle = 5'-0\" wheelchair turning circle (accessible WC).\n"
             "8. Single exit; ward passage is a 43' dead end - fire officer / NBC check needed.")
    ax.text(-14.5, 103.4, notes, fontsize=6.6, color=INK, va="top", linespacing=1.45)

    sched = sorted([(r.name.replace("\n", " "), r.dims, r.area) for r in rooms
                    if r.zone != "circ" and r.name not in ("T", "T (Acc.)", "Duct")],
                   key=lambda t: -t[2])
    lines = ["ROOM SCHEDULE (clear, sf)", "-" * 34]
    for name, dims, area in sched:
        nm = name.title() if name.isupper() else name
        nm = nm.replace("Ot", "OT").replace("Opd", "OPD").replace("X-RAY", "X-ray").replace("DRESSING / PLASTER", "dressing / plaster")
        lines.append(f"{nm[:29]:<30s}{area:>4.0f}")
    wets = [r for r in rooms if r.zone == "wet"]
    lines.append(f"{'Toilets (' + str(len(wets)) + ')':<30s}{sum(r.area for r in wets):>4.0f}")
    lines.append("-" * 34)
    lines.append(f"{'Carpet inside walls':<30s}{carpet:>4.0f}")
    ax.text(38.5, 99.6, "\n".join(lines), fontsize=6.0, color=INK, va="top", family="monospace",
            linespacing=1.3)

    ax.set_title(f"{H.TITLE_H}\nHospital of Dr. Aman Khanna - 7th Floor, Solaris Shine, Althan, Surat\n"
                 f"Based on Ar. Bankim Dave's proposal dated 09-01-2026  ·  {n_ipd} beds + {rec} recovery  ·  "
                 f"carpet ≈ {carpet:,.0f} sq ft", fontsize=11.5, pad=14)

    # scale bar
    ax.plot([-14, -4], [99.6, 99.6], lw=3, color=INK)
    for i in range(0, 11, 5):
        ax.plot([-14 + i, -14 + i], [99.0, 100.2], lw=1.2, color=INK)
        ax.text(-14 + i, 101.6, f"{i}'", ha="center", fontsize=7, color=INK)

    # title block
    tb0, tb1 = 126.0, 134.0
    ax.add_patch(Rectangle((-15, tb0), 76, tb1 - tb0, fc="white", ec=INK, lw=1.2, zorder=3))
    for fx in (9, 31, 46):
        ax.plot([fx, fx], [tb0, tb1], color=INK, lw=0.8, zorder=4)
    for x, head, body in ((-14, "PROJECT", "Hospital of Dr. Aman Khanna\n7th Floor, Solaris Shine, Althan, Surat"),
                          (10, "DRAWING", "Layout H - architect plan improved\nDimensioned plan on DWG geometry"),
                          (32, "SCALE / DATE", f"N.T.S. (scale bar)\n{DATE}"),
                          (47, "STATUS", "Concept for review - to be\nverified by the project architect")):
        ax.text(x, tb0 + 1.5, head, fontsize=6, color="#777", zorder=5)
        ax.text(x, tb0 + 5.0, body, fontsize=7.2, color=INK, va="center", zorder=5)

    ax.set_xlim(-16.5, 62)
    ax.set_ylim(135.5, -13.5)
    ax.axis("off")
    fig.tight_layout()
    ipd.save_sheet(fig, ax, out_base, IPD_WINDOW, os.path.join(os.path.dirname(out_base), "ipd_H.jpg"))
    plt.close(fig)


# ------------------------------------------------------------- other outputs
def export_dxf_h(path):
    import ezdxf
    from dxf_export import export_dxf
    with H.h_geometry():
        export_dxf("H", path)
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    for name, color in (("COLUMNS", 1), ("CORE", 9), ("PLUMBING_EXIST", 4), ("HATCH_PASS", 3)):
        doc.layers.add(name, color=color)
    for k, col in H.COLUMNS_H.items():
        msp.add_lwpolyline(list(col.exterior.coords), close=True, dxfattribs={"layer": "COLUMNS"})
    for lf in H.CORE_H["lifts"] + [H.CORE_H["duct"], H.CORE_H["lobby"], H.CORE_H["stair_a"],
                                   H.CORE_H["stair_b"], H.CORE_H["refuge"]]:
        msp.add_lwpolyline(list(lf.exterior.coords), close=True, dxfattribs={"layer": "CORE"})
    for k, pl in H.PLUMBING_H.items():
        msp.add_lwpolyline(list(pl.exterior.coords), close=True, dxfattribs={"layer": "PLUMBING_EXIST"})
    for (cx, cy, w, o, lbl) in H.HATCHES_H:
        a, b = ((cx - w / 2, cy), (cx + w / 2, cy)) if o == "h" else ((cx, cy - w / 2), (cx, cy + w / 2))
        msp.add_line(a, b, dxfattribs={"layer": "HATCH_PASS"})
    msp.add_lwpolyline(list(H.INNER_H.exterior.coords), close=True, dxfattribs={"layer": "PLATE"})
    _, y1, y2 = H.MD_DOOR_H
    msp.add_line((0, y1), (0, y2), dxfattribs={"layer": "DOORS"})
    doc.saveas(path)
    return len(doc.audit().errors)


def blueprints_h():
    import blueprint_svg as B
    for theme, name in (("blueprint", "layout_H_blueprint.svg"), ("clean", "layout_H_clean.svg")):
        p = os.path.join(OUT, name)
        oy, hh = B.OY, B.H
        B.OY, B.H = 114.0, 1230.0          # room for the top dimension under the title
        cols = "".join(
            '<polygon points="' + " ".join(f"{B.OX + x * B.PPF:.1f},{B.OY + y * B.PPF:.1f}"
                                           for x, y in c.exterior.coords)
            + '" fill="#c0392b" stroke="none"/>' for c in H.COLUMNS_H.values())
        try:
            with H.h_geometry():
                B.render_blueprint("H", theme, p)
        finally:
            B.OY, B.H = oy, hh
        s = open(p, encoding="utf-8").read()
        s = (s.replace("ENVELOPE 48'-6\" × 92'-0\" (REV C)", "48'-1½\" × 92'-4\" (DWG)")
              .replace(">48'-6\"<", ">48'-1½\"<").replace(">92'-0\"<", ">92'-4\"<")
              .replace(">43'-0\"<", ">41'-2\"<").replace("MAIN ENTRY 5'-0\"", "MAIN ENTRY 6'-0\"")
              .replace("VISITOR WC: COMMON-AREA TOILETS OUTSIDE THE MAIN ENTRY (SEE BUILDER'S FLOOR PLAN)",
                       "ACCESSIBLE WC OFF THE CONCOURSE · RED = RCC COLUMNS")
              .replace("</svg>", cols + "</svg>"))
        open(p, "w", encoding="utf-8").write(s)


def schedule_md(rooms, checks):
    ipd, rec = bed_count(rooms)
    rows = ["| Room | Clear size (E-W x N-S) | Area sf | Zone |", "|---|---|---:|---|"]
    for r in rooms:
        if r.zone == "circ":
            continue
        rows.append(f"| {r.name.replace(chr(10), ' ')} ({r.key}) | {r.dims} | {r.area:.0f} | {ZONES[r.zone][1]} |")
    circ = H.circulation_h(rooms).area
    carpet = H.INNER_H.area - H.CUTOUT_H.intersection(H.INNER_H).area
    solid = sum(r.area for r in rooms if r.zone != "circ")
    txt = "\n".join(rows)
    txt += (f"\n\nRooms {solid:.0f} sf + circulation/open areas {circ:.0f} sf + walls/columns "
            f"{carpet - solid - circ:.0f} sf = {carpet:.0f} sf inside the external walls "
            f"(gross over plaster {H.PLATE_H.area:.0f} sf incl. cut-out {H.CUTOUT_H.area:.0f} sf).\n"
            f"\nBeds: {ipd} in-patient + {rec} recovery.\n\nChecks:\n" + "\n".join("- " + c for c in checks) + "\n")
    return txt


def main():
    rooms = H.layout_h_rooms()
    checks = run_checks(rooms)
    for c in checks:
        print(c)
    base = os.path.join(OUT, "layout_H_detailed")
    render_detailed(base)
    n = export_dxf_h(base + ".dxf")
    print("DXF audit errors:", n)
    checks.append(f"DXF audit errors: {n}")
    blueprints_h()
    from render3d import render_3d
    with H.h_geometry():
        render_3d("H", os.path.join(OUT, "3d_layout_H.png"))
    open(os.path.join(OUT, "layout_H_schedule.md"), "w", encoding="utf-8").write(schedule_md(rooms, checks))
    print("done")


if __name__ == "__main__":
    main()
