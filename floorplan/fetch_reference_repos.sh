#!/usr/bin/env bash
# Clone the four reference repos used for methodology (not committed - ~127 MB).
set -e
cd "$(dirname "$0")/reference-repos" 2>/dev/null || { mkdir -p "$(dirname "$0")/reference-repos"; cd "$(dirname "$0")/reference-repos"; }
for r in hellguz/Magnetizing_FloorPlanGenerator \
         LorenaPujante/HospitalEdgeWeigths \
         MoizKhuzema/Automated-FloorPlan-Generator \
         CTLab-ITMO/GenPlan; do
    d=$(basename "$r")
    [ -d "$d" ] || git clone --depth 1 "https://github.com/$r.git" "$d"
done
