"""V2: C cuff, sliding RNA dial, concealed protein store and driven swivel.

Millimetres. Native expressions retain the prescribed motion in the saved FCStd.
CAD checks are geometric; feeding, flex, wear and wire life need bench tests.
"""
from pathlib import Path
from functools import lru_cache
import json
import math
import FreeCAD as App
import Part
from fcgear import involute, fcgear

HERE = Path(__file__).resolve().parent
V = App.Vector
TAU = 2 * math.pi
RNA_R = 36.2
BASES = 144                         # full-circle pitch; the C arc carries 128
PINION_TEETH = 24
MODULE = 2 * RNA_R / BASES
GEAR_RATIO = BASES / PINION_TEETH
SHAFT_Z = RNA_R + MODULE * PINION_TEETH / 2 + .12
BEAD_PITCH = 6.0                    # distance along the nominal wire path
BEAD_R = 2.2
POCKETS = 8
FEED_R = POCKETS * BEAD_PITCH / TAU
STORE_R = SHAFT_Z - FEED_R
CHAIN_Y = 4.4
CHANNEL_R = 2.65
WIRE_R = .18
BEADS = 26
EMIT = 22
MAX_DIAL = EMIT * 360 * 3 / BASES
MOUTH_X = -17.2
HOME_S = math.pi * FEED_R + 14.5
MOUTH_S = math.pi * FEED_R - MOUTH_X
GAP_START, GAP_END = 10.0, 50.0
CUFF_IN, CUFF_OUT = 29.5, 38.5
STOP_R = 33.9
CAM_R, CAM_A = 5.5, .5
CAM_Y = 9.2
PIVOT = V(-11.5, 8.0, SHAFT_Z + 1.6)
LEVER_ARM = 4.8
SWIVEL_MAX = math.degrees(math.atan(CAM_A / LEVER_ARM))
POSE_R = 28.0
POSE_TILT = math.radians(65)
COLORS = {
    'cuff': (.10, .26, .36), 'lid': (.13, .32, .42),
    'rna': (.12, .57, .67), 'lower': (.39, .31, .54),
    'shell': (.66, .55, .80), 'gear': (.73, .78, .81),
    'feed': (.88, .43, .29), 'cam': (.87, .65, .26),
    'protein': (.91, .55, .43), 'wire': (.67, .39, .24),
    'metal': (.50, .56, .61), 'link': (.87, .69, .32),
}


def radial(r, a, y=0):
    a = math.radians(a)
    return V(r * math.sin(a), y, r * math.cos(a))


def cylinder(r, length, base, axis=V(0, 1, 0)):
    return Part.makeCylinder(r, length, base, axis)


def union(shapes):
    return shapes[0].multiFuse(shapes[1:]).removeSplitter() if len(shapes) > 1 else shapes[0]


def sector(inner, outer, a, b, y, width):
    p = lambda r, t: radial(r, t, y)
    edges = [Part.Arc(p(outer, a), p(outer, (a+b)/2), p(outer, b)).toShape(),
             Part.makeLine(p(outer, b), p(inner, b)),
             Part.Arc(p(inner, b), p(inner, (a+b)/2), p(inner, a)).toShape(),
             Part.makeLine(p(inner, a), p(outer, a))]
    return Part.Face(Part.Wire(edges)).extrude(V(0, width, 0))


def ellipsoid(center, radii):
    m = App.Matrix()
    m.A11, m.A22, m.A33 = radii
    s = Part.makeSphere(1).transformGeometry(m)
    s.translate(V(*center))
    return s


def capsule(a, b, r, z, height):
    """XY capsule with its centre line along Y."""
    x, ya = a
    _, yb = b
    return union([Part.makeBox(2*r, yb-ya, height, V(x-r, ya, z)),
                  cylinder(r, height, V(x, ya, z), V(0, 0, 1)),
                  cylinder(r, height, V(x, yb, z), V(0, 0, 1))])


def gear(teeth, module, y, width, phase=0):
    """FreeCAD's native involute generator; tooth zero points radially outward."""
    builder = fcgear.FCWireBuilder()
    involute.CreateExternalGear(builder, module, teeth, 25, split=True)
    wire = Part.Wire([e.toShape() for e in builder.wire])
    s = Part.Face(wire).extrude(V(0, 0, width))
    s.rotate(V(), V(1, 0, 0), -90)
    s.rotate(V(), V(0, 1, 0), -90 + phase)
    s.translate(V(0, y, 0))
    return s


def feature(d, name, label, shape, parent, color):
    o = d.addObject('Part::Feature', name)
    o.Label, o.Shape = label, shape
    parent.addObject(o)
    o.addProperty('App::PropertyColor', 'DisplayColour', 'Presentation')
    o.DisplayColour = COLORS[color] if isinstance(color, str) else color
    return o


