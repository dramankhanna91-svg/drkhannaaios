# Layout H — the architect's plan improved, on the builder's DWG geometry

> **Revision 17-11-2026 (IPD fix).** The ward in this brief is superseded by `IPD_COMPARISON.md`, `layout_H_detailed.jpg`, `ipd_H.jpg` and `layout_H_schedule.md`: Layout H now has **8 in-patient beds in 4 twin rooms, not 10 in 5**. The 10-bed ward only fitted with under-size bed, locker and wardrobe symbols; at true size the west side takes three twin rooms 13'-7" to 15'-0" deep (94 to 122 sf per bed, three 6'-0" x 7'-0" wheelchair toilets). Everything south of the ward is unchanged. The text and tables below were not rewritten.

Solaris Shine, 7th floor, Althan, Surat · Dr. Aman Khanna (Orthopaedics) and Dr. Heena (Psychiatry) · 17-11-2026

Base plan: Ar. Bankim Dave, "Proposed Layout Plan for the Hospital of Dr. Aman Khanna at 7th floor", dated 09-01-2026.
Geometry: `floorplan/source/solaris_typical_5_7_10.dxf` (builder's DWG, mm).

Drawings: `layout_H_detailed.png/.svg` (dimensioned sheet), `layout_H_detailed.dxf` (AutoCAD, feet; layers COLUMNS, CORE, PLUMBING_EXIST added), `layout_H_blueprint.svg/.png`, `layout_H_clean.svg`, `3d_layout_H.png`, `layout_H_schedule.md` (machine-written schedule and check log).
Model: `floorplan/layout_h.py` → `layout_h_rooms()`; build and checks: `cd floorplan && python3 build_h.py`.

## 1. Result in one paragraph

Layout H keeps the three things the clients liked in the architect's plan — the 20'-0" × 17'-0" OT, twin-sharing rooms on the west glass, and a 12'-0" wide public passage — and re-plans around them. It gives **10 in-patient beds in 5 twin rooms, every one with a window and its own toilet, plus 2 recovery beds** (architect: 9 beds in 7 rooms; Singles 1 and 2 sit on the east party wall with no window, and Single 1 has no ensuite). The OT is reached only through Recovery (patients) or Change → Scrub (staff), CSSD is beside it, and soiled goods leave by a separate 3'-6" passage. Three things do not comply or could not be solved and are listed in section 7: a fixed AERB X-ray room does not fit, the unit has a single exit with a 43' dead-end ward passage, and OPD 1 is only 95 sf.

## 2. Geometry check: DWG against Rev C

Origin of the repo coordinates on the DWG: x = 0 at the outer plaster face of the east wall (X = 6,002,110 mm), y = 0 at the outer plaster face of the south wall (Y = −206,341 mm). All sizes below are measured from the DXF, not scaled off an image.

| Item | Rev C (repo) | DWG | Difference |
|---|---|---|---|
| Length, south to north, over plaster | 92'-0" | 92'-4¼" (28,150 mm) | DWG 4¼" longer |
| Width at the south wall, over plaster | 48'-6" | 48'-1½" (14,666 mm); 48'-7¼" to the glass line | Rev C 4½" wider than the plaster line, 1¼" narrower than the glass line |
| West facade at y = 10' / 20' / 30' | 47'-4" / 45'-10" / 44'-4" | 46'-8" / 45'-3" / 43'-9" | Rev C 6" to 7½" wider |
| West facade at y = 50' / 60' / 70' / 80' | 41'-6" / 39'-11" / 38'-6" / 37'-1" | 40'-11" / 39'-5½" / 38'-0" / 36'-7" | Rev C 5" to 7" wider |
| West facade beside the cut-out (y = 39') | 43'-10½" | 42'-6" | Rev C 16½" wider (Rev C has a kink there; the DWG facade is one straight line) |
| North wall: end of the straight part | 31'-0" | 30'-5½" | Rev C 6½" longer |
| Cut-out, east edge | 25'-7" | 24'-9¼" | Rev C 10" too far west |
| Cut-out, south and north edges | 40'-0" and 48'-0" | 40'-2¾" and 48'-1¼" | 1¼" to 2¾" |
| Gross area over plaster | 3,871 sf | 3,824 sf | Rev C 47 sf larger |
| Main entry | 5'-0" door at 43'-0" to 48'-0" | Common passage 7'-10½" clear, 40'-2¾" to 48'-1¼" | Layout H uses a 6'-0" pair at 41'-2" to 47'-2" |

Rev C is good to about 7" everywhere except at the cut-out. It appears to follow the glass line at the south and drifts outside the plaster line further north. Layout H is drawn on the DWG values; layouts A–F are untouched and still use Rev C.

**Taken from the DWG and shown on the sheet:** 14 RCC columns (black with red edge), the four lifts and duct behind the east wall, the cut-out, the glass line, and the builder's three toilet positions and one duct (150 mm raised slab: SE corner of x07, beside the cut-out in x06, east wall of x05). The dead-end lobby in front of x06/x07 (7'-10½" × 19'-10½") and the common passage up to the cut-out are taken into the unit, as the clients said they may.

## 3. What changed against the architect's plan, and why

| # | Architect (09-01-2026) | Layout H | Why |
|---|---|---|---|
| 1 | OT 20' × 17' mid-east; its only door opens on the 12' public passage where patients wait | OT 20' × 17' in the SE corner; doors only from Recovery, Scrub and Dirty Utility | Nobody walks from a public area straight into the OT |
| 2 | Recovery 10'-5½" × 6'-1", across the public passage from the OT | Recovery / Pre-op 14'-1" × 9'-7" (135 sf, 2 beds) against the OT; 5'-0" double doors in line | Post-op trolley never crosses the public area |
| 3 | "Autoclave + Scrub" 10'-8" × 5'-0", reached by the 3'-0" passage, not adjoining the OT | Change (57 sf) → Scrub (33 sf) → OT; CSSD (40 sf) beside the OT with a pass box; sterile store | Correct staff sequence; CSSD beside OT |
| 4 | No dirty route | Dirty Utility (53 sf) off the OT → 3'-6" service passage → door just inside the main entry | Soiled goods and waste leave without crossing recovery, waiting or OPD |
| 5 | 12'-1½" passage north–south, used for waiting; no daylight | 12'-0" concourse east–west, 15 seats, ends on the west glass | Keeps the wide passage; the waiting area gets daylight and no trolley route crosses it |
| 6 | X-ray / dressing 9'-6" × 6'-1" (58 sf), far end | X-ray / dressing / plaster 9'-6" × 12'-0" (115 sf) at the mouth of the concourse, 4'-0" door | Twice the size and next to the entry; still not a fixed-unit room (section 5) |
| 7 | Doctor room 15' × 13'-1" + 3 OPDs; 3'-0" passage to two of them | 3 OPDs on the west glass off a 6'-0" passage; no separate doctor room | Daylight in every consulting room; the 3' passage is gone. Cost: Dr. Aman loses the large cabin |
| 8 | Psychiatry not planned | OPD 3 at the dead end (120 sf, SW glass) behind its own closed sub-wait (54 sf, 3 seats); OPD 2 sits between it and ortho; plaster and dressing are about 45' away at the entry | Quiet, no through traffic, no procedure noise next door |
| 9 | Toilet beside the cut-out 5'-6" × 3'-10½" | Public accessible WC 6'-10" × 7'-3" on the same plumbing position, 3'-0" door opening out, 5'-0" turning circle | Wheelchair toilet for OPD |
| 10 | Ward passage 5'-0" (7'-9½" at the north end) | 6'-6" for its whole length | Bed trolley and a person can pass; brief asks for 6' minimum |
| 11 | Singles 1, 2, 3 on the east party wall (no window on that wall); Single 1 has no ensuite | No bed room on the party wall. East band holds pharmacy, staff WC, nursing station, clean utility, pantry | Every bed room has daylight |
| 12 | 2 twins + 5 singles = 9 beds | 5 twins = 10 beds; toilets 28 to 44 sf, one of them wheelchair-size (7'-3" × 6'-1", Twin 2) | One more bed and an ensuite for every room |
| 13 | Nursing station 7'-6" × 10'-0" behind a door | Open counter at the ward door, sees the whole passage and all five room doors | Supervision |
| 14 | Pharmacy 6'-9½" × 4'-1" inside, beside the cut-out | Pharmacy 6'-5" × 5'-11" with a hatch to the entrance lobby | On the way out |
| 15 | Builder's SE toilet kept as the doctor's toilet | Omitted (slab kept flush inside the OT). Staff WC + shower moves to the builder's x05 toilet | The OT needs the corner; cost: no toilet inside the OT complex |

## 4. Room schedule (clear sizes, east–west × north–south)

| Room | Size | sf |
|---|---|---:|
| Operation theatre | 20'-0" × 17'-0" | 340 |
| Recovery / Pre-op (2 beds) | 14'-1" × 9'-7" | 135 |
| Staff change | 6'-0" × 9'-7" | 57 |
| Scrub | 6'-0" × 5'-6" | 33 |
| CSSD / autoclave | 6'-0" × 6'-8" | 40 |
| Sterile store | 6'-0" × 4'-2" | 25 |
| Dirty utility | 5'-6" × 9'-7" | 53 |
| X-ray (mobile) / dressing / plaster | 9'-6" × 12'-0" | 115 |
| OPD 1 · Ortho (Dr. Aman) | 10'-9" avg × 8'-10" | 95 |
| OPD 2 (visiting consultant) | 12'-1" avg × 8'-4" | 101 |
| OPD 3 · Psychiatry (Dr. Heena) | 13'-4" avg × 9'-0" | 120 |
| Psychiatry sub-wait | 6'-0" × 9'-0" | 54 |
| Accessible public WC | 6'-10" avg × 7'-3" | 50 |
| Pharmacy | 6'-5" × 5'-11" | 38 |
| Staff WC + shower | 3'-10" × 7'-10" | 30 |
| Clean utility | 3'-10" × 8'-7" | 33 |
| Pantry | 6'-5" × 5'-9" | 37 |
| Twin sharing 1 (+ toilet 7'-0" × 6'-0", 42 sf) | 21'-6" avg × 10'-4" | 175 |
| Twin sharing 2 (+ accessible toilet 7'-3" × 6'-1", 44 sf) | 20'-0" avg × 10'-4" | 157 |
| Twin sharing 3 (+ toilet 5'-5" × 5'-7", 30 sf) | 18'-5" avg × 10'-0" | 150 |
| Twin sharing 4 (+ toilet 5'-5" × 5'-3", 28 sf) | 16'-7" avg × 11'-6" | 158 |
| Twin sharing 5 (+ toilet 6'-3" × 5'-8", 35 sf) | 10'-8" × 22'-11" | 205 |

Room areas exclude the nested toilet and its walls. Open areas (not rooms): 12'-0" waiting concourse, entrance lobby 7'-10½" deep with reception, nursing station alcove, 6'-0" OPD passage, 6'-6" ward passage, 3'-6" service passage.
Totals: rooms 2,392 sf + open areas and passages 999 sf + internal walls and columns 182 sf = 3,572 sf inside the external walls.

**Beds: 10 in-patient (5 twin rooms) + 2 recovery.** Waiting: 15 seats in the concourse + 3 in the psychiatry sub-wait.

Passage widths (clear): ward 6'-6"; concourse 12'-0"; gate from the lobby into the concourse 6'-1"; OPD passage 6'-0"; trolley route main door → lobby → gate → Recovery → OT has no point narrower than the 5'-0" double doors; service passage 3'-6" (bins only).

## 5. AERB (X-ray)

The room is 9'-6" × 12'-0" = 115 sf (10.6 m²). A fixed radiography installation needs about 18 m² (≈194 sf) with no side under 4 m, so **this room qualifies only for a mobile / portable unit**, and the rule that a mobile unit used permanently in one room is treated as a fixed installation should be checked with the AERB consultant before buying.

A 13'-3" × 14'-9" room (195 sf) fits in only one place on this plate: the NE corner beside the lift shaft, where the X-ray room is now. Putting it there takes the 3'-6" service passage and 2'-9" from Recovery (leaving 6'-10", too shallow for beds across), or pushes the OT 7'-2" north so that Recovery has to move to the OT's west side, which then blocks the way to the OPD rooms. I worked through both on paper and did not find a version that keeps the 20' × 17' OT, a two-bed recovery next to it, the dirty exit and three OPDs. If a fixed unit is essential, the honest options are a 20' × 15' OT, or one recovery bed.

## 6. Fire

- One exit from the unit: the main door into the common passage. The building's lift lobby is about 10' east of it; from the DWG the two staircases are roughly 30' and 55' from the main door (measured as a walking line on the DXF, not surveyed).
- Longest travel inside the unit to the main door, measured along a route drawn on the model (door to door, corridor centre lines): OPD 3 far corner ≈ 79'; Twin 4 far corner ≈ 76'; Twin 5 and Twin 3 ≈ 68'. Adding ≈ 30' to the nearer stair gives ≈ 109' (33 m) worst case.
- NBC 2016 gives 30 m as the travel-distance limit for institutional buildings as I recall it, with a relaxation for sprinklered buildings. I have not checked the current text or the Surat fire department's conditions, so treat the 30 m figure as something to confirm. On that figure the worst case is marginally over without the sprinkler relaxation.
- The ward passage is a 43' dead end (the architect's plan has the same condition). This needs the fire officer's view; a second door from the north end is not possible because unit x04 is on the other side of the party wall.
- A refuge area is shown on the DWG for the 7th floor, south of the lift core.

## 7. Feasibility

**Checked on the model (`build_h.py`)**: no solid-room overlap above 0.5 sf; no furniture outside its room, in a wall or in a column; no door in a column; all 12 beds have the head against a wall band and none against glass; DXF audit 0 errors.

| # | Issue | Why it matters | Suggested fix |
|---|---|---|---|
| 1 | X-ray room 115 sf | Not a fixed-unit AERB room (section 5) | Mobile DR unit; or accept a smaller OT / one recovery bed |
| 2 | Single exit, 43' dead-end ward passage, worst travel ≈ 109' to a stair | Fire NOC | Fire consultant; sprinklers and detection through the unit; ask the builder whether a fire door into x04's passage side is possible |
| 3 | OPD 1 is 95 sf and Dr. Aman has no separate cabin | Architect gave him 15' × 13' | Remove the OPD 1 / OPD 2 partition for one 196 sf cabin (leaves two consulting rooms), or swap so that he takes OPD 3 |
| 4 | Twin 3 and Twin 4 are tight (18'-5" and 16'-7" long): 2'-9" between beds in Twin 4, small toilets (28–30 sf) | Comfort | Run Twin 4 as a single deluxe → 9 beds |
| 5 | Twin 5 gets daylight only from its north end (10'-8" of window on a 22'-11" deep room) | Comfort | Acceptable; or use as single deluxe |
| 6 | Seven toilets, only three on the builder's raised-slab positions; the four west-side ensuites and Twin 5's are new wet points | Needs 150 mm raised floors and drain runs to the ducts or facade; slab cannot be sunk | Plumbing consultant; the architect's plan has the same condition |
| 7 | Recovery is also the patient route into the OT | A patient going in passes one coming out | One list at a time; curtain the two bays |
| 8 | Used instruments go OT → CSSD through the same pass box as sterile sets | No one-way CSSD flow | Acceptable for one OT; or add a second hatch |
| 9 | No toilet inside the OT complex | Staff must change out to use the staff WC by the nursing station | Accept, or take a WC from the Change room if a drain can reach it |
| 10 | Columns C3 (2'-7" × 2'-2") stands in the Staff Change room and C7, C13 inside toilets / entry nooks of Twin 1 and Twin 4 | Local pinch points; Twin 4 entry is 3'-9" clear with a 3'-6" door | Shown true to DWG; verify column sizes on site |
| 11 | Waiting is 18 seats | Architect's plan showed about the same; may be short on a busy OPD day | Add a second row at the west end (passage drops to about 8'-6") |

## 8. The clients' third sketch (blue pen over the DWG print)

How I read it (the photo has no room names, so this reading needs confirming): OT block east of the central column line in the south unit; one or two narrow strips just west of that column line running north–south (support rooms and a passage); a column of consulting rooms on the west glass, divided by cross lines at roughly 10', 20' and 31' from the south wall; a room in the SW corner (the lounge); and in the north unit two long lines about 5'-6" apart for the ward passage, with ward rooms divided on the column grid.

| Item | Sketch | Layout H | Same? |
|---|---|---|---|
| OT | SE, east of the column line | SE corner, 20'-0" × 17'-0", west wall on the column line | Yes |
| Support strip beside the OT | Narrow strip west of the column line | Sterile store / CSSD / Scrub / Change, 6'-0" wide, on that line | Yes |
| OPD column | On the west glass | On the west glass, three rooms | Yes, but H's rooms start at the south wall and stop at 27'-5"; the sketch runs them to about 31' |
| North–south passage | Runs from the south rooms up to the entry passage beside the cut-out | 6'-0" OPD passage stops at the 12'-0" east–west concourse | No. A straight run to the entry is blocked by column C5 and the cut-out (only 1'-10" between them), so the public must turn through the concourse |
| Lounge | SW corner | None. The SW corner is OPD 3 (psychiatry) because it is the quietest glass room | No. To follow the sketch: make the SW room the doctors' lounge and move psychiatry to OPD 2; H then has two OPDs + lounge, or the concourse loses its west end to a third OPD |
| Ward passage | About 5'-6" wide, 10'-6" to 16' from the east wall | 6'-6" wide, 11'-6" to 18'-0" from the east wall | Wider and 1'-0" further west, to give Twin 5 a workable width |
| Ward rooms | "As they are", divided on the column grid | Four rooms on the west glass with partitions landing on facade columns C10 and C11; one room on the north glass | Partly: partitions are on the grid, but the rooms are re-planned as twins with inboard toilets |

## 9. Not verified

- Site dimensions: everything is from the DWG, nothing was measured on site. Column sizes and the facade line should be checked before setting out.
- Slab levels, drain routes, and whether partitions and raised toilet floors are acceptable structurally.
- AERB, NBC / fire NOC and clinical-establishment rules: figures quoted are from memory and need a consultant's confirmation.
- Whether the common passage and x06/x07 lobby can legally be enclosed inside the unit (the clients say they can use them).
- The AI Plan Creator cross-check in the floorplan-builder skill was not run.
- The reading of the third sketch.

This is a concept drawing for discussion, to be verified by the licensed architect and consultants before construction.
