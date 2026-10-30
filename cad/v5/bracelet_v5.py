"""V5 handheld ribosome: captive bead carousel and an external closed RNA loop.

Millimetres. Native expressions prescribe rigid motion; they are not a physics
simulation. The ratchet leaves are shown unloaded. No cord, rewind spring or
tensioned take-up reel is used. Manufacturing and physical operation are open.
"""
from pathlib import Path
from functools import lru_cache
import math
import FreeCAD as App
import Part
from fcgear import involute, fcgear

HERE = Path(__file__).resolve().parent
DOC_NAME = 'RibosomeV5'
MODEL_FILE = 'RibosomeV5.FCStd'
V = App.Vector
TAU = 2 * math.pi
BEAD_R, BEAD_PITCH, WIRE_R = 2.2, 6.0, .18
BEADS, EMIT, POCKETS = 26, 22, 28
HOME_S, MOUTH_X = 6.0, 9.0
STORE_R = POCKETS * BEAD_PITCH / TAU
BEAD_Z = 11.0
STEP_DEG = 360 / POCKETS
MAX_DRUM = EMIT * STEP_DEG
MODULE = .72
SUN_TEETH, IDLER_TEETH, RNA_TEETH = 84, 14, 112
RNA_R = RNA_TEETH * MODULE / 2
IDLER_R = (SUN_TEETH + IDLER_TEETH) * MODULE / 2
GEAR_Z, GEAR_WIDTH = 3.5, 1.8
RNA_OUT = RNA_R + 1.65
RNA_BASE_LENGTHS = (2.6, 3.1, 2.8, 3.5)
FORK_INNER_Z = .85
FORK_WIDTH = .65
RATCHET_Z = 17.3
RELEASE_LIFT = 3.0
BEAD_FAMILY = ('bilobed', 'offset', 'trilobed')
COLORS = {
    'body': (.43, .35, .59), 'lid': (.58, .49, .72),
    'cap': (.72, .64, .84), 'rna': (.12, .57, .63),
    'drum': (.15, .48, .52), 'gear': (.72, .76, .79),
    'guide': (.65, .69, .73), 'protein': (.94, .56, .34),
    'wire': (.64, .39, .23), 'pawl': (.86, .67, .30),
}


def union(shapes):
    shapes = [s for s in shapes if not s.isNull()]
    return shapes[0].multiFuse(shapes[1:]).removeSplitter() if len(shapes) > 1 else shapes[0]


def cylinder(r, h, base=V(), axis=V(0, 0, 1)):
    return Part.makeCylinder(r, h, base, axis)


def annulus(inner, outer, z, h):
    return cylinder(outer, h, V(0, 0, z)).cut(cylinder(inner, h+2, V(0, 0, z-1)))


def ellipsoid(center, radii):
    matrix = App.Matrix()
    matrix.A11, matrix.A22, matrix.A33 = radii
    shape = Part.makeSphere(1).transformGeometry(matrix)
    shape.translate(V(*center))
    return shape


def radial(r, angle, z=0):
    a = math.radians(angle)
    return V(r*math.sin(a), r*math.cos(a), z)


def sector(inner, outer, a, b, z, h):
    p = lambda r, t: radial(r, t, z)
    wire = Part.Wire([
        Part.Arc(p(outer,a),p(outer,(a+b)/2),p(outer,b)).toShape(),
        Part.makeLine(p(outer,b),p(inner,b)),
        Part.Arc(p(inner,b),p(inner,(a+b)/2),p(inner,a)).toShape(),
        Part.makeLine(p(inner,a),p(outer,a)),
    ])
    return Part.Face(wire).extrude(V(0,0,h))


def gear(teeth, z=GEAR_Z, width=GEAR_WIDTH, internal=False):
    builder = fcgear.FCWireBuilder()
    create = involute.CreateInternalGear if internal else involute.CreateExternalGear
    create(builder, MODULE, teeth, 25, split=True)
    face = Part.Face(Part.Wire([e.toShape() for e in builder.wire]))
    if internal:
        face = Part.Face(Part.Wire([Part.makeCircle(RNA_OUT)])).cut(face)
    shape = face.extrude(V(0,0,width))
    shape.translate(V(0,0,z))
    return shape


def path(s):
    if s < 0:
        a = s / STORE_R
        return V(STORE_R*math.sin(a), STORE_R*math.cos(a), BEAD_Z)
    return V(s, STORE_R, BEAD_Z)