def group(d, name, label, parent=None):
    o = d.addObject('App::Part', name)
    o.Label = label
    if parent:
        parent.addObject(o)
    return o


def path(s, posed=False):
    """Stored arc -> clockwise half-wrap -> straight/illustratively posed output."""
    if s < 0:
        return V(STORE_R * math.sin(s/STORE_R), CHAIN_Y, STORE_R * math.cos(s/STORE_R))
    if s <= math.pi * FEED_R:
        return V(FEED_R * math.sin(s/FEED_R), CHAIN_Y, SHAFT_Z-FEED_R*math.cos(s/FEED_R))
    if posed and s > MOUTH_S:
        w = (s-MOUTH_S) / POSE_R
        return V(MOUTH_X-POSE_R*math.sin(w),
                 CHAIN_Y+POSE_R*math.sin(POSE_TILT)*(1-math.cos(w)),
                 SHAFT_Z+FEED_R+POSE_R*math.cos(POSE_TILT)*(1-math.cos(w)))
    return V(-(s-math.pi*FEED_R), CHAIN_Y, SHAFT_Z+FEED_R)


def storage_tube(r=CHANNEL_R):
    torus = Part.makeTorus(STORE_R, r, V(0, CHAIN_Y, 0), V(0, 1, 0))
    return torus.common(sector(STORE_R-r-1, STORE_R+r+1, GAP_END, 360,
                               CHAIN_Y-r-1, 2*r+2))


def wrap_tube(r=CHANNEL_R):
    torus = Part.makeTorus(FEED_R, r, V(0, CHAIN_Y, SHAFT_Z), V(0, 1, 0))
    return torus.common(Part.makeBox(50, 40, 100, V(0, -15, 0)))


def output_tube(r=CHANNEL_R, length=21):
    return cylinder(r, length, V(-length, CHAIN_Y, SHAFT_Z+FEED_R), V(1, 0, 0))


def rna_shape():
    ring = gear(BASES, MODULE, -3.35, 1.5)
    ring = ring.cut(cylinder(32.8, 3, V(0, -4, 0)))
    ring = ring.common(sector(32.7, 37.0, GAP_END, 360+GAP_START, -3.5, 2))
    # Concealed stop groove; both closed ends are part of the RNA rail itself.
    slot = sector(33.2, 34.6, -MAX_DIAL-1.2, 1.2, -3.6, 2.1)
    ring = ring.cut(slot)
    backbone = sector(35.1, 36.45, GAP_END, 360+GAP_START, -9, 1.4)
    bars = [cylinder(.65, 4.35, radial(35.9, GAP_END+1.25+i*2.5, -7.8))
            for i in range(128)]
    root_web = sector(35.1, 35.55, GAP_END, 360+GAP_START, -3.65, .5)
    return union([ring, backbone, root_web] + bars)


@lru_cache(maxsize=1)
def feed_outline():
    """Pocket flanks generated from bead entry, half-wrap and exit trajectories.

    The two forks contact the off-centre spherical sections. A clear mid-plane
    keeps the copper core out of the teeth. This is a sampled clearance profile.
    """
    tool = math.sqrt(BEAD_R**2 - .85**2) + .13
    centres = []
    for j in range(601):
        s = -12 + (math.pi*FEED_R+24)*j/600
        p = path(s)-V(0, 0, SHAFT_Z)
        theta = -s/FEED_R
        x = p.x*math.cos(theta)-p.z*math.sin(theta)
        z = p.x*math.sin(theta)+p.z*math.cos(theta)
        if math.hypot(x, z) > 9.4+tool+.1:
            continue
        for k in range(POCKETS):
            a = k*TAU/POCKETS
            centres.append((x*math.cos(a)+z*math.sin(a), -x*math.sin(a)+z*math.cos(a)))
    points = []
    for j in range(1440):
        a = j*TAU/1440
        sn, cs, radius = math.sin(a), math.cos(a), 9.4
        for x, z in centres:
            projection = x*sn+z*cs
            disc = tool*tool-(x*x+z*z-projection*projection)
            if disc >= 0 and projection > 0:
                radius = min(radius, projection-math.sqrt(disc))
        points.append((radius*sn, radius*cs))
    return points


def feed_wheel():
    forks = []
    for y in [2.8, 5.25]:
        p = [V(x, y, z) for x, z in feed_outline()]
        p.append(p[0])
        forks.append(Part.Face(Part.makePolygon(p)).extrude(V(0, .75, 0)))
    s = union(forks + [cylinder(5.35, 3.2, V(0, 2.8, 0))])
    return s.cut(Part.makeBox(4.65, 4, 4.65, V(-2.325, 2.5, -2.325)))


