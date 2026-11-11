"""V6 updated print: captive open/closed RNA, direct reverse and rest-disengaged cap input.

Millimetres. Native expressions preserve all rigid and nominal flexible poses.
TPU links and leaf deflections are prescribed kinematic geometry, not FEA.
Physical feeding, forces, clasp retention, fatigue and printing remain open.
"""
from pathlib import Path
from functools import lru_cache
import math
import FreeCAD as App
import Part
from fcgear import involute, fcgear
import rna_path as route
import printed_fasteners as pf

HERE=Path(__file__).resolve().parent
DOC_NAME='RibosomeV6UpdatedPrint'
MODEL_FILE='RibosomeV6UpdatedPrint.FCStd'
V=App.Vector
TAU=2*math.pi
BEAD_R,BEAD_PITCH,WIRE_R=2.2,6.0,.18
BEADS,EMIT,POCKETS=26,22,28
HOME_S,MOUTH_X=6.0,9.0
STORE_R=POCKETS*BEAD_PITCH/TAU
BEAD_Z=11.0
STEP_DEG=360/POCKETS
MAX_DRUM=EMIT*STEP_DEG
MODULE=.72
SUN_TEETH=84
GEAR_Z,GEAR_WIDTH=18.7,1.8
GEAR_PHASE=180/SUN_TEETH
RNA_Y,RNA_Z=-31.8,19.6
RNA_PITCH=route.PITCH
RNA_STEP=route.RNA_PER_STEP
RNA_MAX=route.TRAVEL
RNA_BASE_LENGTHS=(2.6,3.1,2.8,3.5)
RNA_LINKS=range(2,route.CELLS-1)
RNA_GUIDE_HALF=9.0
RNA_GROOVE_RADIUS=3.4
BODY_CAVITY_RADIUS=30.9
LID_COLUMN_RADIUS=3.1
CASE_MOUNTS=((-32.0,-14.0),(32.0,-14.0),(-23.0,26.0))
KEEPER_SEAT_Z,LID_SEAT_Z,GUARD_SEAT_Z=13.5,14.6,20.25
CASE_HEAD_Z,AXLE_TOP=21.3,33.55
# The shallower return crosses farther along the lower flank before passing
# underneath. Its straight drive entry remains at the same position and phase.
RNA_ROUTE_ANGLE=13.2
RNA_SIDE=math.cos(math.radians(RNA_ROUTE_ANGLE))
RNA_DROP=math.sin(math.radians(RNA_ROUTE_ANGLE))
PLANE_NORMAL=V(0,RNA_DROP,RNA_SIDE)
PLANE_DOWN=V(0,RNA_SIDE,-RNA_DROP)
FORK_INNER_Z,FORK_WIDTH=.85,.65
RATCHET_Z=24.4
ENTRY_DEG=6.0
CAP_ANGLE=ENTRY_DEG+STEP_DEG
PAWL_LIFT=2.0
CAM_R,CAM_BALL=22.0,.5
CAM_CENTRE_Z=24.1
CAP_STOP_ANGLE=-60.0
BEAD_FAMILY=('bilobed','offset','trilobed')
COLORS={
 'body':(.43,.35,.59),'lid':(.58,.49,.72),'cap':(.72,.64,.84),
 'rna':(.12,.57,.63),'drum':(.15,.48,.52),'gear':(.72,.76,.79),
 'guide':(.65,.69,.73),'protein':(.94,.56,.34),'wire':(.64,.39,.23),
 'pawl':(.86,.67,.30),
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
    original = Part.makeSphere(1).transformGeometry(matrix)
    # Nonuniformly transformed spheres contain internal C0 spline knots.
    # Boolean projection across those knots produced invalid curves on
    # surfaces even when isValid() returned True. Split EXACTLY at existing
    # knots before any Boolean; each patch retains the original rational
    # quadric, with no tessellation, fit or tolerance increase.
    faces=[]
    for face in original.Faces:
        surface=face.Surface
        us,vs=surface.getUKnots(),surface.getVKnots()
        for u0,u1 in zip(us,us[1:]):
            for v0,v1 in zip(vs,vs[1:]):
                patch=surface.copy();patch.segment(u0,u1,v0,v1)
                faces.append(patch.toShape())
    shell=Part.makeShell(faces);shell.sewShape()
    shape=Part.makeSolid(shell)
    if shape.Volume<0:shape.reverse()
    if not shape.isValid() or len(shape.Solids)!=1:
        raise RuntimeError('Invalid exact ellipsoid patch solid')
    shape.translate(V(*center))
    return shape


def ellipse_face(x,y,z,rx,ry):
    curve=Part.Ellipse(V(x,y,z),max(rx,ry),min(rx,ry))
    wire=Part.Wire([curve.toShape()])
    if ry>rx:wire.rotate(V(x,y,z),V(0,0,1),90)
    return Part.Face(wire)


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


def gear(teeth, z=GEAR_Z, width=GEAR_WIDTH):
    builder = fcgear.FCWireBuilder()
    involute.CreateExternalGear(builder, MODULE, teeth, 25, split=True)
    face = Part.Face(Part.Wire([e.toShape() for e in builder.wire]))
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
    return union(shapes).cut(cylinder(3.15-c,9,V(0,0,6)))


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
    for x,y in CASE_MOUNTS:
        angle=math.degrees(math.atan2(x,y))
        tab=union([sector(STORE_R+2.3,math.hypot(x,y)+1.5,angle-6,angle+6,13.5,1.1),
                   cylinder(3.75,1.1,V(x,y,13.5))])
        tab=tab.cut(cylinder(2.30,2,V(x,y,13)))
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


def polar(r,a,z=0):
    a=math.radians(a)
    return V(r*math.cos(a),r*math.sin(a),z)


def spring_leg(moving=False,radius=.3):
    a=polar(6.75,-120,29.9 if moving else 27.8)
    end_z=29.9+.3*(20-6.75)/(18-6.75) if moving else 27.8
    end=polar(20,-120,end_z);delta=end-a
    return cylinder(radius,delta.Length,a,delta/delta.Length)


def spring_socket(moving=False):
    z=29.9+.3*(15-6.75)/(18-6.75) if moving else 27.8
    a=polar(15,-120,z)
    end_z=29.9+.3*(21-6.75)/(18-6.75) if moving else 27.8
    delta=polar(21,-120,end_z)-a
    return cylinder(.4,delta.Length,a,delta/delta.Length)


def angular_sector(inner,outer,a,b,z,h):
    return sector(inner,outer,90-b,90-a,z,h)


def rna_point(s,closed=True):
    u,v,turn=route.closed(s) if closed else route.opened(s)
    return V(u,RNA_Y+RNA_SIDE*v,RNA_Z-RNA_DROP*v),turn


def rna_pose(material,feed=0,closed=True):
    u,v,turn=route.layout(material,feed,closed)
    return App.Placement(V(u,RNA_Y+RNA_SIDE*v,RNA_Z-RNA_DROP*v),
                         App.Rotation(PLANE_NORMAL,-math.degrees(turn)))


@lru_cache(maxsize=1)
def rna_link_shape():
    # 0.30 mm lap between adjacent nominal TPU cells keeps the represented
    # backbone connected through the bends. These cells are one strip.
    rail=Part.makeBox(RNA_PITCH+.30,1.32,2.3,V(-(RNA_PITCH+.30)/2,-.66,-1.15))
    alpha=math.radians(25)
    root=.9;tip=.72;half=RNA_PITCH/4-.06
    pts=[V(-half-root*math.tan(alpha),.66,-.9),
         V(half+root*math.tan(alpha),.66,-.9),
         V(half-tip*math.tan(alpha),2.28,-.9),
         V(-half+tip*math.tan(alpha),2.28,-.9)]
    tooth=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,1.8))
    return union([rail,tooth])


