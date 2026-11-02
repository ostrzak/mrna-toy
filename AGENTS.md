# Working on mRNA toy

Read `README.md`, then `docs/design.md` and `docs/status.md`. Use `docs/development.md` for commands. These files carry the project context; no previous chat or desktop attachment is required.

## Current design contract

- V6 in `cad/v6/` is the current handheld design, authorized on 2026-10-30. Preserve V5, V4 and V4 Print, V3 with its incomplete report, and V2 with its invalidated-validation warning.
- V6 uses one captive TPU-candidate RNA strip through a short capture channel at the front drive peak. Its ends may be joined underneath or left open; clasp shoulders double as end stops. Both outer holders are removed. The longer closed route crosses the curved flank before returning underneath in an open groove. No bottom rails, parking clip, wrist cuff or finger ring.
- Moving RNA backward directly retracts protein. No external release lever, rewind reel or protein take-up spring. V5's circular loop and release tab are preserved comparisons.
- V6 retains the fuller asymmetric upper from the V5 proportion pass and flatter lower palm dome. The RNA route is inclined 38 degrees, with a nominal 226.195 mm material length. The drive entry, clasp and mechanism remain the same. Ease of use and compact guidance take priority over the loop's exact shape. One 84-tooth shared gear drives the RNA rack. Three bases advance per bead, with a nominal 149.288 mm RNA stroke.
- A driven single-row 28-pocket drum stores 26 connected protein beads. A fixed keeper and tangent guide capture the handoff. Retraction uses the same drive in reverse, without a cord reel or tensioned spring take-up.
- V6 has one aligned three-screw housing stack, an integral fixed spindle/root and a separately seated cap washer. Its rotor is split into two D-keyed parts so the lid and cover can be inserted. Check actual shaft passages, bearing seats, integral roots, key fit/torque and sampled insertion paths; valid individual solids and a collision-only pass do not establish assembly. See `docs/v6-assembly.md`.
- Moving RNA or rocking the upper subunit advances both strands. Retain bounded travel, four hidden beads at maximum feed and at least three at or behind the tangent station. Straighten the emerged chain before reverse. A symmetric detent supplies proposed bidirectional clicks; the cap's rigid internal pawl lifts clear at rest and rises over axial face ramps on return.
- The user authorized compact lobed beads and a less pronounced outlet between the lobes. Three bead variants retain the 4.4 mm spherical bound, common drive shoulders and 6 mm spacing. The chain is shaped by hand; the optional CAD pose is illustrative, with no automatic curling.
- The user authorized A1 mini manufacturing preparation on 2026-10-29. Work in the separate `cad/v4-print/` derivative and `print/v4-a1-mini/` package; preserve V4. Physical qualification remains open.
- Colours and proposed dimensions are secondary. The most recent discussion considered a Moderna-inspired palette, but no branding pass is authorized or implemented.
- `cad/v6/handheld.png`, `open.png`, `underside.png`, `mechanism.png` and `cap-input.png` show current CAD. AI routing concepts and the wearable illustration are not geometry references. Use source/model and `docs/images/README.md` for provenance.

## Engineering and workflow

Continue locally; cloud migration is deferred. The A1 mini prototype derivative is authorized; keep physical evidence distinct from CAD and slicer results.

V6 checks actual bead/drum and RNA rack/gear contacts, guide captivity, clasp fit/travel, continuous envelopes, native positions and orientations in both RNA modes, cap feed/return, fastening, sampled assembly paths and physical stop geometry. Flexible RNA cells and leaf chords represent prescribed deformation; the two cap-input springs are space claims. A `FOCUSED_PASS` does not qualify physical operation or complete V3's `INCOMPLETE_USER_STOPPED` validation.

V6 RNA material length is constant between its two nominal layouts. Sag, stretch, clasp retention, sound, force, fatigue and hand fit need physical tests. V5 retains its circular loop; V4 retains its separate cuff architecture.

- Keep requirements, proposed engineering choices, CAD observations and physical test results distinct. A geometric PASS is not proof of reliable feeding, strength, comfort or printability.
- Preserve the actual bead-to-wheel phase checks. V2's profile-only validation missed interference; do not repeat that mistake.
- Current geometry comes from `cad/v6/bracelet_v6.py` and `rna_path.py`; native expressions preserve saved motion. Use `scripts/cad.py` to build or validate into `build/v6/` (the default version). Select older versions explicitly. Do not silently replace saved models or reports.
- For source changes, run `python scripts/check_repo.py`. For geometry or motion changes, also run the FreeCAD build/validation appropriate to the change. Report unavailable CAD dependencies honestly; static checks do not substitute for a CAD run.
- Keep source, saved CAD, images and reports consistent when intentionally promoting a new CAD revision. Keep generated test outputs, backups and caches out of Git.
- The Windows FreeCAD GUI and its MCP connection are local conveniences, not repository dependencies. Do not assume access to that machine, MCP, private paths, screenshots or cached visualizations in another environment.
- Preserve unrelated Git changes. The user's earlier preference is to keep the working tree focused: superseded experiments belong in Git history, not new archive folders. Preserve explicitly requested version comparisons.

Maintain this file as a short guide. Put design detail in `docs/`, not a transcript or a growing list of speculative mechanisms.
