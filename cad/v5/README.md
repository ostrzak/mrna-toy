# V5 handheld ribosome

V5 is a separate handheld design. V4, V4 Print, V3 and V2 are preserved. The
protein is a preassembled connected strand; the mechanism exposes beads rather
than assembling loose amino acids.

[Saved model](RibosomeV5.FCStd) · [Controls macro](RibosomeV5.FCMacro) ·
[Source](bracelet_v5.py) · [Focused checks](checks.json)

## Interaction

- Move the exposed closed RNA loop, or rock the smaller upper subunit. Both
  inputs share the same bead drum. One completed click advances three visible
  RNA bases and one bead.
- The larger lower body contains a single-row, positively driven storage drum.
  A fixed keeper and short tangent guide retain beads at the handoff. The drum
  has 28 pockets; the strand has 26 beads. The transfer gap is intentional.
- Maximum feed is 22 steps / 132 mm. Four beads remain inside, including at
  least three at or behind the drum's tangent station. A closed arcuate slot
  and moving pin bound travel at both ends.
- Straighten the emerged strand, lift the release tab, and reverse the RNA.
  Both click leaves lift clear. The same drum captures returning beads. There
  is no cord reel, spring-driven rewind, or automatic protein curling.

## Open and inspect

Open the model directly. Its saved expressions retain coupled motion without
the macro. Select **V5 controls** (`Motion`) and edit `BeadSteps` from 0 to 22.
`CapStroke` from 0 to 1 inspects the upper rocker. `ReverseRelease` lifts the
click leaves. These properties prescribe geometry; they do not simulate forces.

Run the adjacent macro for **Click upper subunit**, **Return one bead**,
**Open lower body**, and the RNA travel slider. Return requires the release
checkbox. **Reset view / home** resets the CAD study, not a physical reset action.

The RNA has 112 bases and an inward-facing 112-tooth drive rail. A fixed-axis
14-tooth idler meshes with the 84-tooth common-shaft sun. Three RNA teeth
therefore advance one of the 28 drum pockets. The visible loop is outside the
lower body except at its covered engagement cheek. It is shown on a nominal
circular path; sag, stretch and flex are not solved by the CAD animation.

## Engineering boundary

The drum outline is relieved using the tangent bead path in its rotating frame.
Validation checks actual saved solids at sub-step phases, not just ideal round
pockets. Beads retain the 4.4 mm bound, common drive shoulders, three lobed
variants, nominal 6 mm path pitch and an illustrative 0.36 mm copper core.

The ratchet leaves are shown unloaded. Their elastic contact overlaps are
reported separately. The upper-cap return spring is a labelled space claim;
spring selection, preload, leaf fatigue, reverse-release usability, repeatable
one-step clicks, low-stretch RNA manufacture, fasteners and printed fits remain
open. This is a CAD design prototype, not a dependable print-and-assemble release.

First physical qualification should use the drum, keeper and representative
beads/core, then the RNA mesh, then the click/release assembly. Retraction force,
pitch fixation, handoff, bend fatigue and recovery from a partly shaped strand
must be measured before treating the mechanism as reliable.

## Rebuild

From the repository root, with a compatible FreeCAD runtime:

```sh
python scripts/check_repo.py
python scripts/cad.py doctor
python scripts/cad.py build --version 5 --force
python scripts/cad.py validate --version 5
```

Generated outputs go to ignored `build/v5/`; these commands refuse to overwrite
the saved model or report. Promote source, CAD, images and the fresh report
together after a GUI presentation and normal close-and-reopen check.
