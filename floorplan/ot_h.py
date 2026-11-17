"""Layout H - OT zone: close-up sheet (ot_H_zone.jpg) and OT checks.

Called from build_h.py.  The sheet shows the south 48' of the plate at a larger
scale with the OT equipment key, clear dimensions and the four flows
(patient, staff, clean supply, dirty) as coloured arrows.
"""
import io
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Circle, Rectangle
from shapely.geometry import box
from shapely.ops import unary_union

import ipd
import layout_h as H
from layout_h import fi

INK = "#2b2b2b"
FLOW = {
    "patient": ("#1f5fbf", "-", "Patient (trolley): lift > main door > gate > transfer bay > OT > recovery bay"),
    "staff": ("#2e7d32", (0, (5, 2)), "Staff: concourse > OPD passage > change (lockers, WC) > scrub > OT"),
    "clean": ("#8e24aa", (0, (6, 2, 1.5, 2)), "Clean supply: autoclave > CSSD clean > pass box / sterile store > OT"),
    "dirty": ("#b3541e", (0, (1.5, 1.6)), "Dirty: instruments by hatch to CSSD wash; waste + linen by Dirty Utility "
                                           "> 3'-6\" passage > door beside main entry"),
}
# polylines in plan feet
FLOWS = [
    ("patient", [(-2.5, 44.7), (17.6, 44.7), (17.6, 33.4), (16.5, 31.6), (16.5, 19.2), (13.3, 16.9), (12.3, 13.6)]),
    ("patient", [(14.8, 19.4), (14.8, 22.7), (12.9, 22.7)]),
    ("staff", [(-2.5, 45.6), (18.7, 45.6), (18.7, 34.7), (30.2, 34.7), (30.2, 23.5), (26.2, 23.5),
               (25.6, 22.3),
               (25.6, 20.2), (24.0, 19.9), (18.4, 19.9)]),
    ("clean", [(24.6, 12.6), (24.6, 8.4), (18.0, 8.4)]),
    ("clean", [(21.5, 6.6), (21.5, 3.5), (18.0, 3.3)]),
    ("dirty", [(17.5, 14.3), (22.0, 14.3)]),
    ("dirty", [(5.0, 17.6), (2.4, 19.3), (2.4, 29.0), (1.5, 31.2), (1.5, 41.4), (-2.5, 43.5)]),
]
DOOR_TAGS = [
    (11.55, 19.7, "5'-0\" pair, hermetic", 0), (19.9, 32.0, "5'-0\" pair", 0),
    (19.3, 16.3, "3'-5\"", 0), (19.2, 5.4, "3'-0\"", 0), (4.6, 21.6, "3'-0\"", 0),
    (3.1, 31.9, "2'-10\"", 0), (28.5, 21.6, "2'-10\"", 0), (28.5, 12.3, "2'-7\"", 0),
    (15.5, 35.3, "4'-0\"", 90), (28.2, 10.6, "3'-0\"", 0),
]
# travel route OT door -> stair (stair door positions assumed on the DWG core, to verify)
ROUTE_OUT = [(15.6, 20.65), (15.6, 30.59), (17.3, 33.5), (17.3, 40.0), (17.3, 44.2), (0.0, 44.2), (-14.3, 44.2)]
STAIR_B = [(-14.3, 30.0), (-19.4, 30.0)]
STAIR_A = [(-14.3, 11.0), (-19.4, 11.0)]


def _len(pts):
    return sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))


