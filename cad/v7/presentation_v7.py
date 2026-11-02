"""Present/check V7 in FreeCAD GUI and write review artifacts to build/.

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
import bracelet_v7 as b

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
    if result['timeout']: raise RuntimeError('V7 controls animation did not finish within 35 seconds')


def run(model_path,output_dir):
    """Save a review checkpoint with GUI/native evidence, not a CAD PASS.

    Button animation, full mechanism/assembly validation and physical
    operation are deliberately not asserted by this presentation helper.
    """
    out=Path(output_dir).resolve();model=Path(model_path).resolve()
    if out.is_relative_to(HERE.parent):raise ValueError('GUI output must be outside saved cad/ versions')
    out.mkdir(parents=True,exist_ok=True)
    d=App.openDocument(str(model));view=Gui.activeDocument().activeView()
    evidence={'runtime':'.'.join(App.Version()[:3]),'status':'INCOMPLETE_HANDOFF',
              'controls_animation_checked':False,'full_geometry_checked':False}
    d.Motion.BeadSteps=6;d.Motion.InputKind=0;d.Motion.CyclePosition=0;d.Motion.StrandClosed=True;d.recompute()
    b.present(d,fit=False);_orient(view,'iso');_frame_visible(d,view)
    saved=out/b.MODEL_FILE;d.saveAs(str(saved));App.closeDocument(d.Name)
    original=list(sys.path);sys.path[:]=[p for p in sys.path if Path(p or '.').resolve()!=HERE]
    cached={n:sys.modules.pop(n,None) for n in ('bracelet_v7','rna_path','coupling_v7')}
    poses=[]
    try:
        d=App.openDocument(str(saved))
        for kind in (0,1,2):
            for cycle in (0,.2,.4,.75,1):
                d.Motion.BeadSteps=6;d.Motion.InputKind=kind;d.Motion.CyclePosition=cycle;d.recompute()
                bad=[o.Name for o in d.Objects if 'Invalid' in o.State]
                if bad:raise RuntimeError('Invalid checkpoint expression: '+str(bad))
                cap=d.Motion.CapAngle;feed=d.Motion.EffectiveSteps
                if kind==2:assert cap==0 and abs(feed-(6-cycle))<1e-7
                if cycle==1:assert cap==0 and abs(feed-(5 if kind==2 else 7))<1e-7
                poses.append(dict(input=kind,cycle=cycle,feed=feed,upper_degrees=cap))
        evidence.update(normal_GUI_close_reopen=True,native_update_without_source_directory=True,native_checkpoint_poses=poses)
    finally:
        sys.path[:]=original;sys.modules.update({n:v for n,v in cached.items() if v is not None})
    d.Motion.BeadSteps=6;d.Motion.InputKind=0;d.Motion.CyclePosition=0;d.Motion.StrandClosed=True;d.recompute()
    b.present(d,fit=False);d.save();view=Gui.activeDocument().activeView()
    def snap(name,orientation='iso'):
        QtWidgets.QApplication.processEvents();_orient(view,orientation);_frame_visible(d,view)
        view.redraw();QtWidgets.QApplication.processEvents();view.saveImage(str(out/name),1400,1050,'White')
    snap('handheld.png');snap('side.png','left')
    b.present(d,cutaway=True,fit=False);snap('mechanism.png')
    d.Motion.InputKind=0;d.Motion.CyclePosition=.2;d.recompute()
    d.Protein.ViewObject.Visibility=False;d.RnaStrand.ViewObject.Visibility=False
    d.LowerBody.ViewObject.Visibility=False;d.BeadDrum.ViewObject.Visibility=False
    snap('pickup.png')
    d.Motion.CyclePosition=.7;d.recompute();snap('return.png')
    d.Motion.CyclePosition=0;d.Motion.BeadSteps=6;d.Motion.InputKind=0;d.recompute()
    b.present(d,fit=False);_orient(view,'iso');_frame_visible(d,view);d.save()
    evidence['model_sha256']=hashlib.sha256(saved.read_bytes()).hexdigest()
    evidence['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
    evidence['controls_created']=bool(b.open_controls(d))
    (out/'gui-checks.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    return evidence
