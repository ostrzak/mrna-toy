"""Offline A1 mini plate authoring and slicing. Never connects to a printer."""
from pathlib import Path
import argparse
import json
import math
import struct
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'print/v4-a1-mini'


def profiles(resource):
    index={}
    for path in resource.rglob('*.json'):
        value=json.loads(path.read_text(encoding='utf-8-sig'))
        index[path.stem]=value
        if value.get('name'): index[value['name']]=value
    def flatten(name,stack=()):
        if name in stack: raise ValueError('Profile inheritance cycle: '+name)
        value=index[name]
        result=flatten(value['inherits'],stack+(name,)) if value.get('inherits') else {}
        for include in value.get('include',[]): result.update(flatten(include,stack+(name,)))
        result.update({k:v for k,v in value.items() if k not in ('inherits','include')})
        return result
    target=PACKAGE/'profiles'
    target.mkdir(parents=True,exist_ok=True)
    machine=flatten('Bambu Lab A1 mini 0.4 nozzle')
    assert machine['printable_height']=='180' and 'A1' in machine['machine_start_gcode']
    (target/'A1-mini-0.4.json').write_text(json.dumps(machine,indent=2)+'\n',encoding='utf-8')
    for material in ('PLA','PETG','TPU'):
        filament=flatten('Generic '+material+' @BBL A1M')
        process=flatten('0.12mm Fine @BBL A1M')
        process.update(wall_loops='4',sparse_infill_density='30%',
                       curr_bed_type='Textured PEI Plate',elefant_foot_compensation='0.1',
                       enable_support='0',brim_type='outer_only',brim_width='3',
                       brim_object_gap='0.15',outer_wall_speed='35',inner_wall_speed='50',
                       initial_layer_speed='20',initial_layer_infill_speed='25')
        if material=='TPU':
            filament.update(nozzle_temperature=['230'],nozzle_temperature_initial_layer=['230'],
                            filament_max_volumetric_speed=['1.2'])
            process.update(wall_loops='3',sparse_infill_density='95%',sparse_infill_pattern='rectilinear',
                           outer_wall_speed='20',inner_wall_speed='20',sparse_infill_speed='20',
                           internal_solid_infill_speed='20',top_surface_speed='20',
                           initial_layer_speed='15',initial_layer_infill_speed='15')
        elif material=='PLA':
            process.update(sparse_infill_density='95%',sparse_infill_pattern='rectilinear',enable_support='1',
                           support_type='tree(auto)',support_on_build_plate_only='1')
        else:
            process.update(enable_support='1',support_type='tree(auto)',
                           support_on_build_plate_only='1',outer_wall_speed='30',inner_wall_speed='45')
        for kind,value in [('filament',filament),('process',process)]:
            (target/(material+'-'+kind+'.json')).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    print('Flattened official installed profiles, including A1 mini start/end gcode.')


