"""TRACING SHEET at true 1:100 — the envelope fills the A4 page.

1:100 means 1 cm on paper = 1 m real; 1 ft = 3.048 mm on paper.
Plate 48'-6" x 92'-0" prints 147.8 x 280.4 mm — a near-full A4 portrait.
Geometry: Revision C — the Rev B envelope, confirmed against the builder's
CAD PDF (19'-6.5" + 19'-6.5" + 8'-0" passage + 43'-9.5" + walls = 92'-0";
clinic x07 46'-3" + east band = 48'-6").
"""
import os
from outline_sheet import (Sheet, to_pdf_pages, PLATE, CUTOUT, MD, DUCT,
                           WIDTH_AT, _plate_width_at, _plate_depth_at, fi,
                           INK, THIN, GLASS, VOID, ACCENT, A4W, A4H)

PPF = 96.0 / 25.4 * 3.048          # 11.5200 px per foot at 1:100
OXm, OYm = 36.0, 30.2              # left/top margins in px (9.5 mm / 8 mm)


def P(x, y):
    return (OXm + x * PPF, OYm + y * PPF)


def _glass(s):
    pts = [P(*p) for p in PLATE]
    def off(a, b, d=4.0):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        n = (dx * dx + dy * dy) ** 0.5
        return (x1 + dy / n * d, y1 - dx / n * d, x2 + dy / n * d, y2 - dx / n * d)
    for i in range(1, len(PLATE) - 2):
        x1, y1, x2, y2 = off(pts[i], pts[i + 1])
        s.line(x1, y1, x2, y2, 1.5, GLASS)
    g1, g2 = P(31.0, 92.0), P(8.0, 92.0)
    s.line(g1[0], g1[1] + 4.0, g2[0], g2[1] + 4.0, 1.5, GLASS)


def build_trace(grid=False):
    s = Sheet()
    right = OXm + 48.5 * PPF          # plate right edge on sheet

    if grid:
        for gx in range(5, 49, 5):
            x = OXm + gx * PPF
            s.line(x, OYm, x, OYm + _plate_depth_at(gx) * PPF, 0.35, "#d8dce1")
        for gy in range(5, 92, 5):
            y = OYm + gy * PPF
            s.line(OXm, y, OXm + _plate_width_at(gy) * PPF, y, 0.35, "#d8dce1")

    pts = [P(*p) for p in PLATE]
    s.poly(pts, 2.6, INK, fill="none")
    _glass(s)

    cpts = [P(*p) for p in CUTOUT]
    s.poly(cpts, 1.1, VOID, fill="#f0f1f3")
    cx = (cpts[0][0] + cpts[1][0]) / 2
    s.text(cx, cpts[0][1] + 22, "CUT-OUT / SERVICE", 8.6, INK, "middle", weight="bold")
    s.text(cx, cpts[0][1] + 34, "≈18'-4\" × 8'-0\"", 7.6, INK, "middle")

    dx, dy = P(DUCT[0], DUCT[1])
    s.rect(dx, dy, DUCT[2] * PPF, DUCT[3] * PPF, 0.9, VOID, fill="#f0f1f3", dash=(4, 3))
    s.text(dx + DUCT[2] * PPF / 2, dy + DUCT[3] * PPF / 2 + 3, "DUCT", 7.4, INK, "middle")

    my1, my2 = P(0, MD[0])[1], P(0, MD[1])[1]
    s.line(OXm, my1, OXm, my2, 4.2, "#ffffff")
    s.line(OXm - 2.6, my1, OXm - 2.6, my2, 1.8, ACCENT)
    s.text(OXm + 7, (my1 + my2) / 2 + 3, "ENTRY 5'-0\"", 8.2, ACCENT)
    s.text(OXm + 7, (my1 + my2) / 2 + 14, "43'-0\" from S corner", 7.0, ACCENT)

    # dimension chains, kept inside the margins
    s.dim_h(OXm, right, OYm - 9, "48'-6\"", 9.5)
    s.dim_v(OYm, OYm + 92 * PPF, OXm - 10, "92'-0\"", 9.5)
    for st in (20.0, 40.0, 60.0, 80.0):
        y = P(0, st)[1]
        s.line(OXm - 6, y, OXm, y, 0.45, THIN)
        s.text(OXm - 8, y + 3, fi(st), 6.8, THIN, anchor="end")
        wx = P(_plate_width_at(st), st)[0]
        s.line(wx, y, wx + 5, y, 0.45, THIN)
        s.text(wx + 7, y + 3, fi(_plate_width_at(st)), 7.4, INK)

    # right-margin column: title, scale, checks (read bottom-to-top)
    tx = right + 24
    by = OYm + 92 * PPF - 2
    s.text(tx, by, "HOSPITAL OF DR. AMAN KHANNA — 7TH FLR, SOLARIS SHINE, SURAT",
           9.5, INK, weight="bold", rot=-90)
    s.text(tx + 15, by, "TRACING SHEET — SCALE 1:100  (1 cm = 1 m)", 9.5,
           INK, weight="bold", rot=-90)
    s.text(tx + 29, by, "1'-0\" = 3.05 mm · 5'-0\" = 15.2 mm · 10'-0\" = 30.5 mm"
           " · OT 20'×17' = 61×52 mm", 7.8, INK, rot=-90)
    s.text(tx + 42, by, "CHECK PRINT: east wall 92'-0\" = 280.4 mm · south wall"
           " 48'-6\" = 147.8 mm", 7.8, ACCENT, rot=-90)
    s.text(tx + 55, by, "REV C — envelope confirmed against the builder's CAD "
           "plan (typical floor 3-7)", 7.2, THIN, rot=-90)
    if grid:
        s.text(tx + 68, by, "GRID: 1 square = 5'-0\" (one corridor width)",
               7.8, INK, rot=-90)
    s.text(OXm, OYm + 92 * PPF + 14, "NORTH ↓   (glass on this edge and the "
           "long right-hand edge = WEST, views)", 7.6, THIN)
    s.text(OXm, OYm - 20, "SOUTH ↑  service strip beyond this wall", 7.6, THIN)
    return s


def main():
    deliv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "deliverables")
    pages = [build_trace(False), build_trace(True)]
    to_pdf_pages(pages, os.path.join(deliv, "A4_tracing_sheet_1to100.pdf"))
    print("A4_tracing_sheet_1to100.pdf  (2 pages, true A4 vector, 1:100)")


if __name__ == "__main__":
    main()