def wave_ring(r, amp, half_width, y, depth, count=384):
    wires = []
    for offset in [half_width, -half_width]:
        pts = []
        for j in range(count):
            a = j*TAU/count
            rr = r+amp*math.sin(8*a)+offset
            pts.append(V(rr*math.sin(a), y, rr*math.cos(a)))
        pts.append(pts[0])
        wires.append(Part.makePolygon(pts))
    return Part.Face(wires[0]).cut(Part.Face(wires[1])).extrude(V(0, depth, 0))


def swivel_cam():
    cam = cylinder(7.5, 1.9, V(0, CAM_Y, 0))
    cam = cam.cut(wave_ring(CAM_R, CAM_A, .82, 10.2, 1.3))
    return cam.cut(Part.makeBox(4.65, 3, 4.65, V(-2.325, 9, -2.325)))


def stationary_shapes():
    cuff = sector(CUFF_IN, CUFF_OUT, GAP_END, 360+GAP_START, -.8, 10.4)
    front_seat = sector(31.3, 34.7, GAP_END, 360+GAP_START, -10, 6.4)
    rear_seat = sector(29.5, 32.5, GAP_END, 360+GAP_START, -3.7, 3.1)
    # The front lip retains the RNA backbone; the rear lip is interrupted at readout.
    front_lip = sector(34.4, 37.8, GAP_END, 360+GAP_START, -10, .75)
    front_lip = union([front_lip, sector(36.7, 37.8, GAP_END, 360+GAP_START, -9.8, 1.5)])
    rear_lip = sector(36.95, 38.0, GAP_END, 340, -2.2, 1.6)
    lower_outer = union([ellipsoid((0, 1, 39.8), (16, 11.5, 10.8)),
                         ellipsoid((-8, -3, 40), (8.5, 7.5, 7.8)),
                         ellipsoid((7, 5, 40.8), (9, 8, 8.8)),
                         sector(29.5, 39.0, -25, GAP_START, -10.2, 22.0)])
    lower_outer = lower_outer.common(Part.makeBox(100, 70, SHAFT_Z+.5, V(-50, -30, 0)))
    guard = cylinder(11.9, 6.0, V(0, 1.4, SHAFT_Z))
    cam_guard = cylinder(8.8, 3.0, V(0, 8.8, SHAFT_Z))
    outlet = cylinder(3.65, 18.0, V(-18, CHAIN_Y, SHAFT_Z+FEED_R), V(1, 0, 0))
    bearing = cylinder(2.5, 7.6, V(PIVOT.x, PIVOT.y, SHAFT_Z+2.9), V(0, 0, 1))
    bearing_brace = Part.makeBox(5, 1.05, 12.5, V(PIVOT.x-2.5, 4.55, SHAFT_Z-2))
    rail = Part.makeBox(2.4, 2.2, 2.4, V(-9.6, 11.7, SHAFT_Z-1.2))
    detent_socket = Part.makeBox(2.9, 2.1, 7.3, V(-12.3, -.8, SHAFT_Z-2))
    front_bearing = cylinder(2.8, 7.0, V(0, -10.5, SHAFT_Z))
    outer = union([cuff, front_seat, rear_seat, front_lip, rear_lip,
                   lower_outer, guard, cam_guard, outlet, bearing, bearing_brace, rail, detent_socket, front_bearing])
    # Full annuli avoid coincident angular seams during later booleans.
    rna_clear = cylinder(36.6, 5.7, V(0, -9.2, 0)).cut(cylinder(34.75, 6, V(0, -9.3, 0)))
    rear_clear = cylinder(36.85, 2.2, V(0, -3.65, 0)).cut(cylinder(32.55, 3, V(0, -4, 0)))
    cavities = [storage_tube(), wrap_tube(), output_tube(), rna_clear, rear_clear,
                cylinder(6.78, 1.85, V(0, -3.5, SHAFT_Z)),
                cylinder(2.65, 12.6, V(0, -1.85, SHAFT_Z)),
                cylinder(3.38, 4.0, V(0, 2.5, SHAFT_Z)),
                cylinder(3.38, 2.4, V(0, 9, SHAFT_Z)),
                cylinder(9.65, 3.7, V(0, 2.55, SHAFT_Z)),
                cylinder(7.7, 2.6, V(0, 9.0, SHAFT_Z)),
                Part.makeBox(2.5, .8, 1.5, V(-6.75, 11.45, SHAFT_Z-.75)),
                cylinder(1.12, 28, V(0, -11, SHAFT_Z)),
                cylinder(1.65, 16, V(PIVOT.x, PIVOT.y, SHAFT_Z-3), V(0, 0, 1)),
                cylinder(2.6, 1.4, V(PIVOT.x, PIVOT.y, PIVOT.z-.2), V(0, 0, 1)),
                Part.makeBox(10, 1.7, 1.5, V(-14, 11.95, SHAFT_Z-.75)),
                cylinder(CUFF_IN, 50, V(0, -20, 0))]
    # Detent recess at the front of the mechanism, isolated from the bead path.
    cavities += [Part.makeBox(12, 1.8, 2.3, V(-11, -.65, SHAFT_Z+3.4)),
                 Part.makeBox(1.7, 1.4, 2.6, V(-11.65, -.5, SHAFT_Z+2.8)),
                 cylinder(4.45, 1.5, V(0, -.5, SHAFT_Z))]
    solid = outer.cut(union(cavities)).removeSplitter()
    # Native closed stop groove mates to this fixed pin below the input mesh.
    stop_pin = cylinder(.45, 2.8, radial(STOP_R, 0, -3.2))
    solid = union([solid, stop_pin])
    # Axial case split exposes the entire storage channel for assembly.
    front = solid.common(Part.makeBox(160, 44.25, 160, V(-80, -40, -80))).removeSplitter()
    rear = solid.common(Part.makeBox(160, 40, 160, V(-80, 4.55, -80))).removeSplitter()
    for a in [90, 185, 280]:
        hole = cylinder(.85, 25, radial(31.1, a, -11))
        front, rear = front.cut(hole), rear.cut(hole)
    # Cover locating screws are clear of the stored strand.
    for x, z in [(-12, SHAFT_Z-4), (12, SHAFT_Z-4)]:
        hole = cylinder(.85, 28, V(x, -11, z))
        front, rear = front.cut(hole), rear.cut(hole)
    return front.removeSplitter(), rear.removeSplitter(), [guard, cam_guard, outlet, bearing, rail]


