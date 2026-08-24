---
name: hospital-floorplan
description: Generate or revise the Solaris Shine 7th-floor hospital floor plans (Dr. Aman Khanna). Use whenever the user asks to change rooms, regenerate plan sheets, blueprints, DXF, contractor schedules, or scores for this project. Covers the verified Rev C envelope, the render pipeline, and the Rayon-style SVG blueprint spec.
---

# Hospital floor-plan pipeline (Solaris Shine, 7th floor)

All source lives in `floorplan/`; outputs go to `deliverables/`. Work on
branch `claude/hospital-floorplan-design-p9mczs`, commit and push when done.

## Fixed truth — do not re-derive
- Envelope Rev C (builder-confirmed): 48'-6" (south) x 92'-0" (east), west
  facade tapers 48'-6"→31'-0", curved NW corner. Defined once in
  `plan_model.py` (`PLATE_PTS`, `CUTOUT`, `MD_DOOR`, glass bands) and
  mirrored in `outline_sheet.py`. Main entry: east wall, 43'-0"–48'-0" from
  the south corner. Cut-out/service void at (25'-7" E, 40'-0" S), ~18'-4"x8'.
  Visitor WC = common-area toilets outside the unit.
- The unit is builder clinics x05+x06+x07; `deliverables/typical_floor_builder_extract.dxf`
  is the calibrated builder geometry (feet) for overlay checks.

## How to change the design
1. Edit the room list in `plan_model.py` (`layout_e_rooms()` is the live
   plan). Rooms are `Room(key, name, dims, (x, y, w, h), zone, doors=[...],
   furniture=[...], holes=[...])` in FEET, x from the east wall westward,
   y from the south wall northward. Doors: `(cx, cy, width, wall NSEW)` on a
   real shared wall. Nested toilets = separate wet Room + same rect in the
   parent's `holes`.
2. Check: no solid-room overlaps (intersection area > 2 sf is a bug).
3. Regenerate (from `floorplan/`):
   - `python3 -c "from render import render_layout; render_layout('E','../deliverables/layout_E_final')"` — CAD sheet PNG/SVG
   - `python3 blueprint_svg.py` — Rayon-style blueprint SVGs (spec below)
   - `python3 -c "from dxf_export import export_dxf; print(export_dxf('E','../deliverables/layout_E_final.dxf'))"` — must print 0
   - `python3 -c "from render3d import render_3d; render_3d('E','../deliverables/3d_layout_E.png')"`
   - `python3 setting_out.py` — contractor setting-out + door schedule PDF
   - `python3 -c "from score import comparison_table; print(comparison_table()[0])"` — HospitalEdgeWeigths corridor-L1 scores
4. Visual check every regenerated PNG (Read it) before delivering.

## Blueprint SVG output spec (AI-CAD / Rayon style)
Self-contained SVG only — no external refs. Double-line walls come from
`wall_bands()` fills; door swing arcs; thin parallel window lines on the
glass facade; labeled furniture bounding boxes; explicit dimension lines
with oblique ticks; "ROOM — W x D" labels; scale bar; north arrow. Two
themes in `blueprint_svg.py`: blueprint (white on #0d2a4a) and clean.
Rasterize for checking with the preinstalled headless Chromium
(`/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell
--headless --no-sandbox --screenshot=... --window-size=700,1180 file://...svg`).

## Delivery
SendUserFile the PNG/PDF/DXF outputs; the design canvas (artifact
"Solaris Shine Floor Plate") is re-seeded from `canvas/` working files with
the design skill's helper and republished to the same URL with
`contract: "0.1.31"`, favicon 📐, capabilities omitted.
