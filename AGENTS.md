# Working on mRNA toy

Read `README.md`, then `docs/design.md` and `docs/status.md`. Use `docs/development.md` for commands. These files carry the project context; no previous chat or desktop attachment is required.

## Current design contract

- V5 in `cad/v5/` is the current handheld design, authorized on 2026-10-29. Preserve V4 and V4 Print, V3 with its incomplete report, and V2 with its invalidated-validation warning.
- The whole toy is a palm-held ribosome: larger fixed lower body, smaller rocking upper input, and a separate closed RNA loop around the lower body. RNA enters a covered engagement cheek. No wrist cuff or finger ring in V5.
- A driven single-row 28-pocket drum stores 26 connected protein beads. A fixed keeper and tangent guide capture the handoff. Retraction uses the same drive in reverse, without a cord reel or tensioned spring take-up.
- Moving RNA or clicking the upper subunit advances both strands: three visible bases per bead. Retain bounded travel, four hidden beads at maximum feed and at least three at or behind the tangent station. Straighten the emerged chain and release both click leaves before reverse.
- The user authorized compact lobed beads and a less pronounced outlet between the lobes. Three bead variants retain the 4.4 mm spherical bound, common drive shoulders and 6 mm spacing. The chain is shaped by hand; the optional CAD pose is illustrative, with no automatic curling.
- The user authorized A1 mini manufacturing preparation on 2026-10-29. Work in the separate `cad/v4-print/` derivative and `print/v4-a1-mini/` package; preserve V4. Physical qualification remains open.
- Colours and proposed dimensions are secondary. The most recent discussion considered a Moderna-inspired palette, but no branding pass is authorized or implemented.
- `cad/v5/handheld.png` and its mechanism/drum views show current CAD. The wearable AI concept and conversation sketches are not geometry references. Use source/model and `docs/images/README.md` for provenance.

## Engineering and workflow

Continue locally; cloud migration is deferred. The A1 mini prototype derivative is authorized; keep physical evidence distinct from CAD and slicer results.

V5 checks actual bead/drum handoff solids, gears, housing, travel stops and native forward/reverse motion. The click leaves are unloaded flexures; their preload overlaps are separate. The cap return spring is a space claim. Neither a V5 nor V4 `FOCUSED_PASS` qualifies physical operation or completes V3's `INCOMPLETE_USER_STOPPED` validation.

V5 retains one RNA backbone with free-ended bases and a hidden drive rail. The loose flexible loop is represented on its nominal circular path; sag, stretching and retention require physical tests. V4 retains its separate cuff architecture.

- Keep requirements, proposed engineering choices, CAD observations and physical test results distinct. A geometric PASS is not proof of reliable feeding, strength, comfort or printability.
- Preserve the actual bead-to-wheel phase checks. V2's profile-only validation missed interference; do not repeat that mistake.
- Current geometry comes from `cad/v5/bracelet_v5.py`; native expressions preserve saved motion. Use `scripts/cad.py` to build or validate into `build/v5/` (the default version). Select older versions explicitly. Do not silently replace saved models or reports.
- For source changes, run `python scripts/check_repo.py`. For geometry or motion changes, also run the FreeCAD build/validation appropriate to the change. Report unavailable CAD dependencies honestly; static checks do not substitute for a CAD run.
- Keep source, saved CAD, images and reports consistent when intentionally promoting a new CAD revision. Keep generated test outputs, backups and caches out of Git.
- The Windows FreeCAD GUI and its MCP connection are local conveniences, not repository dependencies. Do not assume access to that machine, MCP, private paths, screenshots or cached visualizations in another environment.
- Preserve unrelated Git changes. The user's earlier preference is to keep the working tree focused: superseded experiments belong in Git history, not new archive folders. Preserve explicitly requested version comparisons.

Maintain this file as a short guide. Put design detail in `docs/`, not a transcript or a growing list of speculative mechanisms.
