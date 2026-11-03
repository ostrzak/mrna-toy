"""Native hardware springs, fixed cup and a one-piece folded detent.

All motion survives a normal reopen without Python proxies. The prescribed
spring geometry describes installation and load paths, not elastic equilibrium.
"""
import math
import FreeCAD as App
import Part
import bracelet_v6_updated as b

V=App.Vector
METAL=(.76,.79,.84)


def colour(o,color=METAL):
    o.addProperty('App::PropertyColor','DisplayColour','Presentation')
    o.DisplayColour=color
    return o


def note(o,role,material,action):
    for name,value in [('GeometryRole',role),('MaterialIntent',material),('Action',action)]:
        o.addProperty('App::PropertyString',name,'Engineering');setattr(o,name,value)


def add_detent(d,parent):
    """Seven transverse webs with alternating round U-bends, printed flat.

    Local Y rows are 2 mm apart; 0.9 mm web and 2 mm height. The fixed root
    is row six. Smooth prescribed radial displacement falls to zero there.
    Native MultiFuse produces ONE connected solid, with hidden construction.
    """
    pieces=[]
    for j in range(7):
        o=d.addObject('Part::Box',f'FlexureWeb{j}');parent.addObject(o)
        left=15.15 if j==0 else 16.0
        right=20.2 if j==6 else 18.3
        o.Length=right-left+.16;o.Width=.9;o.Height=2
        o.Placement.Base=V(left-.08,-2*j-.45,22.2)
        o.setExpression('Placement.Base.x',f'{left-.08} mm+{1-j/6:.16g}*Motion.DetentFlex')
        pieces.append(o)
    for j in range(6):
        right=j%2==0;x=18.3 if right else 16.0
        w1,w2=1-j/6,1-(j+1)/6
        outer=d.addObject('Part::Cylinder',f'FlexureBendOuter{j}')
        inner=d.addObject('Part::Cylinder',f'FlexureBendInner{j}')
        for o,extra,height,z in [(outer,.45,2,22.2),(inner,-.45,2.4,22.0)]:
            parent.addObject(o);o.Height=height;o.Angle=180
            o.setExpression('Radius',f'sqrt(1+({(w1-w2)/2:.16g}*Motion.DetentFlex/1 mm)^2)*1 mm+{extra} mm')
            o.setExpression('Placement.Base.x',f'{x} mm+{(w1+w2)/2:.16g}*Motion.DetentFlex')
            o.Placement.Base.y=-2*j-1;o.Placement.Base.z=z
            expr=f'atan2(1;{(w1-w2)/2:.16g}*Motion.DetentFlex/1 mm)'
            if right:expr+='-180 deg'
            o.setExpression('Placement.Rotation.Angle',expr)
        bend=d.addObject('Part::Cut',f'FlexureBend{j}');parent.addObject(bend)
        bend.Base,bend.Tool=outer,inner;pieces.append(bend)
    leaf=d.addObject('Part::MultiFuse','DetentFlexure');parent.addObject(leaf)
    leaf.Shapes=pieces;leaf.Refine=True
    leaf.Label='One-piece serpentine detent: seven webs, six rounded folds'
    colour(leaf,b.COLORS['pawl'])
    note(leaf,'PRINTED_FLEXURE_CANDIDATE','Printed polymer; grade/process undecided',
         'Rounded follower moves radially over each notch; folded webs bend; root stays fixed. Prescribed poses, force/fatigue unqualified.')


