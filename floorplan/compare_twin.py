"""Side-by-side, same-scale check: architect Twin 1 vs Layout H Twin 1 (beds, lockers, wheelchair circle)."""
import sys, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon as MPoly
from shapely.geometry import box, Point, Polygon
from shapely.ops import unary_union
import plan_model as p

def free_circle(floor, obstacles):
    free = floor.difference(unary_union(obstacles))
    minx, miny, maxx, maxy = floor.bounds
    best = (0, None); step = 0.1
    x = minx
    while x <= maxx:
        y = miny
        while y <= maxy:
            pt = Point(x, y)
            if free.contains(pt):
                d = pt.distance(free.boundary)
                if d > best[0]: best = (d, (x, y))
            y += step
        x += step
    return best  # radius, centre

COL = {"bed": "#ffffff", "side": "#d9c9a8", "wardrobe": "#b8956a", "sofa": "#9fb7c9", "chair": "#9fb7c9"}

def draw(ax, floor, furn, title, extra_obst=(), notes=()):
    minx, miny, maxx, maxy = floor.bounds
    ax.add_patch(MPoly(list(floor.exterior.coords), fc="#f4f1ea", ec="black", lw=2.2))
    for h in floor.interiors:
        ax.add_patch(MPoly(list(h.coords), fc="#dfe9ee", ec="black", lw=1.5, hatch="//"))
    obs = []
    for k, x, y, w, h in furn:
        ax.add_patch(Rectangle((x, y), w, h, fc=COL.get(k, "#ccc"), ec="#333", lw=0.8))
        ax.text(x + w / 2, y + h / 2, k, ha="center", va="center", fontsize=6.5)
        obs.append(box(x, y, x + w, y + h))
    obs += list(extra_obst)
    r, c = free_circle(floor, obs)
    ax.add_patch(Circle(c, 2.5, fc="none", ec="#c0392b", lw=1.6, ls="--"))
    ax.add_patch(Circle(c, r, fc="#e74c3c", alpha=0.18, ec="none"))
    ax.text(c[0], c[1], f"largest clear\ncircle {2*r:.1f} ft\n(need 5.0)", ha="center", va="center", fontsize=8, color="#7b1f14")
    ax.set_title(title, fontsize=11, loc="left")
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    ax.set_aspect("equal", adjustable="box"); ax.set_xlim(cx - 17, cx + 17); ax.set_ylim(cy - 8.5, cy + 8.5)
    ax.grid(True, lw=0.3, alpha=0.5); ax.set_xticks(range(int(cx) - 15, int(cx) + 16, 5)); ax.set_yticks(range(int(cy) - 8, int(cy) + 9, 4))
    ax.text(cx - 16.5, cy - 8.0, "  ".join(notes), fontsize=8, va="top")
    return 2 * r

# --- Layout H Twin 1, from the live model ---
rs = {r.key: r for r in p.LAYOUTS["H"][1]()}
t = rs["twin1"]
floor = t.poly
hf = [(f[0], f[1], f[2], f[3], f[4]) for f in t.furniture]
# --- Architect twin 1, reconstructed from printed size 21'-4.5" x 9'-2" (toilet is a separate band per his drawing) ---
W, D = 21.375, 9.17
afloor = box(0, 0, W, D)
bed_y = D - 7.0
af = [("bed", 6.5, bed_y, 3.25, 7.0), ("side", 9.75, D - 1.5, 1.5, 1.5), ("bed", 11.25, bed_y, 3.25, 7.0),
      ("side", 14.5, D - 1.5, 1.5, 1.5), ("wardrobe", 0.0, D - 2.0, 4.0, 2.0), ("chair", 17.0, D - 1.5, 1.5, 1.5)]
fig, axs = plt.subplots(2, 1, figsize=(14, 15), dpi=110)
d1 = draw(axs[0], afloor, af, f"ARCHITECT  Twin sharing room-1  21'-4\" x 9'-2\"  ({W*D:.0f} sf, 2 beds, toilet 6' x 5' in a separate band, not counted)  [furniture reconstructed from the printed size]",
          notes=("Foot aisle behind beds: %.1f ft" % (bed_y), "Between beds: 3.5 ft (incl. locker)"))
d2 = draw(axs[1], floor, hf, f"LAYOUT H  Twin Sharing 1  clear floor {floor.area:.0f} sf net of the 6' x 7' accessible ensuite, 2 beds ({floor.area/2:.0f} sf/bed)",
          notes=("Beds 3'-3\" x 7'-0\", lockers 1'-6\", wardrobe 2' x 4', sofas 2' x 5'-6\"",))
axs[0].set_xlabel("feet, both panels at the same scale (1 grid square = 1 ft)")
fig.suptitle("Same-scale check: architect vs Layout H twin room, with 5'-0\" wheelchair turning circle", fontsize=13)
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig("../deliverables/twin_compare.jpg", dpi=110, pil_kwargs={"quality": 92})
print("architect circle %.1f ft | H circle %.1f ft | areas %.0f vs %.0f" % (d1, d2, W*D, floor.area))