def rna_base_shape(i):
    length=RNA_BASE_LENGTHS[i%4]
    root=V(0,-.48,0)
    return union([cylinder(.42,length,root,V(0,-1,0)),
                  Part.makeSphere(.53,root+V(0,-length,0))])


def rna_expressions(o,material):
    o.addProperty('App::PropertyFloat','MaterialDistance','RNA kinematics')
    o.MaterialDistance=material
    o.setEditorMode('MaterialDistance',1)
    o.addProperty('App::PropertyFloat','PathCoordinate','RNA kinematics')
    o.setExpression('PathCoordinate',f'{route.JOIN_HOME+material:.16g}+Motion.RnaTravel / 1 mm')
    o.addProperty('App::PropertyFloat','GuideDistance','RNA kinematics')
    o.setExpression('GuideDistance',f'Motion.StrandClosed ? (PathCoordinate < {route.LENGTH:.16g} ? PathCoordinate : PathCoordinate-{route.LENGTH:.16g}) : PathCoordinate-{route.LENGTH:.16g}')
    for name,expression in zip(('CurveU','CurveV','Turn'),route.expressions()):
        o.addProperty('App::PropertyFloat',name,'RNA kinematics')
        o.setExpression(name,expression)
        o.setEditorMode(name,1)
    o.setExpression('Placement.Base.x','CurveU * 1 mm')
    o.setExpression('Placement.Base.y',f'({RNA_Y}+{RNA_SIDE:.16g}*CurveV) * 1 mm')
    o.setExpression('Placement.Base.z',f'({RNA_Z}-{RNA_DROP:.16g}*CurveV) * 1 mm')
    o.Placement.Rotation=App.Rotation(PLANE_NORMAL,0)
    # A zero-angle quaternion forgets its axis. Persist all three axis
    # components as expressions so curved RNA cells really follow the tilted
    # return plane after a native close/reopen and after crossing a straight.
    for axis,value in [('x',0),('y',RNA_DROP),('z',RNA_SIDE)]:
        o.setExpression('Placement.Rotation.Axis.'+axis,format(value,'.16g'))
    o.setExpression('Placement.Rotation.Angle','-Turn * 1 rad')


def clasp_shape(female=False):
    """TPU snap candidate. Connector shoulders also block the guide throats.

    Local X points opposite material travel. In the closed pose the receiver
    overlaps the other end's tongue in Z, with radial button clearance. The
    snap lip is an elastic candidate, not a force-qualified latch.
    """
    if female:
        root=Part.makeBox(4.6,3.2,3.8,V(-2.3,-1.6,-1.9))
        # Tongue enters from local +X, underneath a thin receiver roof.
        root=root.cut(Part.makeBox(3.9,2.45,1.35,V(-.6,-1.225,-1.05)))
        root=root.cut(cylinder(1.02,4,V(.7,0,-2)))
        return root.removeSplitter()
    root=Part.makeBox(4.6,3.2,3.8,V(-2.3,-1.6,-1.9))
    tongue=Part.makeBox(3.5,2.15,1.0,V(-5.5,-1.075,-.95))
    stem=cylinder(.8,2.3,V(-4.3,0,-.3))
    head=Part.makeCone(1.12,.9,.5,V(-4.3,0,1.9))
    # Tapered insertion nose; the receiver is peeled over the button to open.
    return union([root,tongue,stem,head])


@lru_cache(maxsize=4)
def return_clearance(radius=RNA_GROOVE_RADIUS):
    """Continuous groove bound for rail and travelling clasp, excluding bases.

    The free-ended bases face out of the body. Their separate offset sweep
    is checked by base_clearance(); carving their circumcircle on the inward
    side unnecessarily removed 1.05 mm of the groove's supporting material.
    """
    edges=[];bounds=(0,)+route.S+(route.LENGTH,)
    for j,(a,c) in enumerate(zip(bounds,bounds[1:])):
        p= rna_point(a)[0];q=rna_point(c)[0]
        edges.append(Part.Arc(p,rna_point((a+c)/2)[0],q).toShape()
                     if j in (1,3,5,7) else Part.makeLine(p,q))
    return round_sweep(edges,radius)


@lru_cache(maxsize=1)
def open_return_clearance(radius=RNA_GROOVE_RADIUS):
    """Bound both free tails through their complete nominal travel range."""
    t=route.TOP_HALF;q=route.QUARTER
    bounds=(-route.LENGTH,-t-q,-t,t,t+q,route.LENGTH)
    edges=[]
    for j,(a,c) in enumerate(zip(bounds,bounds[1:])):
        p=rna_point(a,False)[0];end=rna_point(c,False)[0]
        edges.append(Part.Arc(p,rna_point((a+c)/2,False)[0],end).toShape()
                     if j in (1,3) else Part.makeLine(p,end))
    return round_sweep(edges,radius)


