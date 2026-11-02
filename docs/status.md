# Project status and next decisions

## V7 cloud handoff — 2026-11-03

V7 is an unfinished candidate on `codex/v7-forward-pickup`, copied separately
from V6 at the user's authorization. It adds two opposing drive/pickup tracks,
a lift fork and latch, nominal trip leaf/reset roof, detachable upper shell
and carrier, and a shallower RNA route around the far flank. The dedicated
click leaf is retained. V6 and older CAD/report/image bytes are preserved.

The source builds with local FreeCAD 1.1.4. Isolated earlier pawl contacts were
checked, but the integrated validation and assembly run did not finish.
The release snap, partial strokes and continuous-pull reset are unresolved;
the GUI's pause is not a mechanical gate. No functional or physical PASS is
claimed. Read [the handoff](v7-cloud-handoff.md), [V7 guide](../cad/v7/README.md)
and [incomplete report](../cad/v7/checks.json) before continuing in the cloud.
The launcher still defaults to V6; select V7 explicitly.

## V6 captive open/closed RNA — 2026-10-31

The user authorized a separate V6 after choosing open-strand play with an
optional joined underside loop. V5 and all earlier CAD/print files are
preserved. The latest contract removes the user-operated reverse release:
backward RNA directly retracts the protein through the same drum. The clasp
halves also act as end stops; captured ports keep either open end from leaving
the setup. The underside return remains external and open, without a parking
clip.

The current in-place refinement removes both outer RNA holders. A short central
capture channel retains the strand; broad curves cross the lower flank before
passing under the flatter dome through an open groove. Its 226.195 mm nominal
material length retains the full 149.288 mm travel. Exact loop shape is secondary
to handling and compact guidance. The side-route adjustment lengthens the strip
by 22.619 mm and keeps the drive entry, fastening, mechanism and clasp geometry.

The [assembly audit](v6-assembly.md) found obstructed housing-screw passages,
a floating spindle and an unsupported washer seat in the preceding V6.
The current design has one aligned three-screw stack, an analytic load-bearing
lid plate, an integral spindle root and a separate seated cap washer. Two keyed
rotor parts permit the lid and cover to be inserted. Checks include real shaft
passages, finite bearing seats, local material sections, integral roots,
key torque blocking and sampled insertion poses, in addition to motion.

V6 replaces the large RNA ring/idler with a straight rack and one shared
84-tooth gear. It retains the 28-pocket bead drum and 22-step / 132 mm protein
feed with four hidden beads. A separate symmetric detent permits bidirectional
clicking. The upper input has an internal cam-lifted pawl, disengaged at rest.
The clasp travels across the underside and stays outside the drive ports.

Consult the [V6 guide](../cad/v6/README.md), [current model](../cad/v6/RibosomeV6.FCStd),
[open mode](../cad/v6/open.png), [underside return](../cad/v6/underside.png)
and [focused report](../cad/v6/checks.json) for the actual result and boundary.
RNA/leaf deformations are nominal prescribed poses and the two input springs
are space claims. TPU behavior, clasp retention, click sound and force,
cap engagement/return under load, overload resistance, hand fit, manufacturing
and reliable physical feeding remain unqualified.

## Preserved V5 proportions and clearance review — 2026-10-30

The upper shell now has a fuller asymmetric head/body/platform silhouette,
guided by RCSB ribosome references. A fixed underside palm swell gives the
supporting hand a surface below the moving RNA plane. The drive architecture
and native motion are retained. Local lid, keeper, axle, cap support and yoke
clearance corrections address clashes omitted by the earlier focused suite.
The expanded checks include nine rocker positions at three release heights.
See the [review and references](v5-proportions.md),
[current CAD](../cad/v5/handheld.png), [grip side view](../cad/v5/grip.png)
and [report](../cad/v5/checks.json). Physical hand fit remains untested.

The user is reconsidering whether the RNA should form a complete loop. It is
retained here to avoid changing the mechanism during the proportion pass;
the final RNA route is not settled.

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

The earlier local-only decision is superseded by the V7 cloud-continuation authorization above. Superseded experiments belong in Git history, not new archive folders.
