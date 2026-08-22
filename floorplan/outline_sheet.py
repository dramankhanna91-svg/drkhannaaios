"""A4 floor-plate OUTLINE sheets for hand-sketching.

One geometry source renders to BOTH:
  * true-vector A4 PDF (matplotlib, exact 210x297 mm) - the print master
  * SVG / .dc.html artboards - the design canvas

Sheet coordinate system = CSS px at 96 dpi, y DOWN.
Plan coordinate system  = feet; x east->west, y south->north.
Drawing scale: 1 cm = 4'-0"  ->  1 ft = 9.4488 px.  South at top, matching
every earlier sheet in this set.
"""
import os

# ----------------------------------------------------------------- constants
PX_PER_CM = 96.0 / 2.54                 # 37.7953
FT_PER_CM = 4.0                         # the chosen scale
PPF = PX_PER_CM / FT_PER_CM             # 9.44881... px per foot
A4W, A4H = 793.70, 1122.52              # 210 x 297 mm at 96 dpi

OX, OY = 92.0, 92.0                     # plate SE corner on the sheet

INK = "#1f2937"
THIN = "#6b7280"
GLASS = "#1d4ed8"
VOID = "#9ca3af"
ACCENT = "#b45309"

PLATE = [(0.0, 0.0), (48.5, 0.0), (44.5, 40.0), (43.0, 55.0), (41.5, 70.0),
         (39.5, 88.0), (38.8, 92.0), (36.5, 97.5), (33.0, 100.2),
         (29.0, 101.0), (0.0, 101.0)]

# cut-out void, clipped to the west facade
CUTOUT = [(27.5, 48.0), (43.7, 48.0), (42.45, 60.5), (27.5, 60.5)]

MD = (49.5, 53.5)                       # main door on the east wall
DUCT = (0.0, 59.2, 4.0, 4.2)            # traced - flagged "verify" on sheet 3
STATIONS = [40.0, 55.0, 70.0, 88.0, 92.0]
WIDTH_AT = {0.0: 48.5, 40.0: 44.5, 55.0: 43.0, 70.0: 41.5,
            88.0: 39.5, 92.0: 38.8, 97.5: 36.5, 100.2: 33.0, 101.0: 29.0}


def fi(v):
    """9.44 -> 9'-5½\" (nearest half inch)."""
    half_in = round(abs(v) * 24)
    ft, rem = divmod(half_in, 24)
    inch, half = divmod(rem, 2)
    return f"{ft}'-{inch}" + ("½" if half else "") + '"'


def P(x_ft, y_ft):
    return (OX + x_ft * PPF, OY + y_ft * PPF)


# ------------------------------------------------------------- draw commands
class Sheet:
    def __init__(self):
        self.c = []

    def line(self, x1, y1, x2, y2, w=0.6, color=INK, dash=None):
        self.c.append(("line", x1, y1, x2, y2, w, color, dash))

    def poly(self, pts, w=1.0, color=INK, fill="none", dash=None, close=True):
        self.c.append(("poly", list(pts), w, color, fill, dash, close))

    def rect(self, x, y, wd, ht, w=1.0, color=INK, fill="none", dash=None):
        self.poly([(x, y), (x + wd, y), (x + wd, y + ht), (x, y + ht)],
                  w, color, fill, dash, True)

    def text(self, x, y, s, size=10.0, color=INK, anchor="start", rot=0.0,
             weight="normal", mono=False, ls=None):
        self.c.append(("text", x, y, s, size, color, anchor, rot, weight, mono, ls))

    # --- dimension primitives (architectural oblique ticks)
    def _tick(self, x, y, vertical=False):
        d = 3.4
        if vertical:
            self.line(x - d, y + d, x + d, y - d, 0.6, INK)
        else:
            self.line(x - d, y + d, x + d, y - d, 0.6, INK)

    def dim_h(self, x1, x2, y, label, size=9.5, ext=None):
        self.line(x1, y, x2, y, 0.55, INK)
        self._tick(x1, y)
        self._tick(x2, y)
        if ext:
            for x in (x1, x2):
                self.line(x, y, x, ext, 0.4, THIN)
        self.text((x1 + x2) / 2, y - 4.5, label, size, INK, "middle")

    def dim_v(self, y1, y2, x, label, size=9.5, ext=None):
        self.line(x, y1, x, y2, 0.55, INK)
        self._tick(x, y1, True)
        self._tick(x, y2, True)
        if ext:
            for y in (y1, y2):
                self.line(x, y, ext, y, 0.4, THIN)
        self.text(x - 4.5, (y1 + y2) / 2, label, size, INK, "middle", rot=-90)


