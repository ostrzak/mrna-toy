"""Prepare an offline PETG fit-test plate; optionally slice with local Bambu Studio.

Uses the exact installed Bambu PETG Translucent / A1 mini 0.4 profiles.
Never connects to a printer or sends a print.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from print_package import stl

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/v6-updated-print/fit-plate'
EXPORTS=ROOT/'build/v6-updated-print/exports'
NAMES=('Fit-CasePost','Fit-CaseStack','PrintedCaseScrew','PrintedKeyedNut',
       'Fit-SpindleTip','Fit-CapBearingGauge','PrintedSpindleCap','Fit-ReturnSpringCup','Fit-PawlSpringPin')


def prepare(resources):
    OUT.mkdir(parents=True,exist_ok=True)
    export_report=json.loads((EXPORTS/'export-report.json').read_text(encoding='utf-8'))
    assert export_report.get('status')=='EXPORT_REVIEW' and not export_report['errors']
    index={}
    for p in resources.rglob('*.json'):
        v=json.loads(p.read_text(encoding='utf-8-sig'))
        index[p.stem]=v
        if v.get('name'):index[v['name']]=v
    def flatten(name,stack=()):
        if name in stack:raise ValueError('Profile cycle: '+name)
        v=index[name]
        result=flatten(v['inherits'],stack+(name,)) if v.get('inherits') else {}
        for item in v.get('include',[]):result.update(flatten(item,stack+(name,)))
        result.update({k:x for k,x in v.items() if k not in ('inherits','include')})
        return result
    machine=flatten('Bambu Lab A1 mini 0.4 nozzle')
    filament=flatten('Bambu PETG Translucent @BBL A1M')
    process=flatten('0.12mm Fine @BBL A1M')
    assert 'Bambu Lab A1 mini 0.4 nozzle' in filament['compatible_printers']
    # Bambu serializes its Rectilinear choice as "zig-zag". The unrelated
    # "rectilinear" key silently falls back to Cubic, invalid at 100% infill.
    process.update(wall_loops='4',sparse_infill_density='100%',sparse_infill_pattern='zig-zag',wall_generator='arachne',
        top_shell_layers='5',bottom_shell_layers='5',enable_support='0',
        curr_bed_type='Textured PEI Plate',brim_type='outer_only',brim_width='3',
        brim_object_gap='0.15',outer_wall_speed='35',inner_wall_speed='50')
    for name,value in [('machine',machine),('filament',filament),('process',process)]:
        (OUT/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
    ET.register_namespace('',ns)
    model=ET.Element('{'+ns+'}model',unit='millimeter')
    ET.SubElement(model,'metadata',name='Title').text='V6 updated — PETG fastening and spring-fit trials'
    resources_xml=ET.SubElement(model,'resources');build=ET.SubElement(model,'build')
    x=y=8.;row_height=0.;parts=[]
    for i,name in enumerate(NAMES,1):
        points,faces=stl(EXPORTS/(name+'.stl'))
        lo=[min(p[j] for p in points) for j in range(3)]
        hi=[max(p[j] for p in points) for j in range(3)]
        width,depth=hi[0]-lo[0],hi[1]-lo[1]
        if x+width>172:x=8.;y+=row_height+8.;row_height=0.
        if y+depth>172:raise ValueError('Fit plate exceeds bed')
        obj=ET.SubElement(resources_xml,'object',id=str(i),type='model',name=name)
        mesh=ET.SubElement(obj,'mesh');vertices=ET.SubElement(mesh,'vertices');triangles=ET.SubElement(mesh,'triangles')
        for p in points:ET.SubElement(vertices,'vertex',x=str(p[0]),y=str(p[1]),z=str(p[2]))
        for a,b,c in faces:ET.SubElement(triangles,'triangle',v1=str(a),v2=str(b),v3=str(c))
        ET.SubElement(build,'item',objectid=str(i),transform=f'1 0 0 0 1 0 0 0 1 {x-lo[0]} {y-lo[1]} {-lo[2]}')
        parts.append(dict(name=name,position_xy_mm=[x,y],bounds_mm=[hi[j]-lo[j] for j in range(3)],
            source_STL_sha256=hashlib.sha256((EXPORTS/(name+'.stl')).read_bytes()).hexdigest()))
        x+=width+8.;row_height=max(row_height,depth)
    source=OUT/'V6-updated-fit-trials-source.3mf'
    with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
    report=dict(status='PREPARED_UNSLICED',source_3mf=str(source),parts=parts,
        model_sha256=export_report['model_sha256'],
        printer=machine['name'],filament=filament['name'],layer_height_mm=.12,
        physically_tested=False,print_dispatched=False)
    return source,report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--resources',type=Path,default=Path('C:/Program Files/Bambu Studio/resources/profiles/BBL'))
    p.add_argument('--bambu',type=Path,default=Path('C:/Program Files/Bambu Studio/bambu-studio.exe'))
    p.add_argument('--slice',action='store_true');args=p.parse_args()
    source,report=prepare(args.resources)
    if args.slice:
        output=OUT/'V6-updated-PETG-fit-trials.3mf'
        command=[str(args.bambu),'--debug','2','--outputdir',str(OUT),'--load-settings',
            str(OUT/'machine.json')+';'+str(OUT/'process.json'),
            '--load-filaments',str(OUT/'filament.json'),'--slice','0','--export-3mf',output.name,str(source)]
        startup=None
        if hasattr(subprocess,'STARTUPINFO'):
            startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        report['command']=command
        run=subprocess.run(command,capture_output=True,text=True,errors='replace',timeout=300,startupinfo=startup)
        (OUT/'bambu-stdout.log').write_text(run.stdout,encoding='utf-8')
        (OUT/'bambu-stderr.log').write_text(run.stderr,encoding='utf-8')
        report.update(cli_return_code=run.returncode,output_3mf=str(output),output_exists=output.is_file())
        result_path=OUT/'result.json'
        if result_path.is_file():
            report['bambu_result']=json.loads(result_path.read_text(encoding='utf-8'))
        if output.is_file():
            with zipfile.ZipFile(output) as z:
                report['gcode_entries']=[n for n in z.namelist() if n.endswith('.gcode')]
                report['archive_valid']=z.testzip() is None
                config=json.loads(z.read('Metadata/project_settings.config'))
                info=ET.fromstring(z.read('Metadata/slice_info.config'))
                objects=info.findall('.//object')
                report['project_checks']=dict(
                    all_nine_objects_present={o.get('name') for o in objects}==set(NAMES) and len(objects)==len(NAMES),
                    no_objects_skipped=all(o.get('skipped')=='false' for o in objects),
                    A1_mini_04=config.get('printer_model')=='Bambu Lab A1 mini' and config.get('nozzle_diameter')==['0.4'],
                    exact_PETG_preset=config.get('filament_settings_id')==['Bambu PETG Translucent @BBL A1M'],
                    fine_layer_height=float(config['layer_height'])==.12)
                meta={o.get('key'):o.get('value') for o in info.findall('.//plate/metadata')}
                report['estimated_time_seconds']=int(meta['prediction'])
                report['estimated_filament_g']=float(meta['weight'])
        report['status']='SLICED_REVIEW' if (run.returncode==0 and report.get('gcode_entries') and
            report.get('archive_valid') and all(report.get('project_checks',{'missing':False}).values())) else 'SLICER_REVIEW_REQUIRED'
    (OUT/'fit-plate-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
