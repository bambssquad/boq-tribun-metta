# Delegation plan
Units: 4

Gate open: four independent units; user explicitly requested colony.

| # | Unit | Files (mine) | Worker | Acceptance | Status |
|---|------|--------------|--------|------------|--------|
| 1 | Global V1/V2, model integration and publication | site_version.py, site-version*.js, site-version.css, build_preview.py, boq-revision.js, check_site_version.cjs, check_r04_web.py, validate.py, kg_pricing.test.cjs, exploded-controller.test.cjs, requirements.txt, .github/workflows/build.yml, DELEGATION.md, tools.html, generated assets/model-*.js and runtime copies | root | Build, version geometry checks and browser switching pass | verified |
| 2 | Reproducible elastic FEM with numerical verification | fem_model.py, check_fem.py, assets/fem/* | fem | Analytical benchmarks, equilibrium and model provenance pass | verified |
| 3 | Zoomable detailed coordination drawings | detail_drawings.py, drawing-viewer.js, drawing-viewer.css, check_detail_drawings.py, assets/drawings/* | drawings | SVG dimensions, both versions and zoom controls verified | verified |
| 4 | Interactive structural result viewer | fem-viewer.js, fem-viewer.css, check_fem_viewer.cjs | viewer | Version, thickness, load case, forces and displacement rendering checks pass | verified |

## Evidence
Existing global-version edits predate the colony request. FEM is an elastic study with explicit assumptions, not fabrication approval or proprietary SAP2000/Tekla execution. Publication CI and live hashes are recorded separately in workspace STATE.md after deployment.

- Root ran `python check_detail_drawings.py`: 19 valid XML vector sheets, all 54 V2 proposed members and 80/100 column schedules. Root rendered and inspected V2 plan, section and coordinate sheet; browser verified zoom 100 to 130 percent, sheet switching, V1 eight sheets / V2 eleven sheets.
- Root ran `node check_site_version.cjs`: finite box sizes, 20 infill columns, 60 mesh panels, repeat/restore without duplicates, correct retained deck and removed RC struts. Browser confirmed V1 restores 56 stair fields and scope full; V2 has45 fields and scope r08.
- Original 33 workflow checks passed after adapting source checks to external model assets. `python validate.py` and `python check_r04_web.py` verify source IDs, links and BOQ after extraction. RAB 180 R08 cases and existing48 SHS cases retain quantities, costs and exports.
- Root ran `python check_fem.py`: analytical axial/torsion/biaxial cantilever, simply supported beam, rigid-body mechanisms, exact offsets, source freshness, pressure force/moment conservation and all24 case equilibrium checks pass. Corrected deck load transfer; final100mm discretization differs from200mm by0.1251percent V1 /0.1281percent V2 at2.3mm service. This measures load-discretization sensitivity, not structural capacity.
- Root ran `node check_fem_viewer.cjs`: all24 compressed solutions hydrate correctly; scaling, failed-result gating, cache deduplication and stale-response checks pass. Actual browser loaded gzip files, changed RHS2.3/service/My, displayed V2 maximum24.182mm and My3.298kNm, synchronized RAB case model, drew load/reaction arrows and toggled animation; console had no errors.

- Final suite: 38 workflow commands including publication-copy check pass. Two legacy tests now read the external model assets: `node kg_pricing.test.cjs` preserves mass/export assertions and `node exploded-controller.test.cjs` exercises real assembly, isolation and animation.