def ot_checks(rooms):
    """Numbers quoted in OT_H_BRIEF.md, measured on the model."""
    by = {r.key: r for r in rooms}
    ot = by["ot"].poly
    x0, y0, x1, y1 = ot.bounds
    out = {"ot_w": x1 - x0, "ot_d": y1 - y0, "ot_area": ot.area, "ot_m2": ot.area * 0.092903}
    cols = {k: ot.intersection(c).area for k, c in H.COLUMNS_H.items() if ot.intersection(c).area > 0.001}
    out["cols_in_ot"] = cols
    t = next(f for f in by["ot"].furniture if f[0] == "ottable")
    tb = box(t[1], t[2], t[1] + t[3], t[2] + t[4])
    fixed = [box(f[1], f[2], f[1] + f[3], f[2] + f[4]) for f in by["ot"].furniture if f[0] in ("shelf", "counter")]
    out["table_wall"] = dict(E=tb.bounds[0] - x0, W=x1 - tb.bounds[2], S=tb.bounds[1] - y0, N=y1 - tb.bounds[3])
    out["table_fixed"] = min(tb.distance(f) for f in fixed)
    far = max(math.dist(ROUTE_OUT[0], c) for c in ot.exterior.coords)
    out["door_to_stair_b"] = _len(ROUTE_OUT + STAIR_B)
    out["door_to_stair_a"] = _len(ROUTE_OUT + STAIR_A)
    out["far_corner"] = far
    out["door_to_main"] = _len(ROUTE_OUT[:-1])
    return out


def check_lines(c):
    tw = c["table_wall"]
    return [
        f"OT clear {fi(c['ot_w'])} x {fi(c['ot_d'])} = {c['ot_area']:.0f} sf ({c['ot_m2']:.1f} m2); "
        f"target 20'-0\" x 20'-0\" / about 36 m2: {'met' if min(c['ot_w'], c['ot_d']) >= 19.99 else 'SHORT'}",
        "columns inside the OT: "
        + (", ".join(f"{k} {a:.2f} sf" for k, a in c["cols_in_ot"].items()) or "none")
        + " (C1 and C3 stand in the west wall line; their faces are 1.5\" proud of the 4.5\" wall)",
        f"OT table to walls: E {fi(tw['E'])}, W {fi(tw['W'])}, S {fi(tw['S'])}, N {fi(tw['N'])}; "
        f"nearest fixed cabinet / shelf {fi(c['table_fixed'])}",
        f"travel OT door -> main door {c['door_to_main']:.0f}'; -> stair B (nearer) {c['door_to_stair_b']:.0f}' "
        f"({c['door_to_stair_b'] * 0.3048:.0f} m); -> stair A {c['door_to_stair_a']:.0f}' "
        f"({c['door_to_stair_a'] * 0.3048:.0f} m); add {c['far_corner']:.0f}' from the far OT corner",
    ]


def pendants(ax, z=9):
    for (x, y) in H.PENDANTS_H:
        ax.plot([x - 0.7, x + 0.7], [y, y], color="#4a4a4a", lw=0.5, zorder=z)
        ax.plot([x, x], [y - 0.7, y + 0.7], color="#4a4a4a", lw=0.5, zorder=z)


def _flow(ax, kind, pts, lw=2.3):
    col, ls, _ = FLOW[kind]
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=col, lw=lw, ls=ls, zorder=13, alpha=0.95, solid_capstyle="round")
    ax.annotate("", xy=pts[-1], xytext=pts[-2], zorder=13,
                arrowprops=dict(arrowstyle="-|>,head_width=0.45,head_length=0.9", color=col, lw=lw))


