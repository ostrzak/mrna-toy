"""Two standard TECH-AR torsion springs, with printed reaction paths.

MS/095P TYP2 returns the upper through a tangent contact on its inner peg.
MS/095L TYP1 lies horizontally in the upper and presses the guided pawl down.
Supplier dimensions are nominal; force estimates and snap installation need
physical trials. Native expressions survive reopening without this module.
"""
import math
import FreeCAD as App
import Part
import bracelet_v6_updated_print as b
from springs_v6_updated_print import colour,note

V=App.Vector
R,WIRE=2.95,.6
CAP_C=V(-16,16,0)
PEG=b.polar(11.5,135)
CONTACT_OFFSET=R-.6-WIRE/2
CAP_PHI0=math.degrees(math.atan2(PEG.y-CAP_C.y,PEG.x-CAP_C.x)-math.asin(CONTACT_OFFSET/(PEG-CAP_C).Length))
CAP_PRELOAD=23.0
CAP_GAMMA=CAP_PHI0-180-CAP_PRELOAD
CAP_FIXED_PHI=CAP_GAMMA-90
PAWL_U=V(.608,.794,0);PAWL_U.normalize()
PAWL_AXIS=V(-PAWL_U.y,PAWL_U.x,0)
TARGET=b.polar(17.7,b.ENTRY_DEG)
PAWL_C=TARGET-PAWL_U*16.2-PAWL_AXIS*.85;PAWL_C.z=29.35
PAWL_FRAME=App.Rotation(PAWL_U,V(0,0,-1),PAWL_AXIS,'ZXY')
PAWL_REST=math.degrees(math.atan2(1.25,16.2)-math.asin((R+.8)/math.hypot(16.2,1.25)))
PAWL_PRELOAD=15.5
PAWL_GAMMA=PAWL_REST+90+PAWL_PRELOAD


def unit(degrees):
    a=math.radians(degrees);return V(math.cos(a),math.sin(a),0)


def rod(a,c,r=.3):
    v=c-a;return b.cylinder(r,v.Length,a,v/v.Length)


def cap_leg_pose(angle):
    p=App.Rotation(V(0,0,1),-angle).multVec(PEG);q=p-CAP_C
    phi=math.degrees(math.atan2(q.y,q.x)-math.asin(CONTACT_OFFSET/q.Length))
    return phi,p


def cap_upper_support():
    arm=b.angular_sector(4.5,12.2,131,139,30.4,1.2)
    peg=b.cylinder(.6,1.8,V(PEG.x,PEG.y,31.5))
    return arm.fuse(peg).removeSplitter()


def bias_clearance():
    return b.cylinder(3.45,5.6,PAWL_C-PAWL_AXIS*2.8,PAWL_AXIS)


def return_cup_relief():
    """Lower only the outer cup wall by 0.3 mm at the upper's full stroke.

    The floor, split mandrel and fixed-leg socket remain unchanged.
    """
    return b.annulus(3.5,4.31,31.3,.4).translated(CAP_C)


def coil(d,name,parent,origin,frame,gamma,turns_expr,height_expr,left=False):
    path=d.addObject('Part::Helix',name+'Path');parent.addObject(path)
    path.Radius=R;path.setExpression('Height',height_expr)
    path.setExpression('Pitch',f'({height_expr})/({turns_expr})')
    if left:
        path.LocalCoord='Left-handed'
        path.Placement=App.Placement(origin,frame.multiply(App.Rotation(V(0,0,1),gamma)))
        spine=path
    else:
        path.Placement=App.Placement(origin,frame.multiply(App.Rotation(V(0,0,1),gamma)))
        spine=path
    # A conservative annular envelope makes the stock coil's occupied space
    # explicit. The native helix remains as a hidden wire-centreline reference.
    # It avoids misleading Boolean results at coincident helical wire ends.
    axis=frame.multVec(V(0,0,1))
    outer=d.addObject('Part::Cylinder',name+'Outer');parent.addObject(outer)
    outer.Radius=3.27;outer.setExpression('Height',name+'Path.Height+0.6 mm')
    outer.Placement=App.Placement(origin-axis*.3,frame)
    inner=d.addObject('Part::Cylinder',name+'Bore');parent.addObject(inner)
    inner.Radius=2.55;inner.setExpression('Height',name+'Path.Height+0.8 mm')
    inner.Placement=App.Placement(origin-axis*.4,frame)
    spring=d.addObject('Part::Cut',name);parent.addObject(spring)
    spring.Base=outer;spring.Tool=inner;colour(spring)
    note(spring,'NONPRINTED_STOCK_COIL_ENVELOPE','1.4310 stainless; stock 0.6 wire / 6.5 OD / 5.3 ID / 5 mm body',
         'Conservative 6.54 OD / 5.10 ID annular coil envelope; hidden helix is the wire-centreline reference. Explicit terminals show reactions. Forces and physical fit remain unqualified.')
    return spring,path



