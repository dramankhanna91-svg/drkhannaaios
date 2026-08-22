"""Single-line architecture diagram (the classic 'line diagram' architects
sketch first): plate + single-line walls + door swings + labels + flow arrows.
No wall poche, no furniture except beds in ward/GW, no tiles."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Arc, FancyArrow, Rectangle, FancyArrowPatch
import numpy as np

from plan_model import (PLATE, CUTOUT, GLASS_WEST, GLASS_NORTH, MD_DOOR, LAYOUTS)

INK = "#22303f"
FLOW = "#c04a2b"


def _outline(ax, poly, lw, z):
    geoms = poly.geoms if poly.geom_type.startswith("Multi") else [poly]
    for g in geoms:
        if g.geom_type != "Polygon" or g.area < 0.5:
            continue
        ax.add_patch(MplPoly(np.asarray(g.exterior.coords), closed=True,
                             fc="white", ec=INK, lw=lw, zorder=z))
        for hole in g.interiors:
            ax.add_patch(MplPoly(np.asarray(hole.coords), closed=True,
                                 fc="none", ec=INK, lw=lw * 0.8, zorder=z + 0.1))


def _door(ax, door, z=8):
    cx, cy, w, wall = door
    r = w
    if wall in ("N", "S"):
        ax.plot([cx - w / 2, cx + w / 2], [cy, cy], color="white", lw=3.4, zorder=z,
                solid_capstyle="butt")
        sgn = 1 if wall == "N" else -1
        ax.add_patch(Arc((cx - w / 2, cy), 2 * r, 2 * r, angle=0,
                         theta1=0 if sgn > 0 else 270, theta2=90 if sgn > 0 else 360,
                         lw=0.7, color=INK, zorder=z + 1))
        ax.plot([cx - w / 2, cx - w / 2], [cy, cy + sgn * r], lw=1.0, color=INK, zorder=z + 1)
    else:
        ax.plot([cx, cx], [cy - w / 2, cy + w / 2], color="white", lw=3.4, zorder=z,
                solid_capstyle="butt")
        sgn = 1 if wall == "E" else -1
        ax.add_patch(Arc((cx, cy - w / 2), 2 * r, 2 * r, angle=0,
                         theta1=0 if wall == "E" else 90, theta2=90 if wall == "E" else 180,
                         lw=0.7, color=INK, zorder=z + 1))
        ax.plot([cx, cx + sgn * r], [cy - w / 2, cy - w / 2], lw=1.0, color=INK, zorder=z + 1)


FLOW_ARROWS = {
    "D": [((-3.0, 51.5), (7.0, 53.5), "enter"),
          ((10.0, 55.5), (18.5, 45.0), "to OPD / waiting", -0.25),
          ((18.8, 40.0), (30.0, 30.0), "", 0.2),
          ((10.5, 8.5), (6.0, 19.5), "OT → Recovery", 0.3),
          ((6.0, 26.5), (10.0, 51.0), "post-op → ward gate", -0.3),
          ((19.0, 62.0), (21.7, 61.5), "", 0.0),
          ((18.9, 68.0), (18.9, 80.0), "wards", 0.0)],
}


def render_line(key, out_path):
    title, factory = LAYOUTS[key]
    rooms = factory()

    fig, ax = plt.subplots(figsize=(11, 19))
    ax.set_aspect("equal")

    ax.add_patch(MplPoly(np.asarray(PLATE.exterior.coords), closed=True,
                         fc="#fcfbf8", ec=INK, lw=2.8, zorder=1))
    ax.add_patch(Rectangle((0, -4.2), 48.5, 3.4, fc="white", ec=INK, lw=0.9,
                           hatch="xxx", zorder=1))
    ax.text(24, -2.5, "SERVICE AREA", ha="center", va="center", fontsize=8.5, color=INK)
    ax.add_patch(MplPoly(np.asarray(CUTOUT.exterior.coords), closed=True,
                         fc="white", ec=INK, lw=1.2, hatch="///", zorder=2))
    c = CUTOUT.centroid
    ax.text(c.x, c.y, "CUT-OUT", ha="center", va="center", fontsize=8, color=INK, zorder=4)

    for (x1, y1), (x2, y2) in GLASS_WEST + GLASS_NORTH:
        dx, dy = x2 - x1, y2 - y1
        n = np.hypot(dx, dy)
        ox, oy = dy / n * 1.2, -dx / n * 1.2
        ax.plot([x1 + ox, x2 + ox], [y1 + oy, y2 + oy], color="#2c6fbb", lw=2.0, zorder=3)

    # rooms: single-line outlines + labels
    for r in rooms:
        p = r.poly
        if p.is_empty:
            continue
        if r.zone == "circ":
            cpt = p.representative_point()
            x0, y0, w0, h0 = r.rect
            if r.key == "lobby":
                cpt = type(cpt)(x0 + w0 * 0.70, y0 + h0 * 0.92)
            rot = 90 if h0 > w0 * 1.4 else 0
            fs = 8 if r.name.isupper() else 7.5
            col = "#22303f" if r.name.isupper() else "#8a8a84"
            wt = "bold" if r.name.isupper() else "normal"
            st = "normal" if r.name.isupper() else "italic"
            ax.text(cpt.x, cpt.y, r.name, ha="center", va="center", fontsize=fs,
                    color=col, weight=wt, style=st, zorder=9, rotation=rot)
            for f in r.furniture:
                if f[0] == "counter":
                    ax.add_patch(Rectangle((f[1], f[2]), f[3], f[4], angle=f[5],
                                           fc="#eee9e0", lw=0.7, ec=INK, zorder=6))
            continue
        _outline(ax, p, 1.5, 3)
        cpt = p.representative_point()
        x0, y0, w0, h0 = r.rect
        rot = 90 if (w0 < 6.4 and h0 > 8) else 0
        fs = 9.5 if p.area > 140 else (8 if p.area > 60 else 6.2)
        label = r.name + ("\n" + r.dims if r.dims else "")
        if p.area < 32:
            label = r.name
        ax.text(cpt.x, cpt.y, label, ha="center", va="center", fontsize=fs,
                weight="bold" if r.name.isupper() else "normal",
                color="#111", zorder=9, linespacing=1.3, rotation=rot)
        # beds only, to read ward capacity at a glance
        for f in r.furniture:
            if f[0] == "bed":
                ax.add_patch(Rectangle((f[1], f[2]), f[3], f[4], fc="white",
                                       lw=0.7, ec="#4a4a4a", zorder=6))
                ax.add_patch(Rectangle((f[1] + 0.25, f[2] + f[4] - 1.3), f[3] - 0.5, 1.0,
                                       fc="#e8e8e8", lw=0.4, ec="#4a4a4a", zorder=6))

    for r in rooms:
        for d in r.doors:
            _door(ax, d)

    # flow arrows (like the notebook sketch)
    for arrow in FLOW_ARROWS.get(key, []):
        (x1, y1), (x2, y2), lbl = arrow[0], arrow[1], arrow[2]
        rad = arrow[3] if len(arrow) > 3 else 0.15
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=15, lw=1.7, color=FLOW, zorder=10,
                                     connectionstyle=f"arc3,rad={rad}"))
        if lbl:
            ax.text(x2 + 0.8, (y1 + y2) / 2, lbl, fontsize=7, color=FLOW,
                    style="italic", zorder=10)

    # main door
    _, y1, y2 = MD_DOOR
    ax.plot([0, 0], [y1, y2], color="white", lw=6, zorder=5, solid_capstyle="butt")
    ax.add_patch(Arc((0, y1), 8, 8, angle=0, theta1=0, theta2=60, lw=0.8, color=INK, zorder=6))
    ax.annotate("MD — MAIN\nENTRY", xy=(-0.3, (y1 + y2) / 2), xytext=(-7.6, 60.0),
                fontsize=9, weight="bold", ha="center", va="center", color=INK,
                arrowprops=dict(arrowstyle="->", lw=1.1, color=INK), zorder=6)

    for x, y, s, rot in [(24, -8.2, "SOUTH SIDE", 0), (24, 106.5, "NORTH SIDE", 0),
                         (-7.5, 25, "EAST SIDE", 90), (53.5, 25, "WEST SIDE — glass", -90)]:
        ax.text(x, y, s, rotation=rot, ha="center", va="center", fontsize=10,
                weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=0.9))
    ax.add_patch(FancyArrow(51.5, 96, 0, 4.5, width=0.5, head_width=1.8, head_length=1.7,
                            fc=INK, ec=INK))
    ax.text(51.5, 94, "N", ha="center", fontsize=12, weight="bold", color=INK)

    ax.annotate("", xy=(48.5, -6.0), xytext=(0, -6.0),
                arrowprops=dict(arrowstyle="<->", lw=1, color=INK))
    ax.text(24.2, -7.1, "48'-6\"", ha="center", fontsize=8.5, color=INK)
    ax.annotate("", xy=(-4.4, 101), xytext=(-4.4, 0),
                arrowprops=dict(arrowstyle="<->", lw=1, color=INK))
    ax.text(-5.5, 14.0, "101'-0\"", rotation=90, va="center", fontsize=8.5, color=INK)

    ax.plot([0, 10], [111.0, 111.0], lw=3, color=INK)
    for i in range(0, 11, 5):
        ax.plot([i, i], [110.4, 111.6], lw=1.1, color=INK)
        ax.text(i, 113.0, f"{i}'", ha="center", fontsize=7, color=INK)

    ax.set_title(f"{title} — SINGLE-LINE DIAGRAM\nHospital of Dr. Aman Khanna — "
                 f"7th Floor, Solaris Shine, Althan, Surat\n"
                 f"(from the notebook sketch; red arrows = patient/staff flow)",
                 fontsize=11.5, pad=14)
    ax.set_xlim(-10.5, 57)
    ax.set_ylim(116, -11)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "deliverables")
    render_line("D", os.path.join(out, "layout_D_sketch_line_diagram.png"))
    print("line diagram ok")