def round_sweep(edges,radius):
    """Exact circular sweep using analytic cylinders and quarter tori.

    Generic makePipeShell over this closed wire creates spline surfaces with
    poorly conditioned coincident cuts in this runtime. The route consists
    exclusively of lines and quarter circles, so no approximation is needed.
    """
    pieces=[]
    for edge in edges:
        p,q=edge.Vertexes[0].Point,edge.Vertexes[-1].Point
        if isinstance(edge.Curve,Part.Circle):
            centre=edge.Curve.Center
            a,c=p-centre,q-centre
            axis=a.cross(c);axis.normalize();a.normalize()
            turn=math.degrees(math.acos(max(-1,min(1,a.dot(c/c.Length)))))
            torus=Part.makeTorus(edge.Curve.Radius,radius,V(),V(0,0,1),-180,180,turn)
            torus.Placement=App.Placement(centre,App.Rotation(a,axis.cross(a),axis,'ZXY'))
            pieces.append(torus)
        else:
            delta=q-p
            pieces.append(cylinder(radius,delta.Length,p,delta/delta.Length))
    result=union(pieces)
    if not result.isValid() or len(result.Solids)!=1:
        raise RuntimeError('Invalid analytic round route sweep')
    return result


@lru_cache(maxsize=2)
def base_clearance(closed=True):
    """Continuous 3D bound of every base orientation on either nominal route.

    Base centreline offsets span .48 to 3.98 mm along rotated local -Y.
    A tube centred at 2.23 mm with radius 1.75+.53=2.28 mm contains every
    cylinder and head. Offset arcs remain circular and coplanar because the
    route and the saved rotations share PLANE_NORMAL. No phase is skipped.
    """
    rho=(.48+.48+max(RNA_BASE_LENGTHS))/2
    radius=max(RNA_BASE_LENGTHS)/2+.53
    def point(s):
        p,turn=rna_point(s,closed)
        return p+App.Rotation(PLANE_NORMAL,-math.degrees(turn)).multVec(V(0,-rho,0))
    if closed:
        bounds=(0,)+route.S+(route.LENGTH,);arcs=(1,3,5,7)
    else:
        t=route.TOP_HALF;q=route.QUARTER
        bounds=(-route.LENGTH,-t-q,-t,t,t+q,route.LENGTH);arcs=(1,3)
    edges=[]
    for j,(a,c) in enumerate(zip(bounds,bounds[1:])):
        edges.append(Part.Arc(point(a),point((a+c)/2),point(c)).toShape()
                     if j in arcs else Part.makeLine(point(a),point(c)))
    return round_sweep(edges,radius)


def shell_ellipsoid(center,radii):
    """Ruled organic skin with closed, non-self-intersecting surface spans.

    Six-degree latitude spans retain the same ellipsoidal cross-sections.
    Their chord error is bounded by max(radii)*(1-cos(3 degrees)); adding
    the 0.001-relative polar cap gives a conservative 0.067 mm skin bound.
    This approximation is confined to the organic skin, never drive contacts.
    """
    wires=[]
    for j in range(31):
        angle=-math.pi/2+math.pi*j/30
        radius=max(.001,math.cos(angle))
        z=center[2]+radii[2]*math.sin(angle)
        rx,ry=radii[0]*radius,radii[1]*radius
        curve=Part.Ellipse(V(center[0],center[1],z),max(rx,ry),min(rx,ry))
        # Keep four exact quadrant edges so each ruled span has explicit
        # seams instead of one surface wrapping the entire closed profile.
        wire=Part.Wire([curve.toShape(k*math.pi/2,(k+1)*math.pi/2) for k in range(4)])
        if ry>rx:wire.rotate(V(center[0],center[1],z),V(0,0,1),90)
        wires.append(wire)
    return Part.makeLoft(wires,True,True)


def lower_outer():
    shell=union([ellipsoid((0,0,8.5),(38.2,36.2,11.5)),
        ellipsoid((-21,-10,9),(18.8,22,10.4)),
        ellipsoid((19,4,10),(20,27,10.2)),
        ellipsoid((0,-34.7,6),(13,9,5))])
    shell=shell.common(Part.makeBox(100,100,14.5,V(-50,-50,0)))
    # A flatter palm dome replaces the tall swell and separate bottom rails.
    # The open return groove is subtracted from this continuous surface.
    palm=union([ellipsoid((-2,-3,-.8),(33,29,7.3)),
                ellipsoid((-15,-8,-.2),(22,24,6.5))])
    return union([shell,palm])


def body_shape():
    # Keep material between the higher far-flank groove and the bead store.
    # Keeper outer radius is 30.538 mm, retaining >.36 mm running clearance.
    body=lower_outer().cut(cylinder(BODY_CAVITY_RADIUS,16,V(0,0,2.7)))
    # The travel slot is integral with the fixed shell, with two supported
    # rims below the pin path. It cannot rotate as a loose ring in the cavity.
    pedestals=[annulus(13.9,14.9,2.65,3.25),annulus(17.1,18.1,2.65,3.25)]
    body=union([body,stop_shape()]+pedestals)
    body=body.cut(Part.makeBox(80,10,9,V(MOUTH_X,STORE_R-5,6.7)))
    # The tangent keeper cheek extends behind the visible outlet and beyond
    # the circular storage bore. Give that cheek a pocket down to its actual
    # insertion plane; the outlet-only cut left 10.78 mm3 of rigid overlap.
    body=body.cut(Part.makeBox(13.4,8.0,6.4,V(-4.2,STORE_R-4,8.4)))
    posts=[cylinder(3.9,KEEPER_SEAT_Z-2.7,V(x,y,2.7)) for x,y in CASE_MOUNTS]
    body=union([body]+posts)
    for x,y in CASE_MOUNTS:
        # Flat, positive keeper seat. The pocket clears the sides of its
        # mounting pad, without a second, offset screw pattern through it.
        angle=math.degrees(math.atan2(x,y));radius=math.hypot(x,y)
        pocket=union([sector(STORE_R+2.1,radius+2.2,angle-7,angle+7,KEEPER_SEAT_Z,3),
                      cylinder(3.8,3,V(x,y,KEEPER_SEAT_Z))])
        body=body.cut(pocket)
        # Bottom-loaded keyed nut stops against a substantial shoulder below
        # the RNA groove. The upper post retains a plain screw passage.
        pocket=pf.keyed_outline(-10,22.0,.15);pocket.translate(V(x,y,0))
        body=body.cut(pocket).cut(cylinder(2.30,1.7,V(x,y,12.0)))
    # The spindle is integral with this floor, represented as a separate
    # feature only for inspection. Do not hollow out its supporting root.
    body=body.cut(cylinder(3.15,35,V(0,0,2.9)))
    body=body.cut(return_clearance())
    pieces=sorted(body.Solids,key=lambda s:s.Volume,reverse=True)
    if sum(s.Volume for s in pieces[1:])>.01:
        raise RuntimeError('V6 updated print housing has a detached meaningful component')
    # Keep the exact patch boundaries. The earlier unsplit representation
    # became unorientable under final seam simplification in this runtime.
    return pieces[0]


