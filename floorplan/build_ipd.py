"""IPD fix (17-11-2026): rebuild Layouts G and H with true-size ward furniture,
measured clear sizes and JPG sheets, and write deliverables/IPD_COMPARISON.md.

    cd floorplan && python3 build_ipd.py

Outputs (../deliverables):
  layout_G_detailed.png/.svg/.jpg/.dxf, layout_G_blueprint.svg, layout_G_clean.svg, 3d_layout_G.png
  layout_H_* (through build_h.main()), ipd_G.jpg, ipd_H.jpg, IPD_COMPARISON.md
"""
import os
from itertools import combinations

from shapely.geometry import LineString, box
from shapely.ops import unary_union

import plan_model  # noqa: F401  (registers G and H)
import layout_g as G
import layout_h as H
import build_h
import ipd
from ipd import fi

OUT = build_h.OUT
G_IPD = ["room1", "room2", "room3", "room4", "suite"]
G_WC = {"room1": "wcR1", "room2": "wcR2", "room3": "wcR3", "room4": "wcR4", "suite": "bath5"}
H_IPD = ["twin1", "twin2", "twin3", "twin4"]
H_WC = {"twin1": "wcW1", "twin2": "wcW2", "twin3": "wcW3", "twin4": "wcN4"}


def _rows(rooms, keys, wcmap, pts):
    by = {r.key: r for r in rooms}
    out = []
    for k in keys:
        r = by[k]
        (wx, wy), (dx, dy) = pts[k]
        a, b = ipd.span(r.poly, wx, wy, "x")
        c, d = ipd.span(r.poly, dx, dy, "y")
        beds = sum(1 for f in r.furniture if f[0] == "bed")
        t = by[wcmap[k]]
        tw, td, ta = ipd.toilet_size(t.poly)
        gross = r.area + t.area
        out.append(dict(key=k, name=r.name.title().replace("Room 5", "Room 5"), w=b - a, d=d - c,
                        area=r.area, beds=beds, tw=tw, td=td, ta=ta, gross=gross))
    return out


def g_checks(rooms):
    walls = G.wall_bands_g(rooms)
    glass = unary_union([LineString(s) for s in G.GLASS_WEST_G + G.GLASS_NORTH_G]).buffer(0.9)
    sub = [r for r in rooms if r.key in G_IPD or r.key in G_WC.values()]
    issues, nb, nh = ipd.audit(sub, walls, glass)
    c = G.checks()
    # door leaves must not sweep over furniture in the IPD rooms
    for r in sub:
        fb = [box(x, y, x + w, y + h) for (_, x, y, w, h, _) in r.furniture]
        for d in r.gdoors:
            if d["kind"] != "single" or r.zone == "wet":
                continue
            w, sgn = d["w"], d["swing"]
            hy = d["cy"] - w / 2 if d["hinge"] == "lo" else d["cy"] + w / 2
            from shapely.geometry import Point
            disc = Point(d["cx"] + 0.19 * sgn, hy).buffer(w)
            quad = box(d["cx"], d["cy"] - w / 2, d["cx"] + sgn * (w + 0.4), d["cy"] + w / 2)
            sweep = disc.intersection(quad)
            for b in fb:
                if sweep.intersection(b).area > 0.05:
                    issues.append(f"{r.key}: door leaf sweeps over furniture")
    return issues, nb, nh, c