def tangent(s):
    return V(math.cos(s/STORE_R), -math.sin(s/STORE_R), 0) if s < 0 else V(1,0,0)


def placed_bead(shape, s, roll=0):
    result = shape.copy()
    result.Placement = App.Placement(path(s), App.Rotation(V(1,0,0),tangent(s)).multiply(App.Rotation(V(1,0,0),roll)))
    return result


@lru_cache(maxsize=3)
def bead_shape(kind=0):
    """Preserved 4.4 mm bound, shared axial shoulders and three lobed middles."""
    sphere = Part.makeSphere(BEAD_R)
    rings = []
    for x in [-1.6,-1.4,-1.1,-.7,-.35,0,.35,.7,1.1,1.4,1.6]:
        radius = math.sqrt(BEAD_R**2-x*x)
        fade = max(0,1-(x/1.35)**2)**2
        pts = []
        for j in range(32):
            a = j*TAU/32
            phase = (.25,.8,-.55)[kind]
            lobes = 3 if kind == 2 else 2
            scallop = .72*(.5+.5*math.cos(lobes*a+phase+.3*x))+.28*(.5+.5*math.sin(a-phase))
            r = radius*(1-.34*fade*scallop)
            pts.append(V(x,r*math.cos(a),r*math.sin(a)))
        curve = Part.BSplineCurve()
        curve.interpolate(pts,PeriodicFlag=True)
        rings.append(Part.Wire([curve.toShape()]))
    middle = Part.makeLoft(rings,True,False)
    shoulders = sphere.cut(Part.makeBox(3,8,8,V(-1.5,-4,-4)))
    bead = sphere.common(union([middle,shoulders]))
    bead = bead.cut(cylinder(.5,6,V(-3,0,0),V(1,0,0)))
    bead = bead.cut(Part.makeCone(1.1,.5,1.5,V(-2.2,0,0),V(1,0,0)))
    bead = bead.cut(Part.makeCone(.5,1.1,1.5,V(.7,0,0),V(1,0,0)))
    return bead.removeSplitter()


@lru_cache(maxsize=1)
def drum_outline():
    """Relieve the real tangent handoff in the rotating frame, not only seats.

    A conservative spherical section at the innermost face of each fork lane
    covers every bead roll. Actual 3D phases are checked separately.
    """
    tool = math.sqrt(BEAD_R**2-FORK_INNER_Z**2)+.16
    centres = []
    for j in range(101):
        s = 18*j/100
        a = s/STORE_R
        x = s*math.cos(a)-STORE_R*math.sin(a)
        y = s*math.sin(a)+STORE_R*math.cos(a)
        for k in range(POCKETS):
            t = k*TAU/POCKETS
            centres.append((x*math.cos(t)+y*math.sin(t), -x*math.sin(t)+y*math.cos(t)))
    pts = []
    for j in range(POCKETS*64):
        a = j*TAU/(POCKETS*64)
        sn,cs,rr = math.sin(a),math.cos(a),STORE_R+1.05
        for x,y in centres:
            projection = x*sn+y*cs
            disc = tool*tool-(x*x+y*y-projection*projection)
            if disc >= 0 and projection > 0:
                rr = min(rr,projection-math.sqrt(disc))
        pts.append(V(rr*sn,rr*cs,0))
    return pts


def drum_shape():
    outline = drum_outline()
    face = Part.Face(Part.makePolygon(outline+[outline[0]]))
    forks=[]
    for z in (BEAD_Z-FORK_INNER_Z-FORK_WIDTH, BEAD_Z+FORK_INNER_Z):
        shape=face.extrude(V(0,0,FORK_WIDTH))
        shape.translate(V(0,0,z))
        forks.append(shape)
    base=cylinder(STORE_R+1.05,1.0,V(0,0,7.4))
    core=cylinder(STORE_R-4.0,5.1,V(0,0,7.4))
    drum=union([base,core]+forks)
    # Open lightening windows in the central carrier, clear of bead pockets.
    windows=[sector(8,19,a+5,a+40,7.2,5.6) for a in range(0,360,60)]
    drum=drum.cut(union(windows))
    return drum.cut(cylinder(3.15,8,V(0,0,6))).removeSplitter()