def lid_shape():
    # A proper load-bearing plate with analytic elliptical edges. Thin slices
    # of overlapping spline ellipsoids gave unreliable Boolean sections at
    # the screw columns even when the basic validity flag was true.
    outline=ellipse_face(0,-1,14.8,35.4,33.8).fuse(ellipse_face(-19,-9,14.8,17,19))
    lid=outline.extrude(V(0,0,2.2))
    # This opening passes the lower rotor's thrust flange during assembly.
    lid=lid.cut(cylinder(6.2,5,V(0,0,14)))
    lid=lid.cut(Part.makeBox(80,10,10,V(MOUTH_X,STORE_R-5,7)))
    # Relieve the organic skin before adding the analytically simple screw
    # columns. Keeping the routing Boolean off those columns also makes
    # subsequent local section/intersection operations more robust in OCC.
    outside_peak=return_clearance().cut(Part.makeBox(20,120,100,V(-10,-60,-50)))
    lid=lid.cut(outside_peak)
    # One coaxial stack per screw: keeper, lid spacer and cover boss.
    # These columns lie outside the complete gear rotation envelope.
    # The previous 3.4 mm margin clipped the travelling rack. A 3.1 mm
    # column retains the complete specified 3.1 mm-radius bearing seat.
    # Only the two front columns approach the travelling rack. The rear
    # column can retain the original 3.4 mm radius and its full local section.
    supports=[cylinder(LID_COLUMN_RADIUS if i<2 else 3.4,
        GUARD_SEAT_Z-LID_SEAT_Z,V(x,y,LID_SEAT_Z)) for i,(x,y) in enumerate(CASE_MOUNTS)]
    lid=union([lid]+supports)
    # Lower half of the central mesh keeper: the flexible rack cannot bow
    # away from the gear while the user pushes an open tail backward.
    shoe=mesh_shoe(False)
    lid=union([lid,shoe])
    for x,y in CASE_MOUNTS:
        lid=lid.cut(cylinder(2.30,9,V(x,y,14)))
    return lid.removeSplitter()


def mesh_shoe(upper=False):
    """Soft outer nose around a precise, straight central capture throat."""
    if upper:
        outer=ellipsoid((0,RNA_Y+2.0,21.0),(9.0,5.5,1.4))
        # The front lip reaches down beside the backbone. The rear roof
        # clears both the rail and gear; only its outside is organically round.
        outer=outer.common(Part.makeBox(24,20,5,V(-12,RNA_Y-8,20.25)))
        clearance=Part.makeBox(24,15,6,V(-12,RNA_Y-1,15.05))
    else:
        outer=ellipsoid((0,RNA_Y+2.3,17.2),(9.3,7.4,2.3))
        outer=outer.common(Part.makeBox(24,22,5,V(-12,RNA_Y-9,13.95)))
        clearance=Part.makeBox(24,17,8,V(-12,RNA_Y-1,18.15))
    return outer.cut(clearance).removeSplitter()


def socket_cut(radius,z,height,centre=V()):
    pts=[centre+V(radius*math.cos(k*TAU/6),radius*math.sin(k*TAU/6),z) for k in range(6)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,height))


def case_screw_shape(x,y):
    screw=pf.case_pair()[0].copy();screw.translate(V(x,y,0));return screw


def axle_shape():
    return pf.spindle_pair()[0].copy()


def cap_screw_shape():
    return pf.spindle_pair()[1].copy()


def keyed_profile(radius=4.5,flat=4.0,z=18.65,height=3):
    return cylinder(radius,height,V(0,0,z)).common(Part.makeBox(radius+flat,2*radius,height,V(-radius,-radius,z)))


def drive_hub_shape():
    # Lower printed rotor: hollow spindle, thrust flange, and positive D key.
    # The lid slides over the flange before the keyed upper rotor is fitted.
    shaft=annulus(3.15,4.5,7.4,10.75)
    flange=annulus(3.15,6,18.1,.6)
    key=keyed_profile(height=2.8).cut(cylinder(3.15,4,V(0,0,18.5)))
    return union([shaft,flange,key])


@lru_cache(maxsize=1)
def cam_shape():
    """Fixed conjugate cam under a spherical follower; clear cap-guide pin.

    The lower envelope of roller positions gives a conservative support
    surface, rather than placing a flat roller through a steep ramp.
    """
    lo,hi=-STEP_DEG-3,ENTRY_DEG+4
    samples=[]
    for j in range(1001):
        a=lo+(hi-lo)*j/1000
        lift=PAWL_LIFT*max(0,min(1,a/ENTRY_DEG))
        samples.append((math.radians(a),CAM_CENTRE_Z+lift))
    wires=[]
    for j in range(145):
        a=lo+(hi-lo)*j/144;rad=math.radians(a)
        candidates=[]
        for t,z in samples:
            distance=2*CAM_R*math.sin((rad-t)/2)
            if abs(distance)<=CAM_BALL:
                candidates.append(z-math.sqrt(CAM_BALL**2-distance**2))
        height=min(candidates)-.025
        pts=[polar(CAM_R-.8,a,21.3),polar(CAM_R+.8,a,21.3),
             polar(CAM_R+.8,a,height),polar(CAM_R-.8,a,height)]
        wires.append(Part.makePolygon(pts+[pts[0]]))
    # Ruled spans stay inside the sampled roller envelope. A global smooth
    # loft can overshoot the height law between sections on this short ramp.
    return Part.makeLoft(wires,True,True).removeSplitter()


def guard_shape():
    # The cover must pass the 14.4 mm click wheel during vertical assembly.
    roof=annulus(15,32.5,20.85,.85)
    wall=annulus(31.35,32.5,17.9,3.8)
    # Straight RNA is visible at the front seam, with gear access behind it.
    wall=wall.cut(Part.makeBox(72,9,4,V(-36,-38,17.8)))
    roof=roof.cut(Part.makeBox(72,9,4,V(-36,-38,18.4)))
    # Rear edge of the RNA throat is beyond the tip sweep of the spur gear.
    bosses=[cylinder(3.4,21.7-GUARD_SEAT_Z,V(x,y,GUARD_SEAT_Z)) for x,y in CASE_MOUNTS]
    post=cylinder(.85,8.5,polar(24,CAP_STOP_ANGLE,21.7))
    # The click leaf has an integral root, not an unsupported fastening hole.
    detent_mount=union([cylinder(2.4,.4,V(12,20,21.7)),
                        cylinder(2.0,.65,V(12,20,21.7))])
    upper_shoe=mesh_shoe(True)
    guard=union([roof,wall,cam_shape(),post,detent_mount,upper_shoe]+bosses)
    for x,y in CASE_MOUNTS:
        guard=guard.cut(cylinder(3.55,GUARD_SEAT_Z-14.65,V(x,y,14.65)))
        guard=guard.cut(cylinder(2.30,7,V(x,y,18)))
        guard=guard.cut(Part.makeCone(1.8,3.0,1.5,V(x,y,20.0)))
        guard=guard.cut(cylinder(3.05,.5,V(x,y,21.5)))
    return guard.removeSplitter()


