"""Shared in-patient (IPD) helpers for Layouts G and H.

* TRUE: real furniture sizes (feet) - every IPD symbol is drawn at these sizes.
* span(): clear wall-face to wall-face distance measured on the room polygon
  (the polygons are built from the builder's DWG wall faces, so nothing is
  eyeballed).
* dim_string(): an in-room dimension string (ticks + feet-inches text).
* audit(): furniture inside the room, no furniture overlaps, bed heads on
  solid walls, furniture clear of walls / columns.
* save_sheet(): PNG + SVG + full-sheet JPG + IPD close-up JPG.
"""
import io
import os

from shapely.geometry import LineString, box

# real sizes, feet (width x length)
TRUE = {
    "bed": (3.25, 7.0),        # hospital bed 3'-3" x 7'-0"
    "locker": (1.5, 1.5),      # bedside locker 1'-6" x 1'-6"
    "sofa": (2.0, 5.5),        # attendant sofa-bed 2'-0" x 5'-6"
    "wardrobe": (2.0, 4.0),    # wardrobe 2'-0" x 4'-0"
}
DIM_COLOR = "#1b4f9c"

# Ar. Bankim Dave's IPD wing, sizes as printed on his drawing (09-01-2026);
# (room, E-W ft, N-S ft, beds, toilet as printed)
ARCHITECT = [
    ("Twin sharing room-1", 21.375, 9.0 + 2 / 12, 2, "6'-0\" x 5'-0\""),
    ("Twin sharing room-2", 18.0 + 4 / 12, 9.0, 2, "6'-0\" x 5'-0\""),
    ("Single room-4", 16.0, 9.0, 1, "about 6'-0\" x 5'-0\""),
    ("Single room-5", 14.0 + 8 / 12, 10.125, 1, "about 6'-0\" x 5'-0\""),
]


def fi(v):
    """feet -> 12'-6\" (nearest inch)."""
    n = int(round(v * 12))
    return f"{n // 12}'-{n % 12}\""


def span(poly, x, y, axis):
    """Clear span of `poly` through (x, y): axis 'x' = east-west, 'y' = north-south.
    Returns (lo, hi) of the segment that contains (or is nearest to) the point."""
    if axis == "x":
        line = LineString([(x - 200, y), (x + 200, y)])
    else:
        line = LineString([(x, y - 200), (x, y + 200)])
    seg = line.intersection(poly)
    if seg.is_empty:
        return None
    geoms = [g for g in (seg.geoms if hasattr(seg, "geoms") else [seg]) if g.geom_type == "LineString"]
    i = 0 if axis == "x" else 1
    p = x if axis == "x" else y
    best = min(geoms, key=lambda g: 0 if g.bounds[i] - 1e-6 <= p <= g.bounds[i + 2] + 1e-6
               else min(abs(g.bounds[i] - p), abs(g.bounds[i + 2] - p)))
    return best.bounds[i], best.bounds[i + 2]


def dim_string(ax, poly, x, y, axis, fs=5.4, at=0.5, off=0.42, color=DIM_COLOR, z=12.5):
    """Draw a wall-to-wall dimension string through (x, y); returns its length."""
    a, b = span(poly, x, y, axis)
    t = 0.22
    if axis == "x":
        ax.plot([a, b], [y, y], color=color, lw=0.55, zorder=z)
        for s in (a, b):
            ax.plot([s - t, s + t], [y + t, y - t], color=color, lw=0.9, zorder=z)
        ax.text(a + (b - a) * at, y - off, fi(b - a), ha="center", va="center", fontsize=fs,
                color=color, zorder=z + 0.1,
                bbox=dict(fc="white", ec="none", pad=0.25, alpha=0.9))
    else:
        ax.plot([x, x], [a, b], color=color, lw=0.55, zorder=z)
        for s in (a, b):
            ax.plot([x - t, x + t], [s + t, s - t], color=color, lw=0.9, zorder=z)
        ax.text(x - off, a + (b - a) * at, fi(b - a), ha="center", va="center", fontsize=fs,
                color=color, rotation=90, zorder=z + 0.1,
                bbox=dict(fc="white", ec="none", pad=0.25, alpha=0.9))
    return b - a


