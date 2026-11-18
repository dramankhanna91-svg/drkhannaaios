# Layout I — pencil sketch with blue-pen sizes, large waiting hall at the entry

Solaris Shine, 7th floor, Althan, Surat · Dr. Aman Khanna (Orthopaedics) and Dr. Heena (Psychiatry) · 18-11-2026

Drawings: `layout_I_detailed.png / .svg / .jpg / .dxf` (whole floor), `ot_I_zone.jpg` (OT zone and waiting hall with the four flows), `layout_I_blueprint.svg / .png`.
Model and checks: `floorplan/layout_i.py` (`cd floorplan && python3 layout_i.py build`). Geometry, columns and the whole IPD block are imported from `layout_g.py`; Layouts G and H are not changed.
Geometry source: builder's DWG extract `floorplan/source/solaris_typical_5_7_10.dxf`. Nothing was measured on site.

Orientation used below is the DWG's: the lift core and main door are on the **east** wall, the tapering glass is on the **west**. On the sketch south is at the top, so east is on the left.

## 1. Result

- **Waiting: 19 seats** — 16 in the entry hall (two rows of 8) and 3 sub-wait seats in the OPD lobby. This is 1 short of the 20–30 target. With the clients' 7 ft + 20 ft + 7 ft the hall is 12'-7" deep and takes two rows; a third row (24 + 3 = 27 seats) needs 1'-5" more.
- **OT: 20'-0" × 20'-0" clear, 400 sf (37.1 m²)**, with an 11-room suite of 844 sf.
- **Beds: 5 in-patient** (4 single rooms + suite) **+ 2 pre-op / recovery + 1 observation**; 1 duty bunk for staff. Single rooms, not twins: the rooms are 10'-3" to 11'-2" deep and a true-size twin needs about 13'-7" (Layout H).
- All eight blue-pen sizes are built exactly and their sum closes on the DWG (section 2).
- The trolley route to the OT does not cross a seat row. It shares a 5'-2" lane with OPD walkers.
- X-ray is a mobile-unit room; a fixed AERB room does not fit.

## 2. Reading of every mark on the sketch

### Blue pen (sizes in feet, as the clients confirmed)

