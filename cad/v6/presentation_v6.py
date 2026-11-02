"""Present/check V6 in FreeCAD GUI and write review artifacts to build/.

Call run(model_path, output_dir) from a FreeCAD macro. Saved cad/ versions
are protected; this helper never closes unrelated documents or promotes files.
"""
from pathlib import Path
import hashlib
import json
import sys
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore,QtWidgets
from pivy import coin
import bracelet_v6 as b

HERE=Path(__file__).resolve().parent


def _orient(view,name):
    # View menu commands animate asynchronously. Assign the camera rotation
    # directly so a capture cannot retain the preceding view's orientation.
    rotations={
        'iso':App.Rotation(App.Vector(1,1,0),App.Vector(-1,1,2),App.Vector(1,-1,1),'ZXY'),
        'front':App.Rotation(App.Vector(1,0,0),90),
        'left':App.Rotation(App.Vector(0,-1,0),App.Vector(0,0,1),App.Vector(-1,0,0),'ZXY'),
        'bottom':App.Rotation(App.Vector(1,0,0),180),
        'top':App.Rotation(),
    }
    view.getCameraNode().orientation.setValue(coin.SbRotation(*rotations[name].Q))


def _frame_visible(d,view):
    """Frame exact visible solids; spline control bounds can dwarf the toy."""
    rotation=view.getCameraOrientation();inverse=rotation.inverted()
    camera_space=App.Placement(App.Vector(),inverse)
    box=App.BoundBox()
    def visible(o):
        if not o.ViewObject.Visibility: return False
        return all(visible(p) for p in o.InList if p.TypeId=='App::Part')
    for o in d.Objects:
        if not hasattr(o,'DisplayColour') or not visible(o): continue
        shape=o.Shape.copy();shape.Placement=camera_space.multiply(o.getGlobalPlacement())
        box.add(shape.optimalBoundingBox(False))
    centre=App.Vector((box.XMin+box.XMax)/2,(box.YMin+box.YMax)/2,(box.ZMin+box.ZMax)/2)
    position=rotation.multVec(centre+App.Vector(0,0,300))
    camera=view.getCameraNode();camera.position.setValue(position.x,position.y,position.z)
    camera.height.setValue(max(box.YLength,box.XLength/(1400/1050))*1.14)
    camera.focalDistance.setValue(300);camera.nearDistance.setValue(.1);camera.farDistance.setValue(2000)


def _wait_animation(dock,observe=None):
    timers=dock.findChildren(QtCore.QTimer)
    animation=next(t for t in timers if t.isActive())
    loop=QtCore.QEventLoop();poll=QtCore.QTimer();poll.setInterval(20)
    timeout=QtCore.QTimer();timeout.setSingleShot(True)
    result={'timeout':False}
    def check():
        if observe: observe()
        if not animation.isActive(): loop.quit()
    def expired(): result['timeout']=True;loop.quit()
    poll.timeout.connect(check);timeout.timeout.connect(expired)
    poll.start();timeout.start(35000);loop.exec();poll.stop();timeout.stop()
    if result['timeout']: raise RuntimeError('V6 controls animation did not finish within 35 seconds')


def _controls_check(d):
    dock=b.open_controls(d)
    buttons={w.text():w for w in dock.findChildren(QtWidgets.QPushButton)}
    slider=dock.findChild(QtWidgets.QSlider)
    closed=next(w for w in dock.findChildren(QtWidgets.QCheckBox) if w.text().startswith('Clasp joined'))
    forward=buttons['Rock upper subunit'];reverse=buttons['RNA backward — one bead']
    slider.setValue(200);forward.click();_wait_animation(dock)
    assert abs(d.Motion.BeadSteps-6)<1e-9 and d.Motion.CapStroke==0
    reverse.click();_wait_animation(dock)
    assert abs(d.Motion.BeadSteps-5)<1e-9 and d.Motion.PawlLift.Value==b.PAWL_LIFT
    before=d.ClaspReceiver.Placement.Base
    closed.setChecked(False)
    assert not d.Motion.StrandClosed and (d.ClaspReceiver.Placement.Base-before).Length>10
    closed.setChecked(True)
    slider.setValue(22*40)
    observed={'maximum_cap_angle':0,'maximum_feed':0}
    def observe():
        observed['maximum_cap_angle']=max(observed['maximum_cap_angle'],d.Motion.CapAngle)
        observed['maximum_feed']=max(observed['maximum_feed'],d.Motion.EffectiveSteps)
    forward.click();_wait_animation(dock,observe)
    assert observed['maximum_cap_angle']<=b.ENTRY_DEG+1e-7
    assert observed['maximum_cap_angle']>b.ENTRY_DEG-.5 and observed['maximum_feed']==22
    assert d.Motion.BeadSteps==22 and d.Motion.CapStroke==0
    reverse.click();_wait_animation(dock)
    assert d.Motion.BeadSteps==21 and not hasattr(d.Motion,'ReverseRelease')
    Gui.getMainWindow().removeDockWidget(dock);dock.deleteLater();QtWidgets.QApplication.processEvents()
    return dict(forward_button_5_to_6=True,direct_reverse_button_6_to_5=True,
                open_closed_checkbox=True,blocked_forward_at_22=True,
                reverse_from_endpoint_22_to_21=True,observed_endpoint=observed)


