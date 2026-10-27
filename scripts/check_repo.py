"""Check handoff integrity without importing FreeCAD or modifying repository files."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+"[^"\n]*")?\s*\)')


def run() -> int:
    errors = []
    required = [
        'README.md', 'AGENTS.md', 'docs/design.md', 'docs/status.md', 'docs/development.md',
        'docs/images/toy-concept.png', 'cad/README.md', 'cad/v3/bracelet.png',
        'cad/v3/bracelet_v3.py', 'cad/v3/validation_v3.py', 'cad/v3/RibosomeV3.FCMacro',
        'cad/v2/bracelet.py', 'cad/v2/Ribosome.FCMacro',
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            errors.append(f'Missing handoff file: {relative}')

    code_count = 0
    for folder in (ROOT / 'cad', ROOT / 'scripts'):
        for path in folder.rglob('*'):
            if path.suffix not in ('.py', '.FCMacro'):
                continue
            try:
                ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
                code_count += 1
            except (OSError, SyntaxError) as error:
                errors.append(f'{path.relative_to(ROOT)}: {error}')

    link_count = 0
    markdown = [ROOT / 'README.md', ROOT / 'AGENTS.md']
    markdown += list((ROOT / 'docs').rglob('*.md')) + list((ROOT / 'cad').rglob('*.md'))
    for path in markdown:
        if not path.is_file():
            continue
        for match in LINK.finditer(path.read_text(encoding='utf-8-sig')):
            target = match.group(1).strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            linked = path.parent / unquote(parsed.path)
            if not linked.exists():
                errors.append(f'{path.relative_to(ROOT)}: broken link {target}')
            link_count += 1

    for relative in ('cad/v2/Ribosome.FCStd', 'cad/v3/RibosomeV3.FCStd'):
        try:
            with zipfile.ZipFile(ROOT / relative) as archive:
                if 'Document.xml' not in archive.namelist() or archive.testzip() is not None:
                    errors.append(f'Invalid CAD container: {relative}')
        except (OSError, zipfile.BadZipFile) as error:
            errors.append(f'{relative}: {error}')

    try:
        current = json.loads((ROOT / 'cad/v3/checks.json').read_text(encoding='utf-8-sig'))
        historical = json.loads((ROOT / 'cad/v2/checks.json').read_text(encoding='utf-8-sig'))
        if current.get('version') != '3.0' or current.get('status') != 'PASS':
            errors.append('Committed V3 report is not a passing V3 snapshot; document the current state.')
        if current.get('invalid_objects') or not current.get('physical_tests_still_required'):
            errors.append('V3 report must retain its validity results and physical-test boundary.')
        if current.get('kinematics', {}).get('rna_bases_per_bead') != 3:
            errors.append('V3 report no longer describes the accepted three-bases-per-bead contract.')
        if historical.get('status') != 'HISTORICAL_PASS_INVALIDATED':
            errors.append('V2 must retain the warning that its historical PASS was invalidated.')
    except (OSError, ValueError) as error:
        errors.append(f'Stored report could not be read: {error}')

    if errors:
        print('\n'.join('ERROR: ' + error for error in errors))
        return 1
    print(f'PASS - {code_count} Python/macro files parsed, {link_count} local Markdown links checked, '
          'both CAD containers readable, report snapshots consistent.')
    print('This is repository integrity checking, not a fresh FreeCAD or physical-mechanism test.')
    return 0


if __name__ == '__main__':
    raise SystemExit(run())