def feed_ratchet_shape():
    # Axial face ramps let a rigid, spring-biased pawl rise on return. The
    # radial step faces transmit feed torque without a buckling drive leaf.
    wires=[]
    for j in range(9):
        a=STEP_DEG*j/8;top=RATCHET_Z+1.25*j/8
        pts=[polar(8,a,23.8),polar(12.3,a,23.8),
             polar(12.3,a,top),polar(8,a,top)]
        wires.append(Part.makePolygon(pts+[pts[0]]))
    tooth=Part.makeLoft(wires,True,False)
    copies=[]
    for k in range(POCKETS):
        s=tooth.copy();s.rotate(V(),V(0,0,1),k*STEP_DEG);copies.append(s)
    return union(copies+[annulus(5.7,8.3,23.8,.6)])


def detent_wheel_shape():
    pts=[]
    for j in range(POCKETS*32):
        a=j*TAU/(POCKETS*32)
        r=14.1-.3*math.cos(POCKETS*a)
        pts.append(V(r*math.cos(a),r*math.sin(a),22.15))
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,1.1)).cut(cylinder(5.7,2,V(0,0,22)))


def cap_shape():
    outer=union([shell_ellipsoid((0,-6,27.7),(28,25,10.1)),
                 shell_ellipsoid((-10,14,31),(19,17,9.2)),
                 shell_ellipsoid((18,-8,26.8),(14,18,7))])
    inner=union([shell_ellipsoid((0,-6,25.4),(25.8,22.8,8.8)),
                 shell_ellipsoid((-10,14,28.7),(16.8,14.8,8)),
                 shell_ellipsoid((18,-8,24.5),(11.8,15.8,5.8)),
                 cylinder(28,8.7,V(0,0,20))])
    shell=outer.cut(inner).common(Part.makeBox(90,90,25,V(-45,-45,21)))
    shell=shell.cut(cylinder(1.75,4.9,polar(17.7,ENTRY_DEG,26.1)))
    shell=shell.cut(angular_sector(22.8,25.2,CAP_STOP_ANGLE-5,
                  CAP_STOP_ANGLE+CAP_ANGLE+5,21.7,8.8))
    hub=annulus(3.5,5.1,21.9,11.5)
    bridge=Part.makeBox(4,28.5,2,V(-2,-27.5,30.4))
    carrier=Part.makeBox(16,3.2,1,V(3,-1.6,31))
    carrier.rotate(V(),V(0,0,1),ENTRY_DEG)
    carrier=union([carrier,cylinder(2,1,polar(17.7,ENTRY_DEG,31))])
    pin=cylinder(.75,9.5,polar(17.7,ENTRY_DEG,21.9))
    # Closed arcuate slot bounds the cap independently of UI limits.
    tab=angular_sector(22,28,CAP_STOP_ANGLE-4,
                       CAP_STOP_ANGLE+CAP_ANGLE+4,28.2,1.6)
    slot=union([angular_sector(22.9,25.1,CAP_STOP_ANGLE,
        CAP_STOP_ANGLE+CAP_ANGLE,28,2)]+[cylinder(1.1,2,polar(24,a,28))
        for a in (CAP_STOP_ANGLE,CAP_STOP_ANGLE+CAP_ANGLE)])
    tab=tab.cut(slot)
    mid=CAP_STOP_ANGLE+CAP_ANGLE/2
    spoke=angular_sector(4.5,27.5,mid-2,mid+2,30.7,1.5)
    column=cylinder(1.1,3.8,polar(27,mid,28.2))
    from stock_springs import cap_upper_support,bias_clearance
    cap=union([shell,hub,bridge,carrier,pin,tab,spoke,column,cap_upper_support()])
    cap=cap.cut(cylinder(3.3,35,V(0,0,20)))
    return cap.cut(cylinder(4.35,20,V(0,0,33.4))).cut(bias_clearance()).removeSplitter()


def drive_carrier_shape():
    boss=Part.makeBox(4.2,4.2,2.2,V(15.6,-2.1,24.1))
    parts=[boss,Part.makeBox(7.3,2.1,1.3,V(12.5,0,25.0)),
           Part.makeBox(5.0,.85,1.3,V(18,-.5,25.0)),drive_tip_shape(),
           Part.makeSphere(CAM_BALL,V(CAM_R,0,CAM_CENTRE_Z)),
           # Preserve the conjugate 1 mm ball; widen its neck above contact.
           cylinder(.40,1.4,V(CAM_R,0,CAM_CENTRE_Z+.30))]
    return union(parts).cut(cylinder(.95,5,V(17.7,0,23.8))).removeSplitter()


def drive_tip_shape():
    return angular_sector(11.05,13.6,0,3,24.8,1.5)


def flexure_segments(d,parent,prefix,x0,y0,length,z,expression,forward=True,thickness=.65,height=.65):
    """Nominal bent leaf as connected rectangular chords, not a stress solve."""
    count=8
    for j in range(count):
        a,b=j/count,(j+1)/count
        # Free tip at t=0; the anchor stays fixed at t=1.
        ya=y0+(length*a if forward else -length*a)
        yb=y0+(length*b if forward else -length*b)
        fa,fb=1-1.5*a+.5*a**3,1-1.5*b+.5*b**3
        o=d.addObject('Part::Box',prefix+str(j));parent.addObject(o)
        o.Width=thickness;o.Height=height
        o.Label='Prescribed flexible leaf chord — force/fatigue unqualified'
        o.addProperty('App::PropertyColor','DisplayColour','Presentation');o.DisplayColour=COLORS['pawl']
        for name,value in [('DeltaX',f'({fb-fa:.16g})*({expression})'),('DeltaY',str(yb-ya))]:
            o.addProperty('App::PropertyFloat',name,'Kinematics');o.setExpression(name,value)
        o.setExpression('Length','sqrt(DeltaX^2+DeltaY^2) * 1 mm + .15 mm')
        o.setExpression('Placement.Base.x',f'({x0}+{fa:.16g}*({expression})) * 1 mm')
        o.Placement.Base.y=ya;o.Placement.Base.z=z
        o.Placement.Rotation=App.Rotation(V(0,0,1),0)
        o.setExpression('Placement.Rotation.Angle','atan2(DeltaY;DeltaX)')


