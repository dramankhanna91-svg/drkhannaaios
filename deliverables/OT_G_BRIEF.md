# Layout G — operation theatre suite brief

Solaris Shine, 7th floor, Althan, Surat · Dr. Aman Khanna (Orthopaedics) and Dr. Heena (Psychiatry) · 17-11-2026

The OT now measures 20'-0" × 20'-0" clear (400 sf, 37.1 m²), the scrub is 6'-1" × 8'-0" and OPD 2 is a 9'-0" × 10'-0" room. Getting there took seven changes to the clients' 3rd sketch, listed in section 5. The OT stays in the south-east, the CSSD and lounge in the top-west, and recovery north of the OT.

- Drawings: `ot_G_zone.jpg` (OT-zone close-up with dimensions, equipment and the four flow routes), `layout_G_detailed.png/.svg/.jpg/.dxf` (whole floor; DXF audit 0 errors).
- Model: `floorplan/layout_g.py`. `python3 layout_g.py` reprints every number below (`ot_suite` block); `python3 layout_g.py build` redraws the Layout G sheets.
- Guideline figures in this brief (NABH, HFG-India, AERB, NBC) are quoted from memory and marked **to verify**. Nothing here was checked against the published documents.

## 1. Room schedule

Clear sizes, plaster face to plaster face. Areas are net of columns.

| Room | Clear size | Area sf | Area m² | Notes |
|---|---|---|---|---|
| Operation theatre | 20'-0" × 20'-0" | 400 | 37.1 | Asked: 20' × 20' (≈ 36 m²) |
| Scrub / clean lobby | 6'-1" × 8'-0" | 49 | 4.5 | 3-tap trough outside the OT staff door |
| Pre-op / recovery | 12'-2" × 10'-0" | 121 | 11.3 | 2 bays: bay 1 pre-op / holding and patient change, bay 2 recovery |
| Anaesthesia / consumable store | 4'-7" × 10'-0" | 46 | 4.3 | Strip behind the lifts; opens to the OT only |
| CSSD clean side + sterile store | 6'-1" × 5'-1" | 29 | 2.7 | Pass box into the OT; door to the scrub |
| CSSD wash (dirty side) | 5'-0" × 5'-1" | 26 | 2.4 | Double-door autoclave in the wall to the clean side |
| Dirty utility | 6'-1" × 6'-2" | 36 | 3.4 | Door from the OT, door out to the OPD passage |
| Staff lobby (air-lock) | 5'-0" × 4'-3" | 21 | 2.0 | South end of the OPD passage, behind a new door |
| OT staff change + WC | ≈8'-1" × 9'-9" | 76 | 7.0 | Two curtained cubicles (M / F), two locker banks, WC |
| Drs' lounge | 5'-5" × 9'-9" | 52 | 4.9 | Unchanged |
| OPD 2 · plaster / procedure | 9'-0" × 10'-0" | 86 | 8.0 | Column C3 stands 1'-8" proud on the south wall; clear of it 9'-0" × 8'-4" |
| X-ray / dressing / emergency | 12'-4" × 8'-7" | 106 | 9.9 | Was 122 sf; mobile X-ray only |

OPD 1 (109 sf), OPD 3 (119 sf), reception, waiting, patient WC and the whole ward block are unchanged. No two rooms overlap by more than 0.5 sf (computed).

## 2. Inside the OT

Drawn at true size on `ot_G_zone.jpg`.

| Item | Size / position |
|---|---|
| OT table | 2'-0" × 6'-9", centred, head to the south |
| Clear round the table | 9'-0" to the east and west walls, 6'-7" south, 6'-8" north; 5'-3" to the wall cabinets |
| Pendants (circles) | P1 anaesthesia pendant at the head, P2 surgical pendant at the foot |
| OT light | Twin dome over the table (dashed circles) |
| Anaesthesia machine | 2'-2" × 2'-5" at the head |
| Instrument trolleys | Two, 1'-6" × 3'-0" |
| Mayo stand, diathermy / suction cart | 1'-4" × 1'-8"; 1'-6" × 1'-10" |
| C-arm parking bay | 2'-10" × 6'-0" on the east wall |
| Wall cabinets | 12'-0" × 1'-4" on the south wall, to be recessed in the panel lining |
| Control panel + X-ray viewer | East wall |
| Pass box | 2'-0" hatch in the west wall from the CSSD clean side |
| Doors | Patient: 5'-0" double sliding, hermetic, north wall. Staff: 3'-6" from the scrub. Soiled: 3'-0" to the dirty utility. Store: 3'-0" |
| Medical gas valve + alarm panel | Recovery side of the patient door |

