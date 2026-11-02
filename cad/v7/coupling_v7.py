"""V7 forward pickup hardware and its prescribed latch states.

Two opposite face tracks share the rotor. The pickup slider may rise freely
over the reverse ramps; its separate fork is latched up only during reset.
The trip leaf/snap is a spring-space study, not a force or dynamic solution.
"""
import math
from functools import lru_cache
import FreeCAD as App
import Part
import bracelet_v7 as b

V=App.Vector
B_ANGLE=120.0
B_INNER,B_OUTER=17.0,20.1
B_GUIDE=25.5
B_LIFT=1.8
RESET_DEG=4.0
ROOF_MOUNT_ANGLE=B_ANGLE-b.STEP_DEG-12
ROOF_MOUNT=b.polar(36,ROOF_MOUNT_ANGLE)
TOOTH_RISE=1.25
TOE_ANGLE=3.0
TOE_FLOOR=24.8


def rotated(shape):
    result=shape.copy();result.rotate(V(),V(0,0,1),B_ANGLE);return result


@lru_cache(maxsize=1)
def pickup_track():
    sections=[]
    for j in range(9):
        a=b.STEP_DEG*j/8
        top=b.RATCHET_Z+TOOTH_RISE*(1-j/8)
        pts=[b.polar(B_INNER,a,23.8),b.polar(B_OUTER,a,23.8),
             b.polar(B_OUTER,a,top),b.polar(B_INNER,a,top)]
        sections.append(Part.makePolygon(pts+[pts[0]]))
    tooth=Part.makeLoft(sections,True,False)
    teeth=[]
    for k in range(b.POCKETS):
        copy=tooth.copy();copy.rotate(V(),V(0,0,1),B_ANGLE+k*b.STEP_DEG);teeth.append(copy)
    return b.union(teeth+[b.annulus(5.7,B_OUTER,23.8,.6)])


def pickup_pawl():
    tip=b.angular_sector(17.05,20.0,-TOE_ANGLE,0,TOE_FLOOR,1.75)
    bridge=Part.makeBox(7.4,1.8,1.0,V(19.0,-1.4,26.35))
    boss=b.cylinder(2,3.8,V(B_GUIDE,0,24.8))
    pawl=b.union([tip,bridge,boss]).cut(b.cylinder(.95,5,V(B_GUIDE,0,24.5)))
    return rotated(pawl)


def pickup_fork():
    collar=b.annulus(1.05,2.25,23.8,1);collar.translate(V(B_GUIDE,0,0))
    arm=Part.makeBox(4.1,1.3,.8,V(B_GUIDE,-.65,24.0))
    tab=Part.makeBox(1.3,1.3,1.2,V(28.5,-.65,24.2))
    follower=Part.makeSphere(.45,V(28.8,0,25.8))
    root=b.cylinder(.3,1.1,V(28.8,0,24.8))
    return rotated(b.union([collar,arm,tab,follower,root]))


def reset_roof():
    """Conjugate upper envelope of the actual spherical fork follower."""
    r,ball=28.8,.45
    samples=[]
    for j in range(401):
        u=-2+(b.CAP_ANGLE+4)*j/400
        lift=B_LIFT*max(0,min(1,u/RESET_DEG))
        samples.append((math.radians(B_ANGLE-u),25.8+lift))
    wires=[]
    for j in range(90):
        u=-1+(b.CAP_ANGLE+2)*j/89;a=B_ANGLE-u
        candidates=[]
        for t,z in samples:
            distance=2*r*math.sin((math.radians(a)-t)/2)
            if abs(distance)<=ball:candidates.append(z+math.sqrt(ball*ball-distance*distance))
        bottom=max(candidates)+.025
        pts=[b.polar(28.25,a,bottom),b.polar(29.35,a,bottom),
             b.polar(29.35,a,bottom+1.05),b.polar(28.25,a,bottom+1.05)]
        wires.append(Part.makePolygon(pts+[pts[0]]))
    roof=Part.makeLoft(wires,True,True)
    support=b.angular_sector(28.25,36.5,ROOF_MOUNT_ANGLE,B_ANGLE-b.CAP_ANGLE+.5,27.5,.9)
    foot=b.cylinder(2.6,6.7,ROOF_MOUNT+V(0,0,21.7))
    key=b.cylinder(.6,.8,ROOF_MOUNT+b.polar(2,ROOF_MOUNT_ANGLE+90)+V(0,0,20.9))
    result=b.union([roof,support,foot,key])
    result=result.cut(b.cylinder(1.15,8,ROOF_MOUNT+V(0,0,21.5)))
    return result.cut(Part.makeCone(1.15,2.1,.95,ROOF_MOUNT+V(0,0,27.65)))


