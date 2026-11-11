#!/usr/bin/env bash
# Download a few official OGS benchmark folders (input files only) from the
# OGS source repository, pinned to the same version as the pip package.
# Usage:  bash fetch_benchmarks.sh            (default tag 6.5.9)
#         bash fetch_benchmarks.sh 6.5.10     (if you updated OGS)
set -euo pipefail
TAG="${1:-6.5.9}"
DIRS=(
  Tests/Data/Parabolic/LiquidFlow/AxiSymTheis          # Day 4: single-phase flow, Theis well test
  Tests/Data/Mechanics/Linear/DiscWithHole             # Day 5: elasticity, borehole stress (Kirsch)
  Tests/Data/HydroMechanics/Linear/Confined_Compression # Day 6: hydro-mechanics
  Tests/Data/TH2M/H2/mcWhorter                         # Day 9-10: two-phase flow vs analytical
  Tests/Data/TH2M/H2M/Liakopoulos                      # Day 11: two-phase + mechanics
  Tests/Data/TH2M/H2/dissolution_diffusion             # Day 12: H2 injection, gas appearance
)
rm -rf ogs_src
git clone --quiet --depth 1 --branch "$TAG" --filter=blob:none --no-checkout \
    https://github.com/ufz/ogs.git ogs_src
cd ogs_src
git sparse-checkout init --cone
git sparse-checkout set "${DIRS[@]}"
git checkout --quiet "$TAG"
cd ..
echo "Benchmarks for OGS $TAG are in ./ogs_src/Tests/Data"
