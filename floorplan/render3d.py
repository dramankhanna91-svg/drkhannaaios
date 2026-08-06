"""Simple extruded 3D visualization of a layout (matplotlib).

matplotlib's painter algorithm mis-sorts a large floor slab against small
room polygons, so every collection gets an explicit zorder band:
slab=1 < room floors=2 < walls=3+ < labels=20.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from plan_model import PLATE, CUTOUT, ZONES, LAYOUTS

WALL_H = 8.5


def _add(ax, verts, fc, ec, lw, alpha, zorder):
    col = Poly3DCollection([verts], facecolors=fc, edgecolors=ec,
                           linewidths=lw, alpha=alpha)
    col.set_zorder(zorder)
    ax.add_collection3d(col)


def render_3d(key, out_path):
    title, factory = LAYOUTS[key]
    rooms = factory()

    fig = plt.figure(figsize=(17, 12))
    ax = fig.add_subplot(111, projection="3d")
    ax.computed_zorder = False   # honor explicit zorder: slab < floors < walls

    slab = [(x, y, 0.0) for x, y in PLATE.exterior.coords]
    _add(ax, slab, "#eceae4", "#999", 1.0, 1.0, 1)

    void = [(x, y, 0.03) for x, y in CUTOUT.exterior.coords]
    _add(ax, void, "white", "#666", 1.0, 1.0, 2)

    # sort rooms south->north so nearer walls draw later at same zorder
    for r in sorted(rooms, key=lambda r: r.rect[1]):
        p = r.poly
        if p.is_empty:
            continue
        col = ZONES[r.zone][0]
        geoms = p.geoms if p.geom_type.startswith("Multi") else [p]
        for g in geoms:
            if g.geom_type != "Polygon" or g.area < 0.5:
                continue
            floor = [(x, y, 0.05) for x, y in g.exterior.coords]
            _add(ax, floor, col, "#666", 0.6, 1.0, 2)
            if r.zone == "circ":
                continue
            wall_h = WALL_H if r.zone not in ("public",) else 3.5
            pts = list(g.exterior.coords)
            for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
                quad = [(x1, y1, 0), (x2, y2, 0), (x2, y2, wall_h), (x1, y1, wall_h)]
                _add(ax, quad, "#d7d3cb", "#7a766e", 0.4, 0.42, 3)
        c = p.representative_point()
        if r.name and p.area > 55 and r.zone != "circ":
            wall_h = WALL_H if r.zone not in ("public",) else 3.5
            txt = ax.text(c.x, c.y, wall_h + 2.2, r.name.title(), fontsize=7.5,
                          ha="center", color="#222")
            txt.set_zorder(20)

    ax.set_xlim(0, 50)
    ax.set_ylim(0, 101)
    ax.set_zlim(0, 26)
    ax.set_box_aspect((50, 101, 15))
    ax.view_init(elev=55, azim=-100)
    ax.axis("off")
    ax.set_title(f"3D view — {title}\n(walls extruded; public-zone walls lowered for visibility)",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