def add_springs(d,fixed,click):
    m=d.Motion
    for name in ('ReturnLegAngle','ReturnSpringStrain','PawlSpringAngle','PawlSpringStrain'):
        m.addProperty('App::PropertyAngle',name,'Stock springs')
    a='(Motion.CapAngle * 1 deg)'
    qx=f'({PEG.x:.16g}*cos({a})+{PEG.y:.16g}*sin({a})+16)'
    qy=f'(-{PEG.x:.16g}*sin({a})+{PEG.y:.16g}*cos({a})-16)'
    m.setExpression('ReturnLegAngle',f'atan2({qy};{qx})-asin({CONTACT_OFFSET}/sqrt({qx}^2+{qy}^2))')
    m.setExpression('ReturnSpringStrain',f'{CAP_PRELOAD-CAP_PHI0} deg+ReturnLegAngle')
    m.setExpression('PawlSpringAngle',f'atan2(3.25-PawlLift/1 mm;16.2)-asin({R+.8}/sqrt(16.2^2+(3.25-PawlLift/1 mm)^2))')
    m.setExpression('PawlSpringStrain',f'{PAWL_REST+PAWL_PRELOAD} deg-PawlSpringAngle')

    # Vertical right-hand return spring. A short fixed leg seats in the cup;
    # the long moving leg slides tangentially along the upper's rounded peg.
    p0=CAP_C+R*unit(CAP_GAMMA)+V(0,0,27.8)
    direction=unit(CAP_FIXED_PHI);end=p0+direction*3.5
    cup=b.union([b.cylinder(3.8,5.8,CAP_C+V(0,0,21.4)),
        b.cylinder(4.3,.8,CAP_C+V(0,0,26.7)),
        b.annulus(3.5,4.3,26.7,4.9).translated(CAP_C),
        b.cylinder(2.2,6.1,CAP_C+V(0,0,26.7)),
        Part.makeCone(2.75,2.2,.5,CAP_C+V(0,0,32.8)),
        b.cylinder(1.2,1.9,V(end.x,end.y,26.7))])
    # Split retaining tip: elastic installation is a physical-test boundary.
    cup=cup.cut(Part.makeBox(.8,6,5.5,CAP_C+V(-.4,-3,28.3)))
    cup=cup.cut(rod(p0-direction*.2,end+direction*.1,.43))
    cup=cup.cut(return_cup_relief()).removeSplitter()
    o=b.feature(d,'ReturnSpringHousing','Integral stock return-spring cup, split mandrel and stator socket',cup,fixed,'lid')
    note(o,'INTEGRAL_WITH_GEAR_GUARD','PETG Translucent','Cup reacts spring torque into cover. Split mandrel tip retains the coil axially; snap deflection requires a coupon.')
    spring,path=coil(d,'CapReturnSpring',fixed,CAP_C+V(0,0,27.8),App.Rotation(),CAP_GAMMA,
        '7.25+Motion.ReturnSpringStrain/(360 deg)','4.4 mm+0.6 mm*Motion.ReturnSpringStrain/(360 deg)')
    spring.Label='Stock MS/095P TYP2 — right-hand cap return, 23 degree proposed preload'
    b.feature(d,'CapFixedSpringLeg','Trimmed fixed return leg — reacts into cup socket',rod(p0-direction*.18,end),fixed,(.76,.79,.84))
    joint=b.group(d,'ReturnLegJoint','Native tangent leg angle');fixed.addObject(joint)
    joint.Placement.Base=CAP_C;joint.setExpression('Placement.Rotation.Angle','Motion.ReturnLegAngle')
    leg=b.feature(d,'CapMovingSpringLeg','Return spring moving leg — tangent sliding contact on upper peg',
        b.cylinder(.3,14.68,V(-.18,R,0),V(1,0,0)),joint,(.76,.79,.84))
    leg.setExpression('Placement.Base.z','27.8 mm+CapReturnSpringPath.Height')

    # Horizontal left-hand stock spring in the upper: its 16 mm free leg
    # presses the pawl's integral annular pad while the original guide slides.
    lower=PAWL_C-PAWL_AXIS*2.2
    spring,path=coil(d,'PawlBiasSpring',click,lower,PAWL_FRAME,PAWL_GAMMA,
        '7+Motion.PawlSpringStrain/(360 deg)','4.4 mm+0.6 mm*Motion.PawlSpringStrain/(360 deg)',True)
    spring.Label='Stock MS/095L TYP1 — horizontal pawl-bias torsion spring'
    profile_start=V(R*math.cos(math.radians(PAWL_GAMMA)),R*math.sin(math.radians(PAWL_GAMMA)),0)
    fixed_direction=unit(PAWL_GAMMA+90)
    start=lower+PAWL_FRAME.multVec(profile_start)
    finish=start+PAWL_FRAME.multVec(fixed_direction)*6
    b.feature(d,'PawlFixedSpringLeg','Trimmed fixed pawl-spring leg in upper socket',
        b.union([rod(start-PAWL_FRAME.multVec(fixed_direction)*.18,finish),Part.makeSphere(.31,start)]),click,(.76,.79,.84))

    shaft=b.cylinder(2,7.1,PAWL_C-PAWL_AXIS*3.5,PAWL_AXIS)
    shaft=shaft.fuse(Part.makeCone(2.75,2,1,PAWL_C+PAWL_AXIS*2.8,PAWL_AXIS))
    slit=Part.makeBox(6,.8,6.2,V(-3,-.4,-1.9))
    slit.Placement=App.Placement(PAWL_C,PAWL_FRAME)
    shaft=shaft.cut(slit)
    post_base=PAWL_C-PAWL_AXIS*3.6
    post=b.cylinder(1.6,4.2,post_base)
    clearance=b.cylinder(3.6,5.6,PAWL_C-PAWL_AXIS*2.8,PAWL_AXIS)
    mount=post.cut(clearance).fuse(shaft).removeSplitter()
    o=b.feature(d,'PawlSpringUpperSeat','Upper-integral stock-spring support and split retaining shaft',mount,click,'cap')
    note(o,'INTEGRAL_WITH_UPPER_LOBE','PETG Translucent','Single supported shaft permits coil installation from its free split tip. Fixed leg seats in a separate integral socket. Physical snap/assembly trial required.')
    anchor=b.cylinder(1.25,31.3-finish.z,V(finish.x,finish.y,finish.z))
    bridge=Part.makeBox(max(1,finish.x-.8),2.2,1.2,V(1.5,finish.y-1.1,30.4))
    anchor=anchor.fuse(bridge).cut(rod(finish-PAWL_FRAME.multVec(fixed_direction)*2,
        finish+PAWL_FRAME.multVec(fixed_direction)*.1,.43)).removeSplitter()
    b.feature(d,'PawlFixedSpringSeat','Upper-integral pawl-spring fixed-leg socket',anchor,click,'cap')
    frame=b.group(d,'PawlSpringFrame','Native horizontal spring frame');click.addObject(frame)
    frame.Placement=App.Placement(PAWL_C+PAWL_AXIS*2.2,PAWL_FRAME)
    joint=b.group(d,'PawlSpringLegJoint','Native pawl spring tip angle');frame.addObject(joint)
    joint.setExpression('Placement.Rotation.Angle','Motion.PawlSpringAngle')
    leg=b.feature(d,'PawlMovingSpringLeg','Pawl-bias free leg — presses printed annular pad',
        b.union([b.cylinder(.3,16.88,V(-.18,R,0),V(1,0,0)),
            Part.makeSphere(.31,V(0,R,0)),Part.makeSphere(.3,V(16.7,R,0))]),joint,(.76,.79,.84))
    leg.setExpression('Placement.Base.z','0.6 mm*Motion.PawlSpringStrain/(360 deg)')
    centre=b.polar(17.7,b.ENTRY_DEG)
    pad=b.union([b.annulus(.95,1.85,0,.25),
        Part.makeSphere(.5,PAWL_AXIS*1.35+V(0,0,.1))]).cut(b.cylinder(.95,2,V(0,0,-.5)))
    pad.translate(V(centre.x,centre.y,0))
    o=b.feature(d,'PawlSpringLowerSeat','Pawl-integral spring contact pad',pad,click,'pawl')
    o.setExpression('Placement.Base.z','26 mm+Motion.PawlLift')
    note(o,'INTEGRAL_WITH_INPUT_PAWL','PETG Translucent','Horizontal spring free end presses this pad down. Its annulus clears the unchanged vertical guide pin.')


