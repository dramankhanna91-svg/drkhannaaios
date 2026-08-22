"""CONTRACTOR SETTING-OUT PACKAGE (A4 PDF) for Layout E rev 2.

Datums: X = inner face of the EAST wall (the straight 92'-0" wall);
        Y = inner face of the SOUTH wall (the 48'-6" wall).
Every partition is located by the room's X, Y, W, D in feet-inches from
those two datums. Plus door schedule and construction notes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outline_sheet import Sheet, to_pdf_pages, title_block, fi, INK, THIN, ACCENT, A4W
from plan_model import LAYOUTS

OX = 92.0


def _door_tag(w):
    return "D1" if w >= 2.75 else ("D2" if w >= 2.25 else "D3")


def build_pages():
    rooms = [r for r in LAYOUTS["E"][1]() if r.zone != "circ" and r.name]
    rooms.sort(key=lambda r: (r.rect[1], r.rect[0]))

    pages = []

    # ---------- pages 1-2: setting-out schedule
    def new_sheet(no, name, total):
        s = Sheet()
        title_block(s, no, name, scale_text="LAYOUT E rev 2 — UNITS: FEET-INCHES", total=total)
        return s

    header = [("ROOM", 0), ("X from EAST wall", 250), ("Y from SOUTH wall", 385),
              ("WIDTH", 520), ("DEPTH", 600), ("AREA", 655)]
    rows_per_page = 34
    chunks = [rooms[i:i + rows_per_page] for i in range(0, len(rooms), rows_per_page)]
    total_pages = len(chunks) + 1
    for pi, chunk in enumerate(chunks):
        s = new_sheet(pi + 1, "SETTING-OUT SCHEDULE — partitions from the two datum walls",
                      total_pages)
        y = 96
        s.text(OX, y, "Datum X = inner face of EAST wall · Datum Y = inner face of SOUTH wall"
               " · dimensions to the room's near corner (SE)", 8.6, ACCENT)
        y += 20
        for htxt, hx in header:
            s.text(OX + hx, y, htxt, 8.6, THIN, weight="bold")
        s.line(OX, y + 5, A4W - 24, y + 5, 0.7, INK)
        y += 19
        for i, r in enumerate(chunk):
            x0, y0, w, h = r.rect
            if i % 2 == 0:
                s.rect(OX - 5, y - 11, A4W - 24 - OX + 10, 16.4, 0, "none", fill="#f4f5f6")
            nm = r.name.title()[:34]
            s.text(OX, y, nm, 9.2, INK)
            s.text(OX + 250, y, fi(x0), 9.2, INK, mono=True)
            s.text(OX + 385, y, fi(y0), 9.2, INK, mono=True)
            s.text(OX + 520, y, fi(w), 9.2, INK, mono=True)
            s.text(OX + 600, y, fi(h), 9.2, INK, mono=True)
            s.text(OX + 655, y, f"{r.area:.0f} sf", 9.2, INK, mono=True)
            y += 16.4
        pages.append(s)

    # ---------- final page: door schedule + notes
    s = new_sheet(total_pages, "DOOR SCHEDULE & CONSTRUCTION NOTES", total_pages)
    y = 100
    s.text(OX, y, "DOOR SCHEDULE", 10.5, INK, weight="bold", ls=1.0)
    s.line(OX, y + 5, A4W - 24, y + 5, 0.7, INK)
    y += 20
    doors = []
    for r in rooms:
        for (cx, cy, w, wall) in r.doors:
            doors.append((r.name.title(), w, _door_tag(w), cx, cy))
    from collections import Counter
    counts = Counter(_door_tag(w) for _, w, _, _, _ in doors)
    for htxt, hx in [("ROOM", 0), ("TAG", 250), ("CLEAR WIDTH", 320),
                     ("X", 470), ("Y", 560)]:
        s.text(OX + hx, y, htxt, 8.6, THIN, weight="bold")
    y += 16
    for i, (nm, w, tag, cx, cy) in enumerate(doors):
        if i % 2 == 0:
            s.rect(OX - 5, y - 10, A4W - 24 - OX + 10, 14.6, 0, "none", fill="#f4f5f6")
        s.text(OX, y, nm[:32], 8.4, INK)
        s.text(OX + 250, y, tag, 8.4, INK, mono=True)
        s.text(OX + 320, y, fi(w), 8.4, INK, mono=True)
        s.text(OX + 470, y, fi(cx), 8.4, INK, mono=True)
        s.text(OX + 560, y, fi(cy), 8.4, INK, mono=True)
        y += 14.6
    y += 8
    _desc = {"D1": "≥2'-9\"", "D2": "≥2'-3\"", "D3": "<2'-3\""}
    tot_txt = "   ".join("%s (%s) × %d" % (t, _desc[t], n)
                         for t, n in sorted(counts.items()))
    s.text(OX, y, "Totals:  " + tot_txt, 8.8, INK)
    y += 24
    s.text(OX, y, "CONSTRUCTION NOTES", 10.5, ACCENT, weight="bold", ls=1.0)
    s.line(OX, y + 5, A4W - 24, y + 5, 0.7, ACCENT)
    y += 18
    for n in [
        "Partitions 100 mm AAC block / 75 mm gypsum metal-stud, as specified by the architect.",
        "OT + Recovery: seamless vinyl flooring with coved skirting; OT walls washable to ceiling;",
        "     positive-pressure AHU for OT, exhaust for toilets. Medical gas: O2 + vacuum to OT,",
        "     Recovery, Obs bed and all 5 rooms; manifold in Stores.",
        "OT suite: patients enter ONLY through Recovery; staff through Scrub. No other opening.",
        "X-ray room: provide AERB lead lining to lobby-side wall if radiography is installed.",
        "Wet areas (all ensuite T, Wash+Bath, pantry) on ganged plumbing near the east duct.",
        "Visitor WC: common-area toilets outside the main entry (builder's provision).",
        "All patient corridors min. 5'-0\" clear. Verify column/shear-wall positions and the",
        "     cut-out slab on site BEFORE marking partitions. All dims to be site-verified.",
        "Reference drawings: layout_E_final.dxf (feet units) overlays the builder's typical plan.",
    ]:
        s.text(OX, y, ("—  " if not n.startswith("     ") else "     ") + n.strip(), 9.4, INK)
        y += 15.5
    pages.append(s)
    return pages


def main():
    deliv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "deliverables")
    pages = build_pages()
    to_pdf_pages(pages, os.path.join(deliv, "contractor_setting_out.pdf"))
    print(f"contractor_setting_out.pdf ({len(pages)} pages)")


if __name__ == "__main__":
    main()