def drum_sweep(clearance=0):
    """Conservative rotational envelope of the real carrier and fork lanes."""
    c=clearance
    shapes=[cylinder(STORE_R+1.05+c,1+2*c,V(0,0,7.4-c)),
            cylinder(STORE_R-4+c,5.1+2*c,V(0,0,7.4-c))]
    for z in (BEAD_Z-FORK_INNER_Z-FORK_WIDTH,BEAD_Z+FORK_INNER_Z):
        shapes.append(cylinder(STORE_R+1.05+c,FORK_WIDTH+2*c,V(0,0,z-c)))
    return union(shapes)


def protein_envelope(radius=2.5, length=155):
    torus=Part.makeTorus(STORE_R,radius,V(0,0,BEAD_Z),V(0,0,1))
    return union([torus,cylinder(radius,length+2,V(-2,STORE_R,BEAD_Z),V(1,0,0))])


def keeper_shape():
    collar=annulus(STORE_R+2.48,STORE_R+3.8,8.6,6.0)
    roof=annulus(STORE_R-2.65,STORE_R+3.8,13.5,1.1)
    # Roof and outer cheek retain the bead against its moving seat. Keeping
    # fixed material above/outside both fork sweeps avoids floating slit ribs.
    nose_roof=Part.makeBox(13,7.6,1.1,V(-4,STORE_R-3.8,13.5))
    nose_outer=Part.makeBox(13,1.3,6,V(-4,STORE_R+2.5,8.6))
    bore=cylinder(2.6,174,V(-4,STORE_R,BEAD_Z),V(1,0,0))
    tabs=[]
    for x,y in ((-29,-18),(29,-18),(-23,26)):
        angle=math.degrees(math.atan2(x,y))
        tab=sector(STORE_R+2.3,math.hypot(x,y)+2.0,angle-4,angle+4,13.5,1.1)
        tab=tab.cut(cylinder(1.15,2,V(x,y,13)))
        tabs.append(tab)
    keeper=union([collar,roof,nose_roof,nose_outer]+tabs).cut(bore)
    # Mouth roof ends before the visible protein; expose the shallow cleft.
    keeper=keeper.cut(Part.makeBox(100,16,16,V(MOUTH_X,STORE_R-8,4)))
    return keeper.removeSplitter()


def stop_shape():
    ring=annulus(14.5,17.5,5.9,1.3)
    slot=union([sector(15.05,16.95,0,MAX_DRUM,5.7,1.8)] +
               [cylinder(.95,1.8,radial(16,a,5.7)) for a in (0,MAX_DRUM)])
    return ring.cut(slot).removeSplitter()


def ratchet_shape():
    pts=[]
    for k in range(POCKETS):
        for phase,r in ((0,10.5),(.12,12.3),(.87,10.8)):
            a=(k+phase)*TAU/POCKETS
            pts.append(V(r*math.cos(a),r*math.sin(a),RATCHET_Z))
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,1.25)).cut(cylinder(3.15,2,V(0,0,RATCHET_Z-.2)))


def lower_outer():
    body=union([ellipsoid((0,0,8.5),(38.2,36.2,11.5)),
                ellipsoid((-21,-10,9),(18.8,22.0,10.4)),
                ellipsoid((19,4,10),(20.0,27,10.2)),
                ellipsoid((0,-34.7,6),(13.0,9.0,5.0))])
    return body.common(Part.makeBox(100,100,14.5,V(-50,-50,0)))


def body_shape():
    body=lower_outer()
    cavity=cylinder(32.0,16,V(0,0,2.7))
    idler=cylinder(6.3,4.4,V(0,-IDLER_R,2.7))
    # RNA passes in/out of this front cheek. The rest of the loop is outside.
    belt=annulus(RNA_R-1.2,RNA_OUT+.70,GEAR_Z-.3,GEAR_WIDTH+1.2)
    base_clear=annulus(RNA_OUT-.3,RNA_OUT+5.3,GEAR_Z+.20,GEAR_WIDTH-.40)
    # Sequential cuts avoid a coincident multi-tool union at the RNA port.
    for tool in (cavity,idler,belt,base_clear):
        body=body.cut(tool)
    # The outlet is a cleft, not a long nozzle. A separate keeper stays inside.
    cleft=Part.makeBox(80,10,9,V(MOUTH_X,STORE_R-5,6.7))
    body=body.cut(cleft)
    posts=[cylinder(3.0,11.8,V(x,y,2.7)) for x,y in ((-29,-18),(29,-18),(-23,26))]
    body=union([body]+posts+[cylinder(3.5,.5,V(0,-IDLER_R,2.7))])
    for x,y in ((-29,-18),(29,-18),(-23,26)):
        body=body.cut(cylinder(1.0,14,V(x,y,1)))
    body=body.cut(cylinder(1.1,8,V(0,-IDLER_R,2.5)))
    # The port Boolean can leave a sub-0.001 mm3 BSpline sliver. Never keep it
    # as a second printable body, and never discard a meaningful component.
    pieces=sorted(body.Solids,key=lambda s:s.Volume,reverse=True)
    if sum(s.Volume for s in pieces[1:])>.01:
        raise RuntimeError('Detached housing component requires redesign')
    return pieces[0].removeSplitter()


