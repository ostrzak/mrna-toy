# V7 cloud continuation — incomplete checkpoint

Repository: `ostrzak/mrna-toy`. Starting branch: `codex/v7-forward-pickup`.
The branch started from `d50dc62` on `main`. The user authorized saving/pushing
the unfinished work and moving further development to Codex Cloud.

Read `AGENTS.md`, `README.md`, `docs/design.md`, `docs/status.md`,
`docs/development.md`, then `cad/v7/README.md`. No previous chat, local desktop,
private filesystem or MCP session is needed.

## What the user authorized

Develop V7 separately; preserve V6 and every older comparison. Reuse V6 solids
where appropriate. Keep the dedicated click/detent leaf.

1. Sliding RNA forward should rock the upper and advance protein.
2. Rocking the upper should itself advance RNA and protein.
3. The upper should disengage on its return, without reversing the drum.
4. RNA backward should retract protein with the upper home, without an
   external release lever. Straighten the emerged chain first.
5. Retain three bases per bead, bounded travel, 26 beads / 28 pockets / 22
   steps, four hidden beads and at least three at/behind the tangent station.
6. Route the closed RNA farther across the body midline and around the far
   flank, close to a matching groove. Retain captive open-strand operation.

The user's marked routing reference is
[v7-routing-request.png](images/v7-routing-request.png). Its red line is a
qualitative path request, not dimensions. The
[generated coupling illustration](images/v7-coupling-concept.png) explains the
proposed opposite catches; it is not current CAD or validated geometry.

## Implemented candidate

`cad/v7/` is a self-contained source copy, not an import of the V6 generator.

- `bracelet_v7.py`: body, shared drive, RNA and protein, native cycle, GUI
  controls. `InputKind`: 0 RNA forward, 1 manual upper, 2 RNA reverse.
- `coupling_v7.py`: opposite pickup track/pawl, lifting fork, hold-open leaf,
  trip/snap leaf, fixed reset roof, upper carrier/shell split and extra screws.
- `rna_path.py`: broad 33 mm bends, 110 pitches; 16-degree routing plane in
  the generator. Front rack mesh is unchanged. Material length 248.814 mm.
- `validation_v7.py`, `assembly_v7.py`: partially adapted development checks.
  They have not completed a successful integrated run.
- `engineering_v7.py`: incomplete starting force budget; it explicitly lists
  missing pickup, snap and reset terms.
- `presentation_v7.py`: checkpoint GUI/native helper. Its evidence is separate
  from integrated CAD validation and controls-animation acceptance.
- `RibosomeV7.FCStd`, actual CAD views, `checks.json`, `gui-checks.json`:
  an explicitly incomplete inspection checkpoint, not a release.

The source now positively drives a complete manual bead step after 3 degrees
of entry. Manual upper travel is 15.857 degrees; RNA pickup travel is 12.857
degrees. This avoids the discarded detent-assisted finishing scheme but is
not an identical angular stroke. Preserve or deliberately improve this
tradeoff; do not conceal it.

## Evidence boundary at handoff

FreeCAD 1.1.4 with `Part` and bundled `fcgear` was available locally. A complete
V7 source build has been run. Earlier isolated actual-solid pawl/track probes
showed zero rigid interference and contact for the active drive directions,
plus clear nominal coast/return poses. Those probes preceded final integration
and timing changes; they do not validate the saved final checkpoint.

The integrated coupling probe was interrupted while checking the first input.
It did not yield a complete report. Full RNA/body/gear/protein phase checks,
new assembly checks and complete native controls acceptance remain unfinished.
Read the machine-readable incomplete report; never substitute V6's PASS.

The most important unresolved issue is **physical control of the trip and
reset sequence**. The fork, latch and trip leaf have native prescribed states.
These do not prove that spring forces will produce those states. Continuous
RNA pull is paused by the GUI, not by a completed mechanical gate. Analyze
snap energy, holding/release loads, reset rate, missed cycles, partial strokes
and reverse attempts before claiming a functional mechanism.

## Suggested next work

1. Provision and verify a compatible FreeCAD runtime; run `doctor`. Ordinary
   Python cannot supply `FreeCAD`, `Part` or the bundled `fcgear` modules.
2. Inspect the saved V7 candidate and source. Resolve actual mechanical
   causality, not only collision-free scripted movement. Simplify if needed,
   but preserve the user's interaction requirements and explain tradeoffs.
3. Finish and run the integrated validator/auditor. Expensive near-coincident
   Booleans should use justified local crops, repeated-pose caching and
   validated envelopes. Do not skip failed pairs or loosen tolerances to pass.
4. Check both RNA modes across full travel, the flank groove, clasp motion,
   wall thickness, protein outlet clearance and actual bead/drum phases.
5. Check the detachable shell, reset bridge, fastener seats, keys, guide pins,
   driver access and real assembly paths. The bridge is intended to be
   inserted radially above its locating pin, then lowered, before the shell.
6. Exercise native forward/manual/reverse cycles and GUI controls, save and
   normally reopen the model, then update source/model/reports/views together.
7. Keep CAD, spring assumptions and physical tests distinct. No model here
   demonstrates printing, feeding, force, fatigue, sound or hand fit.

## Portable commands and constraints

```sh
python scripts/check_repo.py
python scripts/cad.py doctor --freecad /path/to/compatible/FreeCADCmd
python scripts/cad.py build --version 7 --force --freecad /path/to/compatible/FreeCADCmd
python scripts/cad.py validate --version 7 --freecad /path/to/compatible/FreeCADCmd
```

The launcher's default remains V6 while V7 is incomplete. Outputs go to
ignored `build/v7/`. The saved V7 report must stay incomplete until a fresh
appropriate run establishes something stronger. Preserve old CAD/report/image
bytes. Do not use an old V6 report, static checker or illustration as evidence
that V7 works. Cloud FreeCAD/runtime setup is not validated by the Windows run.

V6's preceding Linux GUI workflow is documented, but do not assume access to
that machine or cached dependencies. Install a compatible runtime in the
cloud environment. Use offscreen rendering or a virtual display if available;
if GUI dependencies are unavailable, say so and leave GUI acceptance open.
No Windows GUI/MCP bridge or local personal skill is a repository dependency.

The repository checker accepts exact source digests or CRLF-to-LF-normalized
source digests, because Git can check Python/macros out with Windows line
endings while the earlier reports were generated on Linux. CAD model hashes
remain byte-exact. This normalization does not rewrite preserved sources or
reports and does not permit any other source changes.