def detent_expression():
    # Envelope of the actual roller against the rounded index profile. Merely
    # adding the roller radius to the profile at its centre would intersect
    # the steeper flanks. The .04 mm offset bounds interpolation and facets.
    terms=[]
    for j in range(25):
        a=-.035+.07*j/24
        radius=f'(14.1-.3*cos(360 deg*EffectiveSteps+{28*a:.16g} rad))'
        terms.append(f'({radius}*{math.cos(a):.16g}+sqrt(.3025-({radius}*{math.sin(a):.16g})^2))')
    return '(max('+','.join(terms)+')+.04-14.1) * 1 mm'


def motion(d):
    m=d.addObject('App::FeaturePython','Motion')
    m.Label='V6 updated print — direct reverse RNA, open/closed strand and upper-lobe input'
    for name,val,lo,hi in [('BeadSteps',0,0,EMIT),('CapStroke',0,0,1)]:
        m.addProperty('App::PropertyFloatConstraint',name,'Play')
        setattr(m,name,(val,lo,hi,.025))
    m.addProperty('App::PropertyBool','StrandClosed','Play');m.StrandClosed=True
    m.addProperty('App::PropertyBool','CapReturning','Animation')
    expressions=[
        ('RequestedCapAngle','App::PropertyFloat',f'{CAP_ANGLE:.16g}*CapStroke'),
        ('RequestedAdvance','App::PropertyFloat',f'max(0,(RequestedCapAngle-{ENTRY_DEG})/{STEP_DEG:.16g})'),
        ('AvailableAdvance','App::PropertyFloat',f'min(1,max(0,{EMIT}-BeadSteps))'),
        ('CapAngle','App::PropertyFloat',f'CapReturning ? RequestedCapAngle : min(RequestedCapAngle,{ENTRY_DEG}+{STEP_DEG:.16g}*AvailableAdvance)'),
        ('EffectiveSteps','App::PropertyFloat',f'CapReturning ? BeadSteps : min({EMIT},BeadSteps+RequestedAdvance)'),
        ('FeedDistance','App::PropertyLength',f'{BEAD_PITCH} mm*EffectiveSteps'),
        ('RnaTravel','App::PropertyLength',f'{RNA_STEP:.16g} mm*EffectiveSteps'),
        ('DrumDegrees','App::PropertyFloat',f'-{STEP_DEG:.16g}*EffectiveSteps'),
        ('BasesPassed','App::PropertyFloat','3*EffectiveSteps'),
        ('CamLift','App::PropertyLength',f'{PAWL_LIFT} mm*max(0,min(1,({ENTRY_DEG}-CapAngle)/{ENTRY_DEG}))'),
        ('ReturnDistance','App::PropertyFloat',f'{CAP_ANGLE:.16g}-CapAngle'),
        ('ReturnPhase','App::PropertyFloat',f'ReturnDistance >= {STEP_DEG:.16g} ? ReturnDistance-{STEP_DEG:.16g} : ReturnDistance'),
        ('CoastLift','App::PropertyLength',f'CapReturning ? max(0,min(1.25,1.25*(ReturnPhase+3)/{STEP_DEG:.16g})-.36) * 1 mm : 0 mm'),
        ('PawlLift','App::PropertyLength','max(CamLift;CoastLift)'),
        ('DetentFlex','App::PropertyLength',detent_expression()),
    ]
    for name,kind,expr in expressions:
        m.addProperty(kind,name,'Coupled motion');m.setExpression(name,expr.replace(',',';'));m.setEditorMode(name,1)
    for name,val in [('BasesPerBead',3),('MaximumBeadSteps',EMIT),('BeadCount',BEADS),
        ('RetainedBeads',4),('RnaPitch',RNA_PITCH),('RnaMaximumTravel',RNA_MAX),
        ('RnaLoopLength',route.LENGTH),('ClaspArcReserve',route.JOIN_HOME-RNA_GUIDE_HALF-5)]:
        m.addProperty('App::PropertyFloat',name,'Dimensions');setattr(m,name,val);m.setEditorMode(name,1)
    m.addProperty('App::PropertyString','StudyLimits','Study')
    m.StudyLimits='Nominal TPU layouts and prescribed elastic poses. Spring solids and seats are candidate hardware geometry; forces are unqualified. Reverse RNA directly, after straightening the protein. No physical, print, snap-force or fatigue qualification.'
    return m


