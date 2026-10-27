# Project status and next decisions

Handoff updated 2026-10-27. V3 is the active CAD prototype; no physical prototype results are recorded.

## Immediate continuation plan

The user plans a new local chat to work on the beads; cloud migration is deferred because of issues with that environment. This update regenerated the [current concept illustration](images/toy-concept.png) and corrected the documentation, without changing CAD. The early on-wrist illustration is superseded. The new image uses V3 as a reference and keeps the current rounded bead placeholders; it is not evidence that bead redesign or manufacturing preparation has been implemented. See [image provenance](images/README.md).

## Implemented and checked

- Separate flexible-cuff and RNA-dial C arcs, a fixed ribosome, hidden protein storage, a direct same-direction outlet, a close bead keeper and bounded travel.
- Three RNA bases per bead step, nominal click feedback and a mechanically linked upper-lobe swivel.
- A saved FreeCAD model, procedural source, native motion expressions and a GUI control macro.
- The committed V3 report records **63 valid one-solid components**, **21 coupled poses**, **9 gear phases**, sampled actual bead-to-feeder contacts, stop checks and profile clearance checks. Its smallest sampled bead-pocket clearance is approximately **0.119 mm**.
- The check scope is geometric: prescribed motion, sampled interference and conservative swept envelopes. Wire segments and the posed output are visual approximations. The detent leaf is an unloaded shape with intentional cam preload; its elastic behaviour has not been solved.

See [the saved V3 report](../cad/v3/checks.json). A fresh run goes to `build/v3/checks.json` and is separate from that committed snapshot.

The 2026-10-27 cleanup was checked with the repository checker, runtime doctor, a fresh V3 build, and a separate validation of the committed model on Windows / FreeCAD 1.1.4. Both CAD runs passed. The rebuilt part summaries, dimensions and kinematics matched the stored snapshot, and both committed CAD files retained their original hashes. Linux/cloud execution remains unverified.

## Latest requests: analysed, not implemented

The user asked whether amino-acid beads could look more realistic, similar to earlier compact lobed forms, and how much work remained to make the toy printable. They then explicitly said **not to implement model changes yet**. The repository cleanup preserves the CAD geometry.

The proposed bead direction is a small family of compact asymmetric shapes with consistent spacing and reliable feed contact geometry. The current beads remain spherical. The 4.4 mm bead / 4.9 mm keeper pairing provides only **0.25 mm radial clearance**. New lobes must be checked through the entire guide and in plausible rotated orientations; larger shapes may need guide and feeder changes. The three-to-one ratio should remain.

V3 is a basis for printing prototype parts, **not a dependable print-and-assemble release**. The hardest uncertainties are bidirectional chain feeding and cuff flexibility, not the appearance of the beads.

## Decisions and bench work still needed

| Area | What must be established |
| --- | --- |
| Manufacturing process | Target printer/service, nozzle or process resolution, materials, calibrated fits and print orientations. No printer or production material has been selected in the repository. |
| Feeder and storage | Beads stay fixed at pitch; the close guide maintains engagement in both directions; the straightened wire does not buckle or jam when pushed into the curved store. |
| Wire and beads | Pose retention, bore finish, bead fixation, repeated-bend fatigue, end retention and replacement/assembly method. |
| Cuff and RNA dial | Force and strain needed to spread them at home, fatigue, track retention, wrist comfort and clearance while worn. |
| Small mechanism | Printed gears, approximately 0.12 mm nominal pocket clearance, small pins, sliding fits, cam friction, torque and the 0.45 mm click leaf. |
| Assembly | Actual fasteners, retention and service access; printable supports, wall thicknesses and final part preparation. |

A useful proposed next engineering step is a short feeder-and-channel test assembly with a few beads and the intended core. It would establish practical fits and reverse-feed behaviour before a full wearable build. This is a recommendation, not an instruction to start that work without a new request.

## Version history worth retaining

- **V3:** current same-direction direct feed. The bead home phase is an integral number of pitches, and validation includes actual assembled bead-to-wheel checks.
- **V2:** explicitly retained opposite-direction comparison. A later audit measured approximately **7.167 mm³** interference between a bead and the wheel at home, which its original profile-only check missed. The old PASS was invalidated in its report. Keep the warning and do not present V2 as a validated mechanism.

Other superseded concept studies are available in Git history, not in the active working tree. They are not alternatives to carry forward automatically.