def lid_shape():
    lid=union([ellipsoid((0,-1,14.2),(35.4,33.8,4.4)),
               ellipsoid((-19,-9,14.4),(17,19,4.2))])
    lid=lid.common(Part.makeBox(90,90,3.0,V(-45,-45,14.8)))
    lid=lid.cut(cylinder(13.5,7,V(0,0,14.2)))
    lid=lid.cut(Part.makeBox(80,10,10,V(MOUTH_X,STORE_R-5,7)))
    for x,y in ((-29,-18),(29,-18),(-23,26)):
        lid=lid.cut(cylinder(1.15,5,V(x,y,14)))
    # Windows for the drive and holding leaves, and the release yoke.
    lid=lid.cut(Part.makeBox(37,10,6,V(0,-7,14)))
    lid=lid.cut(Part.makeBox(22,5,6,V(-19,10,14)))
    return lid.removeSplitter()


def cap_shape():
    outer=union([ellipsoid((0,-2,25.4),(25.6,22.4,8.4)),
                 ellipsoid((-13,-7,24.6),(15.5,15.2,7.4))])
    inner=union([ellipsoid((0,-2,22.9),(23.8,20.6,7.3)),cylinder(22,7.4,V(0,0,18))])
    cap=outer.cut(inner).common(Part.makeBox(80,80,18,V(-40,-40,19.0)))
    hub=annulus(3.5,5.1,18.9,10.5)
    bridge=Part.makeBox(4,25,2.0,V(-2,-24,26.0))
    carrier=Part.makeBox(15,3.2,1.0,V(4,-1.6,24.5))
    pin=cylinder(.75,8.0,V(17.7,0,16.7))
    cap=union([cap,hub,bridge,carrier,pin])
    cap=cap.cut(cylinder(3.3,20,V(0,0,17)))
    return cap.cut(cylinder(4.35,6,V(0,0,31.4))).removeSplitter()


def pawl_shape(driving=True):
    # Elastic leaves are deliberately unloaded: tooth preload is reported,
    # not silently counted as rigid-body clearance or feeding evidence.
    if driving:
        return union([Part.makeBox(.65,10.2,.65,V(10.675,0,RATCHET_Z+.28)),
                      Part.makeBox(7.6,1.0,.65,V(10.675,9.5,RATCHET_Z+.28)),
                      Part.makeBox(1.0,10.5,.65,V(17.2,0,RATCHET_Z+.28)),
                      cylinder(.52,.65,V(11.0,0,RATCHET_Z+.28)),
                      Part.makeBox(2.0,3.2,2.0,V(16.7,-1.6,RATCHET_Z-.3))]).cut(cylinder(.9,4,V(17.7,0,16.5)))
    return union([Part.makeBox(15.5,.65,.8,V(-15.5,10.675,RATCHET_Z+.25)),
                  cylinder(.52,.8,V(0,11.0,RATCHET_Z+.25)),
                  Part.makeBox(2.5,3,2.2,V(-17.3,10.5,RATCHET_Z-.4))]).cut(cylinder(.9,4,V(-16,12,16.4)))


def rna_shape():
    ring=gear(RNA_TEETH,internal=True)
    # A single continuous backbone; bases have free outer ends.
    backbone=annulus(RNA_OUT-.7,RNA_OUT+.35,GEAR_Z-.15,GEAR_WIDTH+.6)
    lip=annulus(RNA_R-1.0,RNA_OUT+.35,GEAR_Z+GEAR_WIDTH+.15,.5)
    return union([ring,backbone,lip])


def base_shape(i):
    a=i*TAU/RNA_TEETH
    direction=V(math.cos(a),math.sin(a),0)
    root=direction*(RNA_OUT+.05)+V(0,0,GEAR_Z+GEAR_WIDTH/2)
    length=RNA_BASE_LENGTHS[i%4]
    return union([cylinder(.48,length,root,direction),Part.makeSphere(.58,root+direction*length)])