# --------------------------------------------------------------- sheet build
def title_block(s, sheet_no, sheet_name):
    s.text(OX, 24, "HOSPITAL OF DR. AMAN KHANNA", 15, INK, weight="bold", ls=1.2)
    s.text(OX, 39, "7TH FLOOR, SOLARIS SHINE, ALTHAN, SURAT", 9.5, THIN, ls=0.9)
    s.line(OX, 46, A4W - 24, 46, 0.7, INK)
    s.text(OX, 60, sheet_name, 11, INK, weight="bold", ls=0.6)
    s.text(A4W - 24, 24, f"SHEET {sheet_no} OF 3", 9.5, THIN, anchor="end", ls=0.8)
    s.text(A4W - 24, 39, "SCALE  1 cm = 4'-0\"   (≈ 1:122)   A4",
           9.5, INK, anchor="end", ls=0.4)
    s.text(A4W - 24, 60, "PRINT AT 100% / ACTUAL SIZE — do not 'fit to page'",
           9, ACCENT, anchor="end", ls=0.3)


def plate_outline(s, grid=False):
    pts = [P(*p) for p in PLATE]

    # openable glass: west facade + part of the north edge, offset outward
    def offset_seg(a, b, d=4.6):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        n = (dx * dx + dy * dy) ** 0.5
        ox, oy = dy / n * d, -dx / n * d
        return (x1 + ox, y1 + oy, x2 + ox, y2 + oy)

    for i in range(1, 9):                      # SW corner up the west facade
        x1, y1, x2, y2 = offset_seg(pts[i], pts[i + 1])
        s.line(x1, y1, x2, y2, 1.7, GLASS)
    gx1, gy1 = P(29.0, 101.0)
    gx2, gy2 = P(10.0, 101.0)
    s.line(gx1, gy1 + 4.6, gx2, gy2 + 4.6, 1.7, GLASS)

    if grid:
        # 1 cm = 4'-0" grid, clipped to the tapering plate
        for gxf in range(4, 49, 4):
            x = OX + gxf * PPF
            s.line(x, OY, x, OY + _plate_depth_at(gxf) * PPF, 0.35, "#d8dce1")
        for gyf in range(4, 101, 4):
            y = OY + gyf * PPF
            s.line(OX, y, OX + _plate_width_at(gyf) * PPF, y, 0.35, "#d8dce1")

    s.poly(pts, 2.2, INK, fill="none" if grid else "#ffffff")

    # cut-out void
    cpts = [P(*p) for p in CUTOUT]
    s.poly(cpts, 1.2, VOID, fill="#eef0f2")
    cx = (cpts[0][0] + cpts[1][0]) / 2
    cy = cpts[0][1] + 26
    s.text(cx, cy, "CUT-OUT (VOID)", 9.5, INK, "middle", weight="bold")
    s.text(cx, cy + 15, "27'-6\" from east wall", 8.4, INK, "middle")
    s.text(cx, cy + 27, "48'-0\" from south wall", 8.4, INK, "middle")
    s.text(cx, cy + 39, "12'-6\" deep · 16'-2½\" wide", 8.4, INK, "middle")

    # duct / shaft (traced - verify)
    dx, dy = P(DUCT[0], DUCT[1])
    s.rect(dx, dy, DUCT[2] * PPF, DUCT[3] * PPF, 0.9, VOID, fill="#f3f4f6", dash=(4, 3))
    s.text(dx + DUCT[2] * PPF / 2, dy + DUCT[3] * PPF / 2 + 3, "DUCT", 7.6, INK, "middle")

    # main door opening
    my1, my2 = P(0, MD[0])[1], P(0, MD[1])[1]
    s.line(OX, my1, OX, my2, 3.6, "#ffffff")
    s.line(OX - 2.4, my1, OX - 2.4, my2, 1.6, ACCENT)
    s.text(OX + 8, (my1 + my2) / 2 + 3, "MAIN ENTRY  4'-0\"", 8.6, ACCENT)


def _plate_width_at(y_ft):
    ys = sorted(WIDTH_AT)
    for i in range(len(ys) - 1):
        if ys[i] <= y_ft <= ys[i + 1]:
            t = (y_ft - ys[i]) / (ys[i + 1] - ys[i])
            return WIDTH_AT[ys[i]] + t * (WIDTH_AT[ys[i + 1]] - WIDTH_AT[ys[i]])
    return WIDTH_AT[ys[-1]]


