# Development and handoff

## Repository map

| Path | Responsibility |
| --- | --- |
| [README](../README.md), [AGENTS](../AGENTS.md) | Entry point and concise repository guidance. |
| [Design](design.md), [status](status.md) | Purpose, conceptual mechanics, accepted direction, pending requests and validation limits. |
| [CAD guide](../cad/README.md) | FreeCAD viewing, version selection and movement controls. |
| [V3 generator](../cad/v3/bracelet_v3.py) | Dimensions, shapes, native expressions, presentation and GUI controls. |
| [V3 validator](../cad/v3/validation_v3.py) | Shape, contact, guide, stop and linkage checks. |
| [V3 macro](../cad/v3/RibosomeV3.FCMacro) | Opens the adjacent saved model and its control dock. |
| [V3 report](../cad/v3/checks.json) | Committed geometric validation snapshot, not physical acceptance. |
| [V2](../cad/v2/README.md) | Preserved historical comparison with an invalidated-validation warning. |
| [CAD launcher](../scripts/cad.py) | Portable command-line build and validation into an output directory. |
| [Repository checker](../scripts/check_repo.py) | Python syntax, local Markdown links, CAD container and stored-report sanity checks without FreeCAD. |

## Environment requirements

The known working local runtime is **FreeCAD 1.1.4**. Geometry scripts require its `FreeCAD`, `Part`, and bundled `fcgear` modules. They are not installed by adding a normal Python package requirement. GUI presentation and the macro additionally use `FreeCADGui` and FreeCAD's PySide bindings.

The launcher and repository checker use only the Python 3.10+ standard library. The launcher starts FreeCAD's own command-line executable in a separate process; it does not import FreeCAD into the host Python interpreter. Set `FREECAD_CMD`, supply `--freecad`, or place `FreeCADCmd` / `freecadcmd` on `PATH`.

```sh
python scripts/check_repo.py
python scripts/cad.py doctor
python scripts/cad.py validate
python scripts/cad.py build
```

For the currently verified Windows installation, PowerShell can use:

```powershell
python scripts/cad.py doctor --freecad "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
python scripts/cad.py validate --freecad "C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe"
```

The executable path is an example of the local installation, not a repository dependency. In Linux/cloud, install or provision a compatible FreeCAD command-line runtime with the required modules, then run `doctor`. An installed package's version must be checked; package availability alone does not establish compatibility. A Linux/cloud runtime has not been verified by this Windows cleanup.

## Commands and output boundaries

- `doctor` checks that FreeCAD and the geometry dependencies import, and prints the runtime version. It does not build or modify a CAD file.
- `validate` opens the committed V3 model, checks it in memory, and writes `build/v3/checks.json`. It does not save changes to the model. Use `--model build/v3/RibosomeV3.FCStd` to check a previously generated model.
- `build` regenerates V3 into `build/v3/RibosomeV3.FCStd` and validates it. Use `--force` to replace an existing generated model. It refuses to overwrite the committed CAD or report.
- `--output PATH` selects another output directory. A `REVIEW` result or a failed FreeCAD process gives a nonzero launcher exit status.

`build/`, Python caches and FreeCAD automatic backups are ignored. Compare the generated model, report and rendered motion before intentionally promoting files into `cad/v3/`. Refresh the committed image and report if a promoted geometry revision changes them. A documentation-only cleanup should preserve the binary CAD.

For interactive rebuilding inside FreeCAD's Python console, import the V3 module from its folder and call `build()` only with the V3 document closed. The default direct API still saves beside the source; the command-line launcher is the safer output-isolated workflow. `validate(document, report_path=...)` can write a chosen report path.

To inspect a generated build, open `build/v3/RibosomeV3.FCStd` directly. The version macro deliberately selects its adjacent committed model, so it is not a launcher for a generated build. With `cad/v3` on the FreeCAD Python console's `sys.path`, use `import bracelet_v3 as model`, `model.present(App.ActiveDocument)`, and `controls = model.open_controls(App.ActiveDocument)` on the opened generated document. This also initializes its GUI visibility and colours. Interactive visual review requires a GUI-capable environment.

## What validation establishes

The geometry source defines a wrist axis along Y, dorsal direction +Z and local feed direction +X. At the ribosome, both RNA and the unposed protein outlet travel in +X during forward play. The swivel axis points outward along Z. Shape motion is prescribed using native expressions, not a force-driven simulation.

The validator checks valid one-solid parts, swept guide/rotor clearance, sampled RNA mesh phases, actual bead-to-wheel contacts at selected phases, follower/lever alignment, lobe clearance, nominal limits and overtravel stops. It checks the illustrative posed strand against the cases and lobe. It does not solve elastic deformation, friction, gravity, force, fatigue, material strength or print tolerance.

The closed-groove cam and its captured follower are modelled mechanically. The click leaf is represented in its unloaded state; intended cam preload is not counted as an unintended rigid collision. Its force and life need physical validation. Wire segments are shown as chords and are not a copper fatigue or forming model.

Run only the checks appropriate to the change. For geometry/motion edits, retain actual contact checks, inspect a generated model and record the runtime used. If FreeCAD is unavailable, run the repository checker and report that CAD validation was not performed; do not call a stored PASS a fresh run.

## Continuing in another environment

The immediate plan is to continue in a new **local** chat, with bead design as the intended next focus. Cloud migration is deferred. The portable workflow below remains available; check runtime availability with `doctor` and do not assume an earlier GUI or MCP session is still connected.

Start from the repository files, not this chat. Root `AGENTS.md` points to the current design and pending-work state; this follows the [official OpenAI guidance on repository context](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex). Keep this context short and maintained rather than introducing a transcript or a large prompt bundle.

The previous Windows GUI/MCP connection is not provided by cloning this repository. Headless builds do not require it. If the new environment has no usable FreeCAD runtime, documentation and source review remain possible, but geometry execution must be provisioned separately. No local credentials, user-specific paths or environment files are needed for the basic repository checks.

The next chat should read [status](status.md) before proposing work. In particular, do not treat the earlier bead-shape analysis or manufacturing discussion as approval to alter the model. Ask what concrete task to tackle next if the new user prompt does not provide one.