def around_pivot(shape, angle):
    s = shape.copy()
    s.rotate(PIVOT, V(0, 0, 1), angle)
    return s


def upper_lobe(guards):
    outer = union([ellipsoid((0, .6, 52.5), (17, 12.5, 8.6)),
                   ellipsoid((-8, -4, 52.8), (8.5, 8, 7.1)),
                   ellipsoid((7.5, 4.5, 52.5), (9.5, 9.0, 7.6)),
                   ellipsoid((PIVOT.x, PIVOT.y, 54.8), (4.5, 4.5, 4.5))])
    outer = outer.common(Part.makeBox(120, 100, 50, V(-60, -40, SHAFT_Z+1.3)))
    # A spherical clearance cavity bounds the complete guard at every swivel
    # angle, including between the sampled inverse poses used for the ports.
    envelopes = [Part.makeSphere(14.0, V(0, CHAIN_Y, SHAFT_Z)),
                 cylinder(9.25, 4.0, V(0, 8.3, SHAFT_Z)),
                 cylinder(4.1, 22, V(-21, CHAIN_Y, SHAFT_Z+FEED_R), V(1, 0, 0)),
                 cylinder(2.85, 13, V(PIVOT.x, PIVOT.y, SHAFT_Z-2), V(0, 0, 1)),
                 Part.makeBox(12, 4, 5.4, V(-15, 11.2, SHAFT_Z-1.4)),
                 cylinder(6.95, 2.5, V(0, -3.85, SHAFT_Z)),
                 cylinder(3.5, 9, V(0, -11, SHAFT_Z)),
                 cylinder(4.7, 2, V(0, -.7, SHAFT_Z))]
    envelopes.append(Part.makeBox(3.7, 3, 8, V(-12.7, -1.2, SHAFT_Z-2.2)))
    cavity = union([around_pivot(s, -a) for a in [-7, 0, 7] for s in envelopes])
    boss = cylinder(3.2, 3.7, V(PIVOT.x, PIVOT.y, PIVOT.z+10.3), V(0, 0, 1))
    shell = union([outer, boss]).cut(cavity)
    key = Part.makeBox(2.85, 2.85, 3.5, V(PIVOT.x-1.425, PIVOT.y-1.425, PIVOT.z+9.85))
    shell = shell.cut(key).cut(cylinder(.95, 5, V(PIVOT.x, PIVOT.y, PIVOT.z+10), V(0, 0, 1)))
    shell = shell.cut(cylinder(1.65, 12.4, V(PIVOT.x, PIVOT.y, PIVOT.z-1), V(0, 0, 1)))
    shell = shell.cut(capsule((PIVOT.x, PIVOT.y), (PIVOT.x, PIVOT.y+7), 1.8, PIVOT.z-.2, 1.3))
    shell.translate(-PIVOT)
    return shell.removeSplitter()