def _plate_depth_at(x_ft):
    """How far north the plate reaches at a given x (for grid clipping)."""
    lo, hi = 0.0, 101.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if _plate_width_at(mid) >= x_ft:
            lo = mid
        else:
            hi = mid
    return lo


def dimensions(s):
    x_sw = P(48.5, 0)[0]
    y_n = P(0, 101)[1]
    x_nw = P(29.0, 101.0)[0]

    s.dim_h(OX, x_sw, 82, "48'-6\"", 10.5, ext=OY - 3)
    s.dim_v(OY, y_n, 50, "101'-0\"", 10.5, ext=OX - 3)
    s.dim_h(OX, x_nw, y_n + 20, "29'-0\"", 10, ext=y_n + 3)

    # main-door setting-out on an inner chain
    my1, my2 = P(0, MD[0])[1], P(0, MD[1])[1]
    s.dim_v(OY, my1, 74, "49'-6\"", 8.6)
    s.dim_v(my1, my2, 74, "4'-0\"", 8.0)

    # west-facade stations: tick on the east wall, width called out at the facade
    for st in STATIONS:
        y = P(0, st)[1]
        s.line(OX - 9, y, OX, y, 0.45, THIN)
        s.text(OX - 12, y + 3, fi(st), 8.0, THIN, anchor="end")
        wx = P(_plate_width_at(st), st)[0]
        s.line(wx, y, wx + 7, y, 0.45, THIN)
        s.text(wx + 10, y + 3, fi(_plate_width_at(st)), 8.6, INK)

    s.text(P(36.0, 99.6)[0] + 12, P(0, 99.6)[1], "curved corner", 7.8, THIN)

    # compass
    s.text(x_sw + 12, 86, "SOUTH", 9.5, THIN, weight="bold", ls=1.4)
    s.text(OX + (x_nw - OX) / 2, y_n + 44, "NORTH", 9.5, THIN, "middle",
           weight="bold", ls=1.4)
    s.text(34, OY + 300, "EAST", 9.5, THIN, "middle", rot=-90, weight="bold", ls=1.4)
    s.text(P(48.5, 0)[0] + 92, OY + 250, "WEST — openable glass, views",
           9.5, GLASS, "middle", rot=-90, weight="bold", ls=1.0)


def footer_box(s, extra=None):
    bx, by = 520.0, 946.0
    s.text(bx, by, "SCALE", 8.4, THIN, ls=1.2)
    bar_y = by + 12
    for i in range(4):
        x0 = bx + i * 5 * PPF
        s.rect(x0, bar_y, 5 * PPF, 5.4, 0.5, INK,
               fill=(INK if i % 2 == 0 else "#ffffff"))
    for i in range(0, 5):
        x0 = bx + i * 5 * PPF
        s.text(x0, bar_y + 17, f"{i * 5}", 7.6, INK, "middle")
    s.text(bx + 20 * PPF + 6, bar_y + 17, "ft", 7.6, INK)

    s.line(bx, by + 32, A4W - 24, by + 32, 0.5, THIN)
    s.text(bx, by + 46, "CHECK YOUR PRINT", 8.4, ACCENT, weight="bold", ls=1.0)
    s.text(bx, by + 59, "101'-0\" east wall  =  252.5 mm", 8.6, INK)
    s.text(bx, by + 71, "48'-6\" south wall  =  121.3 mm", 8.6, INK)
    s.text(bx, by + 85, "1'-0\" = 2.5 mm · 5'-0\" corridor = 12.5 mm", 8.0, THIN)
    if extra:
        s.text(bx, by + 99, extra, 8.0, THIN)


def build_outline(grid=False):
    s = Sheet()
    title_block(s, 2 if grid else 1,
                "FLOOR PLATE OUTLINE — 4'-0\" SKETCHING GRID" if grid
                else "FLOOR PLATE OUTLINE — FOR HAND SKETCHING")
    plate_outline(s, grid=grid)
    dimensions(s)
    footer_box(s, "1 square = 4'-0\"" if grid else None)
    return s


