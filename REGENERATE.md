# Regenerating Dr. Khanna's hospital plan — Solaris Shine, 7th floor

Source of truth: repo `dramankhanna91-svg/drkhannaaios`,
branch `claude/hospital-floorplan-design-p9mczs`, folder `floorplan/`.
Everything below is pure Python (CPU-only — no GPU/VPS needed).

## 1. Setup

```bash
python3 -m pip install shapely matplotlib numpy ezdxf pillow
```

(Tested with shapely 2.1, matplotlib 3.11, numpy 2.4, ezdxf 1.4.)

## 2. Regenerate every output

Run from inside `floorplan/` (outputs land in `../deliverables/`):

```bash
mkdir -p ../deliverables
python3 - <<'EOF'
import os
from render import render_layout          # 2D CAD sheet (PNG + SVG)
from render3d import render_3d            # 3D axonometric view
from dxf_export import export_dxf         # AutoCAD R2018 DXF (feet)
from score import comparison_table        # corridor-L1 flow scores

OUT = os.path.abspath(os.path.join(".", "..", "deliverables"))
path = os.path.join(OUT, "layout_E_final")
render_layout("E", path)                              # layout_E_final.png/.svg
print("DXF audit errors:", export_dxf("E", path + ".dxf"))
render_3d("E", os.path.join(OUT, "3d_layout_E.png"))  # <-- the 3D image
table, _ = comparison_table()
open(os.path.join(OUT, "flow_scores.md"), "w").write(
    "# Key clinical-flow travel distances (corridor L1 metric)\n\n" + table + "\n")
EOF
python3 blueprint_svg.py      # layout_E_blueprint.svg + layout_E_clean.svg (Rayon-style)
python3 interiors.py          # 4 enlarged interior boards (PNG)
python3 setting_out.py        # contractor_setting_out.pdf (setting-out + door schedules)
python3 area_statement.py     # floor_space_calculation.pdf (computed areas)
python3 options_board.py      # OPD/OT brainstorm board (historical)
python3 trace_sheet.py        # A4 1:100 tracing sheet PDF
```

Optional PNG of the blueprint SVG (any browser works; headless Chromium shown):

```bash
chromium --headless --no-sandbox --force-device-scale-factor=2 \
  --screenshot=layout_E_blueprint.png --window-size=700,1180 \
  "file://$PWD/../deliverables/layout_E_blueprint.svg"
```

## 3. What the model encodes (do not change casually)

- `plan_model.py` is the single source of truth. **Rev C envelope**
  (builder-confirmed): 48'-6" south x 92'-0" east, west facade tapering
  48'-6" -> 31'-0", curved NW corner; cut-out/service void at the waist;
  main door 5'-0" on the east wall at y 43'-48'.
- Coordinates in feet: x from the EAST wall increasing westward, y from the
  SOUTH wall increasing northward; sheets render south-up like the
  architect's drawing.
- The live plan is `layout_e_rooms()` = **LAYOUT E (rev 3)**: OT 20'x20'
  pod (entry ONLY via Recovery / Scrub), OPD 1-4 + doctors' lounge
  (lounge on the SW glass, private door from OPD 3; OPD 4 with attached
  WC off the link corridor), 216 sf glass waiting + overflow, pharmacy at
  the entry, 4 ensuite rooms + suite + nursing/obs in the ward wing.
- To revise the plan: edit the `Room(...)` entries in `layout_e_rooms()`
  (rect = (x, y, w, h) feet; doors = (cx, cy, width, wall N/S/E/W);
  nested toilets = a wet Room plus the same rect in the parent's `holes`),
  then rerun step 2. Check for overlaps first:

```bash
python3 - <<'EOF'
from plan_model import LAYOUTS, solid_rooms
from itertools import combinations
rooms = solid_rooms(LAYOUTS["E"][1]())
bad = [(a.key, b.key, a.poly.intersection(b.poly).area)
       for a, b in combinations(rooms, 2)
       if a.poly.intersection(b.poly).area > 0.01]
print("overlaps:", bad or "none")
EOF
```
