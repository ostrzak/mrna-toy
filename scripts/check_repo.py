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


def source_matches(path: Path, expected: str) -> bool:
    """Git's Windows CRLF checkout must not invalidate Linux source evidence.

    Compare exact bytes first, then only normalize CRLF to LF. CAD container
    digests remain byte-exact; no source text or saved report is rewritten.
    """
    if not path.is_file():
        return False
    content=path.read_bytes()
    return expected in (hashlib.sha256(content).hexdigest(),
                        hashlib.sha256(content.replace(b'\r\n',b'\n')).hexdigest())


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
        'cad/v5/README.md','cad/v5/handheld.png','cad/v5/mechanism.png','cad/v5/drum.png','cad/v5/home.png','cad/v5/grip.png',
        'docs/v5-proportions.md',
        'cad/v6/bracelet_v6.py','cad/v6/rna_path.py','cad/v6/validation_v6.py','cad/v6/presentation_v6.py',
        'cad/v6/engineering_v6.py','cad/v6/engineering.md',
        'cad/v6/assembly_v6.py','docs/v6-assembly.md','cad/v6/fasteners.png','cad/v6/spindle.png',
        'cad/v6/gui-checks.json',
        'cad/v6/RibosomeV6.FCMacro','cad/v6/README.md',
        'cad/v6/handheld.png','cad/v6/open.png','cad/v6/underside.png',
        'cad/v6/mechanism.png','cad/v6/cap-input.png','cad/v6/home.png',
        'cad/v6/side.png',
        'print/v4-a1-mini/manifest.json','print/v4-a1-mini/handoff.json',
        'cad/v2/bracelet.py', 'cad/v2/Ribosome.FCMacro',
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            errors.append(f'Missing handoff file: {relative}')

    v7_files=('README.md','RibosomeV7.FCStd','RibosomeV7.FCMacro',
              'bracelet_v7.py','rna_path.py','coupling_v7.py','validation_v7.py',
              'assembly_v7.py','engineering_v7.py','presentation_v7.py',
              'mechanical_v7.py','travel_v7.py','engineering.md',
              'checks.json','gui-checks.json','handheld.png','side.png',
              'mechanism.png','pickup.png','return.png','open.png','underside.png')
    for name in v7_files:
        if not (ROOT/'cad/v7'/name).is_file():errors.append('Missing V7 checkpoint file: '+name)
    try:
        v7=json.loads((ROOT/'cad/v7/checks.json').read_text(encoding='utf-8'))
        gui7=json.loads((ROOT/'cad/v7/gui-checks.json').read_text(encoding='utf-8'))
        if v7.get('status') in ('INCOMPLETE_HANDOFF','INCOMPLETE_CONTINUATION'):
            if not v7.get('unfinished_checks') or v7.get('functional_mechanism_established') is not False:
                errors.append('V7 incomplete checkpoint must preserve its unfinished checks and functional boundary.')
        elif v7.get('status') not in ('REVIEW','FOCUSED_PASS','PASS'):
            errors.append('V7 has an unrecognized evidence status.')
        elif v7.get('status') in ('FOCUSED_PASS','PASS') and not (v7.get('logical_checks') and all(v7['logical_checks'].values())):
            errors.append('V7 PASS requires its own complete logical checks.')
        if v7.get('version')=='7.1' and v7.get('status')!='INCOMPLETE_CONTINUATION':
            mechanics=v7.get('mechanical_audit',{})
            if not mechanics.get('required_mechanical_checks') or not mechanics.get('evaluation_status'):
                errors.append('V7.1 requires an independent mechanical necessary-condition audit.')
            if v7.get('status')=='REVIEW' and (v7.get('functional_mechanism_established') is not False or not mechanics.get('blockers')):
                errors.append('V7.1 REVIEW must explicitly retain its mechanical blockers and nonfunctional boundary.')
            if v7.get('status') in ('FOCUSED_PASS','PASS') and not all(mechanics.get('required_mechanical_checks',{}).values()):
                errors.append('V7.1 cannot PASS failed or missing mechanical checks, regardless of animation or rigid clearance.')
            if not gui7.get('normal_GUI_close_reopen') or not gui7.get('native_update_without_source_directory'):
                errors.append('V7.1 requires its own saved-model GUI reopen and self-contained native update evidence.')
        if v7.get('status')=='INCOMPLETE_CONTINUATION':
            if not v7.get('saved_geometry_matches_generator_sources') or not v7.get('reason'):
                errors.append('V7 continuation must identify its matching geometry and interrupted validation boundary.')
            if not gui7.get('normal_GUI_close_reopen') or not gui7.get('native_update_without_source_directory'):
                errors.append('V7 continuation requires native reopen evidence for the current saved geometry.')
        for evidence in (v7,gui7):
            if hashlib.sha256((ROOT/'cad/v7/RibosomeV7.FCStd').read_bytes()).hexdigest()!=evidence.get('model_sha256'):
                errors.append('V7 checkpoint model/report hash mismatch.')
            for name,digest in evidence.get('source_sha256',{}).items():
                p=ROOT/'cad/v7'/name
                if not source_matches(p,digest):
                    errors.append('V7 checkpoint source/report mismatch: '+name)
        with zipfile.ZipFile(ROOT/'cad/v7/RibosomeV7.FCStd') as archive:
            if not {'Document.xml','GuiDocument.xml'}<=set(archive.namelist()) or archive.testzip() is not None:
                errors.append('V7 checkpoint lacks valid native CAD/display data.')
    except (OSError,ValueError,zipfile.BadZipFile) as error:
        errors.append('V7 checkpoint evidence could not be read: '+str(error))

    candidate=ROOT/'cad/v6-updated'
    if candidate.is_dir():
        try:
            required_candidate=('RibosomeV6Updated.FCStd','RibosomeV6Updated.FCMacro','README.md',
                'bracelet_v6_updated.py','rna_path.py','springs_v6_updated.py','validation_v6_updated.py',
                'assembly_v6_updated.py','engineering_v6_updated.py','presentation_v6_updated.py',
                'checks.json','gui-checks.json','engineering.md','handheld.png','side.png','open.png',
                'underside.png','mechanism.png','spring-installation.png','spring-loaded.png',
                'torsion-spring.png','serpentine-leaf.png')
            errors.extend('Missing V6 updated artifact: '+name for name in required_candidate if not (candidate/name).is_file())
            candidate_report=json.loads((candidate/'checks.json').read_text(encoding='utf-8'))
            candidate_gui=json.loads((candidate/'gui-checks.json').read_text(encoding='utf-8'))
            digest=hashlib.sha256((candidate/'RibosomeV6Updated.FCStd').read_bytes()).hexdigest()
            if candidate_report.get('version')!='6-updated' or candidate_report.get('status') not in ('REVIEW','FOCUSED_PASS'):
                errors.append('V6 updated requires its own completed CAD report and explicit evidence boundary.')
            for report in (candidate_report,candidate_gui):
                if report.get('model_sha256')!=digest:errors.append('V6 updated model/report hash mismatch.')
                for name,expected in report.get('source_sha256',{}).items():
                    if not source_matches(candidate/name,expected):errors.append('V6 updated source/report mismatch: '+name)
            if not candidate_gui.get('native_update_without_source_directory') or not candidate_gui.get('normal_GUI_close_reopen'):
                errors.append('V6 updated requires normal GUI reopen and source-independent native spring motion.')
            with zipfile.ZipFile(candidate/'RibosomeV6Updated.FCStd') as archive:
                if not {'Document.xml','GuiDocument.xml'}<=set(archive.namelist()) or archive.testzip() is not None:
                    errors.append('V6 updated lacks valid native CAD/display data.')
        except (OSError,ValueError,zipfile.BadZipFile) as error:
            errors.append('V6 updated evidence could not be read: '+str(error))

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

    for relative in ('cad/v2/Ribosome.FCStd', 'cad/v3/RibosomeV3.FCStd','cad/v4/RibosomeV4.FCStd','cad/v4-print/RibosomeV4Print.FCStd','cad/v5/RibosomeV5.FCStd','cad/v6/RibosomeV6.FCStd'):
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
        v6=json.loads((ROOT/'cad/v6/checks.json').read_text(encoding='utf-8-sig'))
        gui6=json.loads((ROOT/'cad/v6/gui-checks.json').read_text(encoding='utf-8-sig'))
        if not gui6.get('normal_GUI_close_reopen') or not gui6.get('native_update_without_source_directory'):
            errors.append('V6 requires a normal GUI reopen and native update without a source directory.')
        if not (gui6.get('housing_bolt_section_actual_solids') and gui6.get('spindle_section_actual_solids')):
            errors.append('V6 requires current actual-solid housing and spindle sections.')
        if not gui6.get('side_route_view'):
            errors.append('V6 requires its current side-route CAD view.')
        if hashlib.sha256((ROOT/'cad/v6/RibosomeV6.FCStd').read_bytes()).hexdigest()!=gui6.get('model_sha256'):
            errors.append('V6 GUI evidence no longer matches the saved CAD container.')
        for name,digest in gui6.get('source_sha256',{}).items():
            source=ROOT/'cad/v6'/name
            if not source_matches(source,digest):
                errors.append('V6 GUI source/evidence mismatch: '+name)
        if v6.get('version')!='6.0' or v6.get('status')!='FOCUSED_PASS' or not v6.get('logical_checks') or not all(v6.get('logical_checks',{}).values()):
            errors.append('V6 requires its own complete focused geometry result; no earlier PASS may substitute.')
        v6design=v6.get('design',{})
        assembly6=v6.get('assembly_audit',{})
        if not assembly6.get('passed') or not assembly6.get('checks') or not all(assembly6.get('checks',{}).values()):
            errors.append('V6 requires its actual fastener, bearing-seat, integral-root and assembly audit.')
        if len(assembly6.get('housing_screws',[]))!=3 or len(assembly6.get('sampled_assembly_insertions',[]))!=6:
            errors.append('V6 must check all three screw stacks and six insertion stages.')
        routing6=v6.get('housing_refinement',{})
        if routing6.get('outer_RNA_holders') is not False or not routing6.get('central_RNA_capture_only'):
            errors.append('V6 must retain the central RNA channel with both outer holders removed.')
        if not (v6design.get('open_or_closed_captive_RNA') and v6design.get('external_open_underside_return') and v6design.get('direct_RNA_reverse')):
            errors.append('V6 must preserve captive open/closed RNA, external underside return and direct reversal.')
        if any(v6design.get(k) is not False for k in ('parking_clip','external_reverse_release','tensioned_rewind')) or v6design.get('RNA_bases_per_bead')!=3:
            errors.append('V6 must retain three bases per bead, with no parking clip, external release or tensioned rewind.')
        if v6.get('retained_at_full_travel',{}).get('hidden_beads')!=4 or not v6.get('actual_bead_handoff_samples') or v6.get('actual_RNA_gear_phase_samples')!=18:
            errors.append('V6 must retain its four-bead tail and actual bead/drum and RNA/gear phase evidence.')
        if not v6.get('sampled_direct_reverse_poses_per_mode') or not v6.get('sampled_cap_cycle_poses') or not v6.get('physical_tests_still_required'):
            errors.append('V6 must retain direct reverse, upper-input motion and physical-test boundaries.')
        for name,digest in v6.get('source_sha256',{}).items():
            source=ROOT/'cad/v6'/name
            if not source_matches(source,digest):
                errors.append('V6 source/report mismatch: '+name)
        if v5.get('version')!='5.0' or v5.get('status')!='FOCUSED_PASS':
            errors.append('V5 must have a fresh focused geometry result; unfinished checks cannot be promoted as a PASS.')
        design=v5.get('design',{})
        if not design.get('handheld') or not design.get('closed_RNA_loop') or design.get('RNA_bases_per_bead')!=3 or design.get('tensioned_rewind') is not False:
            errors.append('V5 no longer describes the accepted handheld / closed RNA / direct bead-drive contract.')
        if not v5.get('actual_bead_handoff_samples') or not v5.get('sampled_reverse_poses') or not v5.get('physical_tests_still_required'):
            errors.append('V5 must retain actual bead phase checks, reverse-motion evidence and physical-test limitations.')
        if v5.get('sampled_rocker_clearance_poses')!=9 or v5.get('sampled_release_heights_mm')!=[0,1.5,3.0]:
            errors.append('V5 proportion pass requires its expanded rocker/release clearance evidence.')
        if v5.get('retained_at_full_travel',{}).get('hidden_beads')!=4:
            errors.append('V5 must retain four hidden protein beads at full travel.')
        for name,digest in v5.get('source_sha256',{}).items():
            source=ROOT/'cad/v5'/name
            if not source_matches(source,digest):
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
          'saved CAD containers readable, report snapshots consistent.')
    print('This is repository integrity checking, not a fresh FreeCAD or physical-mechanism test.')
    if current.get('status') != 'PASS':
        print('V3 CAD validation is incomplete: '+current['status'])
    if v7.get('status') in ('INCOMPLETE_HANDOFF','INCOMPLETE_CONTINUATION'):
        print('V7 remains '+v7['status']+': integrated mechanism and physical operation unqualified.')
    elif v7.get('status')=='REVIEW':
        print('V7 remains REVIEW: see its actual CAD failures and independent mechanical audit; no functional or physical PASS.')
    return 0


if __name__ == '__main__':
    raise SystemExit(run())
