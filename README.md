# drkhannaaios
developing system for doctors

## Hospital Floorplan — 7th Floor Solaris Shine, Althan, Surat

Parametric redesign of the architect's proposed layout (Ar. Bankim Dave,
09-01-2026), fixing three flagged flaws:

1. **OT → Recovery**: recovery now adjoins the OT with a direct door (no
   public-corridor crossing for post-op patients)
2. **Pharmacy** relocated onto the exit path beside the main door
3. **Waiting area** relocated to the openable-glass west facade for
   7th-floor outside views

### Deliverables (`deliverables/`)

| File | What |
|---|---|
| `layout_A_targeted_revision.png/.svg/.dxf` | Minimal-change revision of the architect's plan |
| `layout_B_fresh_alternative.png/.svg/.dxf` | Re-zoned alternative (scrub anteroom, X-ray at consult cluster, nurses' rest, larger waiting+recreation) |
| `layout_0_architect_asis.png/.svg/.dxf` | The architect's plan re-drawn as baseline |
| `3d_layout_A.png`, `3d_layout_B.png` | Extruded 3D views |
| `DESIGN_BRIEF_PROMPT.md` | Requirements converted into a structured, reusable design brief |
| `DESIGN_RATIONALE.md` | What changed, why, travel-distance scores, architect notes |
| `flow_scores.md` | Key clinical-flow distances: architect 204 ft → A 158 ft → B 131 ft |

DXFs are in feet, layered (WALLS/DOORS/TEXT/FURNITURE/GLASS/PLATE/VOID),
AutoCAD R2018 — they overlay directly on the original drawing.

### Regenerate

```bash
pip install ezdxf shapely matplotlib svgwrite
cd floorplan && python3 generate.py
```

Geometry model: `floorplan/plan_model.py` (floor plate traced from the
dimensioned drawing; all printed room dimensions preserved). Travel-distance
scoring (`floorplan/score.py`) follows the corridor-edge-weight methodology
of [HospitalEdgeWeigths](https://github.com/LorenaPujante/HospitalEdgeWeigths);
run `floorplan/fetch_reference_repos.sh` to pull the four reference repos.
