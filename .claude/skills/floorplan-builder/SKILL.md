---
name: floorplan-builder
description: Build a dimensioned clinic/hospital floor plan from a client sketch, an architect's PDF/image, or a DWG. Use when the user uploads a plate outline, sketch or DWG and wants rooms, beds, toilets, OT/OPD zoning, feasibility, DXF/SVG/PNG output, or a cross-check in AI Plan Creator. Covers DWG conversion, brief, layout, MCP cross-check, scoring.
---

# Floor-plan builder (full pipeline)

Project: Solaris Shine 7th floor, Dr. Aman Khanna (ortho) + Dr. Heena (psychiatry). Units: feet in the repo model, mm in the DWG. Existing engine: `floorplan/` (see the `hospital-floorplan` skill for Rev C plate, render and DXF audit).

## 0. Ask first (do not skip)
Confirm: source layout (client sketch / architect plan / compare), plate outline source (DWG, Rev C), priorities (beds, comfort, clean/dirty flow, code), and the open items: duty-room use, which OPD is whose, fixed vs portable X-ray, single vs twin rooms.

## 1. Get the exact outline
- DWG is not readable by ezdxf. Convert: build LibreDWG once (`curl -L https://github.com/LibreDWG/libredwg/releases/download/0.13.3/libredwg-0.13.3.tar.xz`, `./configure --disable-bindings --disable-python -q && make -j8`), then `programs/dwg2dxf -y --as r2000 -o out.dxf in.dwg`. Needs user approval for the build.
- Units are mm. The sheet holds many floors; find the plan by MTEXT labels (e.g. "5TH, 7TH & 10TH FLOOR PLAN", "505 CLINIC") and cut by bounding box (typical-floor block: x 5,975,000–6,040,000, y -236,000…-200,000). Keep layers DR - WALL, PLASTER LINE, GLASS, COLUMN, CUT OUT, STAIR, DOOR.
- Saved extract: `floorplan/source/solaris_typical_5_7_10.dxf`. East wing = clients' units 705/706/707 (≈ 28,000 mm = 92'-0"), matching Rev C, so Rev C stays the source of truth.
- Clients may use adjoining lobby and move the walls between 705–707.

## 2. Read the brief
Read sketches literally (positions, adjacency), then complete each room: beds with head on a solid wall, ensuite WC/basin/shower, doors, furniture. Record every decision where the sketch is silent. Reference: `deliverables/LAYOUT_F_BRIEF_AND_FEASIBILITY.md`.

## 3. Build
- Repo engine: add `layout_x_rooms()` in `floorplan/plan_model.py`, register in `LAYOUTS`, run render/blueprint/DXF/3D (audit must be 0, no overlaps).
- AI Plan Creator MCP (metres; origin NW corner; x east, y south): `get_account` → `create_design` (type clinic or medical-centre) → `set_plot` (rectangle 14.8 × 28.0 m) → `design_level`/`add_rooms` with room list and areas → `add_constraint` (min-area, adjacent) → `show_design`. It cannot take a tapered or curved outline and its services layouts are schematic. Use it as a cross-check, not the final drawing.

## 4. Check and score
Compare options on: bed count, patient comfort (daylight, ensuite, quiet psychiatry), clean/dirty flow (OT via recovery and change, CSSD beside OT), code (AERB X-ray ≈ 18 m² for fixed unit, passages ≥ 1.8 m for trolleys, fire travel distance, accessible toilet). Say plainly what does not comply.

## 5. Deliver
Dimensioned PNG/SVG, DXF (feet), room schedule, feasibility table, questions. Commit on the session branch; no PR unless asked.