def chain_expressions(o, i):
    o.addProperty('App::PropertyFloat', 'PathDistance', 'Motion')
    o.setExpression('PathDistance', f'{HOME_S-i*BEAD_PITCH} + Motion.FeedDistance / 1 mm')
    s = 'PathDistance'
    inside = f'{s} < 0'
    wrap = f'{s} <= {math.pi*FEED_R}'
    o.addProperty('App::PropertyInteger', 'PoseActive', 'Motion')
    o.setExpression('PoseActive', f'Motion.PoseProtein ? ({s} > {MOUTH_S} ? 1 : 0) : 0')
    posed = 'PoseActive'
    a = f'({s}/{STORE_R} * 1 rad)'
    b = f'({s}/{FEED_R} * 1 rad)'
    w = f'(({s}-{MOUTH_S})/{POSE_R} * 1 rad)'
    xp = f'{MOUTH_X}-{POSE_R}*sin({w})'
    yp = f'{CHAIN_Y}+{POSE_R*math.sin(POSE_TILT)}*(1-cos({w}))'
    zp = f'{SHAFT_Z+FEED_R}+{POSE_R*math.cos(POSE_TILT)}*(1-cos({w}))'
    coords = {
        'x': (f'{STORE_R}*sin({a})', f'{FEED_R}*sin({b})', f'-({s}-{math.pi*FEED_R})', xp),
        'y': (str(CHAIN_Y), str(CHAIN_Y), str(CHAIN_Y), yp),
        'z': (f'{STORE_R}*cos({a})', f'{SHAFT_Z}-{FEED_R}*cos({b})', str(SHAFT_Z+FEED_R), zp),
    }
    for axis, (st, wr, out, po) in coords.items():
        expr = f'({inside} ? ({st}) : ({wrap} ? ({wr}) : ({posed} ? ({po}) : ({out})))) * 1 mm'
        o.setExpression('Placement.Base.'+axis, expr)
    tangents = {
        'X': f'{inside} ? cos({a}) : ({wrap} ? cos({b}) : ({posed} ? -cos({w}) : -1))',
        'Y': f'{posed} ? {math.sin(POSE_TILT)}*sin({w}) : 0',
        'Z': f'{inside} ? -sin({a}) : ({wrap} ? sin({b}) : ({posed} ? {math.cos(POSE_TILT)}*sin({w}) : 0))',
    }
    for axis, expr in tangents.items():
        o.addProperty('App::PropertyFloat', 'Tangent'+axis, 'Motion')
        o.setExpression('Tangent'+axis, expr)
    o.setExpression('Placement.Rotation.Axis.x', '0')
    o.setExpression('Placement.Rotation.Axis.y', 'abs(TangentY)+abs(TangentZ) < 0.000001 ? 1 : -TangentZ')
    o.setExpression('Placement.Rotation.Axis.z', 'abs(TangentY)+abs(TangentZ) < 0.000001 ? 0 : TangentY')
    o.setExpression('Placement.Rotation.Angle', 'acos(TangentX)')


def backbone(d, chain, i):
    o = d.addObject('Part::Cylinder', f'Wire{i:02}')
    o.Label = 'Copper-core segment (nominal Ø0.36 mm)'
    chain.addObject(o)
    o.Radius = WIRE_R
    o.addProperty('App::PropertyColor', 'DisplayColour', 'Presentation')
    o.DisplayColour = COLORS['wire']
    for axis in 'xyz':
        o.addProperty('App::PropertyDistance', 'Delta'+axis.upper(), 'Motion')
        o.setExpression('Delta'+axis.upper(), f'Bead{i+1:02}.Placement.Base.{axis} - Bead{i:02}.Placement.Base.{axis}')
        o.setExpression('Placement.Base.'+axis, f'Bead{i:02}.Placement.Base.{axis}')
    o.setExpression('Height', 'sqrt(DeltaX^2 + DeltaY^2 + DeltaZ^2)')
    o.setExpression('Placement.Rotation.Axis.x', '-DeltaY / Height')
    o.setExpression('Placement.Rotation.Axis.y', 'DeltaX / Height')
    o.setExpression('Placement.Rotation.Axis.z', '0')
    o.setExpression('Placement.Rotation.Angle', 'acos(DeltaZ / Height)')


