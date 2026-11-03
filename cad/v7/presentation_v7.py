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
    poll.start();timeout.start(180000);loop.exec();poll.stop();timeout.stop()
    if result['timeout']: raise RuntimeError('V7 controls animation did not finish within 180 seconds')


def run(model_path,output_dir):
    """Save actual GUI/native evidence, separately from mechanical validation."""
    out=Path(output_dir).resolve();model=Path(model_path).resolve()
    if out.is_relative_to(HERE.parent):raise ValueError('GUI output must be outside saved cad/ versions')
    out.mkdir(parents=True,exist_ok=True)
    d=App.openDocument(str(model));view=Gui.activeDocument().activeView()
    print('GUI stage: opened source build',flush=True)
    evidence={'runtime':'.'.join(App.Version()[:3]),'status':'REVIEW',
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
        print('GUI stage: normal reopen and all native poses completed',flush=True)
    finally:
        sys.path[:]=original;sys.modules.update({n:v for n,v in cached.items() if v is not None})
    d.Motion.BeadSteps=6;d.Motion.InputKind=0;d.Motion.CyclePosition=0;d.Motion.StrandClosed=True;d.recompute()
    b.present(d,fit=False);d.save();view=Gui.activeDocument().activeView()
    def snap(name,orientation='iso'):
        QtWidgets.QApplication.processEvents();_orient(view,orientation);_frame_visible(d,view)
        view.redraw();QtWidgets.QApplication.processEvents();view.saveImage(str(out/name),1400,1050,'White')
        print('GUI view saved: '+name,flush=True)
    snap('handheld.png');snap('side.png','left');snap('underside.png','bottom')
    d.Motion.StrandClosed=False;d.recompute();snap('open.png')
    d.Motion.StrandClosed=True;d.recompute()
    b.present(d,cutaway=True,fit=False);snap('mechanism.png')
    d.Motion.InputKind=0;d.Motion.CyclePosition=.2;d.recompute()
    d.Protein.ViewObject.Visibility=False;d.RnaStrand.ViewObject.Visibility=False
    d.LowerBody.ViewObject.Visibility=False;d.BeadDrum.ViewObject.Visibility=False
    snap('pickup.png')
    d.Motion.CyclePosition=.7;d.recompute();snap('return.png')
    d.Motion.CyclePosition=0;d.Motion.BeadSteps=6;d.Motion.InputKind=0;d.recompute()
    b.present(d,fit=False);_orient(view,'iso');_frame_visible(d,view);d.save()
    dock=b.open_controls(d);evidence['controls_created']=bool(dock)
    results=[]
    try:
        buttons=dock.findChildren(QtWidgets.QPushButton)
        for text,kind in [('RNA forward',0),('Rock upper',1),('RNA backward',2)]:
            button=next(x for x in buttons if x.text().startswith(text))
            d.Motion.BeadSteps=6;d.Motion.InputKind=0;d.Motion.CyclePosition=0;d.recompute()
            button.click();_wait_animation(dock)
            expected=5 if kind==2 else 7
            assert abs(d.Motion.BeadSteps-expected)<1e-8 and abs(d.Motion.CapAngle)<1e-8
            results.append(dict(control=button.text(),completed_index=expected,upper_home=True))
            print('GUI control completed: '+button.text(),flush=True)
        target=next(x for x in dock.findChildren(QtWidgets.QSlider) if x.maximum()==b.EMIT)
        for value in (8,6):
            target.setValue(value)
            # A target may chain timers with a singleShot between indices.
            for j in range(4):
                if abs(d.Motion.BeadSteps-value)<1e-8:break
                QtWidgets.QApplication.processEvents()
                timers=[t for t in dock.findChildren(QtCore.QTimer) if t.isActive()]
                if timers:_wait_animation(dock)
                else:
                    loop=QtCore.QEventLoop();QtCore.QTimer.singleShot(100,loop.quit);loop.exec()
            assert abs(d.Motion.BeadSteps-value)<1e-8
            results.append(dict(control='RNA target slider',completed_index=value,upper_home=abs(d.Motion.CapAngle)<1e-8))
        evidence['controls_animation_checked']=True
    except Exception as exc:
        evidence['controls_animation_failure']=str(exc) or type(exc).__name__
        for timer in dock.findChildren(QtCore.QTimer):timer.stop()
    evidence['controls_results']=results
    d.Motion.BeadSteps=6;d.Motion.InputKind=0;d.Motion.CyclePosition=0;d.Motion.StrandClosed=True;d.recompute()
    b.present(d,fit=False);_orient(view,'iso');_frame_visible(d,view);d.save()
    evidence['model_sha256']=hashlib.sha256(saved.read_bytes()).hexdigest()
    evidence['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.py')}
    evidence['boundary']='Normal GUI reopen, native expressions and control animations only. No automatic trip/reset, elastic equilibrium or physical operation is established by these prescribed motions.'
    (out/'gui-checks.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    return evidence
