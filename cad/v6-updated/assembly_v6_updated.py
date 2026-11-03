"""Actual-solid V6 updated fastening and load-path witnesses, separate from motion.

Thread cylinders are nominal major-diameter envelopes. These checks establish
geometric seating/clearance, not printed thread strength or clamp preload.
"""
import math
import FreeCAD as App
import Part
import bracelet_v6_updated as b

V=App.Vector
TOL=1e-5


def ring(x,y,inner,outer,z,height):
    s=b.annulus(inner,outer,z,height);s.translate(V(x,y,0));return s


def allowed_thread(pair):
    names=set(pair)
    if 'LowerBody' in names and any(n.startswith('HousingScrew') for n in names):
        name=next(n for n in names if n.startswith('HousingScrew'))
        x,y=b.CASE_MOUNTS[int(name[-2:])]
        return name,b.cylinder(1.001,4.20001,V(x,y,9.3))
    if names=={'CentreAxle','CapRetainer'}:
        return 'CapRetainer',b.cylinder(1.001,3.40001,V(0,0,30.15))
    return None


INTEGRAL_PAIRS=({'LowerBody','CentreAxle'},{'GearGuard','DetentAnchor'},{'GearGuard','ReturnSpringHousing'})


def run(d,overlap):
    shapes={n:b.world(d.getObject(n)) for n in ('LowerBody','LowerLid','BeadKeeper','GearGuard',
        'CentreAxle','CapRetainer','CapWasher','DetentAnchor','ReturnSpringHousing')}
    tests={};records=[]
    def contained(name,tool,host):
        missing=max(0,tool.cut(host).Volume);common=tool.common(host)
        tests[name]=missing<TOL and abs(common.Volume-tool.Volume)<TOL and common.isValid()
        return max(missing,abs(common.Volume-tool.Volume))
    for i,(x,y) in enumerate(b.CASE_MOUNTS):
        name=f'HousingScrew{i:02}';s=b.world(d.getObject(name));body=shapes['LowerBody']
        entry=dict(name=name,axis_xy_mm=[x,y],nominal_screw='M2 x 12 countersunk',
            tip_z_mm=round(s.optimalBoundingBox(False).ZMin,6),
            head_top_z_mm=round(s.optimalBoundingBox(False).ZMax,6),
            nominal_pilot_engagement_mm=4.2,pilot_bottom_clearance_mm=.4,
            head_recess_below_cover_mm=.4)
        host_clear={}
        shaft=b.cylinder(1.02,6.88,V(x,y,13.51))
        for n in ('BeadKeeper','LowerLid','GearGuard'):
            host_clear[n]=overlap(shaft,shapes[n])
        tests[name+' unobstructed coaxial passage']=max(host_clear.values())<TOL
        entry['shaft_passage_overlap_mm3']=host_clear
        section=shapes['LowerLid'].common(Part.makeBox(8,4.5,16,V(x-4,y,8)))
        tests[name+' local section preserves screw column']=section.isValid() and section.Volume>90
        entry['actual_lid_column_half_section_volume_mm3']=section.Volume
        pilot_ring=ring(x,y,1.05,2.25,9.5,3.8)
        entry['pilot_wall_witness_missing_mm3']=contained(name+' continuous pilot wall',pilot_ring,body)
        # Each bearing has finite area on both sides of its actual plane.
        seats=[]
        for label,z,below,above in (
            ('body / keeper',13.5,'LowerBody','BeadKeeper'),
            ('keeper / lid',14.6,'BeadKeeper','LowerLid'),
            ('lid / cover',20.25,'LowerLid','GearGuard')):
            a=ring(x,y,1.25,3.1,z-.05,.04);c=ring(x,y,1.25,3.1,z+.01,.04)
            missing_a=contained(name+' '+label+' lower seat',a,shapes[below])
            missing_c=contained(name+' '+label+' upper seat',c,shapes[above])
            seats.append(dict(interface=label,z_mm=z,verified_bearing_area_mm2=math.pi*(3.1**2-1.25**2),
                              missing_lower_mm3=missing_a,missing_upper_mm3=missing_c))
        entry['clamped_stack_seats']=seats
        head=s.common(b.cylinder(3,.8,V(x,y,20.6)))
        gap=head.distToShape(shapes['GearGuard'])[0]
        tests[name+' conical head seated']=gap<1e-6 and overlap(head,shapes['GearGuard'])<TOL
        entry['head_to_seat_gap_mm']=gap
        thread_volume=overlap(s,body)
        tests[name+' thread envelope engages pilot']=thread_volume>1
        entry['intentional_thread_envelope_overlap_mm3']=thread_volume
        wall=ring(x,y,2.4,3.1,20.4,1.2)
        entry['cover_wall_witness_missing_mm3']=contained(name+' continuous cover wall',wall,shapes['GearGuard'])
        access=b.cylinder(1,25,V(x,y,21.31))
        entry['driver_access_overlap_cap_removed_mm3']={n:overlap(access,shapes[n]) for n in
            ('LowerBody','LowerLid','BeadKeeper','GearGuard','CentreAxle')}
        tests[name+' driver access with cap removed']=max(entry['driver_access_overlap_cap_removed_mm3'].values())<TOL
        records.append(entry)
    connections=[]
    for pair in INTEGRAL_PAIRS:
        a,c=sorted(pair);volume=overlap(shapes[a],shapes[c]);fused=shapes[a].fuse(shapes[c])
        ok=volume>1e-3 and fused.isValid() and len(fused.Solids)==1
        tests[a+' integral connection to '+c]=ok
        connections.append(dict(features=[a,c],positive_overlap_mm3=volume,
                                fused_solid_count=len(fused.Solids),fused_valid=fused.isValid()))
    # Washer clamps the fixed spindle. It must not clamp the moving cap.
    washer=shapes['CapWasher'];axle=shapes['CentreAxle'];bolt=shapes['CapRetainer']
    washer_gap=washer.distToShape(axle)[0]
    head=bolt.common(b.cylinder(2,1.7,V(0,0,34.15)))
    head_gap=head.distToShape(washer)[0]
    tests['cap washer seated on fixed spindle']=washer_gap<1e-7
    tests['cap screw head seated on washer']=head_gap<1e-7
    tests['cap screw thread envelope engages pilot']=overlap(bolt,axle)>1
    cap=b.world(d.UpperLobe).common(b.annulus(3.5,4,32,2))
    endplay=washer.distToShape(cap)[0]
    tests['cap positive axial endplay']=abs(endplay-.15)<1e-6
    bore_clear=overlap(b.cylinder(.8,.39,V(0,0,29.71)),axle)
    tests['cap screw blind pilot bottom clearance']=bore_clear<TOL
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
        cap=['UpperLobe','DriveCarrier'])
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
        cap_retainer=dict(nominal_screw='M2 x 4 pan head',separate_washer=True,
            washer_to_fixed_shoulder_gap_mm=washer_gap,screw_head_to_washer_gap_mm=head_gap,
            actual_cap_axial_endplay_mm=endplay,nominal_thread_engagement_mm=3.4,
            intentional_thread_overlap_mm3=overlap(bolt,axle)),
        boundary='Actual coaxial passages, continuous wall/seat witnesses, head seating, access with upper cap removed, integral roots, fixed-spindle retention, keyed rotor fit/torque witnesses and sampled rigid vertical insertions. Threads are major-diameter envelopes. Printed fits, key backlash, insertion under friction/compliance, screw standard selection, preload, stripping, stiffness and strength need physical qualification.')
