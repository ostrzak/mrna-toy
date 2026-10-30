# Development and local handoff

## Current V5 workflow

V5 is the handheld design in `cad/v5/`. Its source, validator, saved model,
macro, report and actual CAD views belong together. It builds from its own
source and does not import or modify V4. The launcher now defaults to V5:

```sh
python scripts/check_repo.py
python scripts/cad.py doctor
python scripts/cad.py build --version 5 --force
python scripts/cad.py validate --version 5
```

With the known local Windows runtime, append
`--freecad "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"`.
Generated files go to ignored `build/v5/`; saved version models and reports
are protected. The same launcher retains explicit `3`, `4` and `4-print` modes.

Before promoting V5, use its `present(document)` in the GUI and save display
state, then close and reopen normally. Save `handheld.png`, `mechanism.png`,
`drum.png` and `home.png` from that geometry. Run a fresh validation against the
promoted model, then the repository checker. Never substitute an AI concept
image or an old V4 report for current CAD evidence.

V5 checks real bead solids and spherical bounds through the sampled pocket
handoff, both actual involute gear meshes, native forward/reverse motion,
housing clearances and geometric stops. Click leaves are unloaded elastic
geometry; their preload overlaps are reported separately. The cap spring is a
space claim. This does not qualify clicking, RNA flex, force, fatigue or printing.

## Preserved V4 development

## Files and versions

V4 in `cad/v4/` is a preserved cuff comparison. Its [source](../cad/v4/bracelet_v4.py), [validator](../cad/v4/validation_v4.py), [model](../cad/v4/RibosomeV4.FCStd), [macro](../cad/v4/RibosomeV4.FCMacro), [report](../cad/v4/checks.json) and views belong together. V3 and V2 retain their original validation boundaries.

The V4 build revises four shapes in its own copied model: cuff front, cuff rear, RNA and upper lobe. It retains the other mechanism shapes and native expressions and does not read or write V3. `build_from_scratch()` remains available for complete procedural generation. The version macro selects its adjacent saved model.

## Runtime and commands

Python 3.10+ runs the repository checker and launcher. Geometry requires FreeCAD's own runtime with `FreeCAD`, `Part` and bundled `fcgear`; installing a normal Python package is insufficient. The known local runtime is FreeCAD 1.1.4. GUI presentation additionally uses `FreeCADGui` and its PySide bindings.

```sh
python scripts/check_repo.py
python scripts/cad.py doctor
python scripts/cad.py build --version 4
python scripts/cad.py validate --version 4
```

Select V4 explicitly. On this Windows installation:

```powershell
python scripts/cad.py build --version 4 --freecad "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
```

That path is a local example, not a repository dependency. Alternatively set `FREECAD_CMD` or put `FreeCADCmd` / `freecadcmd` on PATH. In another environment provision a compatible runtime and run `doctor`; Linux/cloud execution remains unverified. The Windows GUI and MCP connection are local conveniences, not portable dependencies. Cloud migration remains deferred.

## Output boundaries

- `doctor` checks runtime imports and version; it does not build geometry.
- `build` writes and checks `build/v4/RibosomeV4.FCStd` and `build/v4/checks.json`.
- `validate` opens the saved version model in memory and writes a fresh report into `build/v4/`. Use `--model build/v4/RibosomeV4.FCStd` to check a generated model.
- `--force` allows replacing generated CAD; `--output PATH` selects another output folder. The launcher refuses to overwrite saved version CAD or reports.
- `--version 3` selects V3 explicitly. Its report remains incomplete unless a separate full run establishes otherwise.

Child output is streamed for progress. A failed runtime or `REVIEW` result is not a fresh PASS. Generated outputs, caches and FreeCAD backups stay out of Git.

Before promoting a generated model, open it in the GUI, put its source folder on `sys.path`, import `bracelet_v4 as model`, call `model.present(document)`, and save its display state. Verify a normal close-and-reopen. Headless files can otherwise load with all parts hidden; the repository checker rejects missing GUI data. Compare model, report and rendered views before intentionally promoting them together.

To inspect a generated model interactively, open it directly; the version macro deliberately chooses the saved adjacent model. `model.open_controls(document)` adds controls. Do not close or overwrite unrelated unsaved GUI documents.

## Validation scope

V4 returns `FOCUSED_PASS` for its changed geometry: valid connected solids, continuous RNA/protein envelopes, cover clearance, nine actual gear phases, actual saved bead-to-feeder phase contacts, travel stops, prescribed native positions and the example hand pose. Ten coupled poses include both swivel extremes. The cover envelope conservatively bounds its complete inverse rotation range.

This does not complete V3's unfinished full validation. The copied baseline suite remains available separately in the V4 validator. No check proves friction, force, elasticity, print fits, fatigue, strength, comfort or reliable physical feeding. Wire segments are chords and the detent shape represents unloaded geometry with intentional preload.

For source edits run the repository checker. For geometry or motion edits also run appropriate CAD checks and inspect the result. If dependencies are unavailable, say so; a static check or old report is not a CAD run. A1 mini prototype preparation is now authorized in the separate V4 Print derivative.

## A1 mini derivative

Use `python scripts/cad.py build --version 4-print --force` or `validate --version 4-print`. Outputs go to `build/v4-print/`. Source is `cad/v4-print/bracelet_v4_print.py`. Run `export_print.main()` in FreeCAD after adding that folder to `sys.path` to export the generated CAD. `python scripts/print_package.py profiles`, `author`, and `slice` generate the offline plate package, using installed Bambu Studio resources. Review mesh warnings and slicer checks before printing. Do not promote an unfinished export check to a physical PASS.