def latch_tip():
    return rotated(Part.makeBox(1.4,1.5,.4,V(28.8,-.75,25.6)))


def latch_anchor():
    # The root is integral with the upper carrier; eight chords represent
    # the flexible tongue between this root and the separate tip feature.
    return rotated(b.union([Part.makeBox(1.4,2,8.4,V(29.0,6.0,25.6)),
        Part.makeBox(6.4,11.0,1,V(24.0,1.0,33.0)),
        Part.makeBox(2.0,2.0,7.2,V(27.8,9.0,26.8))]))


def cap_supports():
    beam=b.angular_sector(4.7,28.0,B_ANGLE-5,B_ANGLE+5,33.0,1)
    boss=b.cylinder(2.3,1.0,b.polar(B_GUIDE,B_ANGLE,33.0))
    pin=b.cylinder(.75,11.2,b.polar(B_GUIDE,B_ANGLE,22.8))
    seat=b.cylinder(1.65,1,b.polar(B_GUIDE,B_ANGLE,22.8))
    return b.union([beam,boss,pin,seat,latch_anchor()])


def cap_clearance():
    # The fixed reset roof must stay clear of the shell throughout its whole
    # rotation. The carrier beam above z=30.4 remains as a supported bridge.
    return b.angular_sector(23.0,34.0,B_ANGLE-b.CAP_ANGLE-18,
                            B_ANGLE+b.CAP_ANGLE+7,21.0,8.8)


def trip_post():
    a=B_ANGLE-b.STEP_DEG
    return b.union([b.cylinder(.7,6.5,b.polar(30.8,a-1.1,21.3)),
        b.angular_sector(29.8,31.5,a-2.5,a+.4,21.3,1.1)])


