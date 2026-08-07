"""Generate all deliverables into ../deliverables/."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from render import render_layout
from render3d import render_3d
from dxf_export import export_dxf
from score import comparison_table
from plan_model import LAYOUTS, PLATE, CUTOUT

OUT = os.path.join(os.path.dirname(__file__), "..", "deliverables")


def main():
    os.makedirs(OUT, exist_ok=True)
    total = PLATE.area - CUTOUT.area
    print(f"Plate carpet area: {total:,.0f} sq ft")

    for key, base in [("architect", "layout_0_architect_asis"),
                      ("A", "layout_A_targeted_revision"),
                      ("B", "layout_B_fresh_alternative"),
                      ("C", "layout_C_arrival_hub")]:
        path = os.path.join(OUT, base)
        render_layout(key, path)
        print(f"2D  {base}.png/.svg ok")
        errs = export_dxf(key, path + ".dxf")
        print(f"DXF {base}.dxf  audit errors: {errs}")

    for key, base in [("A", "3d_layout_A"), ("B", "3d_layout_B"), ("C", "3d_layout_C")]:
        render_3d(key, os.path.join(OUT, base + ".png"))
        print(f"3D  {base}.png ok")

    table, _ = comparison_table()
    with open(os.path.join(OUT, "flow_scores.md"), "w") as f:
        f.write("# Key clinical-flow travel distances (corridor L1 metric)\n\n" + table + "\n")
    print("Scores written.\n")
    print(table)

    # sanity checks
    for key, factory_name in [("A", "Layout A"), ("B", "Layout B"), ("C", "Layout C")]:
        rooms = LAYOUTS[key][1]()
        seen = {}
        for r in rooms:
            if r.zone == "circ":
                continue
            for s in rooms:
                if s.key >= r.key or s.zone == "circ":
                    continue
                inter = r.poly.intersection(s.poly).area
                if inter > 2.0:
                    seen[(r.key, s.key)] = inter
        if seen:
            print(f"WARNING {factory_name}: overlapping rooms: {seen}")
        else:
            print(f"{factory_name}: no room overlaps > 2 sq ft — OK")


if __name__ == "__main__":
    main()