| Mark | Where written | Applied to | Built | Fit to the DWG |
|---|---|---|---|---|
| 20 (twice) | In the OT and on its east wall | Operation theatre | 20'-0" × 20'-0" | West face on the grid-B column line; column C3 is 1⅜" proud in that wall. Exact |
| 7 (first read as X) | East wall beside AUTOCLAVE | CSSD / autoclave row, depth | 7'-0" | The builder's x07 toilet block ends 6'-6" from the south wall, so the row is 6" deeper than it. Exact as built |
| 7 (first read as X) | East wall beside RECOVERY | Recovery, depth | 7'-0" | No DWG wall on this line; the north wall lands 8" short of the end of the x06 east wall. Exact as built |
| 8 (twice) | At the entry | Entry passage | 8'-0" | The builder's common passage is 8'-0" clear. Exact |
| 4.5 with arrows | OPD passage | Passage width | 4'-6" | New partitions. Exact as built |
| 8.1 | Glass side, beside ticks 3 and 4 | OPD 2 and OPD 1, depth along the glass | 8'-1" each | No DWG wall on these lines. Exact as built |
| 9.3 | Glass side, beside ticks 2 and 1 | Emergency / dressing, depth | 9'-3" | Exact as built |
| 5.9 | Under 9.3 | X-ray room, depth, at the cut-out end | 5'-9" | Its north face is the existing x06 north wall. Exact |
| 1, 2, 3, 4 with ticks | Glass side, one per room | Room order from the cut-out: 1 Emergency / X-ray, 2 OPD 1, 3 OPD 2, 4 Lounge | — | Order kept. Read as room numbers, not sizes |
| Blue line through Recovery | About 8 ft from the east wall | Wall between recovery bay and pre-op | On the x06 east wall line (8'-6") | Matches an existing 100 mm wall |
| "Rec" + short blue line | East of the cut-out | Reception counter | 4'-0" × 7'-11" pocket between columns C5 and C7 | Fits |
| Circled 10 with a stroke, at the seat rows | East end of the seats | Not applied | — | **Could not read.** Possibly 10 seats per row; a row holds 8 at 1'-10" |

**Sum check, glass side.** Lounge + OPD 2 + OPD 1 + Emergency + X-ray + four 4½" partitions = 6'-8" + 8'-1" + 8'-1" + 9'-3" + 5'-9" + 1'-6" = 39'-4", which is the DWG clear depth from the south wall to the x06 north wall. The lounge takes the remainder (6'-8"); the sketch draws it about 7'-6".

**Sum check, east side.** 7'-0" + 20'-0" + 7'-0" + three partitions = 35'-1½"; the hall then runs 12'-7" to the north face of the 8'-0" passage.

**Uncertain, kept as notes.**
- "9.3 / 5.9" is read as two depths because the room label has two lines (Emergency, X-ray room) and the five depths then sum exactly. Other readings: one room 9'-3" × 5'-9"; or OPD 1 = 9'-3", which leaves the Emergency + X-ray end 12'-10" with no use for 5.9. Metres do not fit (8.1 m and 9.3 m exceed any room here).
- "8.1" is applied to both OPD rooms. If it was meant for the lounge too, the OPD rooms stay and the Emergency room loses 1'-5".
- The width of the X-ray room at the cut-out end is 9'-9", not 9'-3"; a 5'-0" passage instead of 4'-6" would make it 9'-3".

### Pencil

| Sketch | Built | Deviation |
|---|---|---|
| AUTOCLAVE in the SE corner | CSSD row 20'-0" × 7'-0": wash (on the builder's toilet slab, the only drain there), clean / pack with a pass-through autoclave, sterile store | Split into three rooms |
| OT about 24' wide to the passage | OT 20'-0" wide; the 6'-1" gained is the staff band: change, scrub, anaesthesia store, dirty utility | As in Layouts G and H |
| Recovery below the OT, arrow into the OT | Recovery bay (1 bed) + pre-op / holding (1 bed) with the transfer zone in line with the 5'-0" OT door | 5'-8" × 2'-0" door recess in its NW corner |
| Two rows of seats across the hall | Two rows of 8 against the recovery wall, 4'-0" aisle | Rows stop 5'-2" short of the west side for the lane |
| Change room beside the passage | Staff change across the south end of the band, with the staff lobby closing the passage | Moved 6' east so the OT is reached only through it |
| Lounge, OPD 2, OPD 1, Emergency / X-ray on the glass | Same order | OPD 2 is taken as psychiatry (two OPD rooms only) |
| Thick bar on the south wall, arrow into the OT's SW corner | Staff door from scrub | Bar not identified (window or locker) |
| Ticks along the passage beside OPD 1 and Emergency | 3 sub-wait seats, on the lobby wall instead | The 4'-6" passage has no room for seats |
| North block: Ph, Pharmacy, NS + bed, Store, 2-bed room, Bath, Pantry, Rooms 1–4, Suite 5 | Layout G's block unchanged, except "Ph" | "Ph" (BP / ECG in G) becomes the accessible patient WC |

## 3. Room schedule (clear, east–west × north–south)

| Room | Clear size | sf | Notes |
|---|---|---:|---|
| Operation theatre | 20'-0" × 20'-0" | 400 | 5'-0" sliding door from pre-op; 3'-6" from scrub; 3'-0" each to sterile store and dirty utility; 2'-9" to anaes. store |
| Pre-op / holding + transfer | 11'-8" × 7'-0" | 72 | 1 bed; 4'-0" pair from the lane |
| Recovery bay | 7'-11" × 7'-0" | 55 | 1 bed; 3'-9" opening |
| Scrub | 6'-1" × 8'-0" | 49 | 3-tap trough |
| OT staff change M / F | 6'-1" × 7'-0" | 40 | One room; column C1 in a corner |
| Staff lobby | 4'-6" × 6'-8" | 30 | 3'-6" door across the passage |
| CSSD clean / pack + autoclave | 7'-6" × 7'-0" | 53 | Pass box to the OT |
| CSSD wash (dirty) | 6'-0" × 7'-0" | 42 | Dirty hatch from the OT |
| Sterile store | 5'-9" × 7'-0" | 40 | |
| Anaes. / consumable store | 6'-1" × 3'-4" | 20 | |
| Dirty utility | 6'-1" × 7'-11" | 43 | Column C3 takes 5.5 sf |
| **OT suite, 11 rooms** | | **844** | |
| Drs' lounge + WC | 14'-7" × 6'-8" | 72 + 21 | |
| OPD 2 · Psychiatry | 13'-3" × 8'-1" | 112 | |
| OPD 1 · Ortho | 10'-2" × 8'-1" | 98 | Clear of column C4; 12'-7" wide at mid-depth |
| Emergency / dressing | 10'-7" × 9'-3" | 104 | 4'-0" pair on the OPD lobby |
| X-ray (mobile) | 8'-7" × 5'-9" | 56 | Clear of column C6 |
| Patient WC (accessible) | 6'-2" × 7'-6" + lobby | 61 | Builder's x05 toilet slab |
| Entry waiting hall (open) | 19'-11" × 12'-7" | 250 | 16 seats |
| OPD lobby (open) | 11'-0" × 11'-7" | 128 | 3 seats |
| Pharmacy · Obs. bed · Nursing stn. | 5'-8" × 6'-9" · 7'-0" × 3'-8" · 7'-4" × 6'-5" | 38 · 25 · 47 | As Layout G |
| Staff change · Store · Duty room · Pantry | — | 37 · 24 · 49 · 37 | As Layout G |
| Rooms 1 / 2 / 3 / 4 | 19'-6" × 10'-5" / 17'-3" × 10'-5" / 16'-5" × 10'-3" / 14'-2" × 11'-2" | 153 / 145 / 120 / 117 | Net of ensuite (32–36 sf each) |
| Suite room 5 + bath | 19'-11" × 12'-8" | 212 + 42 | |

Rooms 2,560 sf + open areas 731 sf + walls and columns 279 sf = 3,570 sf inside the external walls.

## 4. Waiting

| Item | Value |
|---|---|
| Seats | 16 hall + 3 OPD sub-wait = 19 |
| Seat | 1'-10" × 1'-8" |
| Aisle between the rows | 4'-0" |
| Hall area per seat | 15.6 sf (250 sf / 16); seating zone alone 7.0 sf |
| Clear strip in front of the main door | 5'-3", no seat in it |
| Lane to the OPD lobby and pre-op door | 5'-2" beside the rows, no seat in it |
| Opening from the hall to the OPD lobby | 5'-0" (south of column C5) |
| Reception | Faces east: sees the main door along the passage and both rows |
| Wheelchair space | None marked; take the two west-end seats out for two spaces (17 seats) |

**To reach 24 hall seats** take 1'-5" from the 7' + 7': for example autoclave row 5'-7", or recovery 6'-3" and autoclave row 6'-4". Recovery is already tight (section 6), so the autoclave row is the one to shorten.

## 5. Checks

| Check | Result |
|---|---|
| Trolley route to the OT | Main door → 5'-3" strip → 5'-2" lane → 4'-0" pre-op door → 5'-0" OT door: 37 ft. Crosses no seat row; nearest seat 2'-9" from the centre line. Shared with OPD walkers in the lane |
| Recovered patient to ward | Same lane, straight across the entry strip into the 6'-0" ward passage |
| Staff | OPD lobby → passage → staff lobby → change → scrub → OT. No other way in |
| Clean supply | Wash → autoclave → clean / pack → pass box → OT; sterile store → OT |
| Dirty | Instruments by hatch to the wash room. Waste and linen: dirty utility → OPD passage → OPD lobby → lane → main door |
| OT | 400 sf; table to walls 9'-0" east and west, 6'-7" south, 6'-8" north; no fixed item inside the 4'-0" zone; no equipment clash |
| Columns | C3 is 1⅜" proud in the OT west wall. Inside rooms: C1 change, C2 lounge WC, C3 dirty utility, C4 OPD 1, C6 X-ray; ward columns as Layout G |
| Emergency / X-ray against AERB | X-ray 5.2 m², Emergency 9.7 m², together 14.9 m²; longest side 3.2 m. A fixed unit (about 18 m², no side under 4 m) **fails on area and width**. Mobile unit only |
| Emergency access | Main door to the Emergency door 47 ft, through the lane and the 5'-0" opening |
| Passage widths | OPD 4'-6", ward 6'-0", lane 5'-2", entry strip 5'-3", hall-to-lobby 5'-0" |
| Travel to the stair | OT far corner → main door 62 ft, → nearer stair about 110 ft (34 m). Suite far corner → main door 74 ft, → stair about 122 ft (37 m). Main door to stair is about 48 ft, taken from the DWG core outline |
| Model | No room overlap over 0.5 sf; no furniture in a wall, column or other item; all four flows pass only through doors; DXF audit 0 errors |

## 6. Issues

1. **19 seats, not 20–30.** Fixed by the clients' own 7' + 20' + 7'. See section 4.
2. **OPD passage 4'-6".** A wheelchair passes; a trolley and a person do not pass each other, and two wheelchairs cannot. Emergency and X-ray doors are on the lobby, not on this passage, so no trolley needs it. 5'-0" costs every glass-side room 6" of width.
3. **Recovery is 7'-0" deep.** A 6'-6" × 2'-2" trolley has a 6'-10" diagonal, so it only just turns into a bay. Pre-op and recovery are two small rooms rather than one room with two bays.
4. **Lane shared by trolleys and OPD patients**, and the soiled route uses the OPD lobby and the lane. Layout H has a separate soiled exit; here it needs time separation.
5. **CSSD staff reach the wash room through the sterile store and clean room.** The SE corner has no other access.
6. **OT has five doors and two hatches.** Fewer is better for pressure control; the anaesthesia store could be reached from the scrub instead.
7. **One staff change room of 40 sf**, no staff WC inside the suite (the lounge WC is across the staff lobby).
8. **Fixed X-ray does not fit**; the X-ray room stands on the builder's sunk x06 toilet slab, which must be filled, and its west wall is glass that needs lead lining.
9. **Patient WC replaces the BP / ECG room.** It is the only builder's toilet position at the hall once the x06 toilet becomes the X-ray room. If BP / ECG is wanted back, the choice is the x06 toilet (and no X-ray room) or the common toilets outside the main door.
10. **Only two OPD rooms.** Layout G had three (one plaster / procedure); plaster work moves to the Emergency room.
11. **Single exit and travel distance** above 30 m, as in G and H.
12. Carried from Layout G: observation bed is 6'-6" × 2'-11" and Room 4 has a 2'-6" wardrobe.

## 7. Comparison: I vs G vs H

| | Layout I | Layout G | Layout H |
|---|---|---|---|
| Waiting seats | 19 (16 entry hall + 3 OPD lobby) | 19 (OPD waiting area) | 17 (14 concourse + 3 psychiatry sub-wait) |
| Where patients wait | At the main door, in sight of reception | Behind the lobby, at the cut-out | 9'-0" concourse to the west glass |
| OT | 20'-0" × 20'-0" | 20'-0" × 20'-0" | 20'-0" × 20'-0" |
| OT suite | 844 sf, 11 rooms | 803 sf, 10 rooms | 774 sf, 10 rooms |
| Pre-op / recovery | 72 + 55 sf, 2 beds | 121 sf, 2 beds | 124 sf, 2 bays |
| OPD rooms | 2: 98 + 112 sf | 3: 109 + 119 + 86 sf | 3: 111 + 114 + 120 sf |
| Emergency / X-ray | 104 + 56 sf, on the glass | 106 sf, beside the main door | 86 sf, beside the concourse |
| BP / ECG | None | 61 sf | None |
| Drs' lounge | 72 sf | 52 sf | None |
| Patient WC | 61 sf accessible, at the hall | 22 sf, not accessible | 41 sf accessible |
| OPD passage | 4'-6" | 5'-0" | 6'-0" |
| In-patient beds | 5 (4 single + suite) | 5 | 8 (4 twin) |
| Recovery + observation | 2 + 1 | 2 + 1 | 2 + 0 |
| Separate soiled exit | No | No | Yes |
| OT far corner to stair | about 110 ft | about 115 ft | about 100 ft |
| Rooms / open floor | 2,560 / 731 sf | 2,571 / 720 sf | 2,438 / 931 sf |

**What the large waiting costs against G.** Total room area is almost the same (−11 sf). The hall takes the place of G's X-ray / dressing room and lobby; that room moves to the glass, where G had its waiting area. The price is one OPD room (G's 86 sf plaster room), the BP / ECG room, 6" of OPD passage, and a recovery suite 7'-0" deep instead of 10'-0". The seat count does not rise; the seats move to the entry.

**Against H.** Two more seats, a lounge and a larger OT suite, but 3 fewer in-patient beds, one fewer OPD room, a narrower OPD passage and no separate soiled exit.

## 8. Not verified

- NABH, HFG-India, AERB and NBC figures are from memory: 20' × 20' (about 36 m²) OT, 5'-0" OT door, 4'-0" clear round the table, 18 m² and 4 m side for a fixed X-ray room, 30 m travel distance, 5'-0" trolley passage.
- Site dimensions, column sizes, slab levels at the two sunk toilet slabs, service-ledge depth.
- Stair door positions and the true walking distance to them.
- Drain routes for the scrub, CSSD wash, sluice and lounge WC; OT air-handling plant; medical-gas manifold.
- The circled "10" at the seat rows, the bar on the south wall, and the choice between the readings of "9.3 / 5.9".

Concept drawing for discussion, to be verified by the licensed architect, the OT vendor and the consultants before construction.
