# Layout F — design brief (meta-prompt) and feasibility

Solaris Shine, 7th floor, Althan, Surat · Dr. Aman Khanna (Orthopaedics) and
Dr. Heena (Psychiatry) · 16-11-2026 · source: hand sketch on the border-only A4 sheet.

Drawings: `layout_F_detailed.png/.svg` (dimensioned sheet), `layout_F_detailed.dxf`
(AutoCAD, feet), `layout_F_blueprint.svg/.png`, `layout_F_clean.svg`, `3d_layout_F.png`.
Model: `floorplan/plan_model.py` → `layout_f_rooms()`.

## 1. Meta-prompt that was executed

> You are the project architect for a 5-bed orthopaedic + psychiatry day-surgery
> hospital on a fixed floor plate (Rev C envelope: 48'-6" south × 92'-0" east, west
> glass facade tapering to 31'-0", curved NW corner, service cut-out at the waist,
> 5'-0" main entry on the east wall 43'–48' from the south corner).
>
> 1. **Read the clients' line diagram literally.** Keep every room they drew, in the
>    position and adjacency they drew it. Scale it off the printed border.
> 2. **Complete each room.** A box marked "Room" becomes a buildable room: bed with
>    head on a wall, attendant sofa, wardrobe, ensuite toilet (WC + basin + shower),
>    door with swing. Consult rooms get desk, chairs, couch. OT gets scrub, change,
>    sterile store, recovery.
> 3. **Resolve what the sketch leaves open** — which door, which way a patient on a
>    trolley travels, where staff change — choosing the option that keeps clean and
>    public traffic apart. Record every such decision.
> 4. **Fit to the two doctors.** Ortho: trolley-width doors and passages, plaster /
>    procedure room, X-ray beside the entry. Psychiatry: the quietest consult room,
>    acoustic privacy, no clinical couch, discreet approach.
> 5. **Check feasibility** against room sizes, passage widths, statutory items, and
>    say plainly what does not comply.
> 6. **Output** a dimensioned 2D sheet, a CAD file, and a list of points for the
>    clients to confirm. No solid-room overlaps; DXF audit must return 0 errors.

## 2. How the sketch was read

| Sketch mark | Built as | Size |
|---|---|---|
| 20×20 OT | Operation theatre, SE corner | 20'-0" × 20'-0" (400 sf) |
| Autoclave / Scrub / "OT" column | Autoclave-CSSD → Scrub → OT Change, one staff-only column | 9'-2" wide |
| Store + Recovery (below OT) | OT store + Recovery / Pre-op, 2 beds | 5'-10" and 13'-10" × 9'-10" |
| X-ray / Dressing / Emergency | One room off the entry lobby, 4'-0" door | 12'-7" × 10'-5" (131 sf) |
| Drs Lounge + small box | Doctors' lounge with WC, inside the staff zone | ≈17' × 8'-7" |
| OPD 3 | Dr. Heena — Psychiatry (sofa seating, glass side, end of lobby) | ≈15'-6" × 7'-7" (125 sf) |
| OPD 1 | Dr. Aman — Ortho (desk, 3 chairs, exam couch) | ≈9' × 13' (119 sf) |
| OP 2 + "Bed" | Second consultant / plaster and injection room | 9'-2" × 9'-2" |
| Lobby ↑ | 5' OPD lobby serving all three OPDs and the OT staff door | |
| Waiting area | Open-plan, 24 seats, above the cut-out on the west glass | ≈16' × 8' |
| Reception (diagonal) | Angled desk facing the main entry | |
| BP / ECG room · Pharmacy | Side by side, north of the entry | 5'-10" × 10'-2" · 6'-5" × 6'-7" |
| "Bed" under pharmacy | Curtained observation bed next to the nursing station | 6'-5" × 3'-2" |
| Change room · N.S. | Staff change · Nursing station | 5'-10" × 6'-5" · 6'-5" × 6'-5" |
| Store · room with 2 bed marks | Store · Duty doctor / staff rest (bunk) | 3'-5" × 6'-7" · 8'-10" × 6'-7" |
| Bathroom · Pantry | Suite 5's private bath · Pantry | 5'-10" × 5'-0" · 6'-5" × 5'-0" |
| Rooms 1–4 with T\|T pairs | Single rooms, toilets back-to-back at the glass end (1+2, 3+4) | ≈21'/20'/18' × 10'-0", Room 4 ≈16' × 11'-7" |
| Suite Room 5 (door at passage end) | Suite across the north end | ≈19' × 12'-10" (207 sf) + bath |

## 3. Decisions made where the sketch was silent

1. **OT access.** Recovery and the store now close off the whole north face of the
   OT, so there is no corridor to it. Patients go lobby → Recovery/Pre-op → OT through
   two 5'-0" double doors set in line. Staff go OPD lobby → Change → Scrub → OT.
2. **Ward toilets** are drawn side-by-side in the sketch; built back-to-back across
   the shared wall instead. Same position, one plumbing shaft per pair, and each
   toilet is 5'-2" wide instead of about 4'.
3. **Passage widened** from about 5'-6" (as sketched) to 6'-0" clear, taken from the
   east service band, so a bed trolley can turn into the 3'-6" room doors.
4. **Bathroom beside the pantry** is given to Suite 5 as its private bath (it has no
   other possible door).
5. **Bed heads on solid walls**, never on glass; attendant sofa by the window.

## 4. Feasibility

**Works**
- Everything in the sketch fits the plate. No overlaps; 31 rooms, ≈2,700 sf of rooms
  on a ≈3,730 sf carpet, the rest is lobby, waiting and passage.
- Clean separation of three zones from one entry: OT pod (south-east), OPD
  (south-west), wards (north).
- All five rooms get daylight and an ensuite; the nursing station sees the passage
  and four of five room doors.

**Needs a decision or a fix**

| # | Issue | Why it matters | Suggested fix |
|---|---|---|---|
| 1 | X-ray room is 131 sf | AERB asks roughly 18 m² (≈194 sf) with no side under 4 m for a fixed radiography unit | Use a mobile / portable unit here, or extend the room 4' south into Recovery (Recovery drops to one bed) |
| 2 | OT has a single door for clean and dirty traffic, and no separate dirty-utility exit | NABH-style zoning wants soiled material to leave without crossing the clean route | Accept for a single-OT day-surgery unit with timed disposal, or add a pass-box hatch from OT to the OT store |
| 3 | Recovery is also the only patient route into the OT | A patient going in passes one coming out | Works with one list at a time; curtain the two bays |
| 4 | OPD 3 is only 7'-7" deep | Fine for psychiatry seating, tight if a couch is ever needed | Take 1' from the lounge if wanted |
| 5 | BP / ECG room is 5'-10" wide | ECG couch fits, but only one person can stand beside it | Swap widths with pharmacy, or move the pharmacy hatch to the lobby wall and give BP 7' |
| 6 | No patient or visitor toilet inside the unit for OPD | OPD patients use the building's common toilets outside the entry | Confirm this is acceptable; otherwise carve one from the X-ray room corner |
| 7 | Ward toilets ≈37 sf with 2'-10" doors | Usable with a walker; not wheelchair-turning size | Make the Room 1 toilet the accessible one (widen to 6', 3'-0" door) |
| 8 | Duty room fits one bunk, not two separate beds | Sketch shows two bed marks | Confirm the room's purpose (see below) |
| 9 | Fire exits | A single entry on the east; second escape depends on the building's stair core | Check travel distance from Suite 5 (≈55') and the fire NOC conditions with the builder |
| 10 | Staff reach the lounge through the scrub lobby | Keeps it private but puts casual traffic in the semi-clean zone | Acceptable; or give the lounge a door from OPD 3 instead |

## 5. Please confirm

- The room beside the second store (two bed marks, word unclear) is read as
  **Duty doctor / staff rest**. Correct?
- **OPD 3 = Dr. Heena, OPD 1 = Dr. Aman, OP 2 = shared procedure room.** Correct?
- Fixed X-ray machine or portable?
- Rooms 1–4: single occupancy as drawn. Rooms 1 and 2 are long enough for a second
  bed if twin-sharing is wanted, at the cost of the attendant sofa.

This is a concept drawing for discussion. Structure, columns, shafts, fire and
AERB / clinical-establishment compliance need checking by the licensed architect
and consultants before construction.
