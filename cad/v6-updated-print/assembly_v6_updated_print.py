"""Actual-solid V6 updated print fastening and load-path witnesses, separate from motion.

Actual coarse threads are checked for fit, helical insertion and axial
blocking. This does not establish printed thread strength or clamp preload.
"""
import math
import FreeCAD as App
import Part
import bracelet_v6_updated_print as b

V=App.Vector
TOL=1e-5


def ring(x,y,inner,outer,z,height):
    s=b.annulus(inner,outer,z,height);s.translate(V(x,y,0));return s


def allowed_thread(pair):
    # Actual clearance-separated threads replace major-diameter envelopes.
    return None


INTEGRAL_PAIRS=({'LowerBody','CentreAxle'},{'GearGuard','DetentAnchor'},
    {'GearGuard','ReturnSpringHousing'},{'CapRetainer','CapWasher'},
    {'PawlSpringLowerSeat','DriveCarrier'},{'PawlSpringUpperSeat','UpperLobe'},
    {'PawlFixedSpringSeat','UpperLobe'})


def run(d,overlap):
    shapes={n:b.world(d.getObject(n)) for n in ('LowerBody','LowerLid','BeadKeeper','GearGuard',
        'CentreAxle','CapRetainer','CapWasher','DetentAnchor','ReturnSpringHousing',
        'DriveCarrier','UpperLobe','PawlSpringLowerSeat','PawlSpringUpperSeat','PawlFixedSpringSeat')}
    tests={};records=[]
    def contained(name,tool,host):
        missing=max(0,tool.cut(host).Volume)
        tests[name]=missing<TOL
        return missing
    for i,(x,y) in enumerate(b.CASE_MOUNTS):
        name=f'HousingScrew{i:02}';nut_name=f'HousingNut{i:02}'
        screw=b.world(d.getObject(name));nut=b.world(d.getObject(nut_name))
        body=shapes['LowerBody']
        passage=b.cylinder(2.01,6.8,V(x,y,13.51))
        host_clear={n:overlap(passage,shapes[n]) for n in ('BeadKeeper','LowerLid','GearGuard')}
        tests[name+' unobstructed coaxial passage']=max(host_clear.values())<TOL
        tests[name+' threaded fit clear']=overlap(screw,nut)<TOL
        tests[nut_name+' keyed pocket clear']=overlap(nut,body)<TOL
        wall=ring(x,y,3.46,3.75,8.5,3.3)
        contained(nut_name+' continuous pocket wall',wall,body)
        contained(name+' continuous upper post wall',ring(x,y,2.50,3.05,12.05,1.4),body)
        sections=[]
        for label,z,below,above in (('body / keeper',13.5,'LowerBody','BeadKeeper'),
            ('keeper / lid',14.6,'BeadKeeper','LowerLid'),('lid / cover',20.25,'LowerLid','GearGuard')):
            # The lower nut pocket leaves the upper post's bearing annulus.
            inner,outer=2.40,3.05
            a=ring(x,y,inner,outer,z-.05,.04);c=ring(x,y,inner,outer,z+.01,.04)
            missing=contained(name+' '+label+' lower seat',a,shapes[below])
            missing+=contained(name+' '+label+' upper seat',c,shapes[above])
            sections.append(dict(interface=label,missing_mm3=missing))
        bearing=ring(x,y,2.35,2.55,11.96,.04)
        contained(nut_name+' finite upper bearing annulus',bearing,nut)
        tests[nut_name+' seated under body shoulder']=nut.distToShape(body)[0]<1e-6
        load_overlap=[]
        for dz in (-12,-6,-2,0):
            moved=nut.copy();moved.translate(V(0,0,dz));load_overlap.append(overlap(moved,body))
        tests[nut_name+' sampled underside loading']=max(load_overlap)<TOL
        head=screw.common(b.cylinder(3.1,1.5,V(x,y,20)))
        gap=head.distToShape(shapes['GearGuard'])[0]
        tests[name+' conical head seated']=gap<1e-6 and overlap(screw,shapes['GearGuard'])<TOL
        turned=nut.copy();turned.rotate(V(x,y,0),V(0,0,1),10)
        tests[nut_name+' pocket prevents rotation']=overlap(turned,body)>.001
        shifted=screw.copy();shifted.translate(V(0,0,.45))
        tests[name+' threads resist axial pullout']=overlap(shifted,nut)>.001
        # Rotation plus pitch-matched translation must remain possible.
        helical=[]
        for degrees in (90,180,270):
            moved=screw.copy();moved.rotate(V(x,y,0),V(0,0,1),degrees)
            moved.translate(V(0,0,b.pf.CASE_PITCH*degrees/360))
            helical.append(overlap(moved,nut))
        tests[name+' sampled helical insertion']=max(helical)<TOL
        records.append(dict(name=name,axis_xy_mm=[x,y],material='PETG candidate',
            thread_major_diameter_mm=4,pitch_mm=1.2,replaceable_printed_nut=nut_name,
            passage_overlap_mm3=host_clear,stack_seats=sections,head_gap_mm=gap,
            sampled_helical_overlap_mm3=helical))
    connections=[]
    for pair in INTEGRAL_PAIRS:
        a,c=sorted(pair);volume=overlap(shapes[a],shapes[c]);fused=shapes[a].fuse(shapes[c])
        ok=volume>1e-3 and fused.isValid() and len(fused.Solids)==1
        tests[a+' integral connection to '+c]=ok
        connections.append(dict(features=[a,c],positive_overlap_mm3=volume,
                                fused_solid_count=len(fused.Solids),fused_valid=fused.isValid()))
    # The flange is an integral portion of the printed closed cap. Its roof
    # stops on the fixed spindle; the rocking upper retains positive endplay.
    washer=shapes['CapWasher'];axle=shapes['CentreAxle'];bolt=shapes['CapRetainer']
    full=washer.fuse(bolt)
    washer_gap=full.distToShape(axle)[0];head_gap=washer.distToShape(bolt)[0]
    tests['printed cap has one connected solid']=full.isValid() and len(full.Solids)==1
    tests['printed cap threads clear spindle']=overlap(full,axle)<TOL
    raised=full.copy();raised.translate(V(0,0,.6))
    tests['printed cap threads resist axial pullout']=overlap(raised,axle)>.001
    tests['closed cap roof seated on fixed spindle']=washer_gap<1e-6
    cap=b.world(d.UpperLobe).common(b.annulus(3.5,4.1,32,2))
    endplay=washer.distToShape(cap)[0]
    tests['cap positive axial endplay']=abs(endplay-.25)<1e-6
    lowered=full.copy();lowered.translate(V(0,0,-.1))
    tests['positive roof stop prevents clamping upper']=overlap(lowered,axle)>.01
    cap_helical=[]
    for angle in (90,180,270):
        moved=full.copy();moved.rotate(V(),V(0,0,1),angle)
        moved.translate(V(0,0,1.5*angle/360))
        cap_helical.append(overlap(moved,axle))
    tests['spindle cap sampled helical insertion']=max(cap_helical)<TOL
    # A seated CAD arrangement is insufficient if its rigid parts cannot be
    # inserted. Keep lower and upper rotor as two individually connected parts.
    lower=b.union([b.world(d.getObject(n)) for n in ('BeadDrum','DriveHub','TravelPin')])
    upper=b.union([b.world(d.getObject(n)) for n in ('RnaDriveGear','IndexSleeve','IndexWheel','FeedRatchet')])
    tests['lower rotor is one connected part']=lower.isValid() and len(lower.Solids)==1
    tests['upper rotor is one connected part']=upper.isValid() and len(upper.Solids)==1
    tests['two rotor parts have no rigid overlap']=overlap(lower,upper)<TOL
    key_region=b.cylinder(6.1,3,V(0,0,18.6))
    hub=b.world(d.DriveHub).common(key_region);socket=b.world(d.RnaDriveGear).common(key_region)
    key_contacts=[]
    for angle in (-5,5):
        moved=socket.copy();moved.rotate(V(),V(0,0,1),angle)
        key_contacts.append(dict(attempted_relative_degrees=angle,blocking_overlap_mm3=overlap(hub,moved)))
    tests['D key transmits torque in both directions']=all(v['blocking_overlap_mm3']>.001 for v in key_contacts)
    # Cap screws are installed last. The cover's own click leaf/root are one
    # component during insertion; its prescribed home deflection is retained.
    cover=b.union([shapes['GearGuard'],shapes['DetentAnchor'],b.world(d.DetentTip)]+
                  [b.world(d.DetentFlexure),shapes['ReturnSpringHousing']])
    tests['cover and click leaf form one connected part']=cover.isValid() and len(cover.Solids)==1
    groups=dict(body=['LowerBody','CentreAxle'],lower=['BeadDrum','DriveHub','TravelPin'],
        keeper=['BeadKeeper'],lid=['LowerLid'],upper=['RnaDriveGear','IndexSleeve','IndexWheel','FeedRatchet'],
        cover=['GearGuard','DetentAnchor','DetentTip','DetentFlexure','ReturnSpringHousing'],
        cap=['UpperLobe','DriveCarrier','PawlSpringLowerSeat','PawlSpringUpperSeat','PawlFixedSpringSeat'])
    actual={n:b.world(d.getObject(n)) for names in groups.values() for n in names}
    # Verified conservative envelopes avoid repeated Booleans against thousands
    # of tooth/fork faces. Use the actual key socket at the intentional hub fit.
    collision_shapes=dict(actual)
    collision_shapes['BeadDrum']=b.drum_sweep()
    collision_shapes['RnaDriveGear']=b.annulus(3.14,b.MODULE*(b.SUN_TEETH/2+1)+.01,b.GEAR_Z,b.GEAR_WIDTH)
    for n in ('BeadDrum','RnaDriveGear'):
        tests[n+' contained in insertion envelope']=actual[n].cut(collision_shapes[n]).Volume<TOL
    boxes={n:s.optimalBoundingBox(False) for n,s in collision_shapes.items()}
    operations=[('lower rotor','lower',['body']),('bead keeper','keeper',['body','lower']),
        ('lower lid','lid',['body','lower','keeper']),
        ('keyed upper rotor','upper',['body','lower','keeper','lid']),
        ('cover and integral click leaf','cover',['body','lower','keeper','lid','upper']),
        ('upper subunit and lifted input','cap',['body','lower','keeper','lid','upper','cover'])]
    insertions=[]
    for label,moving_group,targets in operations:
        worst=0.0;hits=[]
        for dz in (0,.1,.3,.6,1,2,4,8,16,32):
            for n in groups[moving_group]:
                q=boxes[n];box=App.BoundBox(q.XMin,q.YMin,q.ZMin+dz,q.XMax,q.YMax,q.ZMax+dz)
                for target in (p for group in targets for p in groups[group]):
                    if not box.intersect(boxes[target]):continue
                    moving_shape=collision_shapes[n];fixed_shape=collision_shapes[target]
                    if {n,target}=={'RnaDriveGear','DriveHub'}:
                        if n=='RnaDriveGear':moving_shape=socket
                        else:fixed_shape=socket
                    moved=moving_shape.copy();moved.translate(V(0,0,dz))
                    volume=overlap(moved,fixed_shape);worst=max(worst,volume)
                    if volume>TOL:hits.append(dict(lift_mm=dz,moving=n,target=target,overlap_mm3=volume))
        tests[label+' sampled vertical insertion']=worst<TOL
        insertions.append(dict(part=label,sampled_lifts_mm=[0,.1,.3,.6,1,2,4,8,16,32],
            maximum_unintended_overlap_mm3=worst,failures=hits))
        print('  assembly insertion '+label+': '+str(worst)+' mm3',flush=True)
    return dict(passed=all(tests.values()),checks=tests,housing_screws=records,
        integral_connections=connections,
        rotor_coupling=dict(two_connected_parts=True,nominal_D_key_radial_clearance_mm=.12,
            torque_blocking_witnesses=key_contacts),sampled_assembly_insertions=insertions,
        cap_retainer=dict(type='Printed coarse closed cap and integral flange',separate_washer=False,sampled_helical_overlap_mm3=cap_helical,
            washer_to_fixed_shoulder_gap_mm=washer_gap,screw_head_to_washer_gap_mm=head_gap,
            actual_cap_axial_endplay_mm=endplay,nominal_thread_engagement_mm=b.pf.CAP_STOP-b.pf.CAP_BOTTOM,
            intentional_thread_overlap_mm3=overlap(bolt,axle)),
        boundary='Actual coaxial passages, continuous wall/seat witnesses, head seating, access with upper cap removed, integral roots, fixed-spindle retention, keyed rotor fit/torque witnesses and sampled rigid vertical insertions. Actual coarse threads have radial and axial allowance; sampled rotation/translation and axial blocking are checked. Printed fits, key backlash, insertion under friction/compliance, screw standard selection, preload, stripping, stiffness and strength need physical qualification.')
