"""Check handoff integrity without importing FreeCAD or modifying repository files."""
from __future__ import annotations

import ast
import hashlib
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
        'cad/v4/bracelet_v4.py', 'cad/v4/validation_v4.py', 'cad/v4/RibosomeV4.FCMacro',
        'cad/v4/bracelet.png','cad/v4/rna.png','cad/v4/mechanism.png',
        'cad/v4-print/bracelet_v4_print.py','cad/v4-print/validation_v4_print.py',
        'cad/v4-print/RibosomeV4Print.FCMacro','print/v4-a1-mini/README.md',
        'cad/v5/bracelet_v5.py','cad/v5/validation_v5.py','cad/v5/RibosomeV5.FCMacro',
        'cad/v5/README.md','cad/v5/handheld.png','cad/v5/mechanism.png','cad/v5/drum.png','cad/v5/home.png',
        'print/v4-a1-mini/manifest.json','print/v4-a1-mini/handoff.json',
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
    markdown += list((ROOT / 'print').rglob('*.md'))
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

    for relative in ('cad/v2/Ribosome.FCStd', 'cad/v3/RibosomeV3.FCStd','cad/v4/RibosomeV4.FCStd','cad/v4-print/RibosomeV4Print.FCStd','cad/v5/RibosomeV5.FCStd'):
        try:
            with zipfile.ZipFile(ROOT / relative) as archive:
                if 'Document.xml' not in archive.namelist() or archive.testzip() is not None:
                    errors.append(f'Invalid CAD container: {relative}')
                if '/v2/' not in relative and 'GuiDocument.xml' not in archive.namelist():
                    errors.append(f'{relative} lacks desktop display data; present and save in FreeCAD before promotion.')
        except (OSError, zipfile.BadZipFile) as error:
            errors.append(f'{relative}: {error}')

    try:
        current = json.loads((ROOT / 'cad/v3/checks.json').read_text(encoding='utf-8-sig'))
        historical = json.loads((ROOT / 'cad/v2/checks.json').read_text(encoding='utf-8-sig'))
        v4=json.loads((ROOT/'cad/v4/checks.json').read_text(encoding='utf-8-sig'))
        v5=json.loads((ROOT/'cad/v5/checks.json').read_text(encoding='utf-8-sig'))
        if v5.get('version')!='5.0' or v5.get('status')!='FOCUSED_PASS':
            errors.append('V5 must have a fresh focused geometry result; unfinished checks cannot be promoted as a PASS.')
        design=v5.get('design',{})
        if not design.get('handheld') or not design.get('closed_RNA_loop') or design.get('RNA_bases_per_bead')!=3 or design.get('tensioned_rewind') is not False:
            errors.append('V5 no longer describes the accepted handheld / closed RNA / direct bead-drive contract.')
        if not v5.get('actual_bead_handoff_samples') or not v5.get('sampled_reverse_poses') or not v5.get('physical_tests_still_required'):
            errors.append('V5 must retain actual bead phase checks, reverse-motion evidence and physical-test limitations.')
        if v5.get('retained_at_full_travel',{}).get('hidden_beads')!=4:
            errors.append('V5 must retain four hidden protein beads at full travel.')
        for name,digest in v5.get('source_sha256',{}).items():
            source=ROOT/'cad/v5'/name
            if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=digest:
                errors.append('V5 source/report mismatch: '+name)
        if v4.get('version')!='4.0' or v4.get('status')!='FOCUSED_PASS':
            errors.append('V4 must retain its focused-check result and explicit baseline-validation boundary.')
        if v4.get('baseline_full_validation')!='INCOMPLETE_USER_STOPPED' or not v4.get('physical_tests_still_required'):
            errors.append('V4 must preserve unfinished baseline validation and physical-test limitations.')
        if v4.get('design',{}).get('RNA_bases_per_bead')!=3 or not v4.get('actual_bead_feeder_samples'):
            errors.append('V4 must retain three-base coupling and actual bead-to-feeder phase evidence.')
        if current.get('version') != '3.0' or current.get('status') not in ('PASS', 'INCOMPLETE_USER_STOPPED'):
            errors.append('Committed V3 report must record a PASS or the documented user-stopped state.')
        if current.get('status') == 'INCOMPLETE_USER_STOPPED' and not (current.get('reason') and current.get('unfinished_checks')):
            errors.append('An incomplete V3 report must explain the stop and identify unfinished checks.')
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
          'five CAD containers readable, report snapshots consistent.')
    print('This is repository integrity checking, not a fresh FreeCAD or physical-mechanism test.')
    if current.get('status') != 'PASS':
        print('V3 CAD validation is incomplete: '+current['status'])
    return 0


if __name__ == '__main__':
    raise SystemExit(run())