def run(model_path,output_dir):
    out=Path(output_dir).resolve();model=Path(model_path).resolve()
    if out.is_relative_to(HERE.parent): raise ValueError('GUI output must be outside saved cad/ versions')
    out.mkdir(parents=True,exist_ok=True)
    Gui.getMainWindow().resize(1400,1050);QtWidgets.QApplication.processEvents()
    d=App.openDocument(str(model))
    evidence={'runtime':'.'.join(App.Version()[:3]),'controls':_controls_check(d)}
    d.Motion.BeadSteps=11;d.Motion.CapStroke=0;d.Motion.CapReturning=False;d.Motion.StrandClosed=True;d.recompute()
    b.present(d,fit=False)
    initial_view=Gui.activeDocument().activeView();_orient(initial_view,'iso');_frame_visible(d,initial_view)
    saved=out/b.MODEL_FILE;d.saveAs(str(saved));App.closeDocument(d.Name)
    # The native file opens/updates with its source directory absent. No
    # external Python proxy or private GUI/MCP machine is required.
    original_path=list(sys.path);sys.path[:]=[p for p in sys.path if Path(p or '.').resolve()!=HERE]
    cached_modules={n:sys.modules.pop(n,None) for n in ('bracelet_v6','rna_path')}
    try:
        d=App.openDocument(str(saved));QtWidgets.QApplication.processEvents()
        coloured={o.Name for o in d.Objects if hasattr(o,'DisplayColour')}
        visible={o.Name for o in d.Objects if hasattr(o,'DisplayColour') and o.ViewObject.Visibility}
        assert visible==coloured-{'CapSpringEnvelope','PawlBiasSpringEnvelope','CapFixedSpringLeg','CapMovingSpringLeg'},sorted(coloured-visible)
        assert d.Motion.BeadSteps==11 and d.Motion.StrandClosed
        d.Motion.StrandClosed=False;d.Motion.BeadSteps=0;d.recompute()
        expected=b.rna_pose(2*b.RNA_PITCH,0,False)
        assert (d.RnaLink002.Placement.Base-expected.Base).Length<1e-7
        d.Motion.StrandClosed=True;d.Motion.BeadSteps=11;d.recompute()
        evidence.update(normal_GUI_close_reopen=True,native_update_without_source_directory=True,
                        visible_coloured_parts=len(visible),saved_bead_steps=11)
    finally:
        sys.path[:]=original_path
        sys.modules.update({n:v for n,v in cached_modules.items() if v is not None})
    view=Gui.activeDocument().activeView()
    def snap(name,orientation='iso'):
        QtWidgets.QApplication.processEvents()
        _orient(view,orientation)
        _frame_visible(d,view)
        view.redraw();QtWidgets.QApplication.processEvents()
        view.saveImage(str(out/name),1400,1050,'White')
    b.present(d,fit=False);snap('handheld.png','iso')
    snap('side.png','left');evidence['side_route_view']=True
    snap('underside.png','bottom')
    d.Motion.StrandClosed=False;d.recompute();b.present(d,fit=False);snap('open.png','front')
    d.Motion.StrandClosed=True;d.Motion.BeadSteps=0;d.recompute();b.present(d,fit=False);snap('home.png','top')
    d.Motion.BeadSteps=11;d.recompute();b.present(d,cutaway=True,fit=False);snap('mechanism.png','iso')
    d.Motion.BeadSteps=0;d.Motion.CapStroke=3/b.CAP_ANGLE;d.recompute();b.present(d,cutaway=True,fit=False)
    d.LowerBody.ViewObject.Visibility=False;d.Protein.ViewObject.Visibility=False;d.RnaStrand.ViewObject.Visibility=False
    d.BeadDrum.ViewObject.Visibility=False
    d.GearGuard.ViewObject.Visibility=True;d.GearGuard.ViewObject.Transparency=82;d.GearGuard.ViewObject.DisplayMode='Shaded'
    snap('cap-input.png','iso')
    # Actual sections of the saved assembly, created only in temporary view
    # documents. No idealized bolt stand-ins or changes to the saved model.
    d.Motion.BeadSteps=0;d.Motion.CapStroke=0;d.Motion.CapReturning=False;d.recompute()
    def section(name,box,objects):
        temp=App.newDocument('V6Inspection')
        try:
            for source in objects:
                o=d.getObject(source);shape=b.world(o).common(box)
                if shape.isNull() or shape.Volume<1e-8 or not shape.isValid():
                    raise RuntimeError('Section unexpectedly lost material from '+source)
                f=temp.addObject('Part::Feature',source);f.Shape=shape
                f.addProperty('App::PropertyColor','DisplayColour');f.DisplayColour=o.DisplayColour
                f.ViewObject.ShapeColor=tuple(o.DisplayColour[:3]);f.ViewObject.LineColor=(.12,.12,.12)
                f.ViewObject.DisplayMode='Flat Lines';f.ViewObject.LineWidth=.7;f.ViewObject.Visibility=True
            temp.recompute();v=Gui.activeDocument().activeView();_orient(v,'iso');_frame_visible(temp,v)
            v.redraw();QtWidgets.QApplication.processEvents();v.saveImage(str(out/name),1400,1050,'White')
        finally:App.closeDocument(temp.Name)
    import Part
    section('fasteners.png',Part.makeBox(8,4.5,16,b.V(28,-14,8)),
            ['LowerBody','BeadKeeper','LowerLid','GearGuard','HousingScrew01'])
    section('spindle.png',Part.makeBox(8,8,36,b.V(-8,-4,.5)),
            ['LowerBody','CentreAxle','UpperLobe','CapRetainer','CapWasher','DriveHub','IndexSleeve'])
    evidence.update(housing_bolt_section_actual_solids=True,spindle_section_actual_solids=True)
    App.closeDocument(d.Name)
    evidence['model_sha256']=hashlib.sha256(saved.read_bytes()).hexdigest()
    evidence['source_sha256']={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in
        ('bracelet_v6.py','rna_path.py','presentation_v6.py','RibosomeV6.FCMacro')}
    (out/'gui-checks.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    return evidence
