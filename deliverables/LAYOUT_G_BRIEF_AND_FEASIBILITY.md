# Layout G — brief and feasibility

> **Revision 17-11-2026 (IPD fix).** The ward in this brief is superseded by `IPD_COMPARISON.md`, `layout_G_detailed.jpg` and `ipd_G.jpg`: ward furniture is now drawn at true size, the ward toilets are 5'-0" deep and 6'-0" to 6'-9" long (were 5'-5" x 9'-0"), the suite bath is 7'-0" x 6'-0" wheelchair size, Room 3's door is at the south end of its passage wall, and Store / Duty room / Pantry changed size slightly. Room positions and bed count (5) are unchanged. The text and tables below were not rewritten.

Solaris Shine, 7th floor, Althan, Surat · Dr. Aman Khanna (Orthopaedics) and Dr. Heena (Psychiatry) · 17-11-2026

Layout G puts the clients' sketches on the builder's real geometry (walls, columns, cut-out, lift core) instead of the Rev C outline that Layout F used.

- Drawings: `layout_G_detailed.png/.svg` (dimensioned sheet), `layout_G_detailed.dxf` (feet, audit 0 errors), `layout_G_blueprint.svg/.png`, `layout_G_clean.svg`, `3d_layout_G.png`.
- Model: `floorplan/layout_g.py` → `layout_g_rooms()`, key `'G'` in `LAYOUTS`. Run `python3 layout_g.py` in `floorplan/` to reprint every number quoted below.

## 1. Sources and which one wins

| Source | Used for |
|---|---|
| Builder DWG, typical 5th/7th/10th floor (`floorplan/source/solaris_typical_5_7_10.dxf`, plus column tags and toilet-slab hatches read from the full DWG) | Outline, columns, cut-out, existing walls, toilet slabs, lift core |
| 3rd sketch: blue pen over the DWG print | South block (OT, OPD, lounge, passage, cut-out area). Takes precedence there |
| Blue-pen sketch on the border-only sheet (same sketch as Layout F) | North (IPD) block, unchanged; room names |

## 2. Building geometry read from the DWG

Origin: outer face of the east and south walls. x runs west, y runs north. DWG mm → feet: `x = (X − 6002130) / 304.8`, `y = (−206361 − Y) / 304.8`. Inner plastered faces are at 0.39 ft (120 mm).

- **Extent over walls:** 47'-11¾" on the south, 92'-2¾" on the east. Clear floor inside the walls, less the cut-out: 3,570 sf.
- **West facade:** one straight line, 1.73 in of x per foot of y, with a 4'-11" radius corner at the north-west.
- **Cut-out:** starts 24'-8" from the east wall, between 40'-1" and 48'-1" from the south wall (17'-3" × 8'-0").
- **Entry:** the 8'-0" common passage between units x06 and x05 is a dead end serving only these units. The 5'-0" main door closes its mouth on the east wall line, 43'-0" to 48'-0" from the south corner (same as Rev C).
- **Columns (14):** grid A on the east wall, grid B at 20'-3" to 22'-10" from the east wall, and the facade columns. Rows 1 to 6 are at about 1', 21', 39', 49', 70' and 91' from the south wall. Sizes are taken from the plaster line, so they include plaster.
- **Existing toilet slabs (150 mm raised):** x07 south-east corner, x06 beside the cut-out, x05 south-east corner with its duct.
- **Lift core:** four lift shafts back onto the east wall between 8' and 37' from the south corner; lifts open east into the lift lobby, with two stairs beyond.

### Rev C against the DWG

| Item | Rev C | DWG | Difference |
|---|---|---|---|
| South width | 48'-6" | 47'-11¾" over walls | Rev C +6.2" (it follows the glass line, which sits about 6.7" outside the wall face) |
| East length | 92'-0" | 92'-2¾" over walls | Rev C −2.6" |
| West facade, 0' to 85' north | — | — | Rev C is 6" to 9" further west |
| West facade at 39' (beside the cut-out) | — | — | Rev C +18.4" (it has a kink the building does not have) |
| Cut-out east edge | 25'-7" | 24'-8" | Rev C 11.5" too far west |
| Cut-out south / north edges | 40'-0" / 48'-0" | 40'-1" / 48'-1" | about 1" |

Rev C also had no columns, no lift core and no existing walls.

## 3. What was read from the 3rd sketch (south block)

Positions are feet from the east and south wall faces, read off the print and then snapped.

| Blue line | Read as | Snapped to |
|---|---|---|
| Long vertical just west of the centre columns, south wall to ≈30' | OT and recovery west wall | West face of grid-B columns (22'-10") |
| No new line on the x07/x06 party wall | Wall kept; OT stops at it | Existing wall at 19'-10" |
| Horizontal from the east wall to that vertical at ≈30'-6" | North wall of store + recovery | 30'-7" |
| Existing x06 east wall, left in place | OT store (strip behind the lifts) / recovery divider | Existing wall at 8'-4" |
| Two verticals ≈3'-4" apart, ≈27' and ≈30'-6" from the east wall | Staff strip beside the OT, then the OPD passage | Staff strip 3'-7½", passage widened to 5'-0" (see issue 1) |
| Horizontals at ≈5'-6", ≈9'-7" (wavy) and ≈16'-8" across the strips | Autoclave across the top; scrub; OT change; air-lock | 5'-6", 9'-7", 16'-8" |
| Heavy blob on the strip divider just south of the party wall | Door from the passage into the OT air-lock | Door at 18'-5" |
| Vertical ≈38' from the east wall, south wall to ≈10'-6" | Splits the top-west block in two | 38'-0" |
| Horizontal at ≈10'-6" to the glass | Lounge block / OPD 3 divider | 10'-1" |
| Horizontal at ≈30'-1" from the strip divider to the glass | OPD 1 / waiting divider | 30'-1" |
| Two small rectangles near the glass | Examination couches: the two rooms are OPDs | — |
| Corner at ≈36' north, running west to the strip divider, and its vertical on grid B | Reception box behind the grid-B column; lobby turns west in front of it | 36'-3", grid B |
| Two long verticals through the north block | Ward passage walls on the column grid | 13'-11" and 20'-3" (grid B face); 6'-0" clear |

### Lines that could not be interpreted

1. **Short line across the lift-back strip at ≈34'-7"** (inside the X-ray room as built). Drawn dashed as a screen, not a wall.
2. **The grid-B vertical continuing across the entry passage.** A wall there would only close the 4' dead end beside the cut-out. Drawn dashed; the dead end is shown as a trolley / wheelchair bay.
3. **Short horizontal at ≈26'-4" inside the passage strip, and the cross lines at 9'-7" and 16'-8" where they cross the passage.** Not built (they may be door lines).
4. **Which of the two narrow strips is the passage.** Read as staff strip next to the OT and passage next to the OPDs, the same order as the earlier sketch. If it is the other way round the wall positions stay but the staff rooms and OPD doors swap sides.
5. **The two top-west rooms carry no names.** Read as Drs' lounge (off the passage) and Drs' rest + WC behind it.
6. **X-ray room edges.** The sketch gives its south wall only. Its west wall is set on the ward-passage line and the x06 east wall is removed inside it, to keep the room the earlier sketch showed.

## 4. Room schedule (clear sizes, wall face to wall face)

| Room | Size | Area (sf) |
|---|---|---|
| Operation theatre | 22'-6" × 19'-5" | 434 |
| OT store (strip behind lifts) | 7'-11" × 10'-5" | 82 |
| Recovery / pre-op, 2 beds | 13'-7" × 10'-5" | 141 |
| X-ray / dressing / emergency | 13'-11" × 8'-9" | 122 |
| Autoclave / CSSD | 9'-0" × 5'-1" | 46 |
| Scrub | 3'-8" × 3'-9" | 14 |
| OT change | 3'-8" × 6'-9" | 24 |
| OT air-lock | 3'-8" × 2'-9" | 10 |
| OPD 2 · plaster bay | 3'-8" × 10'-5" | 38 |
| Drs' lounge | 5'-5" × 9'-9" | 52 |
| Drs' rest + WC | ≈8'-1" × 9'-9" | 54 + 21 WC |
| OPD 3 · Psychiatry (Dr. Heena) | ≈12'-9" × 9'-4" | 119 |
| OPD 1 · Ortho (Dr. Aman) | ≈11'-1" × 9'-11" | 109 |
| Reception | 6'-3" × 3'-6" | 19 |
| Patient WC (builder's x06 toilet, kept) | ≈5'-7" × 4'-0" | 22 |
| Waiting area, 19 seats | open plan | — |
| BP / ECG | 7'-6" wide, L-shape | 61 |
| Pharmacy | 5'-8" × 6'-9" | 38 |
| Observation bed | 7'-0" × 3'-8" | 25 |
| Staff change | 5'-10" × 6'-5" | 37 |
| Nursing station | 7'-4" × 6'-5" | 47 |
| Store | ≈4'-1" × 6'-8" | 27 |
| Duty Dr / staff rest (bunk) | 8'-2" × 6'-8" | 54 |
| Suite bath | 5'-10" × 5'-5" | 32 |
| Pantry | 7'-4" × 5'-5" | 40 |
| Room 1 + accessible toilet | ≈19'-2" × 10'-5" | 149 + 40 |
| Room 2 + toilet | ≈17'-7" × 10'-5" | 141 + 36 |
| Room 3 + toilet | ≈16'-1" × 10'-3" | 123 + 32 |
| Room 4 + toilet | ≈14'-6" × 11'-2" | 121 + 30 |
| Suite room 5 (L-shape) | ≈19'-11" × 12'-8" | 212 |

Rooms total 2,562 sf on 3,570 sf of clear floor. No two rooms overlap by more than 0.5 sf (computed).

**Beds:** 5 in-patient (Rooms 1 to 4 and the suite). Also 2 recovery / pre-op trolleys, 1 observation bed, and 2 staff rest beds (duty bunk, Drs' rest).

## 5. Decisions

1. **OT size.** 22'-6" × 19'-5" (434 sf) instead of the 20' × 20' written on the earlier sketch, because the 3rd sketch keeps the party wall and puts the west wall beyond the columns. The grid-B column at the south wall stands 1'-2" into the OT's south-west corner.
2. **OPD passage** widened from about 3'-3" as drawn to 5'-0"; the OPD rooms lose about 1'-9" of width.
3. **OT routes.** Patients: lobby → recovery → OT through two 5'-0" double doors in line. Staff: OPD passage → air-lock → change → scrub → OT. OT store opens to the OT through the builder's x07 door opening.
4. **Entry lobby** runs south from the entry passage in line with the ward passage (5'-7" clear), through a new opening in the x06 north wall, then west past reception to the waiting area.
5. **Existing x06 toilet kept** as a patient WC off the waiting area. It is on its own slab and shaft, and Layout F had no patient toilet.
6. **BP / ECG is L-shaped** around the x05 duct, which has to stay, and uses the builder's x05 door opening. The observation bay is 7'-0" long so a real bed fits.
7. **Ward block** as the blue-pen sketch: 6'-0" passage with its west wall on the grid-B column face; Room 2/3 wall on grid row 5; toilets paired back-to-back at the glass end; bed heads on solid walls.
8. **Doors.** 5'-0" double: OT and recovery. 4'-0": X-ray. 3'-6": ward rooms, suite. 3'-0": OPDs, BP, all ward toilets (opening outward).

## 6. Feasibility

**Checked by computation**

| Check | Result |
|---|---|
| Ward passage, minimum clear width | 6'-0" |
| OPD passage | 5'-0" |
| South lobby | 5'-7" |
| Entry passage | 7'-11½" |
| Every door sits on a wall, none inside a room | yes (37 doors and openings) |
| Travel, far corner of the suite to the main door | 74 ft (22.5 m), path clear of walls |
| Travel, same point to the nearest stair | ≈122 ft (≈37 m); stair position approximated from the DWG core |
| DXF audit | 0 errors |

**Issues, most serious first**

| # | Issue | Why it matters | Suggested fix |
|---|---|---|---|
| 1 | The band between the OT and the OPD rooms is ≈7' wide in the sketch for two strips | Scrub is 14 sf and OPD 2 is a 3'-8" bay, not a consulting room; a 3'-3" passage would not take a wheelchair | Give the band 10' (staff strip 4'-6" + passage 5'), or move OPD 2 into the lounge block |
| 2 | Travel distance to a stair ≈37 m | NBC limit for hospitals is commonly taken as 30 m; the unit has one exit on a dead-end passage | Fire consultant to check; confirm sprinklers and the refuge area beside the lifts |
| 3 | X-ray room is 122 sf (11.3 m²), 8'-9" deep | AERB asks about 18 m² with no side under 4 m for a fixed unit | Mobile / portable unit only, or take 4'-6" from recovery (one trolley) |
| 4 | New ward toilets are at the glass, away from the builder's three shafts | Drains need a raised floor and long runs; core cuts need the builder's consent | MEP design before fixing toilet positions; Suite bath and BP side are near the x05 duct |
| 5 | OT depth is 19'-5", and a column stands in its corner | 7" short of the 20' asked for | Accept, or move the party wall 7" north |
| 6 | Lift shafts back directly onto the OT and OT store | Noise and vibration | Acoustic lining on the east wall |
| 7 | Drs' rest is reached only through the lounge; store only through staff change; staff change only through the nursing station | Rooms in series | Accept, or re-plan with the clients |
| 8 | Reception is 19 sf | One seat only | Extend it into the lobby band, or use the dead end beside the cut-out |
| 9 | Waiting seats 19 | Layout F showed 24 | Bench seating along the lobby band |
| 10 | Walls to be removed are assumed non-structural 100 mm masonry | Read from the DWG wall layer only | Structural engineer to confirm |

## 7. Comparison with Layout F

| | Layout F | Layout G |
|---|---|---|
| Outline | Rev C (glass line, 6" to 18" too wide on the west) | Builder DWG wall faces |
| Columns, lift core, existing walls | not shown | shown; walls snapped to them |
| South block source | blue-pen sketch on the border sheet | 3rd sketch over the DWG print |
| OT | 20'-0" × 20'-0", 400 sf | 22'-6" × 19'-5", 434 sf |
| OPD 1 / OPD 3 | 119 / 125 sf | 109 / 119 sf |
| OPD 2 | 9'-2" square | 3'-8" × 10'-5" bay |
| Recovery | 13'-10" × 9'-10" | 13'-7" × 10'-5" |
| X-ray | 131 sf | 122 sf |
| BP / ECG | 5'-10" wide | 7'-6" wide, 61 sf |
| Observation bay length | 6'-5" (bed did not fit) | 7'-0" |
| Ward toilet doors | 2'-10" | 3'-0", Room 1 toilet accessible size |
| Patient toilet in the unit | none | existing x06 toilet kept |
| Ward passage / OPD passage | 6'-0" / 5'-0" | 6'-0" / 5'-0" |
| In-patient beds | 5 | 5 |
| Rooms / clear floor | ≈2,700 sf on ≈3,730 sf (Rev C, overstated) | 2,562 sf on 3,570 sf |

## 8. Please confirm

- The reading of the two narrow strips (item 4 in section 3) and the two unnamed top-west rooms.
- What the short line at ≈34'-7" in the strip behind the lifts is.
- Whether the line across the entry passage on grid B is a wall, a counter or only a guide line.
- OT 22'-6" × 19'-5" in place of 20' × 20'.
- Fixed or portable X-ray.

Concept drawing for discussion. Structure, shafts, fire and AERB / clinical-establishment compliance need checking by the licensed architect and consultants before construction.