def add_springs(d,fixed,click):
    # The fixed cup is integrated into the cover through a radial bridge to
    # its existing spring-stator post, above the rotor's complete axial sweep.
    cup=b.union([b.annulus(5.25,8.15,26.7,.8),
        b.annulus(5.25,6.05,26.7,3.65),b.annulus(7.35,8.15,26.7,3.65),
        b.angular_sector(6.9,18.7,-123,-117,26.7,.8)])
    cup=cup.cut(b.spring_leg(False,.4))
    cup=cup.cut(b.angular_sector(5.5,8.3,-120-b.CAP_ANGLE-5,-115,29.45,1.1))
    housing=b.feature(d,'ReturnSpringHousing','Fixed torsion-spring cup, mandrel and cover-rooted bridge',cup,fixed,'lid')
    note(housing,'INTEGRAL_WITH_GEAR_GUARD','Printed housing',
         'Floor supports coil; inner mandrel locates it; slotted outer cup contains it. Bridge joins fixed cover post. Open top permits installation before upper shell.')

    # A reflected native helix is left-handed. More cap travel adds winding;
    # mean radius contracts slightly to preserve the centreline length.
    helix=d.addObject('Part::Helix','ReturnCoilPath');fixed.addObject(helix)
    helix.Height=2.1
    helix.setExpression('Pitch','2.1 mm/(3+Motion.CapAngle/360)')
    helix.setExpression('Radius','6.75 mm*3/(3+Motion.CapAngle/360)')
    helix.Placement=App.Placement(V(0,0,27.8),App.Rotation(V(0,0,1),120))
    path=d.addObject('Part::Mirroring','ReturnCoilLeftHanded');fixed.addObject(path)
    path.Source=helix;path.Normal=V(0,1,0)
    profile=d.addObject('Part::Circle','ReturnWireProfile');fixed.addObject(profile)
    profile.Radius=.3
    profile.setExpression('Placement.Base.x','-.5*ReturnCoilPath.Radius')
    profile.setExpression('Placement.Base.y',f'{-math.sqrt(3)/2:.16g}*ReturnCoilPath.Radius')
    profile.Placement.Base.z=27.8
    profile.Placement.Rotation=App.Rotation(V(0,0,1),V(-math.sqrt(3)/2,.5,.018412))
    coil=d.addObject('Part::Sweep','CapReturnSpring');fixed.addObject(coil)
    coil.Sections=[profile];coil.Spine=(path,[]);coil.Solid=True;coil.Frenet=True
    colour(coil);coil.Label='Metal torsion spring: left-handed coil, 22 degree installed preload'
    note(coil,'NONPRINTED_HARDWARE_CANDIDATE','Spring steel, 0.6 mm wire / 13.5 mm mean diameter / three nominal turns',
         'Fixed lower leg reacts into the cover post. Upper leg follows the cap clockwise, winds the coil, then returns the cap counterclockwise. Never rewinds protein.')
    coil.addProperty('App::PropertyAngle','InstalledPreload','Engineering');coil.InstalledPreload=22
    for name,moving,parent in [('CapFixedSpringLeg',False,fixed),('CapMovingSpringLeg',True,click)]:
        leg=b.feature(d,name,('Moving upper' if moving else 'Fixed lower')+' torsion-spring terminal in its radial socket',b.spring_leg(moving),parent,METAL)
        note(leg,'SAME_HARDWARE_AS_CAP_RETURN_SPRING','Spring steel; terminal schematic',
             'Terminal roots lap the coil. End is captured by the '+('moving upper' if moving else 'stationary cover')+' socket. Bend details require spring fabrication review.')

    # Explicit annular end washers locate the compression spring around the
    # existing 1.5 mm guide pin. The spring body uses a native helix/sweep.
    centre=b.polar(17.7,b.ENTRY_DEG)
    for name,z,parent in [('PawlSpringLowerSeat',26.3,click),('PawlSpringUpperSeat',30.85,click)]:
        seat=b.annulus(.85,1.65,0,.15);seat.translate(V(centre.x,centre.y,z))
        o=b.feature(d,name,('Moving lower' if 'Lower' in name else 'Fixed upper')+' pawl spring seat washer',seat,parent,METAL)
        if 'Lower' in name:o.setExpression('Placement.Base.z','26.3 mm+Motion.PawlLift')
        note(o,'NONPRINTED_SEAT_WASHER','Metal washer candidate',
             'Lower washer bears on pawl; upper washer bears under cap carrier. Guide pin passes through the central bore.')
    axial=d.addObject('Part::Helix','PawlCoilPath');click.addObject(axial)
    axial.Radius=1.25
    axial.setExpression('Height','4.25 mm-Motion.PawlLift')
    axial.setExpression('Pitch','(4.25 mm-Motion.PawlLift)/8')
    axial.Placement.Base=V(centre.x,centre.y,26.525)
    axial.setExpression('Placement.Base.z','26.525 mm+Motion.PawlLift')
    section=d.addObject('Part::Circle','PawlWireProfile');click.addObject(section)
    section.Radius=.075;section.Placement.Base=V(centre.x+1.25,centre.y,26.525)
    section.setExpression('Placement.Base.z','26.525 mm+Motion.PawlLift')
    section.Placement.Rotation=App.Rotation(V(0,0,1),V(0,1,.04))
    spring=d.addObject('Part::Sweep','PawlBiasSpring');click.addObject(spring)
    spring.Sections=[section];spring.Spine=(axial,[]);spring.Solid=True;spring.Frenet=True
    colour(spring);spring.Label='Metal compression spring: pushes rigid pawl down onto face track'
    note(spring,'NONPRINTED_HARDWARE_CANDIDATE','Spring steel, 0.15 mm wire / 2.5 mm mean diameter / eight nominal active turns',
         'Cap carrier is the upper reaction seat. Pawl is the moving lower seat. Pawl lift compresses the coil; the fixed cam and tooth ramps lift against it.')