Fixed items (cabinets, C-arm bay, control panel, pass box) are all outside the 4'-0" zone round the table (computed, 0 sf inside).

## 3. Flow routes

| Route | Path |
|---|---|
| Patient (blue) | Main door → entry passage → lobby → 4'-0" recovery door → pre-op bay → 5'-0" sliding door → OT → recovery bay → lobby → wards |
| Staff (green) | OPD passage → staff-lobby door → lounge → change → staff lobby → scrub → OT |
| Clean / sterile (teal) | CSSD wash → autoclave → CSSD clean side / sterile store → pass box, or through the scrub → OT. Consumables: store → OT |
| Dirty / soiled (red) | OT → dirty utility → OPD passage → lobby → main door → service lift. Instruments: dirty utility → OPD passage → staff lobby → CSSD wash, in a closed box |

Clean supply never leaves the staff band. The soiled route leaves the OT by its own door and does not pass through the scrub, the CSSD clean side or recovery.

## 4. Why the sketched band did not work

The sketch gives about 7' between the OT and the OPD rooms for two strips. With a 5'-0" passage that left a 3'-7½" staff strip: scrub 14 sf, OPD 2 a 3'-8" bay.

- **Scrub.** The OT was 22'-6" wide because its west wall was drawn beyond the grid-B columns. Putting that wall on the column line makes the OT exactly 20'-0" and the staff band 6'-1". The OPD rooms and the 5'-0" passage do not move.
- **OPD 2.** North of the OT there is only 20' to 21'-6" between the OT line and the glass, which cannot hold a 9' OPD 2, a 5' passage and OPD 1. OPD 2 is therefore moved east: it takes the west 9'-0" of the row north of the OT, and recovery moves east into most of the old OT store.

## 5. Deviations from the clients' 3rd sketch

Numbered as on `ot_G_zone.jpg` (magenta dash-dot lines are the sketched positions).

