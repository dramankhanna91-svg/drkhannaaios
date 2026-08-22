"""Rayon-style architectural blueprint SVG (per the AI-CAD output spec).

Self-contained SVG, no external refs: double-line walls (the wall-band
geometry gives true thickness), door swing arcs, window tick-pairs on the
glass facade, labeled furniture bounding boxes, explicit dimension lines,
"ROOM — W x D" label strings, scale bar, north arrow.

Two themes: 'blueprint' (white lines on dark blue) and 'clean' (dark grey
lines on white).
"""
import os

from plan_model import (PLATE, CUTOUT, GLASS_WEST, GLASS_NORTH, MD_DOOR,
                        LAYOUTS, wall_bands)

PPF = 10.0                       # px per foot
OX, OY = 96.0, 70.0
W, H = 700.0, 1180.0

THEMES = {
    "blueprint": dict(bg="#0d2a4a", ink="#f2f6fb", faint="#7d9cbd", wall="#f2f6fb",
                      accent="#ffd166", glass="#7fd4ff", void="#5f7fa0"),
    "clean": dict(bg="#ffffff", ink="#3a3f45", faint="#9aa1a9", wall="#2f3439",
                  accent="#b45309", glass="#1d4ed8", void="#9aa1a9"),
}


def P(x, y):
    return (OX + x * PPF, OY + y * PPF)