def group(d,name,label):
    o=d.addObject('App::Part',name)
    o.Label=label
    return o


def feature(d,name,label,shape,parent,color):
    o=d.addObject('Part::Feature',name)
    o.Label,o.Shape=label,shape
    parent.addObject(o)
    o.addProperty('App::PropertyColor','DisplayColour','Presentation')
    o.DisplayColour=COLORS.get(color,color)
    return o


def chain_expressions(o,i):
    o.addProperty('App::PropertyFloat','PathDistance','Motion')
    o.setExpression('PathDistance',f'{HOME_S-i*BEAD_PITCH}+Motion.FeedDistance / 1 mm')
    s='PathDistance'
    a=f'({s}/{STORE_R} * 1 rad)'
    o.setExpression('Placement.Base.x',f'({s} < 0 ? {STORE_R}*sin({a}) : {s}) * 1 mm')
    o.setExpression('Placement.Base.y',f'({s} < 0 ? {STORE_R}*cos({a}) : {STORE_R}) * 1 mm')
    o.setExpression('Placement.Base.z',f'{BEAD_Z} mm')
    o.Placement.Rotation=App.Rotation(V(0,0,1),0)
    o.setExpression('Placement.Rotation.Angle',f'{s} < 0 ? -{a} : 0 deg')


def backbone(d,parent,i):
    o=d.addObject('Part::Cylinder',f'Wire{i:02}')
    parent.addObject(o)
    o.Label='Illustrative copper core segment — not a bending simulation'
    o.Radius=WIRE_R
    o.addProperty('App::PropertyColor','DisplayColour','Presentation')
    o.DisplayColour=COLORS['wire']
    for axis in 'xyz':
        o.addProperty('App::PropertyDistance','Delta'+axis.upper(),'Motion')
        o.setExpression('Delta'+axis.upper(),f'Bead{i+1:02}.Placement.Base.{axis}-Bead{i:02}.Placement.Base.{axis}')
        o.setExpression('Placement.Base.'+axis,f'Bead{i:02}.Placement.Base.{axis}')
    o.setExpression('Height','sqrt(DeltaX^2+DeltaY^2+DeltaZ^2)')
    o.setExpression('Placement.Rotation.Axis.x','-DeltaY/Height')
    o.setExpression('Placement.Rotation.Axis.y','DeltaX/Height')
    o.setExpression('Placement.Rotation.Axis.z','0')
    o.setExpression('Placement.Rotation.Angle','90 deg')