# --------------------------------------------------------------- sheet three
SCHEDULE = [
    ("OVERALL ENVELOPE", [
        ("South wall (top of sheet)", "48'-6\""),
        ("East wall — straight, full length", "101'-0\""),
        ("North wall (short, at the curved end)", "29'-0\""),
        ("Carpet area inside the envelope, less the cut-out", "≈ 4,164 sq ft"),
    ]),
    ("WEST FACADE — WIDTH AT EACH STATION", [
        ("at 0'-0\" (south wall)", "48'-6\""),
        ("at 40'-0\" north of the south wall", "44'-6\""),
        ("at 55'-0\"", "43'-0\""),
        ("at 70'-0\"", "41'-6\""),
        ("at 88'-0\"", "39'-6\""),
        ("at 92'-0\"", "38'-9½\""),
        ("at 97'-6\"  (curve begins)", "36'-6\""),
        ("at 100'-2\"", "33'-0\""),
        ("at 101'-0\" (north wall)", "29'-0\""),
    ]),
    ("FIXED CONSTRAINTS — DO NOT BUILD OVER", [
        ("Main entry door, east wall, from the south corner", "49'-6\" to 53'-6\""),
        ("Cut-out (void) — east edge, from the east wall", "27'-6\""),
        ("Cut-out — south edge, from the south wall", "48'-0\""),
        ("Cut-out — size (runs west to the facade)", "16'-2½\" × 12'-6\""),
        ("Duct / shaft on the east wall  (TRACED — VERIFY)", "≈ 59'-2\", 4'-0\" × 4'-2\""),
        ("Openable glass", "whole west facade + north edge"),
        ("Service area (outside the tenancy)", "beyond the south wall"),
    ]),
    ("HANDY CONVERSIONS AT THIS SCALE", [
        ("1'-0\"", "2.5 mm"),
        ("5'-0\" — minimum wheelchair corridor", "12.5 mm"),
        ("10'-0\"", "25 mm"),
        ("Typical single room, 12'-0\" × 9'-0\"", "30 × 22.5 mm"),
        ("Hospital bed, 3'-3\" × 6'-6\"", "8 × 16 mm"),
        ("Operation theatre, 20'-0\" × 17'-0\"", "50 × 42.5 mm"),
    ]),
]

NOTES = [
    "Geometry is traced from the dimensioned floor-plan drawing, not surveyed.",
    "Columns and shear walls are NOT shown — get the structural grid from the",
    "     DWG before you commit partitions.",
    "The north-west corner is curved; it is drawn here as short straight runs.",
    "Keep every patient corridor at least 5'-0\" clear (12.5 mm on this print).",
]


def build_notes():
    s = Sheet()
    title_block(s, 3, "DIMENSIONS, FIXED CONSTRAINTS & SETTING-OUT DATA")
    y = 108.0
    for heading, rows in SCHEDULE:
        s.text(OX, y, heading, 10.5, INK, weight="bold", ls=1.0)
        s.line(OX, y + 6, A4W - 24, y + 6, 0.6, INK)
        y += 22
        for i, (k, v) in enumerate(rows):
            if i % 2 == 0:
                s.rect(OX - 6, y - 11.5, A4W - 24 - OX + 12, 17, 0, "none", fill="#f6f7f8")
            s.text(OX, y, k, 11, INK)
            s.text(A4W - 24, y, v, 11, INK, anchor="end", mono=True)
            y += 17
        y += 16

    s.text(OX, y, "NOTES", 10.5, ACCENT, weight="bold", ls=1.0)
    s.line(OX, y + 6, A4W - 24, y + 6, 0.6, ACCENT)
    y += 22
    for n in NOTES:
        s.text(OX, y, ("—  " if not n.startswith("     ") else "     ") + n.strip(),
               11, INK)
        y += 17
    return s


# ------------------------------------------------------------------ renderers
def to_svg(sheet, px_size=False):
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{"794" if px_size else "210mm"}" '
            f'height="{"1123" if px_size else "297mm"}" '
            f'viewBox="0 0 {A4W:.2f} {A4H:.2f}">')
    out = [head, f'<rect x="0" y="0" width="{A4W:.2f}" height="{A4H:.2f}" fill="#ffffff"/>']
    for cmd in sheet.c:
        k = cmd[0]
        if k == "line":
            _, x1, y1, x2, y2, w, col, dash = cmd
            d = f' stroke-dasharray="{dash[0]} {dash[1]}"' if dash else ""
            out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                       f'stroke="{col}" stroke-width="{w}" stroke-linecap="butt"{d}/>')
        elif k == "poly":
            _, pts, w, col, fill, dash, close = cmd
            p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
            d = f' stroke-dasharray="{dash[0]} {dash[1]}"' if dash else ""
            tag = "polygon" if close else "polyline"
            sw = f' stroke="{col}" stroke-width="{w}"' if w else ' stroke="none"'
            out.append(f'<{tag} points="{p}" fill="{fill}"{sw} stroke-linejoin="miter"{d}/>')
        elif k == "text":
            _, x, y, txt, size, col, anchor, rot, weight, mono, ls = cmd
            fam = ("ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" if mono
                   else "Helvetica Neue, Helvetica, Arial, sans-serif")
            tr = f' transform="rotate({rot} {x:.2f} {y:.2f})"' if rot else ""
            lsp = f' letter-spacing="{ls}"' if ls else ""
            esc = (txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            out.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" '
                       f'font-size="{size}" fill="{col}" text-anchor="{anchor}" '
                       f'font-weight="{weight}"{lsp}{tr}>{esc}</text>')
    out.append("</svg>")
    return "\n".join(out)