def _poly_pts(geom):
    return " ".join(f"{OX + x * PPF:.1f},{OY + y * PPF:.1f}"
                    for x, y in geom.exterior.coords)


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_blueprint(key, theme_name, out_path):
    t = THEMES[theme_name]
    title, factory = LAYOUTS[key]
    rooms = factory()
    walls = wall_bands(rooms)

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
         f'viewBox="0 0 {W:.0f} {H:.0f}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{W:.0f}" height="{H:.0f}" fill="{t["bg"]}"/>']

    # title strip
    s.append(f'<text x="{OX:.0f}" y="26" fill="{t["ink"]}" font-size="15" '
             f'font-weight="bold" letter-spacing="1.5">{_esc(title.upper())}</text>')
    s.append(f'<text x="{OX:.0f}" y="43" fill="{t["faint"]}" font-size="9.5" '
             f'letter-spacing="0.8">HOSPITAL OF DR. AMAN KHANNA · 7TH FLOOR, SOLARIS '
             f'SHINE, ALTHAN, SURAT · ENVELOPE 48\'-6" × 92\'-0" (REV C)</text>')

    # plate outline (thin, under the walls)
    s.append(f'<polygon points="{_poly_pts(PLATE)}" fill="none" '
             f'stroke="{t["faint"]}" stroke-width="0.8"/>')

    # cut-out void: cross + hatch feel
    cut = CUTOUT.intersection(PLATE)
    s.append(f'<polygon points="{_poly_pts(cut)}" fill="none" '
             f'stroke="{t["void"]}" stroke-width="1.2"/>')
    (cx0, cy0, cx1, cy1) = cut.bounds
    a, b = P(cx0, cy0), P(cx1, cy1)
    c, d = P(cx0, cy1), P(cx1, cy0)
    s.append(f'<line x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}" '
             f'stroke="{t["void"]}" stroke-width="0.7"/>')
    s.append(f'<line x1="{c[0]:.0f}" y1="{c[1]:.0f}" x2="{d[0]:.0f}" y2="{d[1]:.0f}" '
             f'stroke="{t["void"]}" stroke-width="0.7"/>')
    mx, my = P((cx0 + cx1) / 2, (cy0 + cy1) / 2)
    s.append(f'<text x="{mx:.0f}" y="{my:.0f}" fill="{t["void"]}" font-size="8.5" '
             f'text-anchor="middle">CUT-OUT / SERVICE (VOID)</text>')

    # walls: filled bands = true double-line thickness
    geoms = walls.geoms if walls.geom_type.startswith("Multi") else [walls]
    for g in geoms:
        if g.geom_type != "Polygon" or g.area < 0.05:
            continue
        path = f'M {" L ".join(f"{OX + x * PPF:.1f} {OY + y * PPF:.1f}" for x, y in g.exterior.coords)} Z'
        for hole in g.interiors:
            path += f' M {" L ".join(f"{OX + x * PPF:.1f} {OY + y * PPF:.1f}" for x, y in hole.coords)} Z'
        s.append(f'<path d="{path}" fill="{t["wall"]}" fill-rule="evenodd" stroke="none"/>')

    # glass facade: thin parallel window lines
    for (x1, y1), (x2, y2) in GLASS_WEST + GLASS_NORTH:
        (px1, py1), (px2, py2) = P(x1, y1), P(x2, y2)
        dx, dy = px2 - px1, py2 - py1
        n = (dx * dx + dy * dy) ** 0.5 or 1
        ox_, oy_ = dy / n, -dx / n
        for off in (5.0, 8.0):
            s.append(f'<line x1="{px1 + ox_ * off:.1f}" y1="{py1 + oy_ * off:.1f}" '
                     f'x2="{px2 + ox_ * off:.1f}" y2="{py2 + oy_ * off:.1f}" '
                     f'stroke="{t["glass"]}" stroke-width="1.0"/>')

    # rooms: labels + furniture boxes + doors
    for r in rooms:
        p = r.poly
        if p.is_empty:
            continue
        cpt = p.representative_point()
        tx, ty = P(cpt.x, cpt.y)
        if r.zone == "circ":
            if r.name:
                s.append(f'<text x="{tx:.0f}" y="{ty:.0f}" fill="{t["faint"]}" '
                         f'font-size="8" font-style="italic" text-anchor="middle">'
                         f'{_esc(r.name)}</text>')
        elif p.area < 34:
            s.append(f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="7" fill="none" '
                     f'stroke="{t["ink"]}" stroke-width="0.8"/>')
            s.append(f'<text x="{tx:.0f}" y="{ty + 3:.0f}" fill="{t["ink"]}" '
                     f'font-size="7" text-anchor="middle">T</text>')
        else:
            nm = _esc(r.name)
            dims = _esc(r.dims.replace(" x ", " × ")) if r.dims else ""
            fs = 9.5 if p.area > 130 else 8
            s.append(f'<text x="{tx:.0f}" y="{ty - 3:.0f}" fill="{t["ink"]}" '
                     f'font-size="{fs}" font-weight="bold" text-anchor="middle">{nm}</text>')
            if dims:
                s.append(f'<text x="{tx:.0f}" y="{ty + 9:.0f}" fill="{t["faint"]}" '
                         f'font-size="7.5" text-anchor="middle">{dims}</text>')
        # furniture bounding boxes
        for f in r.furniture:
            kind, fx, fy, fw, fh, rot = f
            (bx, by) = P(fx, fy)
            s.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{fw * PPF:.1f}" '
                     f'height="{fh * PPF:.1f}" fill="none" stroke="{t["faint"]}" '
                     f'stroke-width="0.7"'
                     + (f' transform="rotate({rot} {bx:.1f} {by:.1f})"' if rot else "")
                     + '/>')
            if kind in ("bed", "ottable", "desk", "exam") and fw * fh > 6:
                lx, ly = P(fx + fw / 2, fy + fh / 2)
                lbl = {"bed": "BED", "ottable": "OT TABLE", "desk": "DESK",
                       "exam": "EXAM"}[kind]
                s.append(f'<text x="{lx:.0f}" y="{ly + 2.5:.0f}" fill="{t["faint"]}" '
                         f'font-size="5.5" text-anchor="middle">{lbl}</text>')
        # doors: opening + swing arc
        for (dx_, dy_, wdt, wall) in r.doors:
            (px, py) = P(dx_, dy_)
            rr = wdt * PPF
            if wall in ("N", "S"):
                sg = 1 if wall == "N" else -1
                x1, x2 = px - rr / 2, px + rr / 2
                s.append(f'<line x1="{x1:.1f}" y1="{py:.1f}" x2="{x2:.1f}" y2="{py:.1f}" '
                         f'stroke="{t["bg"]}" stroke-width="5"/>')
                s.append(f'<path d="M {x1:.1f} {py:.1f} L {x1:.1f} {py + sg * rr:.1f} '
                         f'A {rr:.1f} {rr:.1f} 0 0 {1 if sg > 0 else 0} {x2:.1f} {py:.1f}" '
                         f'fill="none" stroke="{t["accent"]}" stroke-width="0.9"/>')
            else:
                sg = 1 if wall == "E" else -1
                y1, y2 = py - rr / 2, py + rr / 2
                s.append(f'<line x1="{px:.1f}" y1="{y1:.1f}" x2="{px:.1f}" y2="{y2:.1f}" '
                         f'stroke="{t["bg"]}" stroke-width="5"/>')
                s.append(f'<path d="M {px:.1f} {y1:.1f} L {px + sg * rr:.1f} {y1:.1f} '
                         f'A {rr:.1f} {rr:.1f} 0 0 {1 if sg > 0 else 0} {px:.1f} {y2:.1f}" '
                         f'fill="none" stroke="{t["accent"]}" stroke-width="0.9"/>')

    # main entry
    (ex, ey1) = P(0, MD_DOOR[1])
    (_, ey2) = P(0, MD_DOOR[2])
    s.append(f'<line x1="{ex:.1f}" y1="{ey1:.1f}" x2="{ex:.1f}" y2="{ey2:.1f}" '
             f'stroke="{t["accent"]}" stroke-width="3"/>')
    s.append(f'<text x="{ex - 10:.0f}" y="{(ey1 + ey2) / 2:.0f}" fill="{t["accent"]}" '
             f'font-size="9" font-weight="bold" text-anchor="end">MAIN ENTRY 5\'-0"</text>')

    # dimension lines with oblique ticks
    def dim_h(xa, xb, y, label):
        (x1, yy) = P(xa, y)
        (x2, _) = P(xb, y)
        s.append(f'<line x1="{x1:.0f}" y1="{yy:.0f}" x2="{x2:.0f}" y2="{yy:.0f}" '
                 f'stroke="{t["ink"]}" stroke-width="0.7"/>')
        for xx in (x1, x2):
            s.append(f'<line x1="{xx - 3:.0f}" y1="{yy + 3:.0f}" x2="{xx + 3:.0f}" '
                     f'y2="{yy - 3:.0f}" stroke="{t["ink"]}" stroke-width="0.8"/>')
        s.append(f'<text x="{(x1 + x2) / 2:.0f}" y="{yy - 5:.0f}" fill="{t["ink"]}" '
                 f'font-size="10" text-anchor="middle">{label}</text>')

    def dim_v(ya, yb, x, label):
        (xx, y1) = P(x, ya)
        (_, y2) = P(x, yb)
        s.append(f'<line x1="{xx:.0f}" y1="{y1:.0f}" x2="{xx:.0f}" y2="{y2:.0f}" '
                 f'stroke="{t["ink"]}" stroke-width="0.7"/>')
        for yy in (y1, y2):
            s.append(f'<line x1="{xx - 3:.0f}" y1="{yy + 3:.0f}" x2="{xx + 3:.0f}" '
                     f'y2="{yy - 3:.0f}" stroke="{t["ink"]}" stroke-width="0.8"/>')
        s.append(f'<text x="{xx - 6:.0f}" y="{(y1 + y2) / 2:.0f}" fill="{t["ink"]}" '
                 f'font-size="10" text-anchor="middle" '
                 f'transform="rotate(-90 {xx - 6:.0f} {(y1 + y2) / 2:.0f})">{label}</text>')

    dim_h(0, 48.5, -2.6, "48'-6\"")
    dim_v(0, 92, -3.6, "92'-0\"")
    dim_v(0, MD_DOOR[1], -1.8, "43'-0\"")

    # scale bar + north arrow
    (sx, sy) = P(0, 96.5)
    for i in range(4):
        fill = t["ink"] if i % 2 == 0 else t["bg"]
        s.append(f'<rect x="{sx + i * 5 * PPF:.0f}" y="{sy:.0f}" width="{5 * PPF:.0f}" '
                 f'height="6" fill="{fill}" stroke="{t["ink"]}" stroke-width="0.7"/>')
    for i in range(0, 21, 5):
        s.append(f'<text x="{sx + i * PPF:.0f}" y="{sy + 18:.0f}" fill="{t["ink"]}" '
                 f'font-size="8" text-anchor="middle">{i}\'</text>')
    (nx, ny) = P(52.5, 84)
    s.append(f'<path d="M {nx:.0f} {ny:.0f} l -5 -14 l 5 4 l 5 -4 Z" fill="{t["ink"]}"/>')
    s.append(f'<text x="{nx:.0f}" y="{ny + 12:.0f}" fill="{t["ink"]}" font-size="10" '
             f'font-weight="bold" text-anchor="middle">N</text>')
    s.append(f'<text x="{nx:.0f}" y="{ny - 22:.0f}" fill="{t["faint"]}" font-size="7.5" '
             f'text-anchor="middle">NORTH ↓</text>')

    # compass edges + notes
    s.append(f'<text x="{P(24, -5.4)[0]:.0f}" y="{P(24, -5.4)[1]:.0f}" fill="{t["faint"]}" '
             f'font-size="9" text-anchor="middle" letter-spacing="2">SOUTH — SERVICE STRIP BEYOND</text>')
    (wx, wy) = P(51.5, 30)
    s.append(f'<text x="{wx:.0f}" y="{wy:.0f}" fill="{t["glass"]}" font-size="9" '
             f'text-anchor="middle" letter-spacing="1.5" '
             f'transform="rotate(-90 {wx:.0f} {wy:.0f})">WEST — OPENABLE GLASS · VIEWS</text>')
    (fx_, fy_) = P(0, 99.5)
    s.append(f'<text x="{fx_:.0f}" y="{fy_ + 14:.0f}" fill="{t["faint"]}" font-size="8">'
             f'VISITOR WC: COMMON-AREA TOILETS OUTSIDE THE MAIN ENTRY (SEE BUILDER\'S FLOOR PLAN) · '
             f'OT SUITE ENTERED ONLY VIA RECOVERY (PATIENTS) / SCRUB (STAFF)</text>')
    s.append(f'<text x="{fx_:.0f}" y="{fy_ + 26:.0f}" fill="{t["faint"]}" font-size="8">'
             f'SCALE 1:{int(12 * 96 / PPF / 2.54 * 2.54 / 12 * 12)} ON SCREEN — USE THE BAR · '
             f'CONCEPT FOR REVIEW, TO BE VERIFIED BY THE PROJECT ARCHITECT</text>')

    s.append("</svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(s))
    return out_path


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "deliverables")
    for theme in ("blueprint", "clean"):
        p = render_blueprint("E", theme, os.path.join(out, f"layout_E_{theme}.svg"))
        print("wrote", os.path.basename(p))
