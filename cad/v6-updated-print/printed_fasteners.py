"""Coarse, modelled PETG threads. Nominal fits need a physical coupon.

Use FreeCADCmd for helical Booleans, never the user's GUI process.
Male and female use the same helical phase with radial/axial allowance.
"""
from functools import lru_cache
import math
import FreeCAD as App
import Part

V=App.Vector
CASE_MAJOR=2.0
CASE_ROOT=1.42
CASE_PITCH=1.2
RADIAL_ALLOWANCE=.20
AXIAL_ALLOWANCE=.10
NUT_BOTTOM,NUT_TOP=8.4,12.0
CAP_BOTTOM,CAP_STOP,CAP_TOP=33.65,36.65,37.85


def cylinder(r,z,height):
    return Part.makeCylinder(r,height,V(0,0,z))


def thread(root,major,pitch,z0,height,clearance=0):
    """Trapezoidal ridge swept on a helix, joined to a continuous core."""
    r=root-.03
    points=[V(r,0,z0-.48*pitch-AXIAL_ALLOWANCE*bool(clearance)),
            V(major+clearance,0,z0-.14*pitch-AXIAL_ALLOWANCE*bool(clearance)),
            V(major+clearance,0,z0+.14*pitch+AXIAL_ALLOWANCE*bool(clearance)),
            V(r,0,z0+.48*pitch+AXIAL_ALLOWANCE*bool(clearance))]
    section=Part.makePolygon(points+[points[0]])
    # Explicit ruled sections avoid OCCT's multi-turn sweep C0 surface and
    # unreliable later unions. 24 sections/turn bound radial faceting below
    # 0.028 mm at the largest radius, well inside the 0.20 mm fit allowance.
    sections=[]
    count=math.ceil(height/pitch*24)
    for i in range(count+1):
        q=section.copy()
        q.rotate(V(),V(0,0,1),360*height/pitch*i/count)
        q.translate(V(0,0,height*i/count));sections.append(q)
    ridge=Part.makeLoft(sections,True,True)
    if clearance:
        # Stagger the female facet seams while keeping the same helix phase.
        # Coincident male/female ruled seams can make OCCT report a false zero
        # intersection during an attempted axial pullout.
        ridge.rotate(V(),V(0,0,1),7.5)
        ridge.translate(V(0,0,pitch*7.5/360))
    core=cylinder(root+clearance,z0-pitch, height+2*pitch)
    return core.fuse(ridge).removeSplitter()


def keyed_outline(z,height,allowance=0):
    return cylinder(3.2+allowance,z,height).common(
        Part.makeBox(6.4+2*allowance,5.2+2*allowance,height,
                     V(-3.2-allowance,-2.6-allowance,z)))


@lru_cache(maxsize=1)
def case_pair():
    male=thread(CASE_ROOT,CASE_MAJOR,CASE_PITCH,8.1,6.0)
    male=male.common(cylinder(2.1,8.5,5.0))
    # Revolve the smooth core/head as one solid before joining the thread.
    # Successive coincident-cylinder fuses can yield empty OCCT results here.
    points=[V(0,0,8.5),V(CASE_MAJOR,0,8.5),V(CASE_MAJOR,0,13.3),V(1.8,0,13.3),
            V(1.8,0,20.0),V(3,0,21.5),V(0,0,21.5)]
    core=Part.Face(Part.makePolygon(points+[points[0]])).revolve(V(),V(0,0,1),360)
    # Subtract the complementary groove from a one-piece blank. A fuse may
    # silently omit the threaded lower portion despite returning a valid core.
    groove=cylinder(2.1,8.5,5.0).cut(male)
    screw=core.cut(groove).removeSplitter()
    # A 1.0 mm wide straight driver slot is practical with a 0.4 mm nozzle.
    screw=screw.cut(Part.makeBox(7,1.0,.85,V(-3.5,-.5,20.7))).removeSplitter()
    cutter=thread(CASE_ROOT,CASE_MAJOR,CASE_PITCH,8.1,6.0,RADIAL_ALLOWANCE)
    nut=keyed_outline(NUT_BOTTOM,NUT_TOP-NUT_BOTTOM).cut(cutter).removeSplitter()
    return screw,nut


@lru_cache(maxsize=1)
def spindle_pair():
    # Running journal remains a smooth 6 mm diameter below the new thread.
    male=thread(2.38,3.0,1.5,32.9,7.5)
    male=male.common(cylinder(3.01,33.65,CAP_STOP-33.65))
    spindle=cylinder(3.0,1.0,32.65).fuse(
        Part.makeCone(4.5,3.0,1.8,V(0,0,2.4))).fuse(male).removeSplitter()
    cutter=thread(2.38,3.0,1.5,32.9,7.5,.20)
    cutter=cutter.common(cylinder(3.3,32,CAP_STOP-32))
    full=cylinder(4.1,CAP_BOTTOM,CAP_TOP-CAP_BOTTOM).cut(cutter)
    # Tool access in the closed top. Roof beneath it sets the axial stop.
    full=full.cut(Part.makeBox(9,1.2,.75,V(-4.5,-.6,CAP_TOP-.65))).removeSplitter()
    flange=full.common(cylinder(4.2,CAP_BOTTOM,.85))
    cap=full.common(cylinder(4.2,34.3,CAP_TOP-34.3))
    return spindle,cap,flange
