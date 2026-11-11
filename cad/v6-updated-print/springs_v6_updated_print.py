"""Native hardware springs, fixed cup and a one-piece folded detent.

All motion survives a normal reopen without Python proxies. The prescribed
spring geometry describes installation and load paths, not elastic equilibrium.
"""
import math
import FreeCAD as App
import Part
import bracelet_v6_updated_print as b

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


def present(d):
    for o in d.Objects:
        if o.Name.startswith(('FlexureWeb','FlexureBend','ReturnCoil','ReturnWire','PawlCoil','PawlWire')):
            o.ViewObject.Visibility=False
    for name in ('CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg','PawlBiasSpring',
                 'PawlSpringLowerSeat','PawlSpringUpperSeat','ReturnSpringHousing','DetentFlexure'):
        o=d.getObject(name);o.ViewObject.Visibility=True;o.ViewObject.Transparency=0


