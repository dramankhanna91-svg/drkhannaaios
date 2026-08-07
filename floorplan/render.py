"""CAD-style 2D sheet renderer (SVG + PNG) for the hospital layouts.

Look modeled on the architect's drawing: solid dark wall bands, near-white
rooms with a whisper of zone tint, tile-hatched wet areas, door swing arcs,
keynote circles for small rooms, corridor labels in italic gray.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly, Arc, FancyArrow, Rectangle, Circle
from matplotlib.lines import Line2D
import numpy as np

from plan_model import (PLATE, CUTOUT, GLASS_WEST, GLASS_NORTH, MD_DOOR,
                        ZONES, LAYOUTS, wall_bands, circulation_poly)

INK = "#2b2b2b"
CORRIDOR = "#f7f6f2"


def _tint(hex_color, keep=0.30):
    """Blend a zone color toward white; keep = fraction of original color."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    f = lambda v: int(v * keep + 255 * (1 - keep))
    return f"#{f(r):02x}{f(g):02x}{f(b):02x}"


def _iter_polys(poly):
    if poly.is_empty:
        return
    geoms = poly.geoms if poly.geom_type.startswith("Multi") else [poly]
    for g in geoms:
        if g.geom_type == "Polygon" and g.area > 0.05:
            yield g


def _fill(ax, poly, zorder, **kw):
    for g in _iter_polys(poly):
        ext = np.asarray(g.exterior.coords)
        if g.interiors:
            # draw with holes via Path
            from matplotlib.path import Path
            from matplotlib.patches import PathPatch
            verts = list(ext)
            codes = [Path.MOVETO] + [Path.LINETO] * (len(ext) - 2) + [Path.CLOSEPOLY]
            for hole in g.interiors:
                h = np.asarray(hole.coords)
                verts += list(h)
                codes += [Path.MOVETO] + [Path.LINETO] * (len(h) - 2) + [Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), zorder=zorder, **kw))
        else:
            ax.add_patch(MplPoly(ext, closed=True, zorder=zorder, **kw))


def _tile_hatch(ax, poly, zorder, pitch=1.0):
    """Light tile grid inside wet rooms."""
    minx, miny, maxx, maxy = poly.bounds
    from shapely.geometry import LineString
    xs = np.arange(np.floor(minx), maxx + pitch, pitch)
    ys = np.arange(np.floor(miny), maxy + pitch, pitch)
    for x in xs:
        seg = LineString([(x, miny), (x, maxy)]).intersection(poly)
        _plot_lines(ax, seg, "#c9d4d6", 0.45, zorder)
    for y in ys:
        seg = LineString([(minx, y), (maxx, y)]).intersection(poly)
        _plot_lines(ax, seg, "#c9d4d6", 0.45, zorder)


def _tile_hatch2(ax, poly, zorder, pitch=2.0):
    """Very light 2' floor-tile grid for dry rooms (architect-sheet look)."""
    minx, miny, maxx, maxy = poly.bounds
    from shapely.geometry import LineString
    inner = poly.buffer(-0.15)
    if inner.is_empty:
        return
    for x in np.arange(np.ceil(minx / pitch) * pitch, maxx, pitch):
        _plot_lines(ax, LineString([(x, miny), (x, maxy)]).intersection(inner),
                    "#e6e4de", 0.35, zorder)
    for y in np.arange(np.ceil(miny / pitch) * pitch, maxy, pitch):
        _plot_lines(ax, LineString([(minx, y), (maxx, y)]).intersection(inner),
                    "#e6e4de", 0.35, zorder)


def _plot_lines(ax, geom, color, lw, zorder):
    if geom.is_empty:
        return
    geoms = geom.geoms if geom.geom_type.startswith("Multi") else [geom]
    for g in geoms:
        if g.geom_type == "LineString":
            xs, ys = g.xy
            ax.plot(xs, ys, color=color, lw=lw, zorder=zorder, solid_capstyle="butt")


CAD_PALETTE = dict(chair="white", bed_blanket="#eeeeee", counter="#e7e0d6",
                   desk="#f0f0f0", plant="#e2eddd", wall=INK, tint_keep=0.35,
                   shadow=False)
PRESO_PALETTE = dict(chair="#9fc6bc", bed_blanket="#aecbe8", counter="#c29a6b",
                     desk="#d9c6a5", plant="#8fbf7f", wall="#3a372f", tint_keep=0.62,
                     shadow=True)


