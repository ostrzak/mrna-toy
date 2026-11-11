"""Native GUI reopen, motion and actual-geometry inspection images."""
from pathlib import Path
import hashlib
import json
import sys
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtWidgets
from pivy import coin
import bracelet_v6_updated_print as b

HERE=Path(__file__).resolve().parent


def frame(d,view,orientation='iso',focus=None):
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
        if focus is not None and o.Name not in focus:continue
        if o.Shape.isNull():continue
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
    b.present(d,fit=False);view=Gui.activeDocument().activeView();frame(d,view)
    saved=out/b.MODEL_FILE;d.saveAs(str(saved));App.closeDocument(d.Name)
    original=list(sys.path);sys.path[:]=[p for p in sys.path if Path(p or '.').resolve()!=HERE]
    names=('bracelet_v6_updated_print','rna_path','springs_v6_updated_print','stock_springs','printed_fasteners')
    modules={n:sys.modules.pop(n,None) for n in names}
    checks={}
    try:
        d=App.openDocument(str(saved));QtWidgets.QApplication.processEvents()
        checks['normal_GUI_close_reopen']=True
        d.Motion.CapStroke=1;d.recompute()
        checks['native_stock_return_envelope']=abs(d.CapReturnSpringOuter.Height.Value-(5+.6*d.Motion.ReturnSpringStrain.Value/360))<1e-8
        checks['native_horizontal_bias_envelope']=abs(d.PawlBiasSpringOuter.Height.Value-(5+.6*d.Motion.PawlSpringStrain.Value/360))<1e-8
        checks['native_integral_pawl_contact_tracks_lift']=abs(d.PawlSpringLowerSeat.Placement.Base.z-(26+d.Motion.PawlLift.Value))<1e-8
        checks['native_stock_spring_leg_motion']=d.Motion.ReturnSpringStrain.Value>23 and d.Motion.PawlSpringStrain.Value<15.5
        checks['one_piece_serpentine_without_source']=len(d.DetentFlexure.Shape.Solids)==1 and d.DetentFlexure.Shape.isValid()
        d.Motion.CapStroke=0;d.Motion.StrandClosed=False;d.Motion.BeadSteps=0;d.recompute()
        expected=b.rna_pose(2*b.RNA_PITCH,0,False)
        checks['native_open_RNA_without_source']=(d.RnaLink002.Placement.Base-expected.Base).Length<1e-7
        checks['native_update_without_source_directory']=all(checks.values())
    finally:
        sys.path[:]=original;sys.modules.update({n:v for n,v in modules.items() if v is not None})
    view=Gui.activeDocument().activeView()
    def snap(name,orientation='iso',focus=None):
        QtWidgets.QApplication.processEvents();frame(d,view,orientation,focus);view.redraw()
        QtWidgets.QApplication.processEvents();view.saveImage(str(out/name),1400,1050,'White')
        print('GUI_IMAGE '+name,flush=True)
    d.Motion.StrandClosed=True;d.Motion.BeadSteps=11;d.Motion.CapStroke=0;d.recompute();b.present(d,fit=False)
    snap('handheld.png');snap('underside.png','bottom')
    b.present(d,cutaway=True,fit=False);snap('mechanism.png')
    names={'CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg','ReturnSpringHousing',
        'PawlBiasSpring','PawlFixedSpringLeg','PawlMovingSpringLeg','PawlSpringLowerSeat',
        'PawlSpringUpperSeat','PawlFixedSpringSeat','UpperLobe','DriveCarrier'}
    for o in d.Objects:
        if hasattr(o,'DisplayColour'):o.ViewObject.Visibility=o.Name in names
    d.UpperLobe.ViewObject.DisplayMode='Shaded';d.UpperLobe.ViewObject.Transparency=90
    d.ReturnSpringHousing.ViewObject.Transparency=50
    d.CapReturnSpring.ViewObject.Transparency=35;d.PawlBiasSpring.ViewObject.Transparency=35
    snap('spring-installation.png')
    d.Motion.CapStroke=1;d.recompute();snap('spring-loaded.png')
    d.Motion.CapStroke=0;d.recompute()
    d.UpperLobe.ViewObject.Visibility=False
    contact=d.addObject('Part::Feature','UpperSpringContactSection')
    contact.addProperty('App::PropertyColor','DisplayColour');contact.DisplayColour=b.COLORS['cap']
    contact.Shape=b.world(d.UpperLobe).common(Part.makeCylinder(12.4,3,App.Vector(0,0,30.3)))
    contact.ViewObject.ShapeColor=b.COLORS['cap'];contact.ViewObject.DisplayMode='Shaded'
    contact.ViewObject.Transparency=55
    snap('stock-springs.png');d.removeObject(contact.Name)
    names={'HousingScrew00','HousingNut00','CentreAxle','CapRetainer','CapWasher','LowerBody'}
    for o in d.Objects:
        if hasattr(o,'DisplayColour'):o.ViewObject.Visibility=o.Name in names
    # A render clip exposes the actual pocket without another Boolean against
    # the organic housing's rational patch boundaries.
    clip=coin.SoClipPlane();clip.plane=coin.SbPlane(coin.SbVec3f(0,1,0),-14)
    d.LowerBody.ViewObject.RootNode.insertChild(clip,0)
    d.LowerBody.ViewObject.Transparency=55
    snap('printed-fasteners.png',focus=names-{'LowerBody'})
    d.LowerBody.ViewObject.RootNode.removeChild(clip)
    d.Motion.BeadSteps=11;d.Motion.CapStroke=0;d.Motion.CapReturning=False;d.Motion.StrandClosed=True;d.recompute()
    b.present(d,fit=False);frame(d,view);d.save();App.closeDocument(d.Name)
    checks['model_sha256']=hashlib.sha256(saved.read_bytes()).hexdigest()
    checks['source_sha256']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in
        ('bracelet_v6_updated_print.py','rna_path.py','springs_v6_updated_print.py','stock_springs.py',
         'printed_fasteners.py','presentation_v6_updated_print.py','RibosomeV6UpdatedPrint.FCMacro')}
    (out/'gui-checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    return checks