def toilet_size(poly, step=0.125):
    """Largest clear rectangle (E-W, N-S) inside a toilet polygon and its area.
    Columns standing in the toilet are already cut out of `poly`; the rectangle
    with the largest short side wins, so a column corner is never counted."""
    minx, miny, maxx, maxy = poly.bounds
    rows = []
    yy = miny + step / 2
    while yy < maxy:
        seg = LineString([(minx - 1, yy), (maxx + 1, yy)]).intersection(poly)
        gs = [g for g in (seg.geoms if hasattr(seg, "geoms") else [seg]) if g.geom_type == "LineString"]
        g = max(gs, key=lambda g: g.length)
        rows.append((g.bounds[0], g.bounds[2]))
        yy += step
    best = (0, 0, 0.0, 0.0)
    for i in range(len(rows)):
        lo, hi = rows[i]
        for j in range(i, len(rows)):
            lo, hi = max(lo, rows[j][0]), min(hi, rows[j][1])
            if hi <= lo:
                break
            w, d = hi - lo, (j - i + 1) * step
            key = (round(min(w, d), 2), w * d)
            if key > best[:2]:
                best = key + (w, d)
    return best[2], best[3], poly.area


def bed_head_box(f):
    kind, x, y, w, h, rot = f
    if w > h:
        return box(x - 0.45, y, x + 0.1, y + h) if rot == 180 else box(x + w - 0.1, y, x + w + 0.45, y + h)
    return box(x, y - 0.45, x + w, y + 0.1) if rot == 180 else box(x, y + h - 0.1, x + w, y + h + 0.45)


def audit(rooms, walls, glass=None, zones=("inpatient", "wet")):
    """Checks on the IPD rooms. `glass`: shapely geometry of the glass lines (buffered)."""
    from itertools import combinations
    issues, beds, heads_ok = [], 0, 0
    for r in rooms:
        if r.zone not in zones:
            continue
        p = r.poly
        boxes = []
        for f in r.furniture:
            kind, x, y, w, h, rot = f
            b = box(x, y, x + w, y + h)
            out = b.difference(p.buffer(0.02)).area
            if out > 0.03:
                issues.append(f"{r.key}: {kind}@({x},{y}) is {out:.2f} sf outside the clear room")
            if b.intersection(walls).area > 0.03:
                issues.append(f"{r.key}: {kind}@({x},{y}) hits a wall / column")
            boxes.append((kind, b))
            if kind == "bed":
                beds += 1
                hd = bed_head_box(f)
                ok = hd.intersection(walls).area > 0.25 * min(w, h)
                if glass is not None and hd.intersection(glass).area > 0.01:
                    ok = False
                heads_ok += ok
                if not ok:
                    issues.append(f"{r.key}: bed head @({x},{y}) is not on a solid wall")
            if r.zone == "inpatient":
                std = {"bed": TRUE["bed"], "wardrobe": TRUE["wardrobe"]}.get(kind)
                if kind == "side":
                    std = TRUE["locker"]
                if std and sorted((round(w, 2), round(h, 2))) != sorted(std):
                    issues.append(f"{r.key}: {kind} drawn {w}x{h}, true size {std[0]}x{std[1]}")
        for (ka, a), (kb, b) in combinations(boxes, 2):
            if a.intersection(b).area > 0.03:
                issues.append(f"{r.key}: {ka} overlaps {kb}")
    return issues, beds, heads_ok


def save_sheet(fig, ax, out_base, window=None, crop_path=None, dpi=200, hd=300, min_w=2400):
    """PNG + SVG at `dpi`, full-sheet JPG (>= min_w px wide, quality 92) and, when
    `window` = (x0, x1, y0, y1) in plan feet is given, a close-up JPG crop."""
    import matplotlib
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    fig.savefig(out_base + ".png", dpi=dpi, bbox_inches="tight", facecolor="white")
    fig.savefig(out_base + ".svg", bbox_inches="tight", facecolor="white")
    fig.canvas.draw()
    bb = fig.get_tightbbox(fig.canvas.get_renderer())
    pad = matplotlib.rcParams["savefig.pad_inches"]
    buf = io.BytesIO()
    fig.savefig(buf, dpi=hd, bbox_inches="tight", facecolor="white", format="png")
    buf.seek(0)
    im = Image.open(buf).convert("RGB")
    full = im
    if im.width > 3600:
        full = im.resize((3600, round(im.height * 3600 / im.width)), Image.LANCZOS)
    assert full.width >= min_w, full.width
    full.save(out_base + ".jpg", quality=92, optimize=True)
    if window and crop_path:
        x0, x1, y0, y1 = window
        pts = [ax.transData.transform(p) for p in ((x0, y0), (x1, y1))]
        px = sorted((p[0] / fig.dpi - (bb.x0 - pad)) * hd for p in pts)
        py = sorted(im.height - (p[1] / fig.dpi - (bb.y0 - pad)) * hd for p in pts)
        crop = im.crop((max(0, int(px[0])), max(0, int(py[0])),
                        min(im.width, int(px[1])), min(im.height, int(py[1]))))
        crop.save(crop_path, quality=92, optimize=True)
        return crop.size
    return full.size