def present(d):
    for o in d.Objects:
        if o.Name.endswith(('Path','Profile','Outer','Bore')) or o.Name.endswith('LeftPath'):
            if o.Name.startswith(('CapReturnSpring','PawlBiasSpring')):o.ViewObject.Visibility=False


def audit(d,overlap,strokes=(0,.25,.5,.75,1)):
    old=(d.Motion.BeadSteps,d.Motion.CapStroke,d.Motion.CapReturning,d.Motion.StrandClosed)
    tests={};worst={};rows=[]
    try:
        for stroke in strokes:
            for returning in (False,True):
                d.Motion.BeadSteps=0;d.Motion.CapStroke=stroke;d.Motion.CapReturning=returning;d.recompute()
                objects=('CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg',
                    'PawlBiasSpring','PawlFixedSpringLeg','PawlMovingSpringLeg')
                shapes={n:b.world(d.getObject(n)) for n in objects}
                for n,s in shapes.items():
                    tests[n+' valid '+str((stroke,returning))]=s.isValid() and len(s.Solids)==1
                    for host in ('UpperLobe','DriveCarrier','GearGuard','ReturnSpringHousing','PawlSpringUpperSeat','PawlFixedSpringSeat'):
                        value=overlap(s,b.world(d.getObject(host)))
                        worst[n+'/'+host]=max(value,worst.get(n+'/'+host,0))
                for a in ('CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg'):
                    for c in ('PawlBiasSpring','PawlFixedSpringLeg','PawlMovingSpringLeg'):
                        key=a+'/'+c;worst[key]=max(overlap(shapes[a],shapes[c]),worst.get(key,0))
                pad=b.world(d.PawlSpringLowerSeat)
                tip=shapes['PawlMovingSpringLeg']
                gap=tip.distToShape(pad)[0]
                tests['pawl spring tip seated '+str((stroke,returning))]=gap<.01 and overlap(tip,pad)<1e-5
                for a,c in (('CapReturnSpring','CapFixedSpringLeg'),('CapReturnSpring','CapMovingSpringLeg'),
                    ('PawlBiasSpring','PawlFixedSpringLeg'),('PawlBiasSpring','PawlMovingSpringLeg')):
                    tests[a+'/'+c+' enters coil envelope '+str((stroke,returning))]=overlap(shapes[a],shapes[c])>1e-5
                rows.append(dict(stroke=stroke,returning=returning,pawl_tip_gap_mm=gap,
                    cap_spring_strain_degrees=d.Motion.ReturnSpringStrain.Value,
                    pawl_spring_strain_degrees=d.Motion.PawlSpringStrain.Value))
        tests['stock springs clear printed hosts']=max(worst.values(),default=0)<1e-5
    finally:
        d.Motion.BeadSteps,d.Motion.CapStroke,d.Motion.CapReturning,d.Motion.StrandClosed=old;d.recompute()
    return dict(passed=all(tests.values()),checks=tests,sampled_poses=rows,maximum_host_overlap_mm3=worst,
        representation='CONSERVATIVE_ANNULAR_COIL_ENVELOPES_WITH_NATIVE_HELIX_REFERENCES',
        boundary='Stock coil envelope dimensions, prescribed torsion/leg poses, geometric contact and host clearance only. Actual rates, clipped ends, installation, split-tip snap fits, friction, fatigue and reliable feeding require physical trials.')
