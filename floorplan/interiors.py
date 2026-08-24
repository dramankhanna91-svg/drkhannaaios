"""Enlarged interior-detail boards for Layout E rev 2.

Each board is a zoomed, fully furnished crop of the plan at large scale,
like an architect's interior-detail sheet.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from plan_model import LAYOUTS, CUTOUT, ZONES, wall_bands
from render import _fill, _iter_polys, _tile_hatch, _tint, _furniture, _door, INK

BOARDS = [
    ("OT_suite", "OT SUITE — autoclave · sterile store · scrub · OT 20'×20' · "
     "recovery/pre-op · x-ray/emergency", (0, 0, 28.5, 44)),
    ("patient_room", "TYPICAL ENSUITE PATIENT ROOM (ROOM 2) — bed · sofa · "
     "wardrobe · TV · T with WC/basin/shower", (16.5, 57.5, 43.5, 71.5)),
    ("entry_zone", "ENTRY ZONE — lobby · reception · pharmacy · waiting on glass "
     "· overflow seating", (0, 20.5, 46.5, 56.5)),
    ("ward_band", "WARD SERVICE BAND + SUITE — BP/exam · nursing+obs · wash+bath "
     "· stores · pantry · suite 5", (0, 47.5, 22.5, 92)),
]


def render_board(key, name, title, bbox, out_path):
    x0, y0, x1, y1 = bbox
    _, factory = LAYOUTS[key]
    rooms = factory()
    walls = wall_bands(rooms)

    w_in = max(7.5, (x1 - x0) * 0.30)
    h_in = max(7.5, (y1 - y0) * 0.30)
    fig, ax = plt.subplots(figsize=(w_in, h_in + 0.8))
    ax.set_aspect("equal")

    for r in rooms:
        if r.zone == "circ":
            continue
        p = r.poly
        _fill(ax, p, 2, fc=_tint(ZONES[r.zone][0], 0.35), ec="none")
        for g in _iter_polys(p):
            if r.zone == "wet":
                _tile_hatch(ax, g, 3)
    _fill(ax, walls, 7, fc=INK, ec="none")
    _fill(ax, CUTOUT, 3, fc="white", ec=INK, hatch="//", lw=0.8)

    for r in rooms:
        for f in r.furniture:
            _furniture(ax, f)
        for d in r.doors:
            _door(ax, d)
        p = r.poly
        if p.is_empty or not r.name:
            continue
        c = p.representative_point()
        if not (x0 - 2 < c.x < x1 + 2 and y0 - 2 < c.y < y1 + 2):
            continue
        if r.zone == "circ":
            ax.text(c.x, c.y, r.name, ha="center", va="center", fontsize=9,
                    style="italic", color="#8a8a84", zorder=9)
        else:
            label = r.name + ("\n" + r.dims if r.dims else "")
            fs = 11 if p.area > 100 else (9 if p.area > 34 else 7)
            ax.text(c.x, c.y, label, ha="center", va="center", fontsize=fs,
                    weight="bold" if r.name.isupper() else "normal",
                    color="#111", zorder=9, linespacing=1.3)

    ax.set_title(title, fontsize=12, pad=10)
    ax.set_xlim(x0 - 0.8, x1 + 0.8)
    ax.set_ylim(y1 + 0.8, y0 - 0.8)
    ax.axis("off")
    # 5' scale tick
    ax.plot([x0, x0 + 5], [y1 + 0.4, y1 + 0.4], lw=3, color=INK)
    ax.text(x0 + 2.5, y1 + 0.1, "5'-0\"", ha="center", fontsize=8, color=INK)
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "deliverables")
    for name, title, bbox in [(b[0], b[1], b[2]) for b in BOARDS]:
        render_board("E", name, title, bbox,
                     os.path.join(out, f"interior_{name}.png"))
        print(f"interior_{name}.png")