def comparison_md(g_rows, h_rows, g_issues, h_checks, dxf_g, dxf_h):
    A = ipd.ARCHITECT
    L = []
    L.append("# IPD wing: architect's plan vs Layout G vs Layout H\n")
    L.append("Solaris Shine, 7th floor · 17-11-2026 · machine-written by `floorplan/build_ipd.py`\n")
    L.append("Sheets: `layout_G_detailed.jpg`, `layout_H_detailed.jpg` (full sheets), `ipd_G.jpg`, "
             "`ipd_H.jpg` (ward close-ups with the dimension strings).\n")
    L.append("## 1. Why the old sheets looked cramped\n")
    L.append("| Item | Real size | Layout G before | Layout H before | Now (G and H) |\n|---|---|---|---|---|")
    L.append("| Hospital bed | 3'-3\" x 7'-0\" | 3'-4\" x 6'-10\" | 3'-3\" x 6'-7\" (5\" short) | 3'-3\" x 7'-0\" |")
    L.append("| Bedside locker | 1'-6\" x 1'-6\" | 1'-5\" x 1'-6\" | 1'-2\" x 1'-5\" | 1'-6\" x 1'-6\" |")
    L.append("| Wardrobe | 2'-0\" x 4'-0\" | 2'-0\" x 3'-7\" to 4'-7\" | 1'-5\" to 1'-7\" deep x 4'-0\" | 2'-0\" x 4'-0\" (G Room 4: 2'-0\" x 2'-6\") |")
    L.append("| Attendant seat | sofa-bed 2'-0\" x 5'-6\" | sofa 2'-4\" x 4'-5\" to 5'-5\" | 1'-6\" chairs in the west twins (a sofa only in the east twin) | sofa 2'-0\" x 5'-6\" (G Room 4: 5'-0\") |")
    L.append("| Ward toilet | 5'-0\" x 6'-0\" min | up to 9'-0\" x 5'-5\", across the window | 5'-5\" x 5'-3\" to 7'-3\" x 6'-1\" | see section 3 |")
    L.append("| Room door | 3'-6\" | 3'-6\" | 3'-6\" to 3'-9\" | G 3'-6\", H 3'-9\" |")
    L.append("| Partitions | 4½\" | 4½\" (drawn true) | 4½\" (drawn true) | unchanged |\n")
    L.append("- **Envelope was already right.** Wall faces re-read from `floorplan/source/solaris_typical_5_7_10.dxf` "
             "(layer DR - PLASTER LINE): unit x05 is 13,210 mm = 43'-4\" clear south to north (Y -221141 to -234351) and "
             "about 12,250 mm = 40'-2\" clear east to west at its south wall (X 6002250 to the inner facade line extended, about 6014498), tapering to 10,512 mm = 34'-6\" "
             "at the start of the rounded corner. Both models already used these faces; no room was drawn larger than the building.\n"
             "- **Layout H** fitted five twin rooms (10 beds) only because the symbols were under-size. At true size two beds "
             "and two lockers need 9'-6\" of head wall; the two northern rooms had about 11'-6\" and 10'-10\" between the "
             "toilet wall and the facade column, so nothing was left for a 2' wardrobe plus a 2' attendant sofa, and the "
             "foot aisle of the 10'-0\" to 10'-4\" deep rooms was 3'-0\" to 3'-4\".\n"
             "- **Layout G** furniture was close to true size; the rooms read as cramped because each 9'-0\" long toilet "
             "stood across the window and left an L-shaped room, and because the label (name, an \"≈ average\" size and area "
             "on a white box) sat on top of the bed. The printed \"≈19'-2\" x 10'-5\" incl. toilet\" was an average width, "
             "not a measurable clear size.\n"
             "- **The architect's rooms are not larger.** His four west rooms are 9'-0\" to 10'-1½\" deep as printed; ours are 10'-3\" deep "
             "or more. They look roomy because the twin-room toilets are in a separate 5' band, the rooms are plain "
             "rectangles and the label is small and clear of the furniture.\n")
    L.append("## 2. What changed\n")
    L.append("- **Layout H:** the west side is now three twin rooms 13'-7\" to 15'-0\" deep instead of four at 10'-0\" to 11'-6\"; "
             "with Twin 4 on the east side that is **8 beds, not 10** (architect, per the Layout H brief: 9 beds in 7 rooms; 6 of them in his four "
             "west rooms). Every twin has two true-size beds with 3'-0\" to 3'-6\" between them, two lockers, a 2' x 4' "
             "wardrobe and an attendant sofa. Three ensuites are 6'-0\" x 7'-0\" wheelchair size; ensuites of Twin 1 and 2 are "
             "back to back. Ward passage stays 6'-6\".\n"
             "- **Layout G:** the clients' four single rooms and the suite keep their positions and sizes. The paired toilets stay "
             "back to back at the glass but are 5'-0\" deep and 6'-0\" to 6'-9\" long instead of 5'-5\" x 9'-0\", and sit on the "
             "bed-head side, so the foot side of each room runs clear to the window. The suite bath is enlarged to "
             "7'-0\" x 6'-0\" (wheelchair size, 5'-0\" turning circle); Store and Duty room are 7\" shallower and the Pantry is 14\" narrower and 7\" deeper for it. "
             "Room 3's door moves to the south end of its passage wall.\n"
             "- **Both sheets:** every IPD label gives the clear size (E-W x N-S) and the area net of the toilet, placed on clear "
             "floor; blue dimension strings run wall face to wall face in every ward room; toilets carry their clear size.\n")
    L.append("## 3. Room by room\n")
    L.append("Sizes are clear, plaster face to plaster face, E-W x N-S, read on the blue strings (E-W is taken at the string, "
             "the west wall is the sloping facade). Area is the clear floor net of the toilet and of columns.\n")
    L.append("| Plan | Room | Clear size | Area sf | Beds | Area per bed sf | Toilet (clear) |\n|---|---|---|---:|---:|---:|---|")
    for (nm, w, d, beds, t) in A:
        incl = " incl. its toilet" if beds == 1 else ""
        L.append(f"| Architect | {nm} | {fi(w)} x {fi(d)}{incl} | {w * d:.0f} | {beds} | {w * d / beds:.0f} | {t} |")
    for tag, rows in (("G", g_rows), ("H", h_rows)):
        for r in rows:
            L.append(f"| Layout {tag} | {r['name']} | {fi(r['w'])} x {fi(r['d'])} | {r['area']:.0f} | {r['beds']} | "
                     f"{r['area'] / r['beds']:.0f} | {fi(r['tw'])} x {fi(r['td'])} ({r['ta']:.0f} sf) |")
    a_tw = sum(w * d for (_, w, d, b, _) in A if b == 2)
    a_all = sum(w * d for (_, w, d, b, _) in A)
    a_beds = sum(b for (_, _, _, b, _) in A)
    g_all, g_beds = sum(r["area"] for r in g_rows), sum(r["beds"] for r in g_rows)
    h_all, h_beds = sum(r["area"] for r in h_rows), sum(r["beds"] for r in h_rows)
    L.append("")
    L.append("| Per-bed floor area | Architect | Layout G | Layout H |\n|---|---:|---:|---:|")
    L.append(f"| Twin rooms, sf per bed | {a_tw / 4:.0f} (98 and 82) | no twin rooms | {h_all / h_beds:.0f} "
             f"({', '.join(str(round(r['area'] / r['beds'])) for r in h_rows)}) |")
    sg = [r for r in g_rows]
    L.append(f"| Single rooms, sf per bed | 144 and 148 as printed, toilet included (about 114 and 118 net of a 6' x 5' toilet) | "
             f"{', '.join(str(round(r['area'])) for r in sg)} net of toilet | no single rooms |")
    L.append(f"| All rooms listed | {a_all:.0f} sf / {a_beds} beds = {a_all / a_beds:.0f} | {g_all:.0f} sf / {g_beds} beds = "
             f"{g_all / g_beds:.0f} | {h_all:.0f} sf / {h_beds} beds = {h_all / h_beds:.0f} |")
    L.append("\nThe architect's figures are the sizes printed on his drawing multiplied out; they were not re-measured. His single-room "
             "sizes span the toilet (judged from the drawing: the 16'-0\" of Single room-4 runs from the passage wall to the facade), "
             "his twin-room sizes do not.\n")
    L.append("## 4. Where a room is narrower or smaller than the architect's equivalent\n")
    L.append("| Room | Architect size | Ours | Difference |\n|---|---|---|---|")
    pairs = [("G Room 1 (single) vs Twin sharing room-1", A[0], g_rows[0]),
             ("G Room 2 (single) vs Twin sharing room-2", A[1], g_rows[1]),
             ("G Room 3 (single) vs Single room-4", A[2], g_rows[2]),
             ("G Room 4 (single) vs Single room-5", A[3], g_rows[3]),
             ("H Twin 1 vs Twin sharing room-1", A[0], h_rows[0]),
             ("H Twin 2 vs Twin sharing room-2", A[1], h_rows[1]),
             ("H Twin 3 vs Single room-4 + Single room-5", None, h_rows[2])]

    def sgn(v):
        n = int(round(v * 12))
        return ("+" if n >= 0 else "-") + fi(abs(n) / 12)

    for nm, a, r in pairs:
        if a is None:
            L.append(f"| {nm} | 16'-0\" x 9'-0\" and 14'-8\" x 10'-1\" (2 beds in 2 rooms) | {fi(r['w'])} x {fi(r['d'])} "
                     f"(2 beds in 1 room) | not like for like: one twin room replaces two singles |")
            continue
        L.append(f"| {nm} | {fi(a[1])} x {fi(a[2])} | {fi(r['w'])} x {fi(r['d'])} | "
                 f"E-W {sgn(r['w'] - a[1])}, N-S {sgn(r['d'] - a[2])} |")
    short = [nm.split(" (")[0] for nm, a, r in pairs[:4] if r["w"] < a[1] - 0.04]
    L.append(f"\nE-W: {', '.join(short)} are shorter than the architect's equivalent (Layout G has a 6'-0\" ward passage "
             "against his 5'-0\" and a 13'-6\" deep east service band); no room in H is shorter. N-S: every room in G and H "
             "is deeper than the architect's. Net of the toilet, G Room 4 (117 sf) is about level with his Single room-5 "
             "(about 118 sf net); per bed, every other room gives more floor than its equivalent.\n")
    L.append("## 5. Twin potential in Layout G\n")
    r1 = g_rows[0]
    L.append(f"Checked, not adopted. With the toilet at the glass, Room 1's bed bay (passage wall to toilet wall) is 11'-3\" and "
             f"Room 2's the same; Rooms 3 and 4 have 7'-10\". Two beds with 3'-0\" between them need 9'-6\", so Rooms 1 and 2 "
             f"would take two beds but then have no place for a wardrobe or an attendant sofa clear of the 3'-5\" foot aisle, "
             f"and Room 1 would give {r1['area'] / 2:.0f} sf per bed against the architect's 98. Rooms 3 and 4 cannot take two beds. "
             "A twin room in G needs the toilet moved to the passage end, as in H, which changes the clients' sketch.\n")
    L.append("## 6. Checks run\n")
    L.append(f"- Layout G: room overlaps over 0.5 sf: {g_issues[3]['overlaps_gt_0.5sf'] or 'none'}; doors off a wall: "
             f"{g_issues[3]['doors_off_wall'] or 'none'}; ward passage minimum {g_issues[3]['ward_passage_min_ft']:.2f} ft; "
             f"IPD audit ({g_issues[1]} beds, {g_issues[2]} heads on solid walls; furniture inside the room, clear of walls and "
             f"columns, no overlaps, door leaves clear of furniture, true sizes): "
             f"{[i for i in g_issues[0] if 'room4: wardrobe' not in i] or 'none'}"
             f"{' (Room 4 wardrobe is 2 ft x 2 ft 6 in by design)' if any('room4: wardrobe' in i for i in g_issues[0]) else ''}; "
             f"DXF audit errors: {dxf_g}.")
    for c in h_checks:
        L.append(f"- Layout H: {c}")
    L.append(f"- Layout H: DXF audit errors: {dxf_h}.")
    L.append("\n## 7. Not verified\n")
    L.append("- The architect's room sizes are taken as printed; his drawing was not re-measured against the DWG.\n"
             "- Wall faces are plaster faces from the builder's DWG, not a site survey.\n"
             "- Drainage: only the east-wall toilet position of unit x05 is a builder's wet point. Every ward toilet in G and H "
             "needs a raised floor and new drain runs; this is not designed.\n"
             "- 3'-0\" between twin beds and the 6'-6\" (H) / 6'-0\" (G) ward passage are not checked against NABH or the local "
             "fire officer's requirements.\n"
             "- The two feasibility briefs (`LAYOUT_G_BRIEF_AND_FEASIBILITY.md`, `LAYOUT_H_BRIEF_AND_FEASIBILITY.md`) carry a "
             "revision note at the top; their body text and tables still describe the ward before this fix.\n"
             "- `flow_scores.md` and the 3D / blueprint views were not reviewed for the new ward beyond regenerating them.\n")
    return "\n".join(L) + "\n"


