# Layout H — operation theatre and OT zone

Solaris Shine, 7th floor, Althan, Surat · Dr. Aman Khanna (Orthopaedics) and Dr. Heena (Psychiatry) · 17-11-2026

Drawings: `ot_H_zone.jpg` (OT-zone close-up, equipment key, dimensions, four flows), `layout_H_detailed.png/.svg/.jpg/.dxf` (whole floor; DXF layer `OT_KEY` carries the equipment key), `layout_H_schedule.md` (machine-written schedule and check log).
Model: `floorplan/layout_h.py`; OT sheet and OT checks: `floorplan/ot_h.py`; build: `cd floorplan && python3 build_h.py`.
Geometry: builder's DWG extract `floorplan/source/solaris_typical_5_7_10.dxf`. Nothing was measured on site.

## 1. Result

- **OT: 20'-0" × 20'-0" clear = 400 sf (37.2 m²)**, up from 20'-0" × 17'-0" (340 sf). The 20' × 20' target is met with no shortfall on plaster faces.
- The OT sits in the SE corner exactly between column lines C1 and C3, so **no column stands inside it**. The east face of C1 and C3 is 1½" proud of the 4½" west wall; the wall panel covers it.
- **Beds: 8 in-patient (4 twin rooms) + 2 pre-op / recovery bays. Unchanged** — the whole rework is south of the entrance lobby.
- Three OPD rooms and the closed psychiatry sub-wait are kept. OPD 1 grows from 95 to 111 sf.
- The 60 sf for the OT came from the waiting concourse (12'-0" → 9'-0" wide) and the X-ray room (115 → 86 sf).

## 2. Room schedule (clear, east–west × north–south)

| Room | Size | sf | Before | Notes |
|---|---|---:|---:|---|
| Operation theatre | 20'-0" × 20'-0" | 400 | 340 | 5'-0" pair to the transfer bay, 3'-5" staff door from scrub, 3'-0" to sterile store, 3'-0" to dirty utility |
| Pre-op / recovery + transfer bay | 12'-11" × 9'-7" | 124 | 135 | 2 trolley bays (1 holding, 1 recovery) on the east wall; 5'-10" lane with the red line; 5'-0" pairs in line |
| Staff change | 7'-8" × 9'-7" | 55 | 57 | M and F locker banks; includes column C3 (about 4 sf) |
| Staff WC (inside the complex) | 3'-3" × 4'-10" | 15 | none | New wet point |
| Scrub bay | 6'-0" × 4'-7" | 28 | 33 | 3-tap trough beside the staff OT door |
| CSSD clean (pack, sterile) | 6'-0" × 5'-2" | 31 | 40 (one room) | Pass box to the OT, hatch to the sterile store |
| CSSD wash (dirty side) | 6'-0" × 4'-9" | 28 | — | Dirty return hatch from the OT; door from the OPD passage; pass-through autoclave in the wall to the clean side |
| Sterile store + consumables | 6'-0" × 4'-5" | 27 | 25 | Opens only into the OT |
| Anaesthesia store | 6'-0" × 3'-2" | 19 | none | Reached through the sterile store |
| Dirty utility | 5'-0" × 9'-7" | 48 | 53 | Sluice, waste hold; exit to the 3'-6" service passage |
| **OT suite, rooms only** | | **774** | 683 | |
| X-ray (mobile) / dressing / plaster | 9'-6" × 9'-0" | 86 | 115 | |
| OPD 1 · Ortho | 10'-5" avg × 10'-8" | 111 | 95 | |
| OPD 2 | 11'-11" avg × 9'-7" | 114 | 101 | |
| OPD 3 · Psychiatry | 13'-4" avg × 9'-0" | 120 | 120 | |
| Psychiatry sub-wait | 6'-0" × 5'-6" | 33 | 54 | 3 seats; door now opens out |
| Accessible public WC | 6'-9" avg × 6'-0" | 41 | 50 | 5'-0" turning circle still fits |
| Waiting concourse | 9'-0" wide | — | 12'-0" | 14 seats (was 15) |

Ward, pharmacy, nursing station and entrance lobby are as in `IPD_COMPARISON.md`. Floor totals: rooms 2,438 sf + open areas 931 sf + walls and columns 203 sf = 3,572 sf.

## 3. OT equipment drawn (true plan sizes; numbers as on `ot_H_zone.jpg`)

1 OT table 2'-7" × 6'-6", head to the south, away from the door · 2 Mayo stand · 3 twin-dome light · 4 anaesthesia machine at the head · 5 anaesthesia pendant · 6 surgical pendant · 7 instrument trolley · 8 back table · 9 diathermy / suction cart · 10 C-arm parking 2'-10" × 6'-0" on the east wall · 11 C-arm monitor cart · 12 two recessed wall cabinets 5'-6" on the south wall · 13 writing shelf, control panel, X-ray viewer · 14 sterile pass box · 15 dirty return hatch · 16 scrub trough · 17 medical-gas zone valve box and alarm panel outside the OT door · 18 pass-through autoclave · 19 transfer bay.

Table to wall: east 8'-8", west 8'-8", south 6'-6", north 7'-0"; 5'-2" to the nearest fixed cabinet. The 4'-0" clear ring is met against walls and fixed items; trolleys and the anaesthesia machine stand inside it, as they do in use.

## 4. Flows (coloured arrows on `ot_H_zone.jpg`)

| Flow | Route | Crosses |
|---|---|---|
| Patient (blue) | Lift → main door → lobby → 6'-1" gate → 5'-0" pair → transfer bay (red line) → 5'-0" hermetic pair → OT → recovery bay → same way out | Staff route in the lobby and gate only |
| Staff (green) | Concourse → OPD passage → staff change (lockers, WC) → scrub → 3'-5" door → OT | Nothing inside the suite |
| Clean supply (purple) | CSSD wash → pass-through autoclave → CSSD clean → pass box → OT; or → hatch → sterile store → OT | Nothing |
| Dirty (brown) | Used instruments: OT → dirty hatch → CSSD wash. Waste and linen: OT → dirty utility → 3'-6" passage → door beside the main entry | Lobby for the last 5' |

Kept from the architect's plan and the earlier H: the OT has no door to a public area, CSSD is beside the OT with a pass box, and soiled goods have their own exit.

## 5. Deviations from the previous Layout H and what each costs

| # | Change | Cost |
|---|---|---|
| 1 | OT 17'-0" → 20'-0" deep | Everything north of it moves 3'-0" |
| 2 | Waiting concourse 12'-0" → 9'-0" | 1 seat (15 → 14); 5'-8" clear between seat rows; daylight slot at the west end narrows to 2'-7" |
| 3 | X-ray room 12'-0" → 9'-0" deep | 115 → 86 sf; still mobile-unit only |
| 4 | Accessible WC 7'-3" → 6'-0" deep | 50 → 41 sf |
| 5 | Psychiatry sub-wait gives its south 3'-6" to the anaesthesia store | 54 → 33 sf; still closed, still 3 seats |
| 6 | OPD column lengthened by 3'-0" | Gain: OPD 1 +16 sf, OPD 2 +13 sf |
| 7 | CSSD split into wash and clean with two hatches and a pass-through autoclave | Each room is about 30 sf; one technician at a time |
| 8 | Staff WC and anaesthesia store added | Recovery 135 → 124 sf, dirty utility 53 → 48 sf, scrub 33 → 28 sf |
| 9 | Beds | None: 8 + 2 recovery bays |

## 6. Shortfalls against modular-OT practice

- **One staff change room, not separate male and female rooms.** 55 sf takes two locker banks and a WC; staff change in turn. A second room would cost the WC or 3'-0" of the recovery lane.
- **Pre-op and recovery share one room** with two bays. A patient going in passes one coming out; run one list at a time and curtain the bays.
- **No patient changing room.** All OT patients are admitted, so they change in the ward room.
- **Sterile store is restocked by hatch** from CSSD clean, or through the OT between cases.
- **CSSD wash opens off the OPD passage.** It is outside the sterile zone, but staff carrying sets from OPD dressing use the public passage.
- **No AHU or plant room on the floor.** A 400 sf OT needs its own AHU with HEPA terminal filters. Candidates: ceiling-hung unit above the CSSD / store strip, or outdoor units on the south service ledge. Slab-to-slab height, ledge depth and load, and the builder's permission are not known.
- **Wet points.** Scrub trough, two CSSD sinks, the sluice and the staff WC are all new; the builder's SE toilet position is inside the OT and is not used. The staff WC is about 18' from the cut-out stack and 26' from the SE stack. Drain falls inside a 150 mm raised floor need a plumbing check.
- **Lift shafts** run behind the OT's east wall from 8' to 37' north of the south wall: check noise and vibration for the table and C-arm.
- **Wall panels.** 20'-0" is plaster to plaster. Modular panels take roughly 2" to 3" per wall, so the finished room is about 19'-6" unless the vendor fixes panels direct.

## 7. Checks asked for

| Check | Result |
|---|---|
| OT area against minimum | 400 sf / 37.2 m² against a 20' × 20' (about 36 m²) target: met |
| Columns inside the OT | None. C1 and C3 are in the west wall line, 1½" proud |
| Door sizes | OT main 5'-0" pair (drawn hinged; specify a hermetic sliding door); recovery entry 5'-0" pair; staff 3'-5"; sterile store 3'-0"; dirty 3'-0"; dirty exit 2'-10"; change 2'-10"; CSSD wash 2'-7"; X-ray 4'-0"; main entry 6'-0" pair |
| Trolley route | No point narrower than the 5'-0" doors from the main door to the OT; gate 6'-1" |
| Travel from the OT door | Main door 41'; nearer stair about 75' (23 m); second stair about 94' (29 m); add up to 25' from the far corner of the OT. Stair door positions are assumed from the DWG core outline |
| Fixed 194 sf X-ray room | **Does not fit in the south zone.** See below |
| Overlaps | No room overlap over 0.5 sf; no furniture in a wall, column or another item; DXF audit 0 errors |

**What a fixed X-ray room costs.** Three places were tested on the model:

1. In place, enlarged to 13'-5" × 14'-6" (195 sf): takes the dirty-exit passage and 5'-1" of the recovery room, leaving 4'-6". Cost: the recovery room and the separate soiled exit, or the OT goes back to about 20' × 15'.
2. OPD column: OPD 1 + OPD 2 merged give 225 sf but only 10'-5" to 11'-11" wide, under the 4 m side I recall as the minimum. Cost: two OPD rooms (three → one) and the room still fails on width.
3. Twin 1 beside the lobby (21'-5" × 14'-0", 244 sf): fits. Cost: **2 beds (8 → 6)**, and the glass wall there needs lead lining. The present 86 sf room then becomes plaster and dressing only.

The concourse is 9'-0" deep, so no 4 m room fits there. A C-arm in the OT plus a mobile DR unit is the arrangement this plan supports.

## 8. Not verified

- All NABH, HFG-India, AERB and NBC figures are from memory: 20' × 20' / 36 m² OT, 5'-0" hermetic door, 4'-0" clear around the table, 18 m² and 4 m side for a fixed X-ray room, 30 m travel distance.
- Site dimensions, column sizes, slab-to-slab height and the service-ledge depth.
- Stair door positions and the true walking distance to them.
- Drain routes and falls for every new wet point; medical-gas manifold location.
- AHU size, location and fresh-air route.
- Fire: single exit from the unit, as before.

This is a concept drawing for discussion, to be verified by the licensed architect, the OT vendor and the consultants before construction.
