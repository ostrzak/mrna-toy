"""Native GUI reopen, motion and actual-geometry inspection images."""
from pathlib import Path
import hashlib
import json
import sys
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtWidgets
from pivy import coin
import bracelet_v6_updated as b

HERE=Path(__file__).resolve().parent


def frame(d,view,orientation='iso'):
    rotations={'iso':App.Rotation(App.Vector(1,1,0),App.Vector(-1,1,2),App.Vector(1,-1,1),'ZXY'),
        'front':App.Rotation(App.Vector(1,0,0),90),'top':App.Rotation(),
        'left':App.Rotation(App.Vector(0,-1,0),App.Vector(0,0,1),App.Vector(-1,0,0),'ZXY'),
        'bottom':App.Rotation(App.Vector(1,0,0),180)}
    rotation=rotations[orientation];view.getCameraNode().orientation.setValue(coin.SbRotation(*rotation.Q))
    inverse=rotation.inverted();camera_space=App.Placement(App.Vector(),inverse);box=App.BoundBox()
    def visible(o):
        return o.ViewObject.Visibility and all(visible(p) for p in o.InList if p.TypeId=='App::Part')
    for o in d.Objects:
        if not hasattr(o,'DisplayColour') or not visible(o):continue
        s=o.Shape.copy();s.Placement=camera_space.multiply(o.getGlobalPlacement());box.add(s.optimalBoundingBox(False))
    centre=App.Vector((box.XMin+box.XMax)/2,(box.YMin+box.YMax)/2,(box.ZMin+box.ZMax)/2)
    position=rotation.multVec(centre+App.Vector(0,0,300));camera=view.getCameraNode()
    camera.position.setValue(position.x,position.y,position.z)
    camera.height.setValue(max(box.YLength,box.XLength/(1400/1050))*1.15)
    camera.focalDistance.setValue(300);camera.nearDistance.setValue(.1);camera.farDistance.setValue(2000)


