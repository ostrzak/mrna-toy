"""Export physical printed parts of the V6 updated print candidate.

Run through FreeCADCmd's Python; never saves or mutates the source document.
Outputs are a review set, not proof of printing or assembly.
"""
from pathlib import Path
import hashlib
import json
import sys
import FreeCAD as App
import Part
import Mesh
import MeshPart

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'cad/v6-updated-print'
OUT=ROOT/'build/v6-updated-print/exports'
sys.path.insert(0,str(SOURCE))
import bracelet_v6_updated_print as b


def export(model_path=None):
    model=Path(model_path or SOURCE/b.MODEL_FILE).resolve()
    digest=hashlib.sha256(model.read_bytes()).hexdigest()
    OUT.mkdir(parents=True,exist_ok=True)
    d=App.openDocument(str(model))
    d.Motion.BeadSteps=0;d.Motion.CapStroke=0;d.Motion.CapReturning=False;d.recompute()
    report=dict(model_sha256=digest,parts=[],errors=[],sliced=False,physically_tested=False)
    def save_report():
        (OUT/'export-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def part(name,names,quantity=1,rotation=None,material='Bambu PETG Translucent',shape_override=None,coupon=False):
        shape=shape_override.copy() if shape_override is not None else b.union([b.world(d.getObject(n)) for n in names])
        if rotation:shape.rotate(App.Vector(),App.Vector(*rotation[0]),rotation[1])
        box=shape.optimalBoundingBox(False)
        shape.translate(App.Vector(-box.XMin,-box.YMin,-box.ZMin))
        row=dict(name=name,members=names,quantity=quantity,material=material,fit_coupon=coupon,
                 valid=shape.isValid(),solids=len(shape.Solids),bounds_mm=[box.XLength,box.YLength,box.ZLength])
        report['parts'].append(row);save_report();print('EXPORT '+name,flush=True)
        if not row['valid'] or row['solids']!=1:
            report['errors'].append(name+': disconnected or invalid physical component');return
        step=OUT/(name+'.step');shape.exportStep(str(step))
        check=Part.Shape();check.read(str(step));check=check.cleaned()
        row['step_valid']=check.isValid() and len(check.Solids)==1
        for linear,angular in ((.02,.12),(.005,.07)):
            mesh=MeshPart.meshFromShape(Shape=check,LinearDeflection=linear,AngularDeflection=angular,Relative=False)
            mesh.write(str(OUT/(name+'.stl')))
            read=Mesh.Mesh(str(OUT/(name+'.stl')))
            if read.isSolid() and read.countComponents()==1:break
        row.update(mesh_closed=read.isSolid(),mesh_components=read.countComponents(),mesh_facets=read.CountFacets,
            relative_mesh_volume_error=abs(read.Volume-shape.Volume)/shape.Volume,
            fits_A1_mini=all(v<=180 for v in row['bounds_mm']))
        row['passed']=bool(row['step_valid'] and row['mesh_closed'] and row['mesh_components']==1
            and row['relative_mesh_volume_error']<.02 and row['fits_A1_mini'])
        if not row['passed']:report['errors'].append(name+': export check failed')
        save_report()
    specs=[('LowerHousing',['LowerBody','CentreAxle'],1),('BeadKeeper',['BeadKeeper'],1),
        ('LowerLid',['LowerLid'],1),('LowerRotor',['BeadDrum','DriveHub','TravelPin'],1),
        ('UpperRotor',['RnaDriveGear','IndexSleeve','IndexWheel','FeedRatchet'],1),
        ('RockingUpper',['UpperLobe','PawlSpringUpperSeat','PawlFixedSpringSeat'],1),
        ('InputPawl',['DriveCarrier','PawlSpringLowerSeat'],1),
        ('PrintedCaseScrew',['HousingScrew00'],3),('PrintedKeyedNut',['HousingNut00'],3),
        ('PrintedSpindleCap',['CapRetainer','CapWasher'],1)]
    for name,names,qty in specs:part(name,names,qty)
    # Fit pieces retain actual mating geometry. The stack proxy reproduces
    # the clamped height, passage and conical seat without the full shells.
    x,y=b.CASE_MOUNTS[0]
    column=Part.makeCylinder(4.3,15.7,App.Vector(x,y,6))
    part('Fit-CasePost',['LowerBody'],shape_override=b.world(d.LowerBody).common(column),coupon=True)
    stack=Part.makeCylinder(4.3,8.2,App.Vector(x,y,13.5))
    stack=stack.cut(Part.makeCylinder(2.3,9,App.Vector(x,y,13.4)))
    stack=stack.cut(Part.makeCone(1.8,3.0,1.5,App.Vector(x,y,20)))
    stack=stack.cut(Part.makeCylinder(3.05,.3,App.Vector(x,y,21.5))).removeSplitter()
    part('Fit-CaseStack',['BeadKeeper','LowerLid','GearGuard'],shape_override=stack,coupon=True)
    tip=b.world(d.CentreAxle).common(Part.makeCylinder(3.01,7.3,App.Vector(0,0,31.5)))
    tip=tip.fuse(Part.makeCylinder(5,.6,App.Vector(0,0,31))).removeSplitter()
    part('Fit-SpindleTip',['CentreAxle'],shape_override=tip,coupon=True)
    bearing=b.world(d.UpperLobe).common(b.annulus(3.5,5.1,31.6,1.8))
    part('Fit-CapBearingGauge',['UpperLobe'],shape_override=bearing,coupon=True)
    part('Fit-ReturnSpringCup',['ReturnSpringHousing'],coupon=True)
    import stock_springs as stock
    pin=b.world(d.PawlSpringUpperSeat).common(b.cylinder(2.8,7.4,
        stock.PAWL_C-stock.PAWL_AXIS*3.5,stock.PAWL_AXIS))
    pin.Placement=App.Placement(App.Vector(),App.Rotation(stock.PAWL_AXIS,App.Vector(0,0,1))).multiply(pin.Placement)
    part('Fit-PawlSpringPin',['PawlSpringUpperSeat'],shape_override=pin,coupon=True)
    d.Motion.setExpression('DetentFlex',None);d.Motion.DetentFlex=0;d.recompute()
    part('FixedCover-UnloadedLeaf',['GearGuard','ReturnSpringHousing','DetentAnchor','DetentFlexure','DetentTip'])
    for kind in range(3):
        obj=next(o for o in d.Protein.Group if hasattr(o,'BeadVariant') and o.BeadVariant==kind)
        # Reset the selected bead's assembly pose only on this unsaved copy.
        obj.setExpression('Placement.Base.x',None);obj.setExpression('Placement.Base.y',None)
        obj.setExpression('Placement.Base.z',None)
        for prop in ('Placement.Rotation.Angle','Placement.Rotation.Axis.x','Placement.Rotation.Axis.y','Placement.Rotation.Axis.z'):
            try:obj.setExpression(prop,None)
            except Exception:pass
        obj.Placement=App.Placement();d.recompute()
        qty=sum(1 for o in d.Protein.Group if hasattr(o,'BeadVariant') and o.BeadVariant==kind)
        part('Bead-'+b.BEAD_FAMILY[kind],[obj.Name],qty,((0,1,0),-90),'Bambu TPU 90A')
    report['source_model_unchanged']=hashlib.sha256(model.read_bytes()).hexdigest()==digest
    report['status']='EXPORT_REVIEW' if not report['errors'] else 'EXPORT_REVIEW_WITH_ISSUES'
    report['boundary']='Physical grouping, STEP read-back and mesh checks. RNA remains the preserved nominal-layout reference; no new flat RNA pattern is claimed. Spring force, fits, support choices and physical function remain unqualified.'
    save_report();App.closeDocument(d.Name)
    print('EXPORT_COMPLETE '+report['status'],flush=True)
    return report


if __name__=='__main__':export()
