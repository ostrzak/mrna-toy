"""Run V3 CAD work with FreeCAD's Python runtime, preserving committed artifacts."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'cad' / 'v3'
MODEL = SOURCE / 'RibosomeV3.FCStd'
COMPLETE = 'MRNA_CAD_COMPLETE'


def executable(explicit: str | None) -> str:
    requested = explicit or os.environ.get('FREECAD_CMD')
    if requested:
        found = shutil.which(requested)
        if found:
            return found
        candidate = Path(requested).expanduser()
        if candidate.is_file():
            return str(candidate.resolve())
        raise ValueError(f'FreeCAD command-line executable not found: {requested}')
    for name in ('FreeCADCmd', 'freecadcmd', 'freecadcmd.exe'):
        if found := shutil.which(name):
            return found
    raise ValueError('FreeCADCmd was not found. Set FREECAD_CMD or pass --freecad PATH. '
                     'The host Python interpreter does not supply FreeCAD geometry modules.')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('doctor', 'validate', 'build'))
    parser.add_argument('--freecad', help='FreeCAD command-line executable (or set FREECAD_CMD).')
    parser.add_argument('--output', type=Path, default=ROOT / 'build' / 'v3',
                        help='Generated-output directory; default: build/v3.')
    parser.add_argument('--model', type=Path, default=MODEL,
                        help='Model to open for validate; default: committed V3 model.')
    parser.add_argument('--force', action='store_true', help='Allow replacing a generated build model.')
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    report = output / 'checks.json'
    generated = output / MODEL.name
    model = args.model.expanduser().resolve()
    if args.command != 'doctor':
        if report == SOURCE / 'checks.json' or generated == MODEL:
            parser.error('Refusing to overwrite committed V3 artifacts. Use build/v3 or another output directory.')
        if args.command == 'validate' and not model.is_file():
            parser.error(f'Model not found: {model}')
        if args.command == 'build' and generated.exists() and not args.force:
            parser.error(f'Generated model already exists: {generated}; use --force to replace it.')
    try:
        freecad = executable(args.freecad)
    except ValueError as error:
        parser.error(str(error))

    code = [
        'import sys, json',
        'sys.dont_write_bytecode = True',
        f'sys.path.insert(0, {str(SOURCE)!r})',
        'import FreeCAD as App',
        'import Part',
        'from fcgear import involute, fcgear',
        "print('FreeCAD runtime: ' + '.'.join(App.Version()[:3]), flush=True)",
    ]
    if args.command == 'doctor':
        code.append("print('Geometry dependencies: FreeCAD, Part, fcgear OK', flush=True)")
    else:
        output.mkdir(parents=True, exist_ok=True)
        code.append('import bracelet_v3 as model_source')
        if args.command == 'build':
            code.append(f'document = model_source.build(save_path={str(generated)!r})')
        else:
            code.append(f'document = App.openDocument({str(model)!r})')
        code.extend([
            f'result = model_source.validate(document, report_path={str(report)!r})',
            "if result['status'] != 'PASS': raise RuntimeError('CAD checks require review; see the generated report.')",
        ])
    code.append(f'print({COMPLETE!r}, flush=True)')
    env = os.environ.copy()
    if sys.platform.startswith('linux') and not env.get('DISPLAY'):
        env.setdefault('QT_QPA_PLATFORM', 'offscreen')
    print(f'{args.command}: {freecad}', flush=True)
    completed = subprocess.run([freecad, '-c', '\n'.join(code)], cwd=ROOT, env=env,
                               capture_output=True, text=True, errors='replace')
    print(completed.stdout, end='')
    if completed.stderr:
        print(completed.stderr, end='', file=sys.stderr)
    if completed.returncode or COMPLETE not in completed.stdout:
        print('FreeCAD did not complete successfully. A pre-existing report is not a fresh PASS.', file=sys.stderr)
        return 1
    if args.command != 'doctor':
        result = json.loads(report.read_text(encoding='utf-8'))
        if result.get('status') != 'PASS':
            return 1
        print(f'PASS - fresh report: {report}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