def run(model_path,output_dir):
    out=Path(output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    if out.is_relative_to(HERE.parent):raise ValueError('Render into build/ before promotion')
    d=App.openDocument(str(Path(model_path).resolve()))
    d.Motion.BeadSteps=11;d.Motion.StrandClosed=True;d.Motion.CapStroke=0;d.Motion.CapReturning=False;d.recompute()
    b.present(d,fit=False)
    view=Gui.activeDocument().activeView()
    frame(d,view);saved=out/b.MODEL_FILE;d.saveAs(str(saved));App.closeDocument(d.Name)
    original=list(sys.path);sys.path[:]=[p for p in sys.path if Path(p or '.').resolve()!=HERE]
    names=('bracelet_v6_updated','rna_path','springs_v6_updated')
    modules={n:sys.modules.pop(n,None) for n in names}
    checks={}
    try:
        d=App.openDocument(str(saved));QtWidgets.QApplication.processEvents()
        checks['normal_GUI_close_reopen']=True
        d.Motion.CapStroke=1;d.recompute()
        checks['native_torsion_winds_without_source']=abs(d.ReturnCoilPath.Pitch.Value-2.1/(3+b.CAP_ANGLE/360))<1e-8
        checks['native_compression_changes_without_source']=abs(d.PawlCoilPath.Height.Value-(4.25-d.Motion.PawlLift.Value))<1e-8
        checks['native_lower_washer_tracks_pawl']=abs(d.PawlSpringLowerSeat.Placement.Base.z-(26.3+d.Motion.PawlLift.Value))<1e-8
        checks['one_piece_serpentine_without_source']=len(d.DetentFlexure.Shape.Solids)==1 and d.DetentFlexure.Shape.isValid()
        d.Motion.CapStroke=0;d.Motion.StrandClosed=False;d.Motion.BeadSteps=0;d.recompute()
        expected=b.rna_pose(2*b.RNA_PITCH,0,False)
        checks['native_open_RNA_without_source']=(d.RnaLink002.Placement.Base-expected.Base).Length<1e-7
        checks['native_update_without_source_directory']=all(checks.values())
    finally:
        sys.path[:]=original;sys.modules.update({n:v for n,v in modules.items() if v is not None})
    view=Gui.activeDocument().activeView()
    def snap(name,orientation='iso'):
        QtWidgets.QApplication.processEvents();frame(d,view,orientation);view.redraw()
        QtWidgets.QApplication.processEvents();view.saveImage(str(out/name),1400,1050,'White')
        print('GUI image '+name,flush=True)
    d.Motion.StrandClosed=True;d.Motion.BeadSteps=11;d.recompute();b.present(d,fit=False)
    snap('handheld.png');snap('side.png','left');snap('underside.png','bottom')
    d.Motion.StrandClosed=False;d.recompute();snap('open.png','front')
    d.Motion.StrandClosed=True;d.Motion.BeadSteps=0;d.recompute();b.present(d,cutaway=True,fit=False);snap('mechanism.png')
    spring_names={'CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg','ReturnSpringHousing',
        'PawlBiasSpring','PawlSpringLowerSeat','PawlSpringUpperSeat','DriveCarrier','UpperLobe','GearGuard','CentreAxle','CapWasher','CapRetainer'}
    for o in d.Objects:
        if hasattr(o,'DisplayColour'):o.ViewObject.Visibility=o.Name in spring_names
    # Crop the actual upper to its internal supports so skin seams do not
    # obscure the spring's two attachment points.
    section=d.addObject('Part::Feature','UpperInternalSection')
    section.Shape=b.world(d.UpperLobe).common(b.cylinder(21.5,11.5,b.V(0,0,21)))
    section.ViewObject.ShapeColor=b.COLORS['cap'];section.ViewObject.DisplayMode='Shaded'
    section.ViewObject.Transparency=75
    section.ViewObject.Visibility=True;d.UpperLobe.ViewObject.Visibility=False
    d.GearGuard.ViewObject.Transparency=35;d.GearGuard.ViewObject.DisplayMode='Shaded'
    d.ReturnSpringHousing.ViewObject.Transparency=65
    snap('spring-installation.png')
    d.Motion.CapStroke=1;d.recompute()
    section.Shape=b.world(d.UpperLobe).common(b.cylinder(21.5,11.5,b.V(0,0,21)))
    snap('spring-loaded.png')
    d.Motion.CapStroke=0;d.recompute()
    d.removeObject(section.Name)
    for o in d.Objects:
        if hasattr(o,'DisplayColour'):o.ViewObject.Visibility=o.Name in {'CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg','ReturnSpringHousing'}
    snap('torsion-spring.png')
    for o in d.Objects:
        if hasattr(o,'DisplayColour'):o.ViewObject.Visibility=o.Name in {'DetentFlexure','DetentTip','DetentAnchor','IndexWheel'}
    snap('serpentine-leaf.png','top')
    d.Motion.BeadSteps=11;d.recompute();b.present(d,fit=False);frame(d,view);d.save();App.closeDocument(d.Name)
    checks['model_sha256']=hashlib.sha256(saved.read_bytes()).hexdigest()
    checks['source_sha256']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in
        ('bracelet_v6_updated.py','rna_path.py','springs_v6_updated.py','presentation_v6_updated.py','RibosomeV6Updated.FCMacro')}
    (out/'gui-checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    return checks


def recapture_spring_views(output_dir):
    """Expose the actual internal supports in two close inspection views."""
    out=Path(output_dir);d=App.openDocument(str((out/b.MODEL_FILE).resolve()))
    d.Motion.BeadSteps=0;d.Motion.CapStroke=0;d.recompute();b.present(d,fit=False)
    names={'CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg','ReturnSpringHousing',
        'PawlBiasSpring','PawlSpringLowerSeat','PawlSpringUpperSeat','DriveCarrier',
        'CentreAxle','CapWasher','CapRetainer'}
    for o in d.Objects:
        if hasattr(o,'DisplayColour'):o.ViewObject.Visibility=o.Name in names
    # Exact sections of the actual upper and fixed stator, with the organic
    # roof removed above z=32.5. No idealized replacement brackets.
    upper=d.addObject('Part::Feature','UpperSpringSupports')
    upper.addProperty('App::PropertyColor','DisplayColour');upper.DisplayColour=b.COLORS['cap']
    fixed=d.addObject('Part::Feature','FixedSpringStator')
    fixed.addProperty('App::PropertyColor','DisplayColour');fixed.DisplayColour=b.COLORS['lid']
    fixed.Shape=b.world(d.GearGuard).common(b.cylinder(2.2,7,b.polar(18,-120,21.7)))
    for o in (upper,fixed):
        o.ViewObject.ShapeColor=tuple(o.DisplayColour[:3]);o.ViewObject.DisplayMode='Shaded'
    upper.ViewObject.Transparency=70;fixed.ViewObject.Transparency=45
    d.ReturnSpringHousing.ViewObject.Transparency=60
    view=Gui.activeDocument().activeView()
    for stroke,name in [(0,'spring-installation.png'),(1,'spring-loaded.png')]:
        d.Motion.CapStroke=stroke;d.recompute()
        upper.Shape=b.world(d.UpperLobe).common(b.cylinder(21.5,11.5,b.V(0,0,21)))
        QtWidgets.QApplication.processEvents();frame(d,view);view.redraw()
        QtWidgets.QApplication.processEvents();view.saveImage(str(out/name),1400,1050,'White')
    App.closeDocument(d.Name)
    evidence=json.loads((out/'gui-checks.json').read_text())
    evidence['spring_views_recaptured_from_saved_model']=True
    evidence['source_sha256']['presentation_v6_updated.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (out/'gui-checks.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
