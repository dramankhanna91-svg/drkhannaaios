"""2D sheet renderer (SVG + PNG) for the hospital layouts."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Arc, FancyArrow, Rectangle, Circle
from matplotlib.lines import Line2D
import numpy as np

from plan_model import (PLATE, CUTOUT, GLASS_WEST, GLASS_NORTH, MD_DOOR,
                        ZONES, LAYOUTS)

INK = "#3a3a3a"


def _draw_poly(ax, poly, **kw):
    if poly.is_empty:
        return
    geoms = poly.geoms if poly.geom_type.startswith("Multi") else [poly]
    for g in geoms:
        if g.geom_type != "Polygon" or g.area < 0.5:
            continue
        ax.add_patch(MplPoly(np.asarray(g.exterior.coords), closed=True, **kw))


def _furniture(ax_real, item):
    kind, x, y, w, h, rot = item

    class _Z:
        """Proxy that raises artists above room fills."""
        def add_patch(self, p):
            p.set_zorder(5)
            return ax_real.add_patch(p)

        def plot(self, *a, **kw):
            kw.setdefault("zorder", 5)
            return ax_real.plot(*a, **kw)

    ax = _Z()
    style = dict(lw=0.7, ec=INK, joinstyle="round")
    if kind == "bed":
        ax.add_patch(Rectangle((x, y), w, h, fc="white", **style))
        ax.add_patch(Rectangle((x + 0.25, y + h - 1.5), w - 0.5, 1.1, fc="#dcdcdc", lw=0.5, ec=INK))
    elif kind == "exam":
        ax.add_patch(Rectangle((x, y), w, h, fc="#f0f0f0", **style))
    elif kind == "ottable":
        ax.add_patch(Rectangle((x, y), w, h, fc="#c9d8c9", angle=rot, **style))
        ax.add_patch(Circle((x + w / 2, y + h + 1.2), 0.9, fc="#eef2ee", lw=0.7, ec=INK))
    elif kind in ("desk", "counter", "shelf", "side", "cart"):
        fc = {"desk": "#e3e3e3", "counter": "#cfc4b8", "shelf": "#bfae9e",
              "side": "#e9e9e9", "cart": "#e0e6ea"}[kind]
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, **style))
    elif kind == "chair":
        ax.add_patch(Rectangle((x, y), w, h, fc="#f5efe0", lw=0.6, ec=INK))
    elif kind == "wc":
        ax.add_patch(Rectangle((x, y + h * 0.45), w, h * 0.55, fc="white", lw=0.6, ec=INK))
        ax.add_patch(Circle((x + w / 2, y + h * 0.3), w * 0.42, fc="white", lw=0.6, ec=INK))
    elif kind == "sink":
        ax.add_patch(Circle((x + w / 2, y + h / 2), min(w, h) * 0.48, fc="white", lw=0.6, ec=INK))
    elif kind == "shower":
        ax.add_patch(Rectangle((x, y), w, h, fc="#eaf4f6", lw=0.6, ec=INK))
        ax.plot([x, x + w], [y, y + h], lw=0.4, color=INK)
    elif kind == "plant":
        ax.add_patch(Circle((x + w / 2, y + h / 2), w / 2, fc="#b8d4b0", lw=0.6, ec="#5a7a52"))
    elif kind == "tv":
        ax.add_patch(Rectangle((x, y), w, h, fc="#555", lw=0.5, ec=INK))
    elif kind == "water":
        ax.add_patch(Rectangle((x, y), w, h, fc="#cfe6f4", lw=0.6, ec=INK))
    elif kind == "light":
        ax.add_patch(Circle((x + w / 2, y + h / 2), w / 2, fc="none", lw=0.6, ec=INK))
        ax.plot([x, x + w], [y + h / 2, y + h / 2], lw=0.4, color=INK)


def _door(ax, door):
    cx, cy, w, wall = door
    r = w
    if wall == "N":
        ax.plot([cx - w / 2, cx + w / 2], [cy, cy], color="white", lw=3.2, zorder=6, solid_capstyle="butt")
        ax.add_patch(Arc((cx - w / 2, cy), 2 * r, 2 * r, angle=0, theta1=0, theta2=90,
                         lw=0.7, color=INK, zorder=7))
        ax.plot([cx - w / 2, cx - w / 2], [cy, cy + r], lw=0.9, color=INK, zorder=7)
    elif wall == "S":
        ax.plot([cx - w / 2, cx + w / 2], [cy, cy], color="white", lw=3.2, zorder=6, solid_capstyle="butt")
        ax.add_patch(Arc((cx - w / 2, cy), 2 * r, 2 * r, angle=0, theta1=270, theta2=360,
                         lw=0.7, color=INK, zorder=7))
        ax.plot([cx - w / 2, cx - w / 2], [cy, cy - r], lw=0.9, color=INK, zorder=7)
    elif wall == "E":
        ax.plot([cx, cx], [cy - w / 2, cy + w / 2], color="white", lw=3.2, zorder=6, solid_capstyle="butt")
        ax.add_patch(Arc((cx, cy - w / 2), 2 * r, 2 * r, angle=0, theta1=0, theta2=90,
                         lw=0.7, color=INK, zorder=7))
        ax.plot([cx, cx + r], [cy - w / 2, cy - w / 2], lw=0.9, color=INK, zorder=7)
    elif wall == "W":
        ax.plot([cx, cx], [cy - w / 2, cy + w / 2], color="white", lw=3.2, zorder=6, solid_capstyle="butt")
        ax.add_patch(Arc((cx, cy - w / 2), 2 * r, 2 * r, angle=0, theta1=90, theta2=180,
                         lw=0.7, color=INK, zorder=7))
        ax.plot([cx, cx - r], [cy - w / 2, cy - w / 2], lw=0.9, color=INK, zorder=7)


def render_layout(key, out_base, highlight=True):
    title, factory = LAYOUTS[key]
    rooms = factory()

    fig, ax = plt.subplots(figsize=(13, 22))
    ax.set_aspect("equal")

    # plate + service strip + cut-out
    _draw_poly(ax, PLATE, fc="#fbfaf7", ec=INK, lw=3.0, zorder=1)
    ax.add_patch(Rectangle((0, -4.2), 48.5, 3.4, fc="white", ec=INK, lw=1.0, hatch="xxx", zorder=1))
    ax.text(24, -2.5, "SERVICE AREA", ha="center", va="center", fontsize=9, color=INK)
    _draw_poly(ax, CUTOUT, fc="white", ec=INK, lw=1.4, hatch="///", zorder=3)
    cx, cyc = CUTOUT.centroid.x, CUTOUT.centroid.y
    ax.text(cx, cyc, "CUT-OUT\n(void)", ha="center", va="center", fontsize=9, color=INK, zorder=4)

    # rooms
    for r in rooms:
        col = ZONES[r.zone][0]
        z = 2
        _draw_poly(ax, r.poly, fc=col, ec=INK, lw=1.6 if r.zone != "circ" else 0.0, zorder=z)
        if r.zone == "circ":
            _draw_poly(ax, r.poly, fc=col, ec="none", zorder=1.5)
        p = r.poly
        if p.is_empty:
            continue
        c = p.representative_point()
        if r.name:
            fs = 10 if r.area > 90 else (8 if r.area > 45 else 6.5)
            label = r.name + ("\n" + r.dims if r.dims else "")
            weight = "bold" if r.name.isupper() else "normal"
            x0, y0, w0, h0 = r.rect
            rot = 90 if (w0 < 6.2 and h0 > 8 and r.zone != "circ") else 0
            tx, ty = c.x, c.y
            if r.key == "lobby":
                tx, ty = 15.6, 52.3
                fs = 8
            ax.text(tx, ty, label, ha="center", va="center", fontsize=fs,
                    color="#1a1a1a", weight=weight, zorder=8, linespacing=1.3,
                    rotation=rot)

    # furniture + doors on top
    for r in rooms:
        for f in r.furniture:
            _furniture(ax, f)
        for d in r.doors:
            _door(ax, d)

    # glass facade bands
    for (x1, y1), (x2, y2) in GLASS_WEST + GLASS_NORTH:
        dx, dy = x2 - x1, y2 - y1
        n = np.hypot(dx, dy)
        ox, oy = dy / n * 1.1, -dx / n * 1.1
        ax.plot([x1 + ox, x2 + ox], [y1 + oy, y2 + oy], color="#2c6fbb", lw=2.2, zorder=5)
        ax.plot([x1 + ox * 1.7, x2 + ox * 1.7], [y1 + oy * 1.7, y2 + oy * 1.7],
                color="#2c6fbb", lw=0.8, zorder=5)
    ax.text(47.5, 20, "OPENABLE GLASS", rotation=-84, fontsize=8, color="#2c6fbb",
            ha="center", va="center")
    ax.text(20, 103.6, "OPENABLE GLASS", fontsize=8, color="#2c6fbb", ha="center")

    # main door
    _, y1, y2 = MD_DOOR
    ax.plot([0, 0], [y1, y2], color="white", lw=5, zorder=6, solid_capstyle="butt")
    ax.add_patch(Arc((0, y1), 8, 8, angle=0, theta1=0, theta2=60, lw=0.8, color=INK, zorder=7))
    ax.annotate("MD\nMAIN\nENTRY", xy=(-0.4, (y1 + y2) / 2), xytext=(-6.8, (y1 + y2) / 2 + 6.5),
                fontsize=8.5, weight="bold", ha="center", va="center", color=INK,
                arrowprops=dict(arrowstyle="->", lw=1.2, color=INK))

    # compass labels (sheet keeps the architect's orientation: South at top)
    for x, y, s in [(24, -8.5, "SOUTH SIDE"), (24, 108.5, "NORTH SIDE")]:
        ax.text(x, y, s, ha="center", va="center", fontsize=11, weight="bold",
                bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(-8.5, 30, "EAST SIDE", rotation=90, ha="center", va="center", fontsize=11,
            weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(55, 30, "WEST SIDE", rotation=-90, ha="center", va="center", fontsize=11,
            weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.add_patch(FancyArrow(52.5, 96, 0, 4.5, width=0.6, head_width=2.0, head_length=1.8,
                            fc=INK, ec=INK))
    ax.text(52.5, 94, "N", ha="center", fontsize=13, weight="bold", color=INK)

    # overall dimensions
    ax.annotate("", xy=(48.5, -6.2), xytext=(0, -6.2), arrowprops=dict(arrowstyle="<->", lw=1, color=INK))
    ax.text(24.2, -7.3, "48'-6\"", ha="center", fontsize=9, color=INK)
    ax.annotate("", xy=(-4.5, 101), xytext=(-4.5, 0), arrowprops=dict(arrowstyle="<->", lw=1, color=INK))
    ax.text(-5.6, 25.0, "101'-0\"", rotation=90, va="center", fontsize=9, color=INK)

    # signage markers
    for x, y, s in [(11, 52.5, "i"), (27.6, 44.5, "→"), (18.9, 66.0, "→"), (16.9, 79.5, "→")]:
        ax.add_patch(Circle((x, y), 0.9, fc="#20558a", ec="white", lw=0.8, zorder=9))
        ax.text(x, y, s, color="white", fontsize=7, ha="center", va="center", zorder=10, weight="bold")

    # legend
    lx, ly = 0.5, 111.5
    handles = [Line2D([], [], marker="s", ls="", ms=11, mfc=c, mec=INK, label=lbl)
               for c, lbl in ZONES.values()]
    handles.append(Line2D([], [], color="#2c6fbb", lw=2.2, label="Openable glass facade"))
    handles.append(Line2D([], [], marker="o", ls="", ms=8, mfc="#20558a", mec="white",
                          label="Signage / wayfinding"))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.035),
              ncol=3, fontsize=8.5, frameon=False)

    total = PLATE.area - CUTOUT.area
    ax.set_title(f"{title}\nHospital of Dr. Aman Khanna — 7th Floor, Solaris Shine, Althan, Surat"
                 f"\nCarpet area ≈ {total:,.0f} sq ft  ·  all corridors ≥ 5'-0\" (12'-1½\" spine)"
                 f"  ·  scale bar below", fontsize=12, pad=16)

    # scale bar
    ax.plot([0, 10], [116.5, 116.5], lw=3, color=INK)
    for i in range(0, 11, 5):
        ax.plot([i, i], [115.9, 117.1], lw=1.2, color=INK)
        ax.text(i, 118.3, f"{i}'", ha="center", fontsize=7.5, color=INK)

    ax.set_xlim(-11, 58)
    ax.set_ylim(121, -12)     # inverted: south at top like the architect's sheet
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_base + ".png", dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return total
