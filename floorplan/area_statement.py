"""FLOOR SPACE CALCULATION — Layout E rev 3 on the Rev C envelope.

Computed from the actual geometry (shapely), not hand totals:
gross plate, cut-out deduction, net carpet, per-zone and per-room areas,
wall area, circulation area (the remainder), efficiency ratios, and a
reconciliation against the builder's published carpet areas.
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.ops import unary_union
from plan_model import PLATE, CUTOUT, LAYOUTS, ZONES, wall_bands
from outline_sheet import Sheet, to_pdf_pages, title_block, INK, THIN, ACCENT, A4W

OX = 92.0


def compute():
    rooms = [r for r in LAYOUTS["E"][1]()]
    solids = [r for r in rooms if r.zone != "circ"]
    cut = CUTOUT.intersection(PLATE)
    gross = PLATE.area
    net = gross - cut.area
    room_union = unary_union([r.poly for r in solids])
    walls = wall_bands(rooms).intersection(PLATE).difference(cut)
    wall_area = walls.area
    rooms_area = room_union.area
    circ = net - rooms_area - wall_area

    by_zone = defaultdict(list)
    for r in solids:
        by_zone[r.zone].append(r)

    return dict(gross=gross, cut=cut.area, net=net, rooms=rooms_area,
                walls=wall_area, circ=circ, by_zone=by_zone, solids=solids)


def build_pages(d):
    s = Sheet()
    title_block(s, 1, "FLOOR SPACE CALCULATION — computed from plan geometry",
                scale_text="LAYOUT E rev 3 — AREAS IN SQ FT", total=2)
    y = 98
    s.text(OX, y, "A. ENVELOPE", 10.5, INK, weight="bold", ls=1.0)
    s.line(OX, y + 5, A4W - 24, y + 5, 0.7, INK)
    y += 20
    for k, v in [("Gross plate (48'-6\" × 92'-0\", tapered west facade)", d["gross"]),
                 ("Less: cut-out / service void", -d["cut"]),
                 ("NET CARPET AREA", d["net"])]:
        w = "bold" if k.isupper() else "normal"
        s.text(OX, y, k, 10, INK, weight=w)
        s.text(A4W - 24, y, f"{v:,.0f} sf", 10, INK, anchor="end", mono=True, weight=w)
        y += 17
    y += 10
    s.text(OX, y, "B. BY ZONE", 10.5, INK, weight="bold", ls=1.0)
    s.line(OX, y + 5, A4W - 24, y + 5, 0.7, INK)
    y += 20
    zone_names = {"surgical": "Surgical (OT pod + recovery)",
                  "consult": "Consult / OPD + lounge + emergency",
                  "public": "Public (waiting + pharmacy)",
                  "inpatient": "Inpatient (rooms, suite, nursing)",
                  "support": "Support (stores, pantry, autoclave)",
                  "wet": "Toilets / wet areas"}
    ztot = 0.0
    for z in ("surgical", "consult", "public", "inpatient", "support", "wet"):
        rs = d["by_zone"].get(z, [])
        a = sum(r.area for r in rs)
        ztot += a
        s.text(OX, y, f"{zone_names[z]}  ({len(rs)} rooms)", 10, INK)
        s.text(A4W - 200, y, f"{100 * a / d['net']:.1f}%", 9.5, THIN, anchor="end", mono=True)
        s.text(A4W - 24, y, f"{a:,.0f} sf", 10, INK, anchor="end", mono=True)
        y += 16.4
    for k, v, pct in [("All rooms", d["rooms"], 100 * d["rooms"] / d["net"]),
                      ("Partition walls", d["walls"], 100 * d["walls"] / d["net"]),
                      ("Circulation (corridors, lobbies)", d["circ"], 100 * d["circ"] / d["net"])]:
        s.text(OX, y, k, 10, INK, weight="bold")
        s.text(A4W - 200, y, f"{pct:.1f}%", 9.5, THIN, anchor="end", mono=True)
        s.text(A4W - 24, y, f"{v:,.0f} sf", 10, INK, anchor="end", mono=True, weight="bold")
        y += 17
    y += 10
    s.text(OX, y, "C. PLANNING RATIOS", 10.5, INK, weight="bold", ls=1.0)
    s.line(OX, y + 5, A4W - 24, y + 5, 0.7, INK)
    y += 20
    beds = 6  # 4 rooms + suite + obs
    for k, v in [
        ("Usable efficiency (rooms ÷ net)", f"{100 * d['rooms'] / d['net']:.0f}%  (60-70% is healthy)"),
        ("Circulation share", f"{100 * d['circ'] / d['net']:.0f}%  (25-32% typical for a hospital)"),
        ("Area per inpatient bed (net ÷ 6 beds)", f"{d['net'] / beds:,.0f} sf/bed"),
        ("Waiting provision", "216 sf + overflow = 22 seats for 4 OPDs"),
        ("OT suite share (surgical zone)", f"{sum(r.area for r in d['by_zone']['surgical']):,.0f} sf"),
    ]:
        s.text(OX, y, k, 10, INK)
        s.text(A4W - 24, y, v, 9.6, INK, anchor="end", mono=True)
        y += 17
    y += 10
    s.text(OX, y, "D. RECONCILIATION WITH THE BUILDER'S FIGURES", 10.5, ACCENT, weight="bold", ls=0.6)
    s.line(OX, y + 5, A4W - 24, y + 5, 0.7, ACCENT)
    y += 20
    for line in [
        "Builder's published carpet areas: clinic x05 = 1,639 + x06 = 684 + x07 = 903",
        "   = 3,226 sf (C.A. of the three clinics, excluding their toilets and the",
        "   8'-0\" passage strip absorbed into the combined unit).",
        f"This plan's computed net = {d['net']:,.0f} sf — the difference (~{d['net'] - 3226:,.0f} sf)",
        "   is the toilets + passage + service strips included in the merged demise.",
        "Final chargeable/RERA area to be confirmed from the builder's agreement.",
    ]:
        s.text(OX, y, line, 9.6, INK)
        y += 15.5

    # page 2: per-room table
    s2 = Sheet()
    title_block(s2, 2, "ROOM-BY-ROOM AREA SCHEDULE",
                scale_text="LAYOUT E rev 3 — AREAS IN SQ FT", total=2)
    y = 96
    for htxt, hx in [("ROOM", 0), ("ZONE", 300), ("SIZE", 420), ("AREA", 655)]:
        s2.text(OX + hx, y, htxt, 8.6, THIN, weight="bold")
    s2.line(OX, y + 5, A4W - 24, y + 5, 0.7, INK)
    y += 18
    rows = sorted(d["solids"], key=lambda r: -r.area)
    for i, r in enumerate(rows):
        if i % 2 == 0:
            s2.rect(OX - 5, y - 10.5, A4W - 24 - OX + 10, 15.6, 0, "none", fill="#f4f5f6")
        s2.text(OX, y, r.name.title()[:36], 8.8, INK)
        s2.text(OX + 300, y, r.zone, 8.4, THIN)
        s2.text(OX + 420, y, r.dims.split("(")[0].strip()[:24], 8.4, INK, mono=True)
        s2.text(OX + 655, y, f"{r.area:,.0f}", 8.8, INK, mono=True)
        y += 15.6
    y += 6
    s2.line(OX, y - 4, A4W - 24, y - 4, 0.7, INK)
    s2.text(OX, y + 8, "TOTAL ROOM AREA", 9.5, INK, weight="bold")
    s2.text(OX + 655, y + 8, f"{d['rooms']:,.0f}", 9.5, INK, anchor="end", mono=True, weight="bold")
    return [s, s2]


def main():
    d = compute()
    deliv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "deliverables")
    to_pdf_pages(build_pages(d), os.path.join(deliv, "floor_space_calculation.pdf"))
    print("floor_space_calculation.pdf (2 pages)")
    print(f"gross {d['gross']:,.0f} | cutout {d['cut']:,.0f} | net {d['net']:,.0f} | "
          f"rooms {d['rooms']:,.0f} ({100*d['rooms']/d['net']:.0f}%) | walls {d['walls']:,.0f} | "
          f"circ {d['circ']:,.0f} ({100*d['circ']/d['net']:.0f}%)")


if __name__ == "__main__":
    main()