def build(save_path=None):
    if DOC_NAME in App.listDocuments():
        raise RuntimeError('Close '+DOC_NAME+' before rebuilding.')
    d=App.newDocument(DOC_NAME)
    d.Label='mRNA toy V5 — handheld ribosome, closed RNA, captive bead drum'
    d.Comment='Design prototype. Native prescribed motion; no physical, printing or fatigue qualification.'
    m=d.addObject('App::FeaturePython','Motion')
    m.Label='V5 controls — slide RNA or click; straighten and release before reverse'
    m.addProperty('App::PropertyFloatConstraint','BeadSteps','Play')
    m.BeadSteps=(0,0,EMIT,.025)
    m.addProperty('App::PropertyFloatConstraint','CapStroke','Play')
    m.CapStroke=(0,0,1,.025)
    m.addProperty('App::PropertyBool','ReverseRelease','Play')
    for name,kind,expr in [
        ('FeedDistance','App::PropertyLength',f'{BEAD_PITCH} mm * BeadSteps'),
        ('DrumDegrees','App::PropertyFloat',f'-{STEP_DEG} * BeadSteps'),
        ('RnaDegrees','App::PropertyFloat',f'-{SUN_TEETH/RNA_TEETH} * DrumDegrees'),
        ('IdlerDegrees','App::PropertyFloat',f'-{SUN_TEETH/IDLER_TEETH} * DrumDegrees'),
        ('BasesPassed','App::PropertyFloat','3 * BeadSteps'),
        ('CapDegrees','App::PropertyFloat',f'-{STEP_DEG} * CapStroke'),
        ('ReleaseLift','App::PropertyLength',f'ReverseRelease ? {RELEASE_LIFT} mm : 0 mm'),
    ]:
        m.addProperty(kind,name,'Coupled motion')
        m.setExpression(name,expr)
        m.setEditorMode(name,1)
    for name,value in [('BasesPerBead',3),('BeadCount',BEADS),('MaximumBeadSteps',EMIT),
                       ('RetainedBeads',BEADS-EMIT),('DrumPockets',POCKETS),
                       ('BeadPitch',BEAD_PITCH),('DrumPitchDiameter',2*STORE_R),
                       ('RnaBaseCount',RNA_TEETH),('RnaPitchDiameter',2*RNA_R)]:
        m.addProperty('App::PropertyFloat',name,'Dimensions (edit source to rebuild)')
        setattr(m,name,value)
        m.setEditorMode(name,1)
    m.addProperty('App::PropertyString','StudyLimits','Study')
    m.StudyLimits='Closed flexible RNA shown on its nominal circular path. Ratchet leaves unloaded. Reverse release is required. Force, flex, fatigue and printing need physical tests.'
    fixed=group(d,'Stationary','Larger fixed lower subunit and captive guides')
    rotor=group(d,'Rotor','Direct bead drum + 84-tooth sun + ratchet')
    rotor.Placement.Rotation=App.Rotation(V(0,0,1),0)
    rotor.setExpression('Placement.Rotation.Angle','Motion.DrumDegrees * 1 deg')
    rna=group(d,'RnaLoop','Closed 112-base RNA loop — flexible nominal path')
    rna.Placement.Rotation=App.Rotation(V(0,0,1),0)
    rna.setExpression('Placement.Rotation.Angle','Motion.RnaDegrees * 1 deg')
    idler=group(d,'Idler','Fixed-axis 14-tooth RNA idler')
    idler.Placement=App.Placement(V(0,-IDLER_R,0),App.Rotation(V(0,0,1),0))
    idler.setExpression('Placement.Rotation.Angle','Motion.IdlerDegrees * 1 deg')
    click=group(d,'Clicker','Smaller rocking upper subunit — one pocket per stroke')
    click.Placement.Rotation=App.Rotation(V(0,0,1),0)
    click.setExpression('Placement.Rotation.Angle','Motion.CapDegrees * 1 deg')
    chain=group(d,'Protein','26 lobed beads — connected chain, hand shaping only')
    print('V5: lower shell, keeper and positive travel stops',flush=True)
    feature(d,'LowerBody','Larger lower shell — shallow protein cleft',body_shape(),fixed,'body')
    feature(d,'LowerLid','Removable fixed lower-subunit lid',lid_shape(),fixed,'lid')
    feature(d,'BeadKeeper','Fixed outer keeper + transfer roof',keeper_shape(),fixed,'guide')
    feature(d,'StopRing','Closed arcuate travel slot — limits both ends',stop_shape(),fixed,'guide')
    axle=cylinder(3,30,V(0,0,1)).cut(cylinder(.85,4,V(0,0,28)))
    feature(d,'CentreAxle','Stationary Ø6 mm centre axle with retaining-screw pilot',axle,fixed,'gear')
    retainer=union([cylinder(4.0,.8,V(0,0,31.55)),cylinder(1.0,3.1,V(0,0,28.65))])
    feature(d,'CapRetainer','Recessed M2 screw/washer envelope retaining upper rocker',retainer,fixed,'gear')
    feature(d,'IdlerAxle','Stationary Ø2 mm idler axle',cylinder(1,5.5,V(0,-IDLER_R,2.7)),fixed,'gear')
    print('V5: sampled bead handoff, drum and actual involute gears',flush=True)
    feature(d,'BeadDrum','28-pocket direct storage drum — relieved tangent transfer',drum_shape(),rotor,'drum')
    sun=gear(SUN_TEETH).cut(cylinder(3.15,4,V(0,0,3)))
    feature(d,'SunGear','84-tooth common-shaft sun gear',sun,rotor,'gear')
    hub=annulus(3.15,4.5,5.1,13.6)
    feature(d,'DriveHub','Rigid shared drive sleeve — nominal clearance on fixed axle',hub,rotor,'gear')
    feature(d,'TravelPin','Ø1.5 mm moving travel-stop pin',cylinder(.75,1.9,radial(16,0,5.8)),rotor,'gear')
    feature(d,'Ratchet','28-tooth upper click ratchet',ratchet_shape(),rotor,'gear')
    feature(d,'RnaIdler','14-tooth idler — internal RNA / external sun meshes',gear(IDLER_TEETH).cut(cylinder(1.15,4,V(0,0,3))),idler,'gear')
    feature(d,'Rna','Closed flexible RNA backbone and internal drive teeth',rna_shape(),rna,'rna')
    for i in range(RNA_TEETH):
        color=[(.38,.75,.74),(.87,.67,.34),(.71,.66,.84),(.88,.55,.48)][i%4]
        feature(d,f'Base{i:03}',f'RNA base {i+1:03} — free end',base_shape(i),rna,color)
    print('V5: upper rocker and releaseable click leaves',flush=True)
    feature(d,'UpperLobe','Smaller upper shell — thumb rocker',cap_shape(),click,'cap')
    drive=feature(d,'DrivePawl','Driving leaf — unloaded flexure/preload study',pawl_shape(True),click,'pawl')
    hold=feature(d,'HoldPawl','Holding leaf — unloaded flexure/preload study',pawl_shape(False),fixed,'pawl')
    for o in (drive,hold):
        o.setExpression('Placement.Base.z','Motion.ReleaseLift')
    feature(d,'HoldingPawlGuide','Axial release guide for holding leaf',union([cylinder(2.3,1.4,V(-16,12,15.3)),cylinder(.75,8.3,V(-16,12,16.5))]),fixed,'gear')
    release=union([annulus(6.9,8.2,15.9,.9),
                   Part.makeBox(24.5,2.0,.9,V(7.5,-1,15.9)),
                   Part.makeBox(2.0,6,.9,V(-7,6.3,15.9)),
                   Part.makeBox(2.0,7.0,1.65,V(16.7,0,15.9)),
                   Part.makeBox(2,2.8,1.65,V(-7,10.5,15.9)),
                   cylinder(2.6,3.2,V(32,0,16.0))])
    button=feature(d,'ReleaseYoke','Lift-to-release yoke — clears both ratchet leaves',release,fixed,'pawl')
    button.setExpression('Placement.Base.z','Motion.ReleaseLift')
    # Torsion return spring space claim only; it returns the cap, not protein.
    spring=annulus(5.4,6.7,22.4,2.8)
    o=feature(d,'CapSpringEnvelope','Upper-cap return spring envelope — spring selection open',spring,fixed,'gear')
    o.addProperty('App::PropertyString','GeometryRole','Study')
    o.GeometryRole='SPACE_CLAIM_ONLY: not a manufactured coil or force-qualified spring'
    print('V5: lobed protein and native saved-path expressions',flush=True)
    for i in range(BEADS):
        kind=(0,1,2,1,0,2,2)[i%7]
        o=feature(d,f'Bead{i:02}',f'Amino-acid bead {i+1:02} — {BEAD_FAMILY[kind]}',bead_shape(kind).copy(),chain,'protein')
        o.addProperty('App::PropertyInteger','BeadVariant','Geometry')
        o.BeadVariant=kind
        chain_expressions(o,i)
    for i in range(BEADS-1):
        backbone(d,chain,i)
    d.recompute()
    bad=[o.Name for o in d.Objects if 'Invalid' in o.State]
    if bad:
        raise RuntimeError('Invalid expressions: '+str(bad))
    if App.GuiUp:
        present(d)
    destination=Path(save_path) if save_path else HERE/MODEL_FILE
    destination.parent.mkdir(parents=True,exist_ok=True)
    d.saveAs(str(destination))
    print('V5 saved: '+str(destination),flush=True)
    return d