def build(save_path=None):
    if DOC_NAME in App.listDocuments(): raise RuntimeError('Close '+DOC_NAME+' before rebuilding.')
    d=App.newDocument(DOC_NAME)
    d.Label='mRNA toy V6 updated print — captive open/closed RNA; direct mechanical reverse'
    d.Comment='CAD prototype. Nominal flexible poses, not physical operation or printing qualification.'
    motion(d)
    fixed=group(d,'Stationary','Flattened palm body, central RNA capture and aligned screw stack')
    rotor=group(d,'Rotor','Two keyed rotor parts — shared bead drum and indexed RNA drive')
    rotor.Placement.Rotation=App.Rotation(V(0,0,1),0)
    rotor.setExpression('Placement.Rotation.Angle','Motion.DrumDegrees * 1 deg')
    rna=group(d,'RnaStrand','One TPU-candidate strip — captive open ends or joined external loop')
    click=group(d,'Clicker','Upper subunit — disengaged at rest, one bead per completed stroke')
    click.Placement.Rotation=App.Rotation(V(0,0,1),0)
    click.setExpression('Placement.Rotation.Angle','-Motion.CapAngle * 1 deg')
    drive=group(d,'PawlAssembly','Cam-lifted rigid input — face ramps lift it on return')
    click.addObject(drive)
    drive.Placement.Rotation=App.Rotation(V(0,0,1),ENTRY_DEG)
    drive.setExpression('Placement.Base.z','Motion.PawlLift')
    detent=group(d,'ClickDetent','Symmetric click leaf — freely reversible nominal deflection')
    fixed.addObject(detent);detent.Placement.Rotation=App.Rotation(V(0,0,1),90)
    chain=group(d,'Protein','26 connected lobed protein beads — manual shaping')
    print('V6 updated print: compact shoulder route, central RNA capture and aligned fastener seats',flush=True)
    for name,label,shape,color in [
        ('LowerBody','Flattened palm dome — shallow open RNA return groove',body_shape(),'body'),
        ('LowerLid','Lower shell lid and gear-cover mounts',lid_shape(),'lid'),
        ('GearGuard','Covered drive, short central RNA throat and fixed lift cam',guard_shape(),'lid'),
        ('BeadKeeper','Fixed bead keeper and tangent transfer roof',keeper_shape(),'guide')]:
        feature(d,name,label,shape,fixed,color)
    feature(d,'CentreAxle','Integral smooth spindle and coarse threaded extension',axle_shape(),fixed,'body')
    feature(d,'CapRetainer','Printed closed spindle cap — positive internal shoulder stop',cap_screw_shape(),fixed,'gear')
    feature(d,'CapWasher','Integral printed retaining flange — fuse with spindle cap, 0.25 mm endplay',
        pf.spindle_pair()[2].copy(),fixed,'gear')
    for i,(x,y) in enumerate(CASE_MOUNTS):
        feature(d,f'HousingScrew{i:02}','Printed 4 mm coarse screw — 1.2 mm pitch, recessed slotted head',
                case_screw_shape(x,y),fixed,'gear')
        nut=pf.case_pair()[1].copy();nut.translate(V(x,y,0))
        feature(d,f'HousingNut{i:02}','Replaceable printed keyed nut — load through underside access',nut,fixed,'gear')
    print('V6 updated print: retained 28-pocket bead handoff and direct 84-tooth rack drive',flush=True)
    feature(d,'BeadDrum','Direct 28-pocket storage drum — tangent-relieved forks',drum_shape(),rotor,'drum')
    sun=gear(SUN_TEETH)
    sun.rotate(V(),V(0,0,1),GEAR_PHASE)
    sun=sun.cut(keyed_profile(4.62,4.12,18.65,2))
    feature(d,'RnaDriveGear','84-tooth RNA rack gear — three bases per bead',sun,rotor,'gear')
    feature(d,'DriveHub','Lower rotor D-key spindle and thrust flange — lid installs before upper rotor',drive_hub_shape(),rotor,'drum')
    feature(d,'IndexSleeve','Concentric input carrier outside the cap bearing',annulus(5.7,8,20,5.65),rotor,'gear')
    feature(d,'IndexWheel','28 symmetric rounded click notches — reversible',detent_wheel_shape(),rotor,'gear')
    feature(d,'FeedRatchet','Upper-input-only drive faces — idle input lifts clear',feed_ratchet_shape(),rotor,'gear')
    feature(d,'TravelPin','Positive shared drum travel-stop pin',cylinder(.75,1.9,radial(16,0,5.8)),rotor,'gear')
    print('V6 updated print: native open/closed RNA cells and reusable end-stop clasp',flush=True)
    colors=[(.38,.75,.74),(.87,.67,.34),(.71,.66,.84),(.88,.55,.48)]
    for i in RNA_LINKS:
        o=feature(d,f'RnaLink{i:03}',f'TPU backbone cell {i:03} + drive tooth',rna_link_shape().copy(),rna,'rna')
        rna_expressions(o,i*RNA_PITCH)
        o=feature(d,f'Base{i:03}',f'Free-ended RNA base {i:03}',rna_base_shape(i),rna,colors[i%4])
        rna_expressions(o,i*RNA_PITCH)
    for name,female,material,offset in [('ClaspReceiver',True,2.5,-2.5),('ClaspButton',False,route.LENGTH-2.5,2.5)]:
        o=feature(d,name,'Reusable clasp half and captive strand end stop',clasp_shape(female),rna,'rna')
        rna_expressions(o,material)
        # The mated halves share one rigid frame through bends; open ends
        # follow their own free-tail frames. Their roots overlap the TPU rail.
        o.setExpression('PathCoordinate',f'{route.JOIN_HOME:.16g}+(Motion.StrandClosed ? 0 : {material:.16g})+Motion.RnaTravel / 1 mm')
        o.setExpression('Placement.Base.x',f'(CurveU+(Motion.StrandClosed ? {offset}*cos(Turn * 1 rad) : 0)) * 1 mm')
        o.setExpression('Placement.Base.y',f'({RNA_Y}+{RNA_SIDE:.16g}*CurveV-(Motion.StrandClosed ? {RNA_SIDE*offset:.16g}*sin(Turn * 1 rad) : 0)) * 1 mm')
        o.setExpression('Placement.Base.z',f'({RNA_Z}-{RNA_DROP:.16g}*CurveV+(Motion.StrandClosed ? {RNA_DROP*offset:.16g}*sin(Turn * 1 rad) : 0)) * 1 mm')
    print('V6 updated print: rest-disengaged cap input and bidirectional detent',flush=True)
    feature(d,'UpperLobe','Full asymmetric upper shell — one feed step per stroke',cap_shape(),click,'cap')
    feature(d,'DriveCarrier','Rigid face pawl, axial guide and spherical cam follower',drive_carrier_shape(),drive,'pawl')
    detent_shape=union([cylinder(.55,2,V(14.1,0,22.2)),
        Part.makeBox(1.6,.55,2,V(14.1,-.275,22.2))])
    detent_tip=feature(d,'DetentTip','Symmetric click follower — nominal flexed pose',detent_shape,detent,'pawl')
    detent_tip.setExpression('Placement.Base.x','Motion.DetentFlex')
    import springs_v6_updated_print as springs
    springs.add_detent(d,detent)
    anchor=union([Part.makeBox(5.85,1.0,2,V(14.85,-12.5,22.2)),
                  cylinder(2,2,V(20,-12,22.2))])
    feature(d,'DetentAnchor','Fixed root of the one-piece serpentine detent',anchor,detent,'pawl')
    import stock_springs
    stock_springs.add_springs(d,fixed,click)
    print('V6 updated print: saved protein path and shared forward/reverse native expressions',flush=True)
    for i in range(BEADS):
        kind=(0,1,2,1,0,2,2)[i%7]
        o=feature(d,f'Bead{i:02}',f'Amino-acid bead {i+1:02} — {BEAD_FAMILY[kind]}',bead_shape(kind).copy(),chain,'protein')
        o.addProperty('App::PropertyInteger','BeadVariant','Geometry');o.BeadVariant=kind
        chain_expressions(o,i)
    for i in range(BEADS-1): backbone(d,chain,i)
    d.recompute()
    invalid=[o.Name for o in d.Objects if 'Invalid' in o.State]
    if invalid: raise RuntimeError('Invalid native expressions: '+str(invalid))
    bad=[o.Name for o in d.Objects if hasattr(o,'DisplayColour') and
         (not o.Shape.isValid() or len(o.Shape.Solids)!=1)]
    if bad:raise RuntimeError('Invalid or disconnected physical features: '+str(bad))
    if App.GuiUp: present(d)
    destination=Path(save_path) if save_path else HERE.parents[1]/'build/v6-updated-print'/MODEL_FILE
    destination.parent.mkdir(parents=True,exist_ok=True);d.saveAs(str(destination))
    print('V6 updated print saved: '+str(destination),flush=True)
    return d