def _furniture(ax, item, z=6, pal=CAD_PALETTE):
    kind, x, y, w, h, rot = item
    thin = dict(lw=0.55, ec="#4a4a4a", zorder=z)
    if kind == "bed":
        ax.add_patch(Rectangle((x, y), w, h, fc="white", **thin))
        ax.add_patch(Rectangle((x + 0.25, y + h - 1.4), w - 0.5, 1.0, fc=pal["bed_blanket"],
                               lw=0.4, ec="#4a4a4a", zorder=z))
        if pal["shadow"]:
            ax.add_patch(Rectangle((x + 0.2, y + 0.4), w, h * 0.55, fc=pal["bed_blanket"],
                                   lw=0.3, ec="#4a4a4a", zorder=z))
    elif kind == "exam":
        ax.add_patch(Rectangle((x, y), w, h, fc="#f4f4f4", **thin))
        ax.plot([x, x + w], [y + h * 0.75, y + h * 0.75], color="#4a4a4a", lw=0.4, zorder=z)
    elif kind == "ottable":
        ax.add_patch(Rectangle((x, y), w, h, fc="#eef2ee", angle=rot, **thin))
        ax.add_patch(Circle((x + w / 2, y + h + 1.1), 0.85, fc="none", lw=0.55,
                            ec="#4a4a4a", zorder=z))
    elif kind in ("desk", "side", "cart"):
        ax.add_patch(Rectangle((x, y), w, h, fc=pal["desk"], angle=rot, **thin))
    elif kind == "counter":
        ax.add_patch(Rectangle((x, y), w, h, fc=pal["counter"], angle=rot, **thin))
    elif kind == "shelf":
        ax.add_patch(Rectangle((x, y), w, h, fc="white", **thin))
        n = max(2, int(max(w, h) / 1.4))
        if w >= h:
            for i in range(1, n):
                ax.plot([x + w * i / n] * 2, [y, y + h], color="#4a4a4a", lw=0.35, zorder=z)
        else:
            for i in range(1, n):
                ax.plot([x, x + w], [y + h * i / n] * 2, color="#4a4a4a", lw=0.35, zorder=z)
    elif kind == "chair":
        ax.add_patch(Rectangle((x, y), w, h, fc=pal["chair"], lw=0.5, ec="#4a4a4a", zorder=z))
    elif kind == "wc":
        ax.add_patch(Rectangle((x, y + h * 0.5), w, h * 0.5, fc="white", lw=0.5,
                               ec="#4a4a4a", zorder=z))
        ax.add_patch(Circle((x + w / 2, y + h * 0.28), w * 0.4, fc="white", lw=0.5,
                            ec="#4a4a4a", zorder=z))
    elif kind == "sink":
        ax.add_patch(Circle((x + w / 2, y + h / 2), min(w, h) * 0.45, fc="white", lw=0.5,
                            ec="#4a4a4a", zorder=z))
    elif kind == "shower":
        ax.add_patch(Rectangle((x, y), w, h, fc="white", lw=0.5, ec="#4a4a4a", zorder=z))
        ax.plot([x, x + w], [y, y + h], color="#4a4a4a", lw=0.35, zorder=z)
    elif kind == "plant":
        ax.add_patch(Circle((x + w / 2, y + h / 2), w / 2, fc=pal["plant"], lw=0.5,
                            ec="#6d8a63", zorder=z))
    elif kind == "tv":
        ax.add_patch(Rectangle((x, y), w, h, fc="#666", lw=0.4, ec="#333", zorder=z))
    elif kind == "water":
        ax.add_patch(Rectangle((x, y), w, h, fc="#e4f0f7", lw=0.5, ec="#4a4a4a", zorder=z))
    elif kind == "light":
        ax.add_patch(Circle((x + w / 2, y + h / 2), w / 2, fc="none", lw=0.5,
                            ec="#4a4a4a", zorder=z))


def _door_tag(ax, door, z=11):
    """Architect-style door tags by leaf width: D1 >= 2'-9\", D2 >= 2'-3\", D3 below."""
    cx, cy, w, wall = door
    tag = "D1" if w >= 2.75 else ("D2" if w >= 2.25 else "D3")
    off = 1.6
    dx, dy = {"N": (off, 1.0), "S": (off, -1.0), "E": (1.0, off), "W": (-1.0, off)}[wall]
    ax.text(cx + dx, cy + dy, tag, fontsize=5.5, color="#666", zorder=z,
            ha="center", va="center")