def render_ot_zone(path, B):
    """B = the build_h module (base drawing, labels, door symbol)."""
    rooms = H.layout_h_rooms()
    walls = H.walls_h(rooms)
    by = {r.key: r for r in rooms}
    chk = ot_checks(rooms)
    fig = plt.figure(figsize=(16, 21.2))
    ax = fig.add_axes([0.01, 0.262, 0.98, 0.715])
    ax.set_aspect("equal")
    B._draw_base(ax, rooms, walls, B.RD.CAD_PALETTE)
    pendants(ax)
    S = 1.5      # font scale against the full sheet

    for r in rooms:
        p = r.poly
        if p.is_empty or not r.name or p.bounds[1] > 48.4:
            continue
        if r.zone == "circ":
            o = B.CIRC_LABELS.get(r.key, {})
            if r.key in ("ns", "wardcorr"):
                continue
            ax.text(o.get("x", 0), o.get("y", 0), r.name, ha="center", va="center",
                    fontsize=o.get("fs", 7) * S * 0.9, rotation=o.get("rot", 0), zorder=9,
                    color="#222" if o.get("bold") else "#77776f",
                    weight="bold" if o.get("bold") else "normal",
                    style="normal" if o.get("bold") else "italic")
            continue
        if r.zone == "wet":
            x, y = {"wc_ot": (20.9, 27.2), "wc_acc": (38.6, 35.3)}.get(r.key, (p.centroid.x, p.centroid.y))
            ax.text(x, y, f"WC\n{r.dims.replace(' avg', '')}", ha="center", va="center", fontsize=5.6,
                    color=INK, zorder=11, linespacing=1.2, bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.8))
            continue
        o = dict(B.LABELS.get(r.key, {}))
        if r.key == "ot":
            ax.text(7.5, 4.25, f"OPERATION THEATRE\n20'-0\" × 20'-0\" clear\n{p.area:.0f} sf = {chk['ot_m2']:.1f} m²",
                    ha="center", va="center", fontsize=11, weight="bold", color="#111", zorder=9, linespacing=1.3)
            continue
        cp = p.representative_point()
        fs = o.get("fs", 6.0) * S
        txt = o.get("name", r.name) + ("\n" + r.dims if r.dims else "") + f"\n{p.area:.0f} sf"
        ax.text(o.get("x", cp.x), o.get("y", cp.y), txt, ha="center", va="center", fontsize=fs,
                color="#111", weight="bold" if r.name.isupper() or "·" in r.name else "normal",
                rotation=o.get("rot", 0), zorder=9, linespacing=1.22)

    # hatch names
    for x, y, t, rot in ((19.95, 7.0, "pass box", 90), (19.95, 14.3, "dirty hatch", 90),
                         (7.9, 47.45, "pharmacy hatch", 0)):
        ax.text(x, y, t, fontsize=6.3, color="#c0392b", rotation=rot, ha="center", va="center", zorder=9)

    # clear dimensions inside the OT (blue = room, grey = table to wall)
    ot = by["ot"].poly
    ipd.dim_string(ax, ot, 9.0, 17.75, "x", fs=7.5, at=0.42, off=0.5)
    ipd.dim_string(ax, ot, 18.05, 9.0, "y", fs=7.5, at=0.32, off=0.5)
    g = "#555"
    for (a, b, axis, lbl) in (((0.46, 7.45), (9.16, 7.45), "x", None), ((11.76, 12.9), (20.46, 12.9), "x", None),
                              ((10.75, 0.46), (10.75, 7.0), "y", None), ((11.5, 13.5), (11.5, 20.46), "y", None)):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=g, lw=0.6, ls=(0, (4, 2)), zorder=12)
        if axis == "x":
            ax.text((a[0] + b[0]) / 2 + (2.6 if a[0] < 1 else -1.2), a[1] - 0.42, fi(b[0] - a[0]), fontsize=6.6, color=g, ha="center",
                    va="center", zorder=12.2, bbox=dict(fc="white", ec="none", pad=0.2, alpha=0.9))
        else:
            ax.text(a[0] + (0.9 if a[1] < 5 else 0.45), (a[1] + b[1]) / 2 + (2.6 if a[1] < 5 else 1.2),
                    fi(b[1] - a[1]), fontsize=6.6,
                    color=g, ha="center", va="center", rotation=0 if a[1] < 5 else 90, zorder=12.2,
                    bbox=dict(fc="white", ec="none", pad=0.2, alpha=0.9))

    # red line of the transfer bay + gas panel
    ax.plot([12.9, 18.8], [28.0, 28.0], color="#d32f2f", lw=2.2, zorder=8.5)
    ax.text(18.0, 28.45, "red line", fontsize=5.8, color="#d32f2f", ha="center", va="center", zorder=9)
    ax.add_patch(Rectangle((18.2, 20.84), 0.55, 0.28, fc="#f6c343", ec=INK, lw=0.6, zorder=9))

    for x, y, t, rot in DOOR_TAGS:
        ax.text(x, y, t, fontsize=6.0, color="#7a1f1f", ha="center", va="center", rotation=rot, zorder=12.4,
                bbox=dict(fc="white", ec="none", pad=0.25, alpha=0.88))
    for kind, pts in FLOWS:
        _flow(ax, kind, pts)
    for n, (x, y), _ in H.OT_KEY_H:
        ax.add_patch(Circle((x, y), 0.47, fc="#fff8d6", ec=INK, lw=0.7, zorder=14))
        ax.text(x, y, str(n), ha="center", va="center", fontsize=6.6, weight="bold", color=INK, zorder=14.1)

    # main door
    _, y1, y2 = H.MD_DOOR_H
    for hy, t1, t2 in ((y1, 90, 180), (y2, 180, 270)):
        ax.add_patch(Arc((0.2, hy), 6, 6, theta1=t1, theta2=t2, lw=0.7, color=INK, zorder=8))
        ax.plot([0.2, -2.8], [hy, hy], lw=1.1, color=INK, zorder=8)
    ax.text(-6.6, 44.2, "MAIN ENTRY 6'-0\" pair\ncommon passage to\nlift lobby and stairs", fontsize=7, ha="center",
            va="center", color=INK)
    ax.text(-4.9, 39.0, "duct", ha="center", va="center", fontsize=6, color="#666", style="italic")
    ax.text(9.0, -2.15, "outdoor units of the OT AHU / gas manifold on the ledge: to verify", ha="center",
            va="center", fontsize=6.2, color=INK, bbox=dict(fc="white", ec="none", pad=1.0), zorder=3)
    ax.text(48.4, 14, "OPENABLE GLASS", rotation=-81.8, fontsize=8, color="#2c6fbb", ha="center", va="center")

    B._dim_chain(ax, [0, 20.65, 27.02, 33.4, 48.12], -5.3, "x", side=1, fs=8)
    B._dim_chain(ax, [0, 20.65, 30.59, 40.0, 48.33], -11.0, "y", side=-1, fs=8)
    B._dim_chain(ax, [0, 3.77, 9.65, 19.59, 30.59, 40.0], 50.0, "y", side=1, fs=7.5)
    for x, y, s_ in ((24, -8.3, "SOUTH"), (53.2, 22, "WEST"), (-13.6, 22, "EAST")):
        ax.text(x, y, s_, ha="center", va="center", fontsize=9, weight="bold", rotation=90 if x != 24 else 0,
                bbox=dict(fc="#eeeeee", ec=INK, lw=0.8))
    ax.set_xlim(-14.8, 54.6)
    ax.set_ylim(50.2, -9.6)
    ax.axis("off")
    fig.text(0.5, 0.984, "LAYOUT H - OT ZONE: modular OT 20'-0\" × 20'-0\", equipment and flows   ·   "
             "Hospital of Dr. Aman Khanna, 7th floor, Solaris Shine, Surat   ·   " + B.DATE,
             ha="center", va="center", fontsize=12.5, weight="bold", color=INK)

    # ------------------------------------------------------------ text panel
    tx = fig.add_axes([0.01, 0.005, 0.98, 0.25])
    tx.axis("off")
    tx.set_xlim(0, 100)
    tx.set_ylim(0, 100)
    tx.add_patch(Rectangle((0.3, 0.5), 99.4, 99, fc="white", ec=INK, lw=1.0))
    tx.text(1.5, 95, "FLOWS", fontsize=10, weight="bold", color=INK, va="center")
    for i, (k, (col, ls, lbl)) in enumerate(FLOW.items()):
        y = 88 - i * 6.4
        tx.plot([1.5, 6.5], [y, y], color=col, lw=2.6, ls=ls)
        tx.text(7.5, y, lbl, fontsize=8.6, color=INK, va="center")
    tx.text(1.5, 60.5, "EQUIPMENT KEY (drawn at true plan size)", fontsize=10, weight="bold", color=INK, va="center")
    for i, (n, _, d) in enumerate(H.OT_KEY_H):
        cx, row = (1.5, i) if i < 10 else (29.5, i - 10)
        y = 54 - row * 5.3
        tx.text(cx + 0.7, y, str(n), ha="center", va="center", fontsize=7, weight="bold",
                bbox=dict(boxstyle="circle,pad=0.25", fc="#fff8d6", ec=INK, lw=0.7))
        tx.text(cx + 2.3, y, d, fontsize=8.2, color=INK, va="center")
    sched = ["ot", "recovery", "change", "wc_ot", "scrub", "cssd", "wash", "otstore", "anstore", "dirty"]
    tx.text(61, 95, "OT SUITE - clear sizes (E-W × N-S)", fontsize=10, weight="bold", color=INK, va="center")
    lines = []
    tot = 0
    nm = {"ot": "Operation theatre", "recovery": "Pre-op / recovery, 2 bays + transfer bay", "change": "Staff change",
          "wc_ot": "Staff WC", "scrub": "Scrub bay, 3 taps", "cssd": "CSSD clean (pack / sterile)",
          "wash": "CSSD wash (dirty side)", "otstore": "Sterile store", "anstore": "Anaesthesia store",
          "dirty": "Dirty utility"}
    for k in sched:
        r = by[k]
        tot += r.area
        lines.append(f"{nm[k]:<41s}{r.dims:>17s}{r.area:>6.0f} sf")
    lines.append(f"{'OT suite, rooms only':<41s}{'':>17s}{tot:>6.0f} sf")
    tx.text(61, 90, "\n".join(lines), fontsize=7.6, family="monospace", color=INK, va="top", linespacing=1.42)
    tw = chk["table_wall"]
    notes = [
        f"OT {fi(chk['ot_w'])} × {fi(chk['ot_d'])} clear of plaster; modular wall panels (about 2\" to 3\" each side) "
        "come off this - to verify with the OT vendor.",
        f"Table to walls: E {fi(tw['E'])}, W {fi(tw['W'])}, S {fi(tw['S'])}, N {fi(tw['N'])}; "
        f"to the nearest fixed cabinet {fi(chk['table_fixed'])}. Mobile items stand inside this zone.",
        "No column inside the OT: C1 and C3 are in the west wall line (faces 1.5\" proud, covered by the panel).",
        f"Travel: OT door to main door {chk['door_to_main']:.0f}', to the nearer stair about "
        f"{chk['door_to_stair_b']:.0f}' ({chk['door_to_stair_b'] * 0.3048:.0f} m); stair doors assumed - to verify.",
        "AHU: no plant room on the floor. Ceiling-hung AHU over the CSSD / store strip or on the ledge - to verify.",
        "X-ray is 86 sf (mobile unit). A fixed 194 sf room costs OPD 2 or Twin 1 (2 beds) - see OT_H_BRIEF.md.",
        "Concept for review. NABH / HFG-India figures quoted from memory - to verify.",
    ]
    tx.text(61, 43, "CHECKS", fontsize=10, weight="bold", color=INK, va="center")
    tx.text(61, 39, "\n".join("• " + n for n in notes), fontsize=7.5, color=INK, va="top", linespacing=1.5,
            wrap=True)

    buf = io.BytesIO()
    fig.savefig(buf, dpi=150, facecolor="white", format="png")
    plt.close(fig)
    buf.seek(0)
    from PIL import Image
    im = Image.open(buf).convert("RGB")
    assert im.width == 2400, im.width
    im.save(path, quality=92, optimize=True)
    return im.size