def world(o):
    shape=o.Shape.copy();shape.Placement=o.getGlobalPlacement();return shape


def present(d,cutaway=False,underside=False,fit=True):
    import FreeCADGui as Gui
    for o in d.Objects:
        if hasattr(o,'DisplayColour'):
            o.ViewObject.ShapeColor=tuple(o.DisplayColour[:3]);o.ViewObject.LineColor=(.16,.17,.19)
            o.ViewObject.DisplayMode='Flat Lines';o.ViewObject.LineWidth=.5
            o.ViewObject.Deviation=.12;o.ViewObject.AngularDeflection=12
            o.ViewObject.Visibility=True;o.ViewObject.Transparency=0
            if o.Name in ('LowerBody','UpperLobe') or o.Name.startswith(('RnaLink','DetentLeaf','Bead0','Bead1','Bead2')):
                o.ViewObject.DisplayMode='Shaded'
        if o.TypeId=='App::Part': o.ViewObject.Visibility=True
    for name in ('UpperLobe','LowerLid','GearGuard'):
        d.getObject(name).ViewObject.Visibility=not cutaway
    d.LowerBody.ViewObject.Transparency=85 if cutaway else 0
    import springs_v6_updated_print as springs
    springs.present(d)
    import stock_springs
    stock_springs.present(d)
    if fit:
        view=Gui.activeDocument().activeView()
        if underside: view.viewBottom()
        else: view.viewAxonometric()
        view.fitAll()


def validate(d,report_path=None):
    import validation_v6_updated_print
    return validation_v6_updated_print.run(d,report_path)


def open_controls(d):
    import FreeCADGui as Gui
    from PySide import QtCore,QtWidgets
    win=Gui.getMainWindow();old=win.findChild(QtWidgets.QDockWidget,'RibosomeV6UpdatedPrintControls')
    if old: win.removeDockWidget(old);old.deleteLater()
    dock=QtWidgets.QDockWidget('V6 updated print — move RNA either way; clasp open or closed',win)
    dock.setObjectName('RibosomeV6UpdatedPrintControls');box=QtWidgets.QWidget();layout=QtWidgets.QVBoxLayout(box)
    label=QtWidgets.QLabel();layout.addWidget(label)
    slider=QtWidgets.QSlider(QtCore.Qt.Horizontal);slider.setRange(0,EMIT*40)
    slider.setValue(round(d.Motion.BeadSteps*40));layout.addWidget(slider)
    row=QtWidgets.QHBoxLayout();layout.addLayout(row)
    forward=QtWidgets.QPushButton('Rock upper subunit');reverse=QtWidgets.QPushButton('RNA backward — one bead')
    home=QtWidgets.QPushButton('Home');closed=QtWidgets.QCheckBox('Clasp joined — external underside loop')
    closed.setChecked(d.Motion.StrandClosed);cut=QtWidgets.QCheckBox('Open mechanism')
    for w in (forward,reverse,home): row.addWidget(w)
    layout.addWidget(closed);layout.addWidget(cut)
    note=QtWidgets.QLabel('Straighten the emerged protein before reversing. No release lever.\nFlexible poses and leaf motion are prescribed CAD; physical tests remain open.')
    note.setWordWrap(True);layout.addWidget(note)
    timer=QtCore.QTimer(dock);timer.setInterval(35);state={'frame':0,'start':0,'back':False,'blocked':False}
    def update():
        d.recompute()
        label.setText('Protein %.2f / 22 steps · RNA %.2f bases · %s' %
            (d.Motion.EffectiveSteps,d.Motion.BasesPassed,'closed loop' if d.Motion.StrandClosed else 'captive open strand'))
    def slide(value):
        if timer.isActive(): return
        d.Motion.CapStroke=0;d.Motion.CapReturning=False;d.Motion.BeadSteps=value/40;update()
    def frame():
        state['frame']+=1;f=min(1,state['frame']/32)
        if state['blocked']:
            d.Motion.BeadSteps=EMIT;d.Motion.CapReturning=False
            d.Motion.CapStroke=(ENTRY_DEG/CAP_ANGLE)*(2*f if f<=.5 else 2*(1-f))
        elif state['back']:
            d.Motion.BeadSteps=state['start']-f;d.Motion.CapStroke=0
        elif f<=.5:
            d.Motion.CapReturning=False;d.Motion.BeadSteps=state['start'];d.Motion.CapStroke=2*f
        else:
            d.Motion.CapReturning=True;d.Motion.BeadSteps=state['start']+1;d.Motion.CapStroke=2*(1-f)
        update();slider.blockSignals(True);slider.setValue(round(d.Motion.EffectiveSteps*40));slider.blockSignals(False)
        if f>=1:
            timer.stop();d.Motion.CapStroke=0;d.Motion.CapReturning=False;update()
    def animate(back=False):
        if timer.isActive(): return
        s=d.Motion.BeadSteps
        blocked=not back and s>=EMIT-1e-7
        if (back and s<1) or (not back and s>EMIT-1 and not blocked): return
        state.update(frame=0,start=s,back=back,blocked=blocked);timer.start()
    def set_closed(value): d.Motion.StrandClosed=value;update()
    def set_cut(value): present(d,cutaway=value)
    def reset():
        timer.stop();d.Motion.CapStroke=0;d.Motion.CapReturning=False;d.Motion.BeadSteps=0
        slider.setValue(0);update()
    slider.valueChanged.connect(slide);timer.timeout.connect(frame)
    slider.sliderReleased.connect(lambda:slider.setValue(round(slider.value()/40)*40))
    forward.clicked.connect(lambda:animate(False));reverse.clicked.connect(lambda:animate(True));home.clicked.connect(reset)
    closed.toggled.connect(set_closed);cut.toggled.connect(set_cut)
    dock.setWidget(box);win.addDockWidget(QtCore.Qt.BottomDockWidgetArea,dock);dock.show();update()
    return dock