def build():
    if 'Ribosome' in App.listDocuments():
        raise RuntimeError('Close Ribosome before rebuilding.')
    d = App.newDocument('Ribosome')
    d.Label = 'mRNA toy V2 — cuff, RNA dial and hidden protein'
    d.Comment = 'V2 geometric prototype. Native prescribed motion; not a validated print release.'
    m = d.addObject('App::FeaturePython', 'Motion')
    m.Label = 'V2 controls — turn RNA, reverse only after straightening'
    m.addProperty('App::PropertyFloatConstraint', 'DialDegrees', 'Play')
    m.DialDegrees = (0, 0, MAX_DIAL, .25)
    m.addProperty('App::PropertyBool', 'PoseProtein', 'Play')
    m.PoseProtein = False
    for name, kind, expr in [
        ('FeedDistance', 'App::PropertyLength', f'{BEAD_PITCH/(360*3/BASES)} mm * DialDegrees'),
        ('RotorDegrees', 'App::PropertyFloat', f'-{GEAR_RATIO} * DialDegrees'),
        ('BasesPassed', 'App::PropertyFloat', f'{BASES/360} * DialDegrees'),
        ('BeadSteps', 'App::PropertyFloat', f'DialDegrees / {360*3/BASES}'),
        ('FollowerShift', 'App::PropertyDistance', f'{CAM_A} mm * sin(8 * RotorDegrees * 1 deg)'),
        ('SwivelDegrees', 'App::PropertyFloat', f'-atan(FollowerShift / {LEVER_ARM} mm) / 1 deg'),
    ]:
        m.addProperty(kind, name, 'Coupled motion')
        m.setExpression(name, expr)
        m.setEditorMode(name, 1)
    for name, value in [('BasesPerBead', 3), ('BeadCount', BEADS), ('MaximumBeadSteps', EMIT),
                        ('CuffInsideDiameter', 2*CUFF_IN), ('CuffGapDegrees', GAP_END-GAP_START),
                        ('RnaBasePitch', TAU*RNA_R/BASES), ('BeadPitch', BEAD_PITCH),
                        ('StoreCentreRadius', STORE_R), ('SwivelAmplitudeDegrees', SWIVEL_MAX)]:
        m.addProperty('App::PropertyFloat', name, 'Dimensions (edit source to rebuild)')
        setattr(m, name, value)
        m.setEditorMode(name, 1)
    m.addProperty('App::PropertyString', 'StudyLimits', 'Study')
    m.StudyLimits = 'Return dial home to don; straighten protein before reverse. Flex, feed force, fatigue and print fit untested.'
    fixed = group(d, 'Stationary', 'Stationary C cuff and ribosome guide')
    dial = group(d, 'RnaDial', 'RNA C dial — home aligns with cuff opening')
    dial.Placement.Rotation = App.Rotation(V(0, 1, 0), 0)
    dial.setExpression('Placement.Rotation.Angle', 'Motion.DialDegrees * 1 deg')
    rotor = group(d, 'Rotor', 'Common shaft — RNA pinion, feeder, cam')
    rotor.Placement = App.Placement(V(0, 0, SHAFT_Z), App.Rotation(V(0, 1, 0), 0))
    rotor.setExpression('Placement.Rotation.Angle', 'Motion.RotorDegrees * 1 deg')
    swivel = group(d, 'Swivel', 'Upper lobe — groove cam, slider, slotted lever')
    swivel.Placement = App.Placement(PIVOT, App.Rotation(V(0, 0, 1), 0))
    swivel.setExpression('Placement.Rotation.Angle', 'Motion.SwivelDegrees * 1 deg')
    chain = group(d, 'Protein', '26 plain beads on a poseable copper core')
    print('V2: building concealed-track C cuff and RNA dial', flush=True)
    front, rear, guards = stationary_shapes()
    feature(d, 'CuffFrame', 'Front cuff half + fixed ribosome guide', front, fixed, 'cuff')
    feature(d, 'CuffRear', 'Rear cuff half — remove to load the protein', rear, fixed, 'lid')
    feature(d, 'Rna', '128 RNA bases + concealed 144-pitch gear rail', rna_shape(), dial, 'rna')
    print('V2: building positive feed and mechanically driven swivel', flush=True)
    pinion = gear(PINION_TEETH, MODULE, -3.35, 1.5, 7.5)
    keys = [Part.makeBox(4.4, length, 4.4, V(-2.2, y, -2.2)) for y, length in [(2.6, 3.4), (9.1, 2)]]
    shaft = union([pinion, cylinder(2.4, 14.45, V(0, -3.35, 0))] + keys)
    shaft = shaft.cut(cylinder(1.15, 17, V(0, -4, 0)))
    feature(d, 'InputDrive', '24-tooth RNA pinion + keyed drive shaft', shaft, rotor, 'gear')
    feature(d, 'BeadWheel', '8-pocket forked bead feeder — wire-clear mid-plane', feed_wheel(), rotor, 'feed')
    feature(d, 'SwivelCam', '8-cycle closed-groove swivel cam', swivel_cam(), rotor, 'cam')
    # Separate rounded detent track on the same rigid shaft, one click per bead.
    pts = []
    for j in range(257):
        a = j*TAU/256
        rr = 3.8+.32*math.cos(8*a)
        pts.append(V(rr*math.sin(a), -.35, rr*math.cos(a)))
    detent = Part.Face(Part.makePolygon(pts)).extrude(V(0, 1.1, 0))
    detent = detent.cut(cylinder(2.3, 2, V(0, -.6, 0)))
    d.InputDrive.Shape = union([shaft, detent])
    # Unloaded cantilever is intentionally penetrated by its preload cam.
    leaf = union([Part.makeBox(10.8, 1.1, .45, V(-10.8, -.35, SHAFT_Z+4.0)),
                  cylinder(.65, 1.1, V(0, -.35, SHAFT_Z+4.03)),
                  Part.makeBox(1.4, 1.1, 2.0, V(-11.5, -.35, SHAFT_Z+3.0))])
    feature(d, 'DetentLeaf', 'Replaceable click flexure — unloaded, intentional cam preload', leaf, fixed, 'link')
    axle = cylinder(1.0, 21.1, V(0, -9.5, SHAFT_Z))
    feature(d, 'Axle', 'Common stationary Ø2 mm axle', axle, fixed, 'metal')
    slider = union([Part.makeBox(7.5, 1.4, 1.1, V(-13.0, 12.1, SHAFT_Z-.55)),
                    cylinder(.5, 2.85, V(-CAM_R, 10.35, SHAFT_Z)),
                    cylinder(.5, 2.6, V(PIVOT.x, 12.8, SHAFT_Z+.45), V(0, 0, 1))])
    o = feature(d, 'FollowerSlider', 'Captured cam pin + guided slider + lever pin', slider, fixed, 'link')
    o.setExpression('Placement.Base.x', 'Motion.FollowerShift')
    lever = union([cylinder(2.2, .9, V(), V(0, 0, 1)),
                   capsule((0, 0), (0, 6.0), 1.4, 0, .9),
                   cylinder(1.5, 11, V(), V(0, 0, 1)),
                   Part.makeBox(2.6, 2.6, 3, V(-1.3, -1.3, 10))])
    lever = lever.cut(capsule((0, 4.0), (0, 5.6), .7, -.1, 1.2))
    lever = lever.cut(cylinder(.85, 4, V(0, 0, 10), V(0, 0, 1)))
    feature(d, 'LeverPost', 'Radial slotted lever + vertical swivel post + square key', lever, swivel, 'gear')
    feature(d, 'UpperLobe', 'Organic upper lobe — swivels about outward wrist axis', upper_lobe(guards), swivel, 'shell')
    cap = union([cylinder(.75, 2.6, V(0, 0, 11.6), V(0, 0, 1)),
                 cylinder(2.6, .7, V(0, 0, 14.0), V(0, 0, 1))])
    feature(d, 'SwivelRetainer', 'Swivel-post retaining screw envelope', cap, swivel, 'metal')
    print('V2: building plain beads, flared core bores and native expressions', flush=True)
    bead = Part.makeSphere(BEAD_R).cut(cylinder(.5, 6, V(-3, 0, 0), V(1, 0, 0)))
    bead = bead.cut(Part.makeCone(1.1, .5, 1.5, V(-2.2, 0, 0), V(1, 0, 0)))
    bead = bead.cut(Part.makeCone(.5, 1.1, 1.5, V(.7, 0, 0), V(1, 0, 0)))
    for i in range(BEADS):
        o = feature(d, f'Bead{i:02}', f'Amino-acid bead {i+1:02} — plain Ø4.4 mm', bead.copy(), chain, 'protein')
        chain_expressions(o, i)
    for i in range(BEADS-1):
        backbone(d, chain, i)
    d.recompute()
    bad = [o.Name for o in d.Objects if 'Invalid' in o.State]
    if bad:
        raise RuntimeError('Expression failures: '+str(bad))
    if App.GuiUp:
        present(d)
    d.saveAs(str(HERE/'Ribosome.FCStd'))
    print('Saved V2 model', flush=True)
    return d