def _door(ax, door, z=8):
    cx, cy, w, wall = door
    r = w
    if wall in ("N", "S"):
        sgn = 1 if wall == "N" else -1
        ax.add_patch(Arc((cx - w / 2, cy), 2 * r, 2 * r, angle=0,
                         theta1=0 if sgn > 0 else 270, theta2=90 if sgn > 0 else 360,
                         lw=0.6, color=INK, zorder=z))
        ax.plot([cx - w / 2, cx - w / 2], [cy, cy + sgn * r], lw=1.0, color=INK, zorder=z)
    else:
        sgn = 1 if wall == "E" else -1
        ax.add_patch(Arc((cx, cy - w / 2), 2 * r, 2 * r, angle=0,
                         theta1=0 if wall == "E" else 90,
                         theta2=90 if wall == "E" else 180,
                         lw=0.6, color=INK, zorder=z))
        ax.plot([cx, cx + sgn * r], [cy - w / 2, cy - w / 2], lw=1.0, color=INK, zorder=z)


KEYNOTES = {"wet": ("T", "Toilet — tiled, floor trap; wheelchair-accessible where marked (Acc.)"),
            "exam": ("X", "Examination bed 2'-3\" × 5'-6\" with curtain track"),
            "duct": ("D", "Service duct / shaft")}


def _keynote_code(room):
    if room.zone == "wet":
        return "T"
    if room.key.startswith("exam"):
        return "X"
    if room.key == "duct":
        return "D"
    return None


