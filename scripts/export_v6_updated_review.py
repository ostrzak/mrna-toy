"""FreeCAD worker: grouped V6 updated STEP/STL feasibility exports, not print release.

Run from the repository root with FreeCADCmd's Python command:
FreeCADCmd -c "import runpy; runpy.run_path('scripts/export_v6_updated_review.py',run_name='__main__')"
The saved CAD is opened read-only in memory; no document is saved or rebuilt.
Outputs and the report belong under ignored build/v6-updated-print-review/.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import traceback

import FreeCAD as App
import Part
import Mesh
import MeshPart

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'cad/v6-updated'
OUT=ROOT/'build/v6-updated-print-review'
sys.path.insert(0,str(SOURCE))
import bracelet_v6_updated as b


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source=SOURCE/b.MODEL_FILE
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    doc=App.openDocument(str(source))
    doc.Motion.BeadSteps=0;doc.Motion.CapStroke=0
    doc.Motion.CapReturning=False;doc.Motion.StrandClosed=True
    doc.recompute()
    report=dict(status='EXPORT_REVIEW_IN_PROGRESS',runtime='.'.join(App.Version()[:3]),
        source_model_sha256=digest,printer='Bambu Lab A1 mini',nozzle_mm=.4,
        material_direction='PETG rigid/leaf candidates; user-owned Bambu TPU 90A RNA/bead trials; PLA fit studies',
        sliced=False,physically_tested=False,manufacturing_release=False,parts=[],errors=[])
    def checkpoint():
        (OUT/'export-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def export(name,shape,members,notes,material='PETG',rotation=None,reference=False):
        print('EXPORT '+name,flush=True)
        record=dict(name=name,members=members,material_candidate=material,notes=notes,
                    reference_only=reference,print_orientation_validated=False)
        report['parts'].append(record);checkpoint()
        try:
            shape=shape.copy()
            if rotation:shape.rotate(App.Vector(),App.Vector(*rotation[0]),rotation[1])
            box=shape.optimalBoundingBox(False)
            shape.translate(App.Vector(-box.XMin,-box.YMin,-box.ZMin))
            record.update(valid=shape.isValid(),solids=len(shape.Solids),volume_mm3=shape.Volume,
                bounds_mm=[box.XLength,box.YLength,box.ZLength],
                fits_180mm_axis_aligned=all(v<=180 for v in (box.XLength,box.YLength,box.ZLength)))
            if not shape.isValid() or len(shape.Solids)!=1:
                raise ValueError('Export requires one valid fused physical solid')
            folder=OUT/('reference-only' if reference else 'review-parts')
            folder.mkdir(exist_ok=True)
            step=folder/(name+'.step');shape.exportStep(str(step))
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.025,AngularDeflection=.15,Relative=False)
            stl=folder/(name+'.stl');mesh.write(str(stl))
            reread=Mesh.Mesh(str(stl))
            record.update(step=step.relative_to(OUT).as_posix(),stl=stl.relative_to(OUT).as_posix(),
                mesh_facets=reread.CountFacets,mesh_points=reread.CountPoints,
                mesh_closed=reread.isSolid(),mesh_volume_mm3=reread.Volume)
            if hasattr(reread,'isManifold'):record['mesh_manifold']=reread.isManifold()
            if hasattr(reread,'countComponents'):record['mesh_components']=reread.countComponents()
            record['relative_mesh_volume_error']=abs(reread.Volume-shape.Volume)/shape.Volume
            # Read STEP back with the same kernel, checking actual export units/shape.
            readback=Part.Shape();readback.read(str(step))
            rb=readback.optimalBoundingBox(False)
            record['step_readback_valid']=readback.isValid()
            record['step_readback_solids']=len(readback.Solids)
            record['step_readback_dimension_error_mm']=max(abs(a-c) for a,c in zip(
                (box.XLength,box.YLength,box.ZLength),(rb.XLength,rb.YLength,rb.ZLength)))
            if not record['mesh_closed'] or record.get('mesh_components',1)!=1:
                record['initial_mesh_issue']=dict(closed=record['mesh_closed'],components=record.get('mesh_components'))
                # A fresh STEP reconstruction clears cached trim/mesh state.
                # This changes tessellation, never the saved CAD geometry.
                clean=readback.cleaned()
                mesh=MeshPart.meshFromShape(Shape=clean,LinearDeflection=.005,AngularDeflection=.07,Relative=False)
                mesh.write(str(stl));reread=Mesh.Mesh(str(stl))
                record.update(mesh_facets=reread.CountFacets,mesh_points=reread.CountPoints,
                    mesh_closed=reread.isSolid(),mesh_volume_mm3=reread.Volume,
                    mesh_components=reread.countComponents(),
                    relative_mesh_volume_error=abs(reread.Volume-shape.Volume)/shape.Volume,
                    mesh_export_route='STEP read-back, cleaned shape, 0.005 mm / 0.07 rad tessellation')
            record['export_passed']=bool(record['mesh_closed'] and record.get('mesh_manifold',True)
                and record['step_readback_valid'] and record['step_readback_solids']==1
                and record['step_readback_dimension_error_mm']<1e-5
                and record['relative_mesh_volume_error']<.02)
            if not record['export_passed']:report['errors'].append(name+': export/mesh check failed')
        except Exception as exc:
            record['error']=str(exc);report['errors'].append(name+': '+str(exc))
            traceback.print_exc()
        checkpoint()
    def fused(names):return b.union([b.world(doc.getObject(n)) for n in names])
    specs=[
        ('LowerHousing',['LowerBody','CentreAxle'],'Integral 6 mm spindle retained; screw pilots are not insert pockets.'),
        ('BeadKeeper',['BeadKeeper'],'Pocket/guide finish and fit remain unqualified.'),
        ('InternalLid',['LowerLid'],'Review support access and bearing/screw seats.'),
        ('LowerRotor',['BeadDrum','DriveHub','TravelPin'],'Two thin fork levels and stop pin need support/orientation study.'),
        ('UpperRotor',['RnaDriveGear','IndexSleeve','IndexWheel','FeedRatchet'],'One fused keyed rotor; verify small teeth/ramp slicing.'),
        ('RockingUpper',['UpperLobe'],'Integral 1.5 mm guide pin; organic shell and internal supports need print access review.'),
        ('InputPawl',['DriveCarrier'],'1 mm follower ball on a 0.5 mm neck is a manufacturing concern.'),
    ]
    for name,names,notes in specs:
        try:export(name,fused(names),names,notes)
        except Exception as exc:
            report['errors'].append(name+': grouping failed: '+str(exc));checkpoint()
    # Export the cover in the proposed FREE state. Printing the installed
    # pre-deflected leaf would remove the intended assembly preload.
    doc.Motion.setExpression('DetentFlex',None);doc.Motion.DetentFlex=0;doc.recompute()
    names=['GearGuard','ReturnSpringHousing','DetentAnchor','DetentFlexure','DetentTip']
    try:export('FixedCover-UnloadedLeaf',fused(names),names,
        'Leaf displacement set to zero on this in-memory copy; preload/installation/force remain unqualified.')
    except Exception as exc:report['errors'].append('FixedCover: '+str(exc));checkpoint()
    for kind in range(3):
        obj=next(o for o in doc.Protein.Group if hasattr(o,'BeadVariant') and o.BeadVariant==kind)
        bead=obj.Shape.copy();bead.Placement=App.Placement()
        export('Bead-'+b.BEAD_FAMILY[kind],bead,[obj.Name],
            'Original 1 mm bore; no flat sole or wire retention. Review geometry, not calibrated production bead.',
            material='TPU 90A candidate',rotation=((0,1,0),-90))
    # The RNA is nominal prescribed deformation, not a manufacturing flat
    # pattern. Fuse it for a SINGLE reference object; never print 216 cells.
    doc.Motion.StrandClosed=False;doc.Motion.BeadSteps=11;doc.recompute()
    names=[o.Name for o in doc.RnaStrand.Group if hasattr(o,'DisplayColour')]
    try:export('RNA-Open-NominalPose-REFERENCE',fused(names),names,
        'Single fused nominal U-shaped layout. Needs an unloaded flat print pattern and clasp/TPU qualification.',
        material='TPU 90A candidate',rotation=((1,0,0),b.RNA_ROUTE_ANGLE),reference=True)
    except Exception as exc:report['errors'].append('RNA grouping: '+str(exc));checkpoint()
    report['source_model_unchanged']=hashlib.sha256(source.read_bytes()).hexdigest()==digest
    report['status']='EXPORT_REVIEW' if not report['errors'] else 'EXPORT_REVIEW_WITH_ISSUES'
    report['boundary']='Grouped geometry export and closed/manifold mesh/STEP round-trip checks only. No orientations, supports, slicing, fits, strength, spring selection or physical operation qualified.'
    checkpoint();App.closeDocument(doc.Name)
    print('EXPORT_REVIEW_COMPLETE '+report['status'],flush=True)


if __name__=='__main__':main()