def main():
    # ---- Layout G
    rooms_g = G.layout_g_rooms()
    gi = g_checks(rooms_g)
    print("G IPD audit:", gi[0] or "none", "| beds", gi[1], "heads ok", gi[2])
    print("G overlaps:", gi[3]["overlaps_gt_0.5sf"], "doors off wall:", gi[3]["doors_off_wall"])
    base = os.path.join(OUT, "layout_G_detailed")
    G.render_sheet(base)
    from dxf_export import export_dxf
    dxf_g = export_dxf("G", base + ".dxf")
    print("G DXF audit errors:", dxf_g)
    import blueprint_svg as B
    for theme in ("blueprint", "clean"):
        B.render_blueprint("G", theme, os.path.join(OUT, f"layout_G_{theme}.svg"))
    from render3d import render_3d
    render_3d("G", os.path.join(OUT, "3d_layout_G.png"))
    # ---- Layout H
    rooms_h = H.layout_h_rooms()
    h_checks = build_h.run_checks(rooms_h)
    build_h.main()
    import ezdxf
    dxf_h = len(ezdxf.readfile(os.path.join(OUT, "layout_H_detailed.dxf")).audit().errors)
    # ---- comparison
    g_pts = {k: (v["w"][:2], v["d"][:2]) for k, v in G.IPD_G.items()}
    g_rows = _rows(rooms_g, G_IPD, G_WC, g_pts)
    h_rows = _rows(rooms_h, H_IPD, H_WC, H.IPD_PTS)
    md = comparison_md(g_rows, h_rows, gi, h_checks, dxf_g, dxf_h)
    open(os.path.join(OUT, "IPD_COMPARISON.md"), "w", encoding="utf-8").write(md)
    print(md)


if __name__ == "__main__":
    main()