def world(o):
    shape=o.Shape.copy()
    shape.Placement=o.getGlobalPlacement()
    return shape


def present(d,cutaway=False,drum_only=False,fit=True):
    import FreeCADGui as Gui
    for o in d.Objects:
        if hasattr(o,'DisplayColour'):
            o.ViewObject.ShapeColor=tuple(o.DisplayColour[:3])
            o.ViewObject.LineColor=(.16,.17,.19)
            o.ViewObject.DisplayMode='Flat Lines'
            o.ViewObject.LineWidth=.6
            o.ViewObject.Deviation=.12
            o.ViewObject.AngularDeflection=12
            o.ViewObject.Visibility=True
            o.ViewObject.Transparency=0
        if o.TypeId=='App::Part':
            o.ViewObject.Visibility=True
    for name in ('UpperLobe','LowerLid'):
        d.getObject(name).ViewObject.Visibility=not cutaway and not drum_only
    d.LowerBody.ViewObject.Visibility=not drum_only
    d.LowerBody.ViewObject.Transparency=82 if cutaway else 0
    d.BeadKeeper.ViewObject.Transparency=70 if cutaway or drum_only else 0
    d.CapSpringEnvelope.ViewObject.Visibility=cutaway and not drum_only
    if drum_only:
        allowed={'BeadDrum','BeadKeeper','TravelPin','StopRing'}
        for o in d.Objects:
            if hasattr(o,'DisplayColour') and o.Name not in allowed and not o.Name.startswith(('Bead0','Bead1','Bead2','Wire')):
                o.ViewObject.Visibility=False
    if fit:
        Gui.activeDocument().activeView().viewAxonometric()
        Gui.activeDocument().activeView().fitAll()