def world(o):
    s = o.Shape.copy()
    s.Placement = o.getGlobalPlacement()
    return s


def common_volume(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    if a.distToShape(b)[0] > 1e-6:
        return 0.0
    return a.common(b).Volume


def present(d, shell=True, rear=True):
    import FreeCADGui as Gui
    for o in d.Objects:
        if hasattr(o, 'DisplayColour'):
            o.ViewObject.ShapeColor = tuple(o.DisplayColour[:3])
            o.ViewObject.LineColor = (.14, .18, .22)
            o.ViewObject.DisplayMode = 'Shaded'
            o.ViewObject.Deviation = .15
            o.ViewObject.AngularDeflection = 18
            o.ViewObject.Transparency = 0
            o.Visibility = True
            o.ViewObject.Visibility = True
            if o.Name in ['CuffFrame', 'CuffRear']:
                o.ViewObject.DiffuseColor = [COLORS['lower'] if f.CenterOfMass.z > 36.5 and abs(f.CenterOfMass.x) < 19 else tuple(o.DisplayColour[:3]) for f in o.Shape.Faces]
    # Four abstract base colours are confined to the crossbars, in codon triplets.
    base_colors = [(.38, .75, .74), (.87, .67, .34), (.71, .66, .84), (.88, .55, .48)]
    colors = []
    for f in d.Rna.Shape.Faces:
        surf = f.Surface
        if hasattr(surf, 'Radius') and abs(surf.Radius-.65) < 1e-4:
            a = math.degrees(math.atan2(f.CenterOfMass.x, f.CenterOfMass.z)) % 360
            colors.append(base_colors[int(((a-GAP_END) % 360)/2.5) % 4])
        else:
            colors.append(COLORS['rna'])
    d.Rna.ViewObject.DiffuseColor = colors
    for name in ['Stationary', 'RnaDial', 'Rotor', 'Swivel', 'Protein']:
        d.getObject(name).Visibility = True
        d.getObject(name).ViewObject.Visibility = True
    d.UpperLobe.Visibility = shell
    d.UpperLobe.ViewObject.Visibility = shell
    d.CuffRear.Visibility = rear
    d.CuffRear.ViewObject.Visibility = rear
    Gui.activeDocument().activeView().viewAxonometric()
    Gui.activeDocument().activeView().fitAll()


def validate(d):
    import validation
    return validation.run(d)


def open_controls(d):
    import FreeCADGui as Gui
    from PySide import QtCore, QtWidgets
    win = Gui.getMainWindow()
    old = win.findChild(QtWidgets.QDockWidget, 'RibosomeControls')
    if old:
        win.removeDockWidget(old)
        old.deleteLater()
    dock = QtWidgets.QDockWidget('mRNA toy V2 — 3 bases → 1 bead', win)
    dock.setObjectName('RibosomeControls')
    box = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(box)
    label = QtWidgets.QLabel()
    slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    slider.setRange(0, int(MAX_DIAL*4))
    slider.setValue(round(d.Motion.DialDegrees*4))
    row = QtWidgets.QHBoxLayout()
    step = QtWidgets.QPushButton('One codon ▶')
    home = QtWidgets.QPushButton('Home')
    shell = QtWidgets.QCheckBox('Show swivelling lobe')
    shell.setChecked(True)
    cut = QtWidgets.QCheckBox('Open storage / mechanism')
    pose = QtWidgets.QCheckBox('Pose emerged protein (straighten before reverse)')
    pose.setChecked(bool(d.Motion.PoseProtein))
    row.addWidget(step)
    row.addWidget(home)
    row.addWidget(shell)
    row.addWidget(cut)
    row.addWidget(pose)
    layout.addWidget(label)
    layout.addWidget(slider)
    layout.addLayout(row)
    def update():
        d.Motion.DialDegrees = slider.value()/4
        d.Motion.PoseProtein = pose.isChecked()
        d.recompute()
        d.UpperLobe.Visibility = shell.isChecked() and not cut.isChecked()
        d.UpperLobe.ViewObject.Visibility = d.UpperLobe.Visibility
        d.CuffRear.Visibility = not cut.isChecked()
        d.CuffRear.ViewObject.Visibility = d.CuffRear.Visibility
        d.CuffFrame.ViewObject.Transparency = 65 if cut.isChecked() else 0
        label.setText('RNA %.1f° / %.0f bases    Protein %.1f bead steps    Home aligns the C openings for wearing.' %
                      (d.Motion.DialDegrees, d.Motion.BasesPassed, d.Motion.BeadSteps))
        Gui.activeDocument().activeView().redraw()
    slider.valueChanged.connect(update)
    for check in [shell, cut, pose]:
        check.toggled.connect(update)
    timer = QtCore.QTimer(dock)
    timer.setInterval(35)
    target = [0]
    def advance():
        slider.setValue(min(target[0], slider.value()+1))
        if slider.value() >= target[0]:
            timer.stop()
    def codon():
        target[0] = min(slider.maximum(), slider.value()+30)
        timer.start()
    def go_home():
        timer.stop()
        pose.setChecked(False)
        slider.setValue(0)
    timer.timeout.connect(advance)
    step.clicked.connect(codon)
    home.clicked.connect(go_home)
    dock.setWidget(box)
    dock.setMaximumHeight(135)
    win.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock)
    win.resizeDocks([dock], [115], QtCore.Qt.Vertical)
    dock.show()
    update()
    return dock

