"""Actual-solid V7 fastening and load-path witnesses, separate from motion.

Thread cylinders are nominal major-diameter envelopes. These checks establish
geometric seating/clearance, not printed thread strength or clamp preload.
"""
import math
import FreeCAD as App
import Part
import bracelet_v7 as b
import coupling_v7 as c

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
    if names=={'DetentScrew','GearGuard'}:
        return 'DetentScrew',b.cylinder(1.001,1.50001,V(*b.DETENT_ROOT,20.85))
    return None


INTEGRAL_PAIRS=({'LowerBody','CentreAxle'},)


def run(d,overlap):
    shapes={n:b.world(d.getObject(n)) for n in ('LowerBody','LowerLid','BeadKeeper','GearGuard',
        'CentreAxle','CapRetainer','CapWasher','DetentAnchor')}
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
    cap=b.world(d.UpperCarrier).common(b.annulus(3.5,4,32,2))
    endplay=washer.distToShape(cap)[0]
    tests['cap positive axial endplay']=abs(endplay-.15)<1e-6
    bore_clear=overlap(b.cylinder(.8,.39,V(0,0,29.71)),axle)
    tests['cap screw blind pilot bottom clearance']=bore_clear<TOL
    # A seated CAD arrangement is insufficient if its rigid parts cannot be
    # inserted. Keep lower and upper rotor as two individually connected parts.
    lower=b.union([b.world(d.getObject(n)) for n in ('BeadDrum','DriveHub','TravelPin')])
    upper=b.union([b.world(d.getObject(n)) for n in ('RnaDriveGear','IndexSleeve','IndexWheel','FeedRatchet','PickupRatchet')])
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
    # The leaf cannot be lowered through the outer pickup track. Install it
    # radially beneath that track after seating the cover; clamp it separately.
    leaf=b.union([shapes['DetentAnchor'],b.world(d.DetentTip)]+
                  [b.world(d.getObject(f'DetentLeaf{i}')) for i in range(8)])
    tests['separate click leaf is one connected part']=leaf.isValid() and len(leaf.Solids)==1
    groups=dict(body=['LowerBody','CentreAxle'],lower=['BeadDrum','DriveHub','TravelPin'],
        keeper=['BeadKeeper'],lid=['LowerLid'],upper=['RnaDriveGear','IndexSleeve','IndexWheel','FeedRatchet','PickupRatchet'],
        cover=['GearGuard'],
        detent=['DetentAnchor','DetentTip']+[f'DetentLeaf{i}' for i in range(8)],
        cap=['UpperCarrier','DriveCarrier','PickupPawl','PickupFork','PickupLatchTip','PickupTripFoot']+[f'PickupLatchLeaf{i}' for i in range(8)]+[f'PickupTripLeaf{i}' for i in range(10)])
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
        ('cover before separate click leaf','cover',['body','lower','keeper','lid','upper']),
        ('upper subunit and lifted input','cap',['body','lower','keeper','lid','upper','cover','detent'])]
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
    radial_hits=[]
    direction=V(*b.DETENT_ROOT,0);direction.normalize()
    for offset in (32,16,8,4,2,1,.5,.2,0):
        q=leaf.copy();q.translate(direction*offset)
        for target in (p for group in ('body','lower','keeper','lid','upper','cover') for p in groups[group]):
            amount=overlap(q,collision_shapes[target])
            if amount>TOL:radial_hits.append(dict(offset_mm=offset,target=target,overlap_mm3=amount))
    tests['dedicated click leaf sampled radial insertion']=not radial_hits
    root=V(*b.DETENT_ROOT,0)
    seat=ring(root.x,root.y,1.25,1.8,22.30,.04)
    tests['detent root has finite cover bearing seat']=seat.cut(shapes['GearGuard']).Volume<TOL
    bolt=b.world(d.DetentScrew);washer=b.world(d.DetentWasher)
    mask=allowed_thread({'DetentScrew','GearGuard'})[1]
    tests['detent screw clears leaf and washer']=max(overlap(bolt,leaf),overlap(bolt,washer))<TOL
    tests['detent screw thread engages cover']=overlap(bolt,shapes['GearGuard'])>1
    tests['detent screw only overlaps allowed pilot']=overlap(bolt.cut(mask),shapes['GearGuard'])<TOL
    tests['detent washer seated on leaf']=washer.distToShape(leaf)[0]<1e-7
    tests['detent screw seated on washer']=bolt.distToShape(washer)[0]<1e-7
    result=dict(passed=all(tests.values()),checks=tests,housing_screws=records,
        integral_connections=connections,
        rotor_coupling=dict(two_connected_parts=True,nominal_D_key_radial_clearance_mm=.12,
            torque_blocking_witnesses=key_contacts),sampled_assembly_insertions=insertions,
        cap_retainer=dict(nominal_screw='M2 x 4 pan head',separate_washer=True,
            washer_to_fixed_shoulder_gap_mm=washer_gap,screw_head_to_washer_gap_mm=head_gap,
            actual_cap_axial_endplay_mm=endplay,nominal_thread_engagement_mm=3.4,
            intentional_thread_overlap_mm3=overlap(bolt,axle)),
        detent_assembly=dict(radial_insertion_failures=radial_hits,standard_screw='M2 x 3 pan head',washer_height_mm=.5,
            nominal_pilot_engagement_mm=1.5,leaf_height_mm=1,leaf_radial_thickness_mm=1.3),
        boundary='Actual coaxial passages, continuous wall/seat witnesses, head seating, access with upper cap removed, integral roots, fixed-spindle retention, keyed rotor fit/torque witnesses, sampled rigid vertical insertions and separate radial insertion of the dedicated leaf. Threads are major-diameter envelopes. Printed fits, key backlash, insertion under friction/compliance, screw standard selection, preload, stripping, stiffness and strength need physical qualification.')

    return augment(d,result,overlap)