def to_pdf_pages(sheets, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.patches import Polygon as MplPoly, Rectangle

    PT = 0.75                                   # 1 css px -> 0.75 pt at 96 dpi
    with PdfPages(path) as pdf:
        for sheet in sheets:
            fig = plt.figure(figsize=(A4W / 96.0, A4H / 96.0))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, A4W)
            ax.set_ylim(A4H, 0)
            ax.axis("off")
            ax.add_patch(Rectangle((0, 0), A4W, A4H, fc="white", ec="none"))
            for cmd in sheet.c:
                k = cmd[0]
                if k == "line":
                    _, x1, y1, x2, y2, w, col, dash = cmd
                    kw = {}
                    if dash:
                        kw["dashes"] = [dash[0] * PT, dash[1] * PT]
                    ax.plot([x1, x2], [y1, y2], color=col, lw=w * PT,
                            solid_capstyle="butt", **kw)
                elif k == "poly":
                    _, pts, w, col, fill, dash, close = cmd
                    ax.add_patch(MplPoly(pts, closed=close,
                                         fc=(fill if fill != "none" else "none"),
                                         ec=(col if w else "none"),
                                         lw=w * PT, joinstyle="miter"))
                elif k == "text":
                    _, x, y, txt, size, col, anchor, rot, weight, mono, ls = cmd
                    ha = {"start": "left", "middle": "center", "end": "right"}[anchor]
                    ax.text(x, y, txt, fontsize=size * PT, color=col, ha=ha,
                            va="baseline", rotation=-rot, rotation_mode="anchor",
                            fontweight=weight,
                            family=("monospace" if mono else "sans-serif"))
            pdf.savefig(fig)
            plt.close(fig)


DC_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
  <style>
    body {{ margin: 0; background: #ffffff; }}
    a {{ color: #b45309; }} a:hover {{ color: #92400e; }}
  </style>
</helmet>
<div style="width: 794px; height: 1123px; background: #ffffff; overflow: hidden;">
{svg}
</div>
</x-dc>
</body>
</html>
"""


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    deliv = os.path.join(here, "..", "deliverables")
    canvas = os.path.join(here, "..", "canvas")
    os.makedirs(deliv, exist_ok=True)
    os.makedirs(canvas, exist_ok=True)

    sheets = [("Main", build_outline(False)),
              ("SketchGrid", build_outline(True)),
              ("Dimensions", build_notes())]

    to_pdf_pages([s for _, s in sheets],
                 os.path.join(deliv, "A4_floor_plate_outline.pdf"))
    print("PDF  A4_floor_plate_outline.pdf  (3 pages, true A4 vector)")

    for name, s in sheets:
        with open(os.path.join(deliv, f"A4_outline_{name}.svg"), "w") as f:
            f.write(to_svg(s))
        with open(os.path.join(canvas, f"{name}.dc.html"), "w") as f:
            f.write(DC_TEMPLATE.format(svg=to_svg(s, px_size=True)))
        print(f"     {name}.dc.html + A4_outline_{name}.svg")

    with open(os.path.join(canvas, "canvas.json"), "w") as f:
        f.write("""{
  "artboards": [
    { "file": "Main.dc.html", "x": 0, "y": 0, "w": 794, "h": 1123, "print": "fixed", "title": "1 \\u2014 Outline" },
    { "file": "SketchGrid.dc.html", "x": 894, "y": 0, "w": 794, "h": 1123, "print": "fixed", "title": "2 \\u2014 Outline + 4 ft grid" },
    { "file": "Dimensions.dc.html", "x": 1788, "y": 0, "w": 794, "h": 1123, "print": "fixed", "title": "3 \\u2014 Dimensions & constraints" }
  ],
  "launch": { "view": "focused", "file": "Main.dc.html" }
}
""")
    print("     canvas.json")


if __name__ == "__main__":
    main()