def render_layout(key, out_base, highlight=True, style="cad"):
    pal = PRESO_PALETTE if style == "presentation" else CAD_PALETTE
    title, factory = LAYOUTS[key]
    if style == "presentation":
        title += " — presentation visual"
    rooms = factory()
    walls = wall_bands(rooms)

    fig, ax = plt.subplots(figsize=(13, 22))
    ax.set_aspect("equal")

    # plate = corridor background
    _fill(ax, PLATE, 1, fc=CORRIDOR, ec="none")

    # service strip + cut-out
    ax.add_patch(Rectangle((0, -4.2), 48.5, 3.4, fc="white", ec=INK, lw=0.9,
                           hatch="xxx", zorder=1))
    ax.text(24, -2.5, "SERVICE AREA", ha="center", va="center", fontsize=9, color=INK)
    _fill(ax, CUTOUT, 2, fc="white", ec="none", hatch="///", lw=0)
    c = CUTOUT.centroid
    ax.text(c.x, c.y, "CUT-OUT\n(void)", ha="center", va="center", fontsize=9,
            color=INK, zorder=4)

    # room fills (zone tints); tile grids: fine in wet, light 2' elsewhere
    for r in rooms:
        if r.zone == "circ":
            continue
        p = r.poly
        _fill(ax, p, 2, fc=_tint(ZONES[r.zone][0], pal["tint_keep"]), ec="none")
        for g in _iter_polys(p):
            if r.zone == "wet":
                _tile_hatch(ax, g, 3)
            elif g.area > 30:
                _tile_hatch2(ax, g, 2.5)

    # walls: soft drop shadow (presentation) then solid fill
    if pal["shadow"]:
        from shapely.affinity import translate as _shtr
        _fill(ax, _shtr(walls, 0.45, 0.7), 6.5, fc="#5a564c", ec="none", alpha=0.30)
    _fill(ax, walls, 7, fc=pal["wall"], ec="none")

    # furniture + doors + door tags
    for r in rooms:
        for f in r.furniture:
            _furniture(ax, f, pal=pal)
        for d in r.doors:
            _door(ax, d)
            if style != "presentation":
                _door_tag(ax, d)

    # ------------------------------------------------------------- labels
    keynote_pts = []
    for r in rooms:
        p = r.poly
        if p.is_empty or not r.name:
            continue
        cpt = p.representative_point()
        if r.zone == "circ":
            x0, y0, w0, h0 = r.rect
            rot = 90 if h0 > w0 * 1.4 else 0
            if r.key == "lobby":
                tx, ty, rot = x0 + w0 * 0.72, y0 + h0 * 0.9, 0
            else:
                tx, ty = cpt.x, cpt.y
            if r.name.isupper():
                ax.text(tx, ty, r.name, ha="center", va="center", fontsize=8.5,
                        color="#222", weight="bold", zorder=9, rotation=rot)
            else:
                ax.text(tx, ty, r.name, ha="center", va="center", fontsize=7.5,
                        color="#8a8a84", style="italic", zorder=9, rotation=rot)
            continue
        code = _keynote_code(r)
        if code:
            keynote_pts.append((cpt.x, cpt.y, code, "Acc" in r.name or "Acc" in r.dims))
            continue
        x0, y0, w0, h0 = r.rect
        rot = 90 if (w0 < 6.4 and h0 > 8) else 0
        fs = 10 if p.area > 110 else (8.5 if p.area > 60 else 7)
        if r.key == "wait":
            fs = 8.5
            cpt = type(cpt)(cpt.x - 1.2, cpt.y)
        if r.key in ("pharm", "triage") and p.area < 50:
            fs = 6.2
        label = r.name + ("\n" + r.dims if r.dims else "")
        ax.text(cpt.x, cpt.y, label, ha="center", va="center", fontsize=fs,
                color="#111", weight="bold" if r.name.isupper() else "normal",
                zorder=9, linespacing=1.35, rotation=rot)

    for (x, y, code, acc) in keynote_pts:
        ax.add_patch(Circle((x, y), 1.05, fc="white", ec=INK, lw=0.8, zorder=10))
        ax.text(x, y, code, ha="center", va="center", fontsize=7.5, weight="bold",
                color=INK, zorder=11)
        if acc:
            ax.text(x, y - 1.9, "Acc.", ha="center", va="center", fontsize=5.5,
                    color=INK, zorder=11)

    # glass facade bands
    for (x1, y1), (x2, y2) in GLASS_WEST + GLASS_NORTH:
        dx, dy = x2 - x1, y2 - y1
        n = np.hypot(dx, dy)
        ox, oy = dy / n * 1.2, -dx / n * 1.2
        ax.plot([x1 + ox, x2 + ox], [y1 + oy, y2 + oy], color="#2c6fbb", lw=2.0, zorder=5)
        ax.plot([x1 + ox * 1.65, x2 + ox * 1.65], [y1 + oy * 1.65, y2 + oy * 1.65],
                color="#2c6fbb", lw=0.7, zorder=5)
    ax.text(48.3, 20, "OPENABLE GLASS", rotation=-84, fontsize=8, color="#2c6fbb",
            ha="center", va="center")
    ax.text(20, 103.8, "OPENABLE GLASS", fontsize=8, color="#2c6fbb", ha="center")

    # main door: swing + label (wall already has the opening punched)
    _, y1, y2 = MD_DOOR
    ax.add_patch(Arc((0, y1), 8, 8, angle=0, theta1=0, theta2=60, lw=0.8, color=INK, zorder=8))
    ax.annotate("MD — MAIN\nENTRY", xy=(-0.3, (y1 + y2) / 2), xytext=(-8.4, 58.5),
                fontsize=9, weight="bold", ha="center", va="center", color=INK,
                arrowprops=dict(arrowstyle="->", lw=1.1, color=INK))

    # compass labels
    for x, y, s in [(24, -8.5, "SOUTH SIDE"), (24, 108.5, "NORTH SIDE")]:
        ax.text(x, y, s, ha="center", va="center", fontsize=11, weight="bold",
                bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(-8.5, 24, "EAST SIDE", rotation=90, ha="center", va="center", fontsize=11,
            weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.text(55, 24, "WEST SIDE", rotation=-90, ha="center", va="center", fontsize=11,
            weight="bold", bbox=dict(fc="#eeeeee", ec=INK, lw=1))
    ax.add_patch(FancyArrow(52.5, 96, 0, 4.5, width=0.6, head_width=2.0, head_length=1.8,
                            fc=INK, ec=INK))
    ax.text(52.5, 94, "N", ha="center", fontsize=13, weight="bold", color=INK)

    # overall dimensions
    ax.annotate("", xy=(48.5, -6.2), xytext=(0, -6.2),
                arrowprops=dict(arrowstyle="<->", lw=1, color=INK))
    ax.text(24.2, -7.3, "48'-6\"", ha="center", fontsize=9, color=INK)
    ax.annotate("", xy=(-4.8, 101), xytext=(-4.8, 0),
                arrowprops=dict(arrowstyle="<->", lw=1, color=INK))
    ax.text(-5.9, 14.0, "101'-0\"", rotation=90, va="center", fontsize=9, color=INK)

    # legend + keynote table
    handles = [Line2D([], [], marker="s", ls="", ms=11, mfc=_tint(col, 0.35), mec="#999",
                      label=lbl) for col, lbl in ZONES.values() if lbl != "Circulation"]
    handles.append(Line2D([], [], marker="s", ls="", ms=11, mfc=INK, mec=INK, label="Walls"))
    handles.append(Line2D([], [], color="#2c6fbb", lw=2.0, label="Openable glass facade"))
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.045),
              ncol=3, fontsize=8.5, frameon=False)

    code_desc = {v[0]: v[1] for v in KEYNOTES.values()}
    keys_used = sorted({k for _, _, k, _ in keynote_pts})
    if keys_used:
        note = "KEYNOTES:\n" + "\n".join(f"  ({k})  {code_desc[k]}" for k in keys_used)
        ax.text(-8, 123.5, note, fontsize=7.5, color=INK, va="top", linespacing=1.5)

    total = PLATE.area - CUTOUT.area
    ax.set_title(f"{title}\nHospital of Dr. Aman Khanna — 7th Floor, Solaris Shine, Althan, Surat"
                 f"\nCarpet area ≈ {total:,.0f} sq ft  ·  corridors ≥ 5'-0\" (12'-1½\" spine)",
                 fontsize=12, pad=16)

    # scale bar
    ax.plot([0, 10], [117.5, 117.5], lw=3, color=INK)
    for i in range(0, 11, 5):
        ax.plot([i, i], [116.9, 118.1], lw=1.2, color=INK)
        ax.text(i, 119.6, f"{i}'", ha="center", fontsize=7.5, color=INK)

    # title block (architect-sheet style)
    tb_y0, tb_y1 = 130.5, 139.5
    ax.add_patch(Rectangle((-8, tb_y0), 66, tb_y1 - tb_y0, fc="white", ec=INK, lw=1.2,
                           zorder=3))
    for fx in (12, 30, 44):
        ax.plot([fx, fx], [tb_y0, tb_y1], color=INK, lw=0.8, zorder=4)
    ax.text(-6.5, tb_y0 + 1.6, "PROJECT", fontsize=6, color="#777")
    ax.text(-6.5, tb_y0 + 5.4, "Hospital of Dr. Aman Khanna\n7th Floor, Solaris Shine,\nAlthan, Surat",
            fontsize=7.5, color=INK, va="center")
    import textwrap
    ax.text(13.5, tb_y0 + 1.6, "DRAWING", fontsize=6, color="#777")
    ax.text(13.5, tb_y0 + 5.4,
            textwrap.fill(title, 30) + "\nDimensioned layout plan", fontsize=6.8,
            color=INK, va="center")
    ax.text(31.5, tb_y0 + 1.6, "SCALE / DATE", fontsize=6, color="#777")
    ax.text(31.5, tb_y0 + 5.4, "N.T.S. (scale bar)\n07-08-2026", fontsize=7.5,
            color=INK, va="center")
    ax.text(45.5, tb_y0 + 1.6, "STATUS", fontsize=6, color="#777")
    ax.text(45.5, tb_y0 + 5.4, "Concept for review —\nto be verified by the\nproject architect",
            fontsize=7, color=INK, va="center")

    # room schedule (right margin block)
    sched = [(r.name.title(), r.dims, r.area) for r in rooms
             if r.zone not in ("circ",) and r.name and r.area > 8]
    sched.sort(key=lambda t: -t[2])
    lines = ["ROOM SCHEDULE", "—" * 34]
    for name, dims, area in sched[:22]:
        nm = (name[:20] + "…") if len(name) > 21 else name
        lines.append(f"{nm:<22s} {area:>4.0f} sf")
    ax.text(50.5, 108.5, "\n".join(lines), fontsize=6.2, color=INK, va="top",
            family="monospace", linespacing=1.35)

    ax.set_xlim(-11.5, 62)
    ax.set_ylim(141, -12)     # inverted: south at top, matching the architect's sheet
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_base + ".png", dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return total
