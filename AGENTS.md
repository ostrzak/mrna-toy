# Working on mRNA toy

Read `README.md`, then `docs/design.md` and `docs/status.md`. Use `docs/development.md` for commands. These files carry the project context; no previous chat or desktop attachment is required.

## Current design contract

- V3 in `cad/v3/` is the working baseline. Preserve V2 in `cad/v2/` as a historical comparison, including its invalidated-validation warning.
- A fixed ribosome mounts to one end of a flexible C cuff. A separate RNA-like C dial aligns its opening with the cuff at home, then moves across that opening during play. Do not rigidly bridge the cuff ends.
- A hidden channel stores the protein chain. In V3 the chain exits beside the RNA in the **same local direction**, through a short outlet and close bead keeper. The upper lobe's driven swivel is independent of this route.
- Retain three visible RNA bases per bead step, bounded dial travel, an engaged hidden tail, and reversible feed after the user straightens the emerged chain.
- More realistic bead shapes and manufacturing preparation were requested for **analysis only**. Do not implement those changes just because they appear in the backlog; follow the current user's scope.
- Colours and proposed dimensions are secondary. The most recent discussion considered a Moderna-inspired palette, but no branding pass is authorized or implemented.
- `docs/images/toy-concept.png` is the refreshed V3-based AI illustration; the early on-wrist image is superseded. Use CAD/source for geometry, and `docs/images/README.md` for image provenance. Illustration changes do not implement or approve bead geometry.

## Engineering and workflow

The immediate continuation plan is a new **local** chat focused on beads; cloud migration is deferred. Preserve the analysis-only boundary until the new user request authorizes implementation.

- Keep requirements, proposed engineering choices, CAD observations and physical test results distinct. A geometric PASS is not proof of reliable feeding, strength, comfort or printability.
- Preserve the actual bead-to-wheel phase checks. V2's profile-only validation missed interference; do not repeat that mistake.
- Geometry comes from `cad/v3/bracelet_v3.py`; native expressions preserve saved motion. Use `scripts/cad.py` to build or validate into `build/v3/`. Do not silently replace committed models or reports.
- For source changes, run `python scripts/check_repo.py`. For geometry or motion changes, also run the FreeCAD build/validation appropriate to the change. Report unavailable CAD dependencies honestly; static checks do not substitute for a CAD run.
- Keep source, saved CAD, images and reports consistent when intentionally promoting a new CAD revision. Keep generated test outputs, backups and caches out of Git.
- The Windows FreeCAD GUI and its MCP connection are local conveniences, not repository dependencies. Do not assume access to that machine, MCP, private paths, screenshots or cached visualizations in another environment.
- Preserve unrelated Git changes. The user's earlier preference is to keep the working tree focused: superseded experiments belong in Git history, not new archive folders. Preserve explicitly requested version comparisons.

Maintain this file as a short guide. Put design detail in `docs/`, not a transcript or a growing list of speculative mechanisms.