def add(d):
    rotor=d.Rotor;upper=d.Clicker;fixed=d.Stationary
    b.COLORS.update(pickup=(.69,.31,.55),latch=(.54,.61,.65))
    track=b.feature(d,'PickupRatchet','B: reverse-facing 28-tooth forward-pickup track',pickup_track(),rotor,'gear')
    track.addProperty('App::PropertyString','ContactRole','Study')
    track.ContactRole='Rotor drives upper forward; opposite tooth orientation to FeedRatchet A.'
    pawl_group=b.group(d,'PickupPawlAssembly','B: freely overrunning slider on the upper carrier')
    upper.addObject(pawl_group)
    pawl_group.setExpression('Placement.Base.z','Motion.PickupPawlLift')
    b.feature(d,'PickupPawl','B: forward-pickup pawl, independent reverse coast',pickup_pawl(),pawl_group,'pickup')
    fork_group=b.group(d,'PickupForkAssembly','Fork lifts B during reset; B can rise independently on reverse')
    upper.addObject(fork_group);fork_group.setExpression('Placement.Base.z','Motion.PickupForkLift')
    b.feature(d,'PickupFork','Lift collar, reset follower and hold-open tab',pickup_fork(),fork_group,'pickup')
    latch_group=b.group(d,'PickupLatchAssembly','Upper-mounted hold-open leaf and its supported root')
    upper.addObject(latch_group);latch_group.Placement.Rotation=App.Rotation(V(0,0,1),B_ANGLE)
    latch=b.feature(d,'PickupLatchTip','Hold-open lip — under fork tab during upper return',
        Part.makeBox(1.4,1.5,.4,V(28.8,-.75,25.6)),latch_group,'latch')
    latch.setExpression('Placement.Base.x','Motion.LatchDeflection')
    # Free tip is at local y=0, root at -7. Connected beam chords are a
    # prescribed deformation, as in the retained click leaf.
    b.flexure_segments(d,latch_group,'PickupLatchLeaf',29.8,0,7,25.6,
                      'Motion.LatchDeflection / 1 mm',True,.8,.4)
    roof=b.feature(d,'PickupResetRoof','Fixed roof lowers the pickup fork on approach to home',reset_roof(),fixed,'guide')
    b.feature(d,'PickupTripPost','Fixed end-of-stroke trigger post — trip snap study',trip_post(),fixed,'guide')
    # A long, upper-rooted trigger leaf stores nominal axial buckling
    # displacement against the fixed post. Its free end bears on the fork.
    # Chords are a prescribed snap shape; this is not an elastic solution.
    trip_group=b.group(d,'PickupTripAssembly','Upper-rooted trip leaf — prescribed elastic snap shape')
    upper.addObject(trip_group);trip_group.Placement.Rotation=App.Rotation(V(0,0,1),B_ANGLE)
    for j in range(10):
        a,c=j/10,(j+1)/10;fa,fc=(1-a)**2,(1-c)**2
        o=d.addObject('Part::Box',f'PickupTripLeaf{j}');trip_group.addObject(o)
        o.Label='Trip spring chord — force, buckling and fatigue unqualified'
        o.Length=2.2;o.Height=.4;o.Placement.Base.x=27.8
        for name in ('DeltaY','DeltaZ'):
            o.addProperty('App::PropertyLength',name,'Kinematics')
        o.setExpression('DeltaY',f'{10*(c-a):.16g} mm+({fc-fa:.16g})*Motion.TripCompression')
        o.setExpression('DeltaZ',f'({fc-fa:.16g})*(Motion.TripLeafLift-1.4 mm)')
        o.setExpression('Placement.Base.y',f'{10*a:.16g} mm+{fa:.16g}*Motion.TripCompression')
        o.setExpression('Placement.Base.z',f'26.8 mm+{fa:.16g}*(Motion.TripLeafLift-1.4 mm)')
        o.setExpression('Width','sqrt(DeltaY^2+DeltaZ^2)+0.1 mm')
        o.Placement.Rotation=App.Rotation(V(1,0,0),0)
        o.setExpression('Placement.Rotation.Axis.x','1');o.setExpression('Placement.Rotation.Axis.y','0');o.setExpression('Placement.Rotation.Axis.z','0')
        o.setExpression('Placement.Rotation.Angle','atan2(DeltaZ;DeltaY)')
        o.addProperty('App::PropertyColor','DisplayColour','Presentation');o.DisplayColour=b.COLORS['latch']
    foot=b.feature(d,'PickupTripFoot','Trip contact toe — compresses leaf against fixed post',
        Part.makeBox(2.0,.55,1.2,V(29.8,-.275,25.4)),trip_group,'latch')
    foot.setExpression('Placement.Base.y','Motion.TripCompression')
    foot.setExpression('Placement.Base.z','Motion.TripLeafLift')
    # Keep the reserved upper spring seat fixed while the coil envelope
    # compresses. Both cylinders use saved native expressions.
    tools=[]
    for name,radius in [('PickupSpringOuter',1.5),('PickupSpringBore',.95)]:
        cylinder=d.addObject('Part::Cylinder',name);upper.addObject(cylinder)
        cylinder.Radius=radius;cylinder.Placement.Base=b.polar(B_GUIDE,B_ANGLE,28.6)
        cylinder.setExpression('Placement.Base.z','28.6 mm+Motion.PickupPawlLift')
        cylinder.setExpression('Height','4.4 mm-Motion.PickupPawlLift');tools.append(cylinder)
    spring=d.addObject('Part::Cut','PickupBiasSpringEnvelope');upper.addObject(spring)
    spring.Base,spring.Tool=tools
    spring.Label='B downward-bias spring reservation — selected spring and forces open'
    spring.addProperty('App::PropertyColor','DisplayColour','Presentation');spring.DisplayColour=b.COLORS['guide']
    spring.addProperty('App::PropertyString','GeometryRole','Study');spring.GeometryRole='SPACE_CLAIM_ONLY'
    # Separate shell and carrier: install carrier/pawls first, slide the
    # removable reset bridge in radially, then fasten the outer shell.
    shell=b.cap_shape('shell').cut(cap_clearance())
    carrier=b.union([b.cap_shape('carrier'),cap_supports()])
    for x in (-14,14):
        point=V(x,-2,0)
        boss=b.cylinder(2.6,3.6,point+V(0,0,29.4))
        spoke=Part.makeBox(14,3.0,1.3,V(-14 if x<0 else 0,-3.5,31.7))
        carrier=b.union([carrier,boss,spoke]).cut(b.cylinder(.85,3.8,point+V(0,0,29.2)))
        pad=b.cylinder(3.3,1.9,point+V(0,0,33.0))
        shell=b.union([shell,pad])
        shell=shell.cut(b.cylinder(2.8,3.8,point+V(0,0,29.2)))
        shell=shell.cut(b.cylinder(1.15,8,point+V(0,0,32.9)))
        shell=shell.cut(Part.makeCone(1.15,2.1,.95,point+V(0,0,35.05)))
        shell=shell.cut(b.cylinder(2.1,7,point+V(0,0,36.0)))
        screw=b.union([b.cylinder(1,5.1,point+V(0,0,29.8)),
                       Part.makeCone(1,1.9,.9,point+V(0,0,34.9))])
        screw=screw.cut(b.socket_cut(.72,35.3,.8,point))
        b.feature(d,'UpperShellScrew'+('Left' if x<0 else 'Right'),
                  'M2 x 6 countersunk — detachable upper shell',screw,upper,'gear')
    # A long service window permits the fixed bridge screw to be inserted
    # before fitting the shell; it also clears the fixed hardware in motion.
    shell=shell.cut(carrier).removeSplitter()
    pieces=sorted(shell.Solids,key=lambda s:s.Volume,reverse=True)
    if sum(s.Volume for s in pieces[1:])>1e-5:
        raise RuntimeError('V7 upper shell has a detached meaningful component')
    d.UpperLobe.Shape=pieces[0]
    b.feature(d,'UpperCarrier','Separate keyed/input carrier — shell attaches with two M2 screws',carrier,upper,'cap')
    # Cover opens over both concentric tracks for axial assembly. Its click
    # root remains attached outside this larger opening.
    d.GearGuard.Shape=d.GearGuard.Shape.cut(b.cylinder(20.35,4,V(0,0,20.0)))
    pad=b.cylinder(3.1,4.2,ROOF_MOUNT+V(0,0,17.5))
    bridge=b.angular_sector(30.4,39.1,ROOF_MOUNT_ANGLE-5,ROOF_MOUNT_ANGLE+5,20.85,.85)
    guard=b.union([d.GearGuard.Shape,pad,bridge])
    guard=guard.cut(b.cylinder(.85,4.2,ROOF_MOUNT+V(0,0,17.9)))
    guard=guard.cut(b.cylinder(.75,.8,ROOF_MOUNT+b.polar(2,ROOF_MOUNT_ANGLE+90)+V(0,0,20.9)))
    d.GearGuard.Shape=guard
    screw=b.union([b.cylinder(1,9.1,ROOF_MOUNT+V(0,0,18.4)),
                   Part.makeCone(1,1.9,.9,ROOF_MOUNT+V(0,0,27.5))])
    screw=screw.cut(b.socket_cut(.72,27.9,.8,ROOF_MOUNT))
    b.feature(d,'PickupRoofScrew','M2 x 10 countersunk — removable pickup reset bridge',screw,fixed,'gear')
    return dict(track=track,roof=roof)
