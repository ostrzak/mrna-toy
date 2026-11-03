# V7 continuation — user-stopped checkpoint, mechanism REVIEW

Repository: `ostrzak/mrna-toy`, branch `codex/v7-forward-pickup`.
The cloud continuation started at **fa32f91**, an **INCOMPLETE_HANDOFF** checkpoint,
not a functional or fully validated mechanism. V6 and every earlier version
remain preserved. V6 is still the launcher default.

The follow-up fetched and checked **5c4b2c02f2925befef8537cb0fb1ea4ea1ee6e3d**
before editing. It repairs the keeper/housing fit, rear screw column, lifted-A
clearance, shell screw seats and shell insertion access. The upper organic
skin and anchor pocket are repaired for the extended BOP check. These are
rigid and assembly corrections; the requested mechanical finish remains open.

The user then paused work and requested a GitHub push. The saved checkpoint is
**INCOMPLETE_CONTINUATION**, with mechanical status **REVIEW**. Its build, all
five structural extended-BOP checks, 332-feature regeneration comparison,
normal GUI reopen and control animations completed. The integrated audit was
stopped during the RNA-forward coupling sweep. Its 23 observed collision pairs
are partial evidence; remaining coupling poses, final assembly, continuous
travel certificates and the final mechanical aggregation are not completed.
The previous completed report remains available in Git at `5c4b2c0`.

Read `AGENTS.md`, `README.md`, `docs/design.md`, `docs/status.md`,
`docs/development.md`, [the V7 guide](../cad/v7/README.md) and
[mechanical audit](../cad/v7/engineering.md). No previous chat, Windows desktop,
private filesystem or local MCP connection is required.

## Required behavior

1. Forward RNA must drive protein and rock the upper.
2. Upper input must positively advance three RNA teeth per bead.
3. The upper must automatically disengage on return without drum rollback.
4. Backward RNA must retract protein with the upper home, without an external
   release lever. Straighten emerged protein first.
5. Retain three bases per bead, bounded travel, 26 beads, 28 pockets, 22 steps,
   four hidden beads and at least three at or behind the tangent station.
6. Keep the dedicated bidirectional detent leaf.
7. Close RNA farther across the body midline and around the far flank, snugly
   beside a matching groove, while retaining captive open-strand operation.

The marked [routing reference](images/v7-routing-request.png) is qualitative,
not dimensional. The [coupling illustration](images/v7-coupling-concept.png)
is an illustration, not CAD evidence.

## Current source and evidence

`cad/v7/` remains self-contained; it does not import the V6 generator.

- `bracelet_v7.py`: body, shared drive, RNA, protein, native study and controls.
- `coupling_v7.py`: opposite A/B tracks, pickup fork/latch, prescribed trip,
  reset roof, carrier/shell split and fasteners.
- `rna_path.py`: nominal inextensible open/closed layouts, 33 mm bends,
  110 pitches / 248.814 mm length. The generator now uses a 13.2° plane.
- `validation_v7.py`, `assembly_v7.py`: actual-solid contacts, continuous bounds,
  native coordinates/orientations, stops, wall/seat witnesses and sampled assembly.
- `mechanical_v7.py`, `engineering_v7.py`: independent causal rejection audit,
  partial-return solid witnesses, spring/leaf assumptions and force calculations.
- `presentation_v7.py`: GUI reopen, native motion, control tests and actual views.
- Saved CAD, `checks.json`, `gui-checks.json` and the CAD views are promoted
  together as an **INCOMPLETE_CONTINUATION** checkpoint at the user's stop.
  Mechanical status remains REVIEW. Read the precise evidence boundaries.

The continuation corrects manual-pawl crossover interference by placing its
14.7 mm-radius guide between the tracks and its bridge above B. It reopens the
carrier spindle/retainer passages and the complete fork guide bore after unions.
The fork arm and lip no longer deliberately occupy the same bearing volume.
The dedicated detent is a separate radially installed leaf below the pickup
track, clamped by an M2 x 3 screw and 0.5 mm washer.

The two 22-pitch end reserves preserve the front rack phase with 110 pitches.
Front lid columns are 3.1 mm radius; the rear column is 3.4 mm. Their verified
bearing seats and the existing local-section threshold are retained.
Continuous interval checks use actual saved RNA/base/clasp solids against fixed
housing and conservative protein/drum/upper bounds, not only sampled poses.

RNA returns approximately through y=35.118, z=3.904 mm. Its 3.4 mm groove bounds
rail and clasp; a separate continuous offset tube bounds the outward-facing
bases. The storage cavity is 30.9 mm radius. The validator tests a protected
wall region and finite actual far-flank material. The broad inward 4.65 mm
circumcircle cut is removed. Nominal layouts still do not establish TPU strain,
tension, sag or hand comfort.

Manual input retains 3° entry plus a full 12.857° positive feed, or 15.857° total.
RNA pickup rocks 12.857°. This unequal-stroke tradeoff remains deliberate;
the detent is not used to finish a manual feed step.

## Mechanical blockers remain

**The requested mechanical finish has not been achieved.**

- Return torque at home is about 4.28 N·mm; A's entry cam needs about
  6.26 N·mm even without friction, before latch/bearing/reset loads.
- The trip's snap branch, stored energy and reset remain prescribed rather
  than a contact-driven elastic solution. Its animated centreline changes length.
- There is no physical continuous-pull interlock or qualified reset speed.
  The animation's stationary RNA interval does not constrain hardware.
- Before the end trip, B can prevent partial upper return once A's entry
  clearance is recovered. With B engaged, upper return at fixed drum angle
  contradicts the drive-face constraint. Spring sizing alone cannot fix this.
- Native reverse-at-home poses do not establish a transition from every
  partial, loaded or latched state. `InputKind` is not a physical actuator.

Do not eliminate these failures by changing animation timing, excluding contacts,
loosening interference tolerances, substituting V6 evidence or marking missing
analysis as passed. Resolve the actual contact sequence before choosing final
springs or promoting a functional result. Remaining rigid collisions and assembly
failures are also recorded in `checks.json`; local corrections are not a global PASS.

## Portable runtime and checks

FreeCAD 1.1.4 with Part and bundled fcgear passed `doctor` in the cloud. A user-space
Xvfb display permits native GUI work without a desktop connection. Generated
models, diagnostics, runtime helpers and views belong under ignored `build/v7/`.
V7 `build()` defaults there, and the launcher protects saved version artifacts.

```sh
python scripts/cad.py doctor --freecad /path/to/compatible/FreeCADCmd
python scripts/cad.py build --version 7 --force --freecad /path/to/compatible/FreeCADCmd
python scripts/cad.py validate --version 7 --freecad /path/to/compatible/FreeCADCmd
python scripts/check_repo.py
```

`validate` returning nonzero for REVIEW is expected and must not be hidden.
`checks.events.jsonl` retains offending poses during a new run. Exact local
Boolean crops use bounding-box intersection identities; failed localization
falls back to the whole solid, never a skipped pair. The interference tolerances
remain 1e-5 mm³, and 5e-5 mm³ for the actual involute rack mesh.

Ellipsoids are partitioned at existing rational-surface knots before Booleans,
without changing their exact geometry. Round route bounds use cylinders and
quarter tori. The original generic spline representation passed basic validity
but failed extended BOP checks and returned incorrect intersections. The new
validator records extended checks on five structural solids; patch boundaries
are retained without final seam simplification.

CAD and analytical necessary conditions are distinct from physical qualification.
No printed V7, measured forces, spring/latch reliability, feed/retraction,
clasp retention, fatigue, sound or ergonomic qualification exists. The V4 Print
package does not qualify this mechanism.
