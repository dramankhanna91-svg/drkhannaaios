"""Brainstorm board: 4 options for the OPD + OT section, side by side.

South half of the Rev C plate only (y 0..48); the ward wing north of the
entry is identical in every option and is shown greyed.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Rectangle
from shapely.geometry import box as sbox
import numpy as np

from plan_model import PLATE, CUTOUT, MD_DOOR

INK = "#22303f"
COL = {"surg": "#cfe3cd", "opd": "#c7d9ec", "pub": "#f7e9c4",
       "supp": "#e4e4e0", "circ": "#f4f3ef"}

COMMON = [
    ("Autoclave", (0.4, 0.4, 9.8, 5.2), "surg"),
    ("Sterile/Chg", (10.6, 0.4, 9.8, 5.2), "surg"),
    ("OT 20x20", (0.4, 6.0, 20.0, 20.0), "surg"),
    ("Scrub", (20.9, 2.0, 5.2, 7.0), "surg"),
]

OPTIONS = [
    ("OPTION 1 — X-ray beside OPDs",
     "Dressing next to consult rooms; waiting moves to the entry zone (loses the glass)",
     COMMON + [
         ("Bath", (26.5, 0.4, 3.0, 5.0), "supp"),
         ("LOUNGE", (29.9, 0.4, 17.4, 9.0), "opd"),
         ("OPD 3", (31.6, 9.8, 12.6, 12.3), "opd"),
         ("OPD 2", (20.9, 13.0, 10.2, 7.4), "opd"),
         ("lobby", (20.9, 20.8, 10.2, 4.6), "circ"),
         ("OPD 1", (20.9, 25.8, 10.2, 7.6), "opd"),
         ("X-RAY / DRESS", (31.6, 22.5, 12.8, 8.6), "opd"),
         ("RECOVERY", (0.4, 26.4, 12.0, 8.0), "surg"),
         ("WAITING (no window)", (0.4, 34.8, 12.0, 7.6), "pub"),
         ("WAITING 2 / over.", (31.6, 31.5, 12.8, 8.1), "pub"),
     ]),
    ("OPTION 2 — as built (E rev 2)",
     "Emergency at the door; waiting on the glass; recovery-only OT entry",
     COMMON + [
         ("Bath", (26.5, 0.4, 3.0, 5.0), "supp"),
         ("LOUNGE", (29.9, 0.4, 17.4, 9.0), "opd"),
         ("OPD 3 +lounge door", (31.6, 9.8, 12.6, 12.3), "opd"),
         ("OPD 2", (20.9, 13.0, 10.2, 7.4), "opd"),
         ("lobby", (20.9, 20.8, 10.2, 4.6), "circ"),
         ("OPD 1", (20.9, 25.8, 10.2, 7.6), "opd"),
         ("RECOVERY", (0.4, 26.4, 12.0, 8.0), "surg"),
         ("X-RAY / EMERG", (0.4, 34.8, 12.0, 7.6), "opd"),
         ("WAITING 216sf 16+6", (31.6, 22.5, 12.8, 17.1), "pub"),
     ]),
    ("OPTION 3 — 4th OPD in the waiting slot",
     "Four consult rooms; waiting drops to ~100 sf (8-10 seats) — too small for 4 clinics",
     COMMON + [
         ("Bath", (26.5, 0.4, 3.0, 5.0), "supp"),
         ("LOUNGE", (29.9, 0.4, 17.4, 9.0), "opd"),
         ("OPD 3", (31.6, 9.8, 12.6, 12.3), "opd"),
         ("OPD 2", (20.9, 13.0, 10.2, 7.4), "opd"),
         ("lobby", (20.9, 20.8, 10.2, 4.6), "circ"),
         ("OPD 1", (20.9, 25.8, 10.2, 7.6), "opd"),
         ("OPD 4", (31.6, 22.5, 12.8, 8.3), "opd"),
         ("WAITING small", (31.6, 31.6, 12.8, 8.0), "pub"),
         ("RECOVERY", (0.4, 26.4, 12.0, 8.0), "surg"),
         ("X-RAY / EMERG", (0.4, 34.8, 12.0, 7.6), "opd"),
     ]),
    ("OPTION 4 — HYBRID (recommended)",
     "O2 kept whole + 4th OPD carved from the lounge band on the glass; lounge stays w/ bath",
     COMMON + [
         ("Bath", (26.5, 0.4, 3.0, 5.0), "supp"),
         ("Lounge", (29.9, 0.4, 6.8, 9.0), "opd"),
         ("OPD 4 (glass)", (37.1, 0.4, 10.2, 9.0), "opd"),
         ("OPD 3 +lounge door", (31.6, 9.8, 12.6, 12.3), "opd"),
         ("OPD 2", (20.9, 13.0, 10.2, 7.4), "opd"),
         ("lobby", (20.9, 20.8, 10.2, 4.6), "circ"),
         ("OPD 1", (20.9, 25.8, 10.2, 7.6), "opd"),
         ("RECOVERY", (0.4, 26.4, 12.0, 8.0), "surg"),
         ("X-RAY / EMERG", (0.4, 34.8, 12.0, 7.6), "opd"),
         ("WAITING 216sf 16+6", (31.6, 22.5, 12.8, 17.1), "pub"),
     ]),
]


def draw_option(ax, title, pitch, blocks):
    south = sbox(-1, -1, 50, 48.6)
    plate_s = PLATE.intersection(south)
    ax.add_patch(MplPoly(np.asarray(plate_s.exterior.coords), closed=True,
                         fc="#fcfbf8", ec=INK, lw=2.0, zorder=1))
    cut = CUTOUT.intersection(PLATE)
    ax.add_patch(MplPoly(np.asarray(cut.exterior.coords), closed=True,
                         fc="white", ec=INK, lw=0.9, hatch="///", zorder=2))
    for name, (x, y, w, h), z in blocks:
        p = sbox(x, y, x + w, y + h).intersection(PLATE).difference(CUTOUT)
        if p.is_empty:
            continue
        geoms = p.geoms if p.geom_type.startswith("Multi") else [p]
        for g in geoms:
            ax.add_patch(MplPoly(np.asarray(g.exterior.coords), closed=True,
                                 fc=COL[z], ec=INK, lw=1.0, zorder=3))
        c = p.representative_point()
        fs = 7.5 if p.area > 90 else 6.2
        ax.text(c.x, c.y, name, ha="center", va="center", fontsize=fs, zorder=5,
                weight="bold" if name.isupper() else "normal", linespacing=1.15)
    # entry
    y1, y2 = MD_DOOR[1], MD_DOOR[2]
    ax.plot([0, 0], [y1, y2], color="#c04a2b", lw=4, zorder=6)
    ax.text(-1.6, (y1 + y2) / 2, "ENTRY", rotation=90, fontsize=6.5, ha="center",
            va="center", color="#c04a2b", weight="bold")
    ax.add_patch(Rectangle((0.4, 48.8), 43, 3.4, fc="#eeeeee", ec="#aaa", lw=0.6, zorder=1))
    ax.text(21, 50.6, "WARD WING — unchanged in every option", fontsize=6.5,
            ha="center", va="center", color="#888")
    ax.set_title(title + "\n" + pitch, fontsize=8.6, pad=6, linespacing=1.4)
    ax.set_xlim(-3.2, 51)
    ax.set_ylim(53, -2.5)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    import os
    fig, axes = plt.subplots(1, 4, figsize=(22, 8.2))
    for ax, (title, pitch, blocks) in zip(axes, OPTIONS):
        draw_option(ax, title, pitch, blocks)
    fig.suptitle("OPD + OT SECTION — BRAINSTORM BOARD (south zone; Rev C envelope; sheet oriented south-up)",
                 fontsize=13, y=0.99)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "deliverables", "opd_ot_options_board.png")
    fig.savefig(out, dpi=170, bbox_inches="tight", facecolor="white")
    print("opd_ot_options_board.png")


if __name__ == "__main__":
    main()
