# V7 — unfinished forward-pickup candidate

**Status: INCOMPLETE_HANDOFF. The mechanism is not established as functional.**
This separate version was authorized on 2026-11-02. V6 and all earlier models,
reports and views are preserved. V6 remains the launcher's default.

[Cloud handoff and next work](../../docs/v7-cloud-handoff.md) ·
[Saved checkpoint](RibosomeV7.FCStd) · [Controls macro](RibosomeV7.FCMacro) ·
[Incomplete report](checks.json) · [GUI checkpoint evidence](gui-checks.json)

![V7 CAD checkpoint](handheld.png)

[Flank route](side.png) · [Open mechanism](mechanism.png) ·
[Forward pickup](pickup.png) · [Return state](return.png)

## Intended behaviour

- RNA forward carries the upper forward through pawl B, then releases it for
  spring return. Pawl A lets the upper itself drive a full bead step.
- A and B reach separate, oppositely facing 28-tooth tracks on the same rotor.
  A fork lifts B, and a leaf latch holds the fork during upper return.
- Backward RNA reverses the protein drum while the upper is home. A lifts
  clear and B rises over its reverse ramps. Retain the dedicated bidirectional
  click leaf; neither the hold-open latch nor a clicking sound replaces it.
- Each completed feed step is three RNA teeth / one 6 mm protein bead. The
  26-bead chain, 22 available steps and four retained beads are unchanged.
- Manual input has 3 degrees of entry followed by 12.857 degrees of positive
  drive (15.857 degrees total). RNA pickup rocks through 12.857 degrees.
  Both return home, but their angular strokes are not identical. Do not
  reinstate the earlier idea of letting the detent finish manual feeding.

## RNA routing request

The user asked for RNA to cross farther over the lower body's midline and
close around the far flank, tucked closely into a groove. The current first
layout changes the inclination from V6's 38 degrees to 16 degrees and uses
33 mm bends on both ends. It has 110 nominal pitch positions / 248.814 mm
material length, with the front drive entry and 149.288 mm stroke retained.
Its nominal return centre is about y=34.272, z=0.654 mm, compared with V6's
y=5.672, z=-9.677 mm. This layout needs full solid clearance, groove-wall and
clasp-travel checks; numerical proximity is not proof of a snug usable fit.

## Inspecting the checkpoint

Open the saved model directly, or run the adjacent macro. The macro provides
RNA-forward, upper-input and RNA-backward buttons, a target index slider,
cycle inspection, clasp mode and cutaway. The button/target animations have
not completed acceptance testing.

The saved expressions are self-contained. In `Motion`, `InputKind` is 0 for
RNA forward, 1 for upper input, 2 for reverse; `CyclePosition` runs 0–1.
The cycle prescribes feed, trip, then return/reset. `BeadSteps` is its starting
index. This is kinematic bookkeeping, not a physical automatic release.

## Critical unfinished work

1. Integrated rigid clearance and assembly validation did not finish. The
   current validator/auditor are development code, not completed evidence.
2. The trip leaf's snap, latch forces and spring return are prescribed shapes
   and states. They are not an elastic or dynamic solution.
3. Animation pauses RNA for reset. A mechanical continuous-pull gate is not
   implemented. Reset speed, partial strokes, mid-stroke reversal and the
   possibility of missed pickup cycles remain unresolved.
4. New assembly features include a detachable upper shell/carrier, reset
   bridge and three extra M2 fasteners. Verify all insertion paths, seating,
   access, wall sections and integral roots; do not reuse the V6 audit result.
5. No printed prototype, force, fatigue, clasp-retention or reliable feeding
   qualification exists. The V4 Print package does not apply to V7.

## Commands

```sh
python scripts/check_repo.py
python scripts/cad.py doctor
python scripts/cad.py build --version 7 --force
python scripts/cad.py validate --version 7
```

Builds and validation write to ignored `build/v7/`. A `REVIEW`, exception or
unavailable runtime is not a PASS. Saved CAD and reports are protected from
launcher overwrites. See the handoff for the exact interrupted work.
