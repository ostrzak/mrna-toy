# mRNA toy

A wearable mechanical fidget inspired by protein translation. Turning an RNA-like dial around a cuff makes a hidden amino-acid chain emerge from an organic ribosome. The user can shape the exposed chain into a protein-like fold, straighten it, and reverse the dial to retract it.

**V3 is the current CAD prototype. It has geometric motion checks, but has not been physically built or qualified for printing.**

![Updated V3 concept illustration, with provisional rounded protein beads](docs/images/toy-concept.png)

AI-generated appearance illustration based on V3. The [actual CAD view](cad/v3/bracelet.png) and saved model define the implemented geometry; [image provenance](docs/images/README.md) records the reference and prompt. The early on-wrist illustration is superseded.

## Start here

- [Toy purpose and conceptual mechanics](docs/design.md)
- [Current state, pending requests and engineering risks](docs/status.md)
- [Development, local/headless CAD commands and handoff](docs/development.md)
- [FreeCAD viewing and movement controls](cad/README.md)
- [Repository instructions for coding agents](AGENTS.md)

## CAD versions

| Version | Model and controls | Role |
| --- | --- | --- |
| **V3** | [Model](cad/v3/RibosomeV3.FCStd) · [Macro](cad/v3/RibosomeV3.FCMacro) · [Guide](cad/v3/README.md) | Current: direct protein outlet, moving in the same local direction as RNA. |
| **V2** | [Model](cad/v2/Ribosome.FCStd) · [Macro](cad/v2/Ribosome.FCMacro) · [Guide](cad/v2/README.md) | Preserved comparison. Its older validation missed bead-to-wheel interference; do not use it as the working baseline. |

In FreeCAD, run the version's macro to open the model and controls. **Home** resets the dial, **One codon** animates a bead step, and the slider covers the intended range. **Open storage / mechanism** reveals the internals. See the [operating guide](cad/README.md) for exact steps.

## Development quick start

Python 3.10+ can check the repository without FreeCAD:

```sh
python scripts/check_repo.py
```

Geometry work requires a separate FreeCAD command-line runtime with `Part` and the bundled `fcgear` modules. The known local baseline is FreeCAD 1.1.4. With `FreeCADCmd` or `freecadcmd` on `PATH`:

```sh
python scripts/cad.py doctor
python scripts/cad.py validate
python scripts/cad.py build
```

The launcher also accepts `--freecad /path/to/FreeCADCmd` or the `FREECAD_CMD` environment variable. Generated models and reports go to the ignored `build/v3/` directory; the committed CAD is preserved. The [development guide](docs/development.md) explains prerequisites and validation limits.

## What remains open

The next session is planned locally, with bead design as the intended focus; cloud migration is deferred. The user has requested more molecular-looking, asymmetric amino-acid beads. That request has been **analysed only**; the current model still uses spheres. The printer, nozzle/process, final materials, bead fixation, wire life, cuff flexibility, fasteners and reliable reverse feeding remain unresolved. These are recorded in [project status](docs/status.md), so work can continue without this chat.

Superseded layout studies and duplicate chat handoff files have been removed from the working tree. They remain recoverable from Git history. V2 is retained because it was explicitly requested as a comparison.