| # | Change | Amount | Effect |
|---|---|---|---|
| 1 | OT west wall moved east onto the grid-B column line | 2'-5¾" (29¾") | OT 22'-6" → 20'-0" wide; staff band 3'-7½" → 6'-1" |
| 2 | x07 / x06 party wall rebuilt further north | 7" | OT depth 19'-5" → 20'-0"; row north of the OT is 10'-0" deep |
| 3 | OT-store wall (builder's x06 east wall) moved east | 3'-4" | Store 7'-11" → 4'-7" wide; recovery takes the rest |
| 4 | X-ray west wall moved east | 1'-2" (14") | Makes room for the 4'-0" recovery door on the lobby; X-ray 122 → 106 sf; lobby 5'-7" → 7'-2" |
| 5 | OPD 2 moved out of the strip | — | 3'-8" × 10'-5" bay → 9'-0" × 10'-0" room, door on the OPD passage |
| 6 | Unnamed corner room re-used | — | Drs' rest + WC becomes OT staff change + WC; the Drs' rest bed is lost |
| 7 | New door across the OPD passage, about 9'-9" from the south wall face | — | The passage south of it is the staff lobby; OPD 1 and OPD 3 doors are north of it |

Also: the north wall of the recovery row sits 2" north of where it was, and autoclave / CSSD keeps its sketched place across the top of the band but is split into a wash side and a clean side.

## 6. Checks

**OT area.** 399.8 sf = 37.1 m² against the 20' × 20' (≈ 36 m²) asked for. This is masonry face to masonry face. Modular wall panels usually take 3" to 4" per wall (**to verify** with the OT vendor), which would leave about 19'-4" clear inside the lining.

**Columns inside the 20' × 20'.** Two corner nibs only: C1 stands 1.3" into the south-west corner over 13.8", C3 stands 1.3" into the north-west corner over 6.8". Both disappear behind the panel lining. No column stands in the floor of the OT.

**Door sizes in the suite.**

| Door | Width |
|---|---|
| OT patient door (recovery → OT) | 5'-0" double sliding |
| Recovery from the lobby | 4'-0" double |
| X-ray | 4'-0" |
| Scrub → OT, OPD 2, staff-lobby door | 3'-6" |
| OT → dirty utility, dirty utility → passage, scrub from the staff lobby, store → OT | 3'-0" |
| CSSD clean, CSSD wash, lounge | 2'-9" |
| Staff change | 2'-6" |
| Pass box | 2'-0" hatch |

**Travel distance.** OT far corner to the main door: 66 ft (20.2 m), path clear of walls (computed). To the nearest stair: about 115 ft (34.9 m); the stair position is approximated from the DWG core. NBC is commonly read as 30 m for hospitals (**to verify**); the unit has one exit.

**X-ray.** A fixed unit is commonly taken to need about 18 m² (194 sf) with no side under 4 m (13'-1") (**AERB, to verify**).

| Option | Result |
|---|---|
| Mobile / portable unit in the room as drawn | 106 sf. Recommended; the C-arm covers imaging in the OT |
| Push the room 2'-0" north into the entry passage, east of the main door | 12'-4" × 10'-7", 131 sf. Still short |
| Take the whole recovery row east of the lobby as well | 12'-4" × 19'-0", 234 sf, but 12'-4" is under 13'-1" and recovery has to go to OPD 2's room, so OPD 2 is lost |

A fixed X-ray room does not fit in Layout G without giving up recovery or OPD 2.

**Ventilation / HVAC plant (note only, not designed).** From memory, **to verify**: an OT of this class is usually designed for 20 to 30 air changes an hour through ceiling HEPA filters, at positive pressure. For 400 sf with a 10' ceiling that is roughly 1,300 to 2,000 cfm. Space to allow:

- A dedicated air-handling unit, about 5' × 8' plus service clearance (≈ 8' × 11'). The only places are a platform over the cut-out (17'-3" × 8'-0", needs the builder's consent) or hung above the scrub / dirty utility if the ceiling void allows.
- Condensing units on the service ledge (1'-11" deep) or the cut-out.
- Return-air risers in the OT corners, about 1' × 1' each; the two column corners suit.
- About 2' of ceiling void over the OT and the staff band; floor-to-floor height is not known.
- A medical gas cylinder manifold and the UPS / isolation panel. No space is drawn for the manifold.

## 7. What the plan does not achieve

Most serious first.

| # | Issue | Why it matters | Suggested fix |
|---|---|---|---|
| 1 | No separate clean corridor; the scrub doubles as the clean lobby | A full corridor needs about 5' × 20' that the plate does not have | Accept for a single-OT unit, or give up OPD 2 |
| 2 | Soiled goods leave by the public OPD passage and lobby; instruments cross the staff lobby | There is no second exit from the suite | Closed containers and timed removal; no layout fix found |
| 3 | Staff change is one room with two curtained cubicles, reached through the lounge | Separate M / F rooms with their own toilet do not fit | Accept, or take the lounge as well |
| 4 | Recovery bays are 5'-0" wide; pre-op shares the room | Guidance is usually nearer 8' per bay (**to verify**) | One 10' bay, or accept |
| 5 | Recovery door from the lobby is 4'-0", not 5'-0" | A 5'-0" door needs the X-ray wall moved a further 12" | Decide with the X-ray choice |
| 6 | OPD 2 has column C3 on its south wall | Clear rectangle is 9'-0" × 8'-4"; the sink counter and trolley use the two recesses | Accept |
| 7 | Sterile store shares the CSSD clean side (29 sf); the consumable store opens only into the OT | Restocking goes through the OT out of hours | Accept, or lose a recovery bay for a store door |
| 8 | X-ray room is smaller (106 sf) | Mobile unit only | See section 6 |
| 9 | Scrub, dirty utility and CSSD need drains but are 20' or more from the builder's shafts | Raised floor or runs in the ceiling below | MEP design before the walls are fixed |
| 10 | The builder's x07 toilet slab (150 mm raised) lies in the OT's south-east corner | Has to be broken out and levelled, drains capped | Structural / plumbing check |
| 11 | Lift shafts back onto the OT east wall | Noise and vibration | Acoustic lining; cabinets or the C-arm bay on that wall |
| 12 | Party wall and three other walls move; a beam probably runs on grid row 2 | Assumed non-structural 100 mm masonry, read from the DWG wall layer only | Structural engineer to confirm |
| 13 | Travel to a stair ≈ 35 m, one exit | See section 6 | Fire consultant |

## 8. Alternative that keeps the OT at 22'-6"

Leave the OT west wall as sketched and widen the band westward instead. The 6'-0" scrub then comes out of the OPD rooms: OPD 3 drops from 12'-9" to about 10'-4" wide and OPD 1 from 11'-1" to about 8'-8" (≈ 86 sf). The OT would be 22'-6" × 20'-0" (450 sf), which leaves room for the panel lining. Not drawn.

## 9. Please confirm

- OT 20'-0" × 20'-0" between masonry faces, or the 22'-6" alternative in section 8.
- Giving up the Drs' rest room for the OT staff change.
- OPD 2 on the lobby side, north of the OT, with the column on its south wall.
- Mobile X-ray, and the X-ray room at 106 sf.
- Whether the door across the OPD passage is acceptable (the lounge then sits inside the staff zone).

Concept drawing for discussion. Structure, shafts, fire, AERB, HVAC and clinical-establishment compliance need checking by the licensed architect and consultants before construction.
