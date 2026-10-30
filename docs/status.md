# Project status and next decisions

## V5 handheld redesign — 2026-10-29

The user authorized V5 after choosing a handheld ribosome and a closed RNA loop.
V5 is a separate design in `cad/v5/`; V4 and all previous CAD/print files are
preserved. The single-row drum directly carries returning beads in pockets,
without a cord reel or tensioned spring take-up. The lower body is larger; the
upper body is a smaller rocking input.

The source, native motion, focused geometric checks and desktop presentation
are being built together. Consult [V5 checks](../cad/v5/checks.json) for the exact
result rather than reusing a V4 PASS. No V5 physical or slicer qualification is
claimed. The upper-return spring is a space claim; ratchet leaf behaviour,
reverse release, flexible RNA retention, bead fixation, fatigue and printed
assembly remain open. See the [V5 guide](../cad/v5/README.md).

The older status below is retained for the cuff comparisons.

## A1 mini derivative - 2026-10-29

The user authorized manufacturing preparation. [V4 Print](../cad/v4-print/README.md) is separate from V4, with TPU beads, candidate 0.6 mm bores and 0.25 mm copper wire; bore samples span 0.4-0.8 mm. The package includes oriented STL parts, fit and feeder fixtures, proposed M2 hardware and assembly instructions. Focused CAD checks passed. Export/slicer qualification is being saved at the user's request before all checks finish; consult [handoff status](../print/v4-a1-mini/handoff.json). No physical printing or assembly is demonstrated.


Updated 2026-10-28. **V4 is the current working CAD**, copied from V3 at the user's request. V3 files are preserved as the preceding comparison; V2 retains its invalidated historical-validation warning. No physical prototype results are recorded.

## V4 changes

- A rounded fixed front cover and curved upper pinion guard conceal the front mechanism. The upper lobe is cleared around a conservative full-swivel envelope.
- The cuff edge is recessed beside the RNA. Retaining ledges and a recessed outer shield preserve guidance while hiding the gear rail.
- One rounded RNA backbone carries 128 free-ended rounded bases. Their nominal tips project 4.5–5.64 mm ahead of the recessed cuff face. This is geometric finger access, not a usability test.
- Protein beads, their pitch, the storage path and outlet, common drive shaft, click/swivel coupling, three bases per bead, bounded travel and the engaged hidden tail are retained. Protein shaping remains manual.

See the [V4 guide](../cad/v4/README.md), [current view](../cad/v4/bracelet.png), [RNA detail](../cad/v4/rna.png) and [covered mechanism](../cad/v4/mechanism.png). The older AI illustration predates these changes; it is not a geometry reference.

## Check boundary

The local FreeCAD 1.1.4 V4 build passed focused checks for the four revised connected solids, RNA/protein envelopes, nine actual gear phases, ten coupled poses, actual saved bead-to-feeder contacts, native position expressions, travel stops and the illustrative hand-shaped strand. The report labels this **FOCUSED_PASS** and keeps V3's full baseline validation **INCOMPLETE_USER_STOPPED**.

The saved model must include desktop visibility and colours and be checked by normal GUI close-and-reopen. Its report and views are promoted together. The repository checker checks source syntax, links, CAD containers and report boundaries; it does not prove physical operation.

## Physical and manufacturing work still open

V4 remains an engineering prototype, not a dependable print-and-assemble release. A1 mini prototype preparation is now authorized in the separate V4 Print derivative.

| Area | Unresolved work |
| --- | --- |
| RNA and cuff | Finger purchase, turning force, retention, spread force/strain at home, fatigue and comfort. |
| Protein feed | Bead fixation at pitch, forward/reverse handoff, wire buckling, friction and end retention. |
| Wire and beads | Bore finish, pose retention, repeated-bend fatigue and assembly/replacement method. |
| Mechanism | Printed gears, approximately 0.12 mm nominal pocket clearance, cam/slider fits, torque, wear and the 0.45 mm click leaf. |
| Manufacturing | Printer/process, materials, calibrated fits, wall thicknesses, support access, print orientations and final fasteners. |

A short feeder-and-channel bench assembly with representative beads and wire remains a useful proposed next engineering step. A short feeder fixture is now included in the V4 Print package; no physical tests have been run. Full wearable reliability will require physical testing.

## Preserved comparisons

**V3:** compact lobed beads and a shallow same-direction protein exit. The user stopped full validation and accepted an immediate save; its report remains incomplete. Its 2026-10-28 desktop repair restored visibility without changing geometry or native motion expressions. V4 is a separate copy.

**V2:** opposite-direction feed comparison. A later audit found about 7.167 mm³ bead-to-wheel interference at home that its profile-only check missed. Keep `HISTORICAL_PASS_INVALIDATED`; it is not a validated baseline.

Continue locally; cloud migration remains deferred. Superseded experiments belong in Git history, not new archive folders.