def validate(d,report_path=None):
    import validation_v5
    return validation_v5.run(d,report_path)


def open_controls(d):
    import FreeCADGui as Gui
    from PySide import QtCore,QtWidgets
    win=Gui.getMainWindow()
    old=win.findChild(QtWidgets.QDockWidget,'RibosomeV5Controls')
    if old:
        win.removeDockWidget(old)
        old.deleteLater()
    dock=QtWidgets.QDockWidget('V5 handheld ribosome — 3 RNA bases / 1 bead',win)
    dock.setObjectName('RibosomeV5Controls')
    box=QtWidgets.QWidget()
    layout=QtWidgets.QVBoxLayout(box)
    label=QtWidgets.QLabel()
    slider=QtWidgets.QSlider(QtCore.Qt.Horizontal)
    slider.setRange(0,EMIT*40)
    slider.setValue(round(d.Motion.BeadSteps*40))
    row=QtWidgets.QHBoxLayout()
    forward=QtWidgets.QPushButton('Click upper subunit')
    reverse=QtWidgets.QPushButton('Return one bead')
    home=QtWidgets.QPushButton('Reset view / home')
    cut=QtWidgets.QCheckBox('Open lower body')
    release=QtWidgets.QCheckBox('Release for reverse (straighten chain first)')
    for widget in (forward,reverse,home,cut,release):
        row.addWidget(widget)
    layout.addWidget(label)
    layout.addWidget(slider)
    layout.addLayout(row)
    timer=QtCore.QTimer(dock)
    timer.setInterval(30)
    animation={'frame':0,'start':0.0,'reverse':False}
    previous=[d.Motion.BeadSteps]
    view_state=[None]
    def refresh():
        target=slider.value()/40
        if target<previous[0] and not release.isChecked() and not timer.isActive():
            slider.blockSignals(True)
            slider.setValue(round(previous[0]*40))
            slider.blockSignals(False)
            target=previous[0]
        d.Motion.BeadSteps=target
        previous[0]=target
        d.Motion.ReverseRelease=release.isChecked()
        d.recompute()
        if view_state[0]!=cut.isChecked():
            present(d,cut.isChecked(),fit=False)
            view_state[0]=cut.isChecked()
        label.setText('Protein %.2f / %d steps   RNA %.2f bases   Drum %.1f°   Four beads retained at full travel' % (d.Motion.BeadSteps,EMIT,d.Motion.BasesPassed,-d.Motion.DrumDegrees))
    def frame():
        animation['frame']+=1
        f=min(1,animation['frame']/24)
        if animation['reverse']:
            value=animation['start']-f
            d.Motion.CapStroke=0
        else:
            value=animation['start']+min(1,2*f)
            d.Motion.CapStroke=2*f if f<.5 else 2*(1-f)
        slider.blockSignals(True)
        slider.setValue(round(max(0,min(EMIT,value))*40))
        slider.blockSignals(False)
        refresh()
        if f>=1:
            timer.stop()
            d.Motion.CapStroke=0
            d.recompute()
    def animate(back=False):
        if timer.isActive() or (back and not release.isChecked()):
            return
        start=d.Motion.BeadSteps
        if (back and start<1) or (not back and (start>EMIT-1 or release.isChecked())):
            return
        animation.update(frame=0,start=start,reverse=back)
        timer.start()
    def go_home():
        timer.stop()
        d.Motion.CapStroke=0
        previous[0]=0
        slider.setValue(0)
        release.setChecked(False)
        refresh()
    slider.valueChanged.connect(refresh)
    cut.toggled.connect(refresh)
    release.toggled.connect(refresh)
    forward.clicked.connect(lambda:animate(False))
    reverse.clicked.connect(lambda:animate(True))
    home.clicked.connect(go_home)
    timer.timeout.connect(frame)
    dock.setWidget(box)
    win.addDockWidget(QtCore.Qt.BottomDockWidgetArea,dock)
    dock.show()
    refresh()
    return dock