def augment(d,result,overlap):
    tests=result['checks'];extra={}
    frame=b.world(d.UpperCarrier);shell=b.world(d.UpperLobe)
    roof=b.world(d.PickupResetRoof);guard=b.world(d.GearGuard)
    screw=b.world(d.PickupRoofScrew)
    tests['detachable upper shell clears carrier']=overlap(shell,frame)<TOL
    tests['removable reset roof is a connected part']=roof.isValid() and len(roof.Solids)==1
    tests['reset roof has a finite seated foot']=overlap(
        b.cylinder(2.3,.04,c.ROOF_MOUNT+V(0,0,21.71)).cut(b.cylinder(1.25,.1,c.ROOF_MOUNT+V(0,0,21.7))),roof)>0.3
    mask=b.cylinder(1.001,3.30001,c.ROOF_MOUNT+V(0,0,18.4))
    tests['reset roof screw clears bridge']=overlap(screw,roof)<TOL
    tests['reset roof screw seated']=screw.distToShape(roof)[0]<1e-6
    tests['reset roof pilot engagement']=overlap(screw,guard)>1
    tests['reset roof screw outside allowed thread zone clears cover']=overlap(screw.cut(mask),guard)<TOL
    roof_key=[]
    for angle in (-10,10):
        moved=roof.copy();moved.rotate(c.ROOF_MOUNT,V(0,0,1),angle)
        roof_key.append(overlap(moved,guard))
    tests['reset roof key blocks mounting rotation']=min(roof_key)>.001
    shells=[]
    for side,x in [('Left',-14),('Right',14)]:
        bolt=b.world(d.getObject('UpperShellScrew'+side));point=V(x,-2,0)
        thread=b.cylinder(1.001,3.20001,point+V(0,0,29.8))
        tests['upper shell '+side+' screw clears shell']=overlap(bolt,shell)<TOL
        tests['upper shell '+side+' screw head seated']=bolt.distToShape(shell)[0]<1e-6
        tests['upper shell '+side+' screw pilot engagement']=overlap(bolt,frame)>1
        tests['upper shell '+side+' screw clears frame outside thread']=overlap(bolt.cut(thread),frame)<TOL
        seat=b.annulus(1.3,2.5,32.95,.05);seat.translate(point)
        upper=b.annulus(1.3,2.5,33.0,.05);upper.translate(point)
        tests['upper shell '+side+' lower bearing seat']=seat.cut(frame).Volume<TOL
        tests['upper shell '+side+' upper bearing seat']=upper.cut(shell).Volume<TOL
        shells.append(dict(side=side,head_gap_mm=bolt.distToShape(shell)[0],pilot_overlap_mm3=overlap(bolt,frame)))
    # The carrier goes in before the removable bridge. The bridge is slid
    # inward 1 mm above its seat, then lowered over its locating pin.
    carrier_parts=['UpperCarrier','DriveCarrier','PickupPawl','PickupFork','PickupLatchTip','PickupTripFoot']+[
        f'PickupLatchLeaf{i}' for i in range(8)]+[f'PickupTripLeaf{i}' for i in range(10)]
    installed=[b.world(d.getObject(n)) for n in carrier_parts]+[guard]
    direction=b.polar(1,c.ROOF_MOUNT_ANGLE)
    samples=[(offset,1.0) for offset in (32,16,8,4,2,1,0)]+[(0,z) for z in (.8,.5,.25,0)]
    hits=[]
    for offset,lift in samples:
        q=roof.copy();q.translate(direction*offset+V(0,0,lift))
        for index,target in enumerate(installed):
            amount=overlap(q,target)
            if amount>TOL:hits.append(dict(radial_offset_mm=offset,lift_mm=lift,target=(carrier_parts+['GearGuard'])[index],overlap_mm3=amount))
    tests['reset bridge sampled radial insertion after carrier']=not hits
    shell_hits=[]
    targets=installed+[roof]
    for dz in (0,.2,.5,1,2,4,8,16,32):
        moved=shell.copy();moved.translate(V(0,0,dz))
        for i,target in enumerate(targets):
            amount=overlap(moved,target)
            if amount>TOL:shell_hits.append(dict(lift_mm=dz,target=(carrier_parts+['GearGuard','PickupResetRoof'])[i],overlap_mm3=amount))
    tests['outer shell sampled installation after reset bridge']=not shell_hits
    extra.update(reset_roof_mount_key_overlap_mm3=roof_key,upper_shell_screws=shells,
        reset_bridge_insertion=dict(samples=samples,failures=hits),
        outer_shell_insertion=dict(failures=shell_hits),
        assembly_order='Body, lower rotor, bead keeper, lid, keyed upper rotor, cover/click leaf, internal upper carrier with pawls, removable reset bridge (radial at +1 mm then lower), bridge screw, outer upper shell and its two screws, central washer/retainer.')
    result['V7_additions']=extra;result['passed']=all(tests.values())
    return result
