# Delegation plan
Units: 3

Gate open: three independent units; user requested colony. Current correction replaces the sketched right stair strip with seating deck, and investigates structural improvements. V1 design remains archived, with corrected interpretation of native diagonal axes.

| # | Unit | Files (mine) | Worker | Acceptance | Status |
|---|------|--------------|--------|------------|--------|
| 1 | Geometry, quantities, PDF, integration and publication | r08.py, r08_options.py, boq_revision_web.py, check_r08.py, r08.test.cjs, pdf-mass.test.cjs, r08-pdf.cjs, generated assets/r08 data/geometry/audit/csv/pdf, DELEGATION.md, workflow, publication copies | root | Sketched strip has no stairs; geometry and quantities reconcile; PDF and publication payload match | verified |
| 2 | Version display and technical drawings | r04_model.py, site_version.py, site-version.js, site-version-viewer.js, boq-revision.js, boq-revision-controller.js, r08_drawings.py, detail_drawings.py, check_site_version.cjs, check_detail_drawings.py, drawing-viewer.js, generated SVG and drawing manifests | drawings + root integration | V2 infill 1400 mm and two stair strips; V1 geometry retained with corrected member axes; browser and drawing tests pass | verified |
| 3 | Structural diagnosis and verified improvement study | fem_model.py, check_fem.py, geometry_axes.py, data/member-axis-corrections.json, assets/fem/*, fem-viewer.js, check_fem_viewer.cjs, structural-study.py, assets/structural-study/* | fem | Numerical benchmarks and equilibrium pass; improvement compared under identical loads; limitations explicit | verified |

## Evidence
User selected comparison A (main concrete columns) and C (independent frame). All three local acceptance units are verified; publication follows. No safety or fabrication approval is inferred from elastic deformation alone.

- Root independently ran `node check_site_version.cjs` and `python check_detail_drawings.py`; actual A/C member vertices, column counts, independent edits and XML sheets match. Browser front view confirms precisely two stair strips and continuous seating at the sketched strip. Root applied final component-label integration for main-floor anchors.
- Root independently checked eight reconstructed axis lengths against native Cut Length; four bearer bounding residuals below0.022mm and four brace residuals below2.712mm. Corrections describe geometry interpretation, not new steel.
- Root rendered and inspected all26 portrait RAB pages (base8,A9,C9). `python check_r08.py` reconciles source cut deltas, all thickness masses, removed struts, shared plate nesting, floor/RC anchor counts, and every PDF row and total.

- Root independently passed all 38 workflow checks, including 48 equilibrium/benchmark FEM cases, 540 RAB combinations and 30 PDF exports. Browser confirms A/C service displacements 1.267/1.266 mm at RHS 2.3, and 1.777 mm A at 1.6. Fixed stale FEM fetch and missing-model failure gating; targeted viewer tests passed again.