def stl(path):
    data=path.read_bytes()
    if len(data)>=84 and len(data)==84+50*struct.unpack_from('<I',data,80)[0]:
        triangles=[struct.unpack_from('<9f',data,84+50*i+12) for i in range((len(data)-84)//50)]
        triangles=[[tuple(t[j:j+3]) for j in (0,3,6)] for t in triangles]
    else:
        vertices=[tuple(map(float,line.split()[1:])) for line in data.decode('ascii').splitlines() if line.strip().startswith('vertex ')]
        triangles=[vertices[i:i+3] for i in range(0,len(vertices),3)]
    points=[]; indices={}; faces=[]; edges={}
    for triangle in triangles:
        face=[]
        for point in triangle:
            key=tuple(round(v,5) for v in point)
            if key not in indices: indices[key]=len(points); points.append(point)
            face.append(indices[key])
        faces.append(face)
        for a,b in zip(face,face[1:]+face[:1]):
            key=tuple(sorted((a,b))); edges[key]=edges.get(key,0)+1
    bad=sum(count!=2 for count in edges.values())
    if bad: print('MESH_REVIEW:',path.name,bad,'non-manifold mesh edges; inspect/repair before printing.',flush=True)
    if not edges: raise ValueError('Empty STL: '+str(path))
    return points,faces


def author():
    manifest=json.loads((PACKAGE/'manifest.json').read_text(encoding='utf-8'))
    ns='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
    ET.register_namespace('',ns)
    for plate in manifest['plates']:
        model=ET.Element('{'+ns+'}model',unit='millimeter')
        ET.SubElement(model,'metadata',name='Title').text=plate['name']
        resources=ET.SubElement(model,'resources'); build=ET.SubElement(model,'build')
        x=y=8.; row=0.
        for i,part in enumerate(plate['parts'],1):
            points,faces=stl(PACKAGE/part['file'])
            lo=[min(p[a] for p in points) for a in range(3)]
            hi=[max(p[a] for p in points) for a in range(3)]
            width,height=hi[0]-lo[0],hi[1]-lo[1]
            if x+width>172: x=8.; y+=row+8.; row=0.
            if y+height>172 or hi[2]>180.001: raise ValueError('Plate exceeds A1 mini: '+plate['name'])
            obj=ET.SubElement(resources,'object',id=str(i),type='model',name=part['name'])
            mesh=ET.SubElement(obj,'mesh'); vertices=ET.SubElement(mesh,'vertices'); triangles=ET.SubElement(mesh,'triangles')
            for p in points: ET.SubElement(vertices,'vertex',**{a:f'{v:.6f}' for a,v in zip('xyz',p)})
            for face in faces: ET.SubElement(triangles,'triangle',**{f'v{j+1}':str(v) for j,v in enumerate(face)})
            ET.SubElement(build,'item',objectid=str(i),transform=f'1 0 0 0 1 0 0 0 1 {x-lo[0]:.5f} {y-lo[1]:.5f} {-lo[2]:.5f}')
            x+=width+8.; row=max(row,height)
        output=PACKAGE/'plates'/(plate['name']+'.3mf'); output.parent.mkdir(exist_ok=True)
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
            z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
            z.writestr('3D/3dmodel.model',ET.tostring(model,encoding='utf-8',xml_declaration=True))
        print('Authored',output.name,flush=True)


def slice_plates(executable,only=None):
    manifest=json.loads((PACKAGE/'manifest.json').read_text(encoding='utf-8'))
    results=[]
    for plate in manifest['plates']:
        if only and plate['name']!=only: continue
        material=plate['material']; name=plate['name']
        output=PACKAGE/'sliced'/(name+'.gcode.3mf'); output.parent.mkdir(exist_ok=True)
        p=PACKAGE/'profiles'
        command=[str(executable),'--debug','2','--load-settings',str(p/'A1-mini-0.4.json')+';'+str(p/(material+'-process.json')),
                 '--load-filaments',str(p/(material+'-filament.json')),'--slice','0','--export-3mf',str(output),str(PACKAGE/'plates'/(name+'.3mf'))]
        print('Slicing',name,flush=True)
        result=subprocess.run(command,capture_output=True)
        (ROOT/'build/v4-print'/(name+'-slice.log')).write_bytes(result.stdout+result.stderr)
        if result.returncode or not output.is_file(): raise RuntimeError('Slicing failed: '+name+' exit '+str(result.returncode))
        with zipfile.ZipFile(output) as z:
            settings=json.loads(z.read('Metadata/project_settings.config'))
            gcode=z.read('Metadata/plate_1.gcode').decode('utf-8')
            assert settings['printer_model']=='Bambu Lab A1 mini',settings['printer_model']
            assert settings['nozzle_diameter']==['0.4']
            assert settings['filament_type']==[material],settings['filament_type']
            assert 'A1' in settings['machine_start_gcode'] and len(settings['machine_start_gcode'])>5000
            assert 'M109 S230' in gcode or material!='TPU'
            summary=json.loads(z.read('Metadata/plate_1.json'))
            results.append(dict(plate=name,material=material,bytes=output.stat().st_size,
                                nozzle=settings['nozzle_diameter'],temperature=settings['nozzle_temperature'],
                                bed=settings.get('textured_plate_temp'),summary=summary))
        print('Verified machine, material and embedded toolpaths:',name,flush=True)
    destination=PACKAGE/'slicer-checks.json'
    if only and destination.exists():
        old=json.loads(destination.read_text(encoding='utf-8'))['plates']
        results=[r for r in old if r['plate']!=only]+results
    destination.write_text(json.dumps(dict(status='OFFLINE_SLICED',physical_print_tested=False,plates=results),indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['profiles','author','slice'])
    parser.add_argument('--resources',type=Path,default=Path(r'C:\Program Files\Bambu Studio\resources\profiles\BBL'))
    parser.add_argument('--bambu',type=Path,default=Path(r'C:\Program Files\Bambu Studio\bambu-studio.exe'))
    parser.add_argument('--only')
    args=parser.parse_args()
    if args.command=='profiles': profiles(args.resources)
    elif args.command=='author': author()
    else: slice_plates(args.bambu,args.only)