def present(d):
    for o in d.Objects:
        if o.Name.startswith(('FlexureWeb','FlexureBend','ReturnCoil','ReturnWire','PawlCoil','PawlWire')):
            o.ViewObject.Visibility=False
    for name in ('CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg','PawlBiasSpring',
                 'PawlSpringLowerSeat','PawlSpringUpperSeat','ReturnSpringHousing','DetentFlexure'):
        o=d.getObject(name);o.ViewObject.Visibility=True;o.ViewObject.Transparency=0


def audit(d,overlap):
    """Actual seats, coil clearances and connected flexure at sampled loads."""
    m=d.Motion;old=(m.BeadSteps,m.CapStroke,m.CapReturning,m.StrandClosed)
    rows=[];tests={};worst={}
    try:
        for step in (0,.25,.5,.75,1):
            for stroke in (0,.25,.5,.75,1):
                m.BeadSteps=step;m.CapStroke=stroke;m.CapReturning=False;d.recompute()
                coil=b.world(d.CapReturnSpring);bias=b.world(d.PawlBiasSpring)
                housing=b.world(d.ReturnSpringHousing)
                fused=b.union([b.world(d.getObject(n)) for n in ('DetentFlexure','DetentTip','DetentAnchor')])
                tests['connected serpentine at '+str((step,stroke))]=fused.isValid() and len(fused.Solids)==1
                outside_root=b.world(d.DetentFlexure).cut(b.world(d.DetentAnchor))
                tests['folded leaf clears cover outside root '+str((step,stroke))]=overlap(outside_root,b.world(d.GearGuard))<1e-5
                for n in ('CapReturnSpring','PawlBiasSpring','DetentFlexure'):
                    o=d.getObject(n);tests[n+' valid at '+str((step,stroke))]=o.Shape.isValid() and len(o.Shape.Solids)==1
                for n in ('UpperLobe','DriveCarrier','GearGuard','ReturnSpringHousing'):
                    for label,s in [('torsion',coil),('axial',bias)]:
                        value=overlap(s,b.world(d.getObject(n)))
                        key=label+'/'+n;worst[key]=max(worst.get(key,0),value)
                for n in ('CapFixedSpringLeg','CapMovingSpringLeg'):
                    tests[n+' connected to coil '+str(stroke)]=overlap(coil,b.world(d.getObject(n)))>1e-5
                    key=n+'/ReturnSpringHousing'
                    worst[key]=max(worst.get(key,0),overlap(b.world(d.getObject(n)),housing))
                for name in ('PawlSpringLowerSeat','PawlSpringUpperSeat'):
                    seat=b.world(d.getObject(name))
                    for host in ('UpperLobe','DriveCarrier','GearGuard','ReturnSpringHousing','FeedRatchet'):
                        key=name+'/'+host
                        worst[key]=max(worst.get(key,0),overlap(seat,b.world(d.getObject(host))))
                rows.append(dict(step=step,stroke=stroke,coil_mean_radius_mm=d.ReturnCoilPath.Radius.Value,
                    compression_coil_height_mm=d.PawlCoilPath.Height.Value,
                    housing_coil_clearance_mm=coil.distToShape(housing)[0],
                    lower_spring_seat_gap_mm=bias.distToShape(b.world(d.PawlSpringLowerSeat))[0],
                    upper_spring_seat_gap_mm=bias.distToShape(b.world(d.PawlSpringUpperSeat))[0]))
        tests['all hardware clear of rigid hosts']=max(worst.values())<1e-5
        tests['compression ends seated']=max(max(r['lower_spring_seat_gap_mm'],r['upper_spring_seat_gap_mm']) for r in rows)<.01
        tests['torsion coil supported by cup']=max(r['housing_coil_clearance_mm'] for r in rows)<.01
    finally:
        m.BeadSteps,m.CapStroke,m.CapReturning,m.StrandClosed=old;d.recompute()
    return dict(passed=all(tests.values()),checks=tests,sampled_poses=rows,maximum_host_overlap_mm3=worst,
        boundary='Geometric candidate hardware, seats, terminal connections and prescribed flexure poses. End coils/terminal bends are schematic; no supplier selection, elastic equilibrium, preload assembly under force or printed durability qualified.')
