"""V6 updated focused CAD evidence. Real saved contacts, native poses and travel stops.

Flexible layouts and leaf deflections are prescribed. No force, acoustic,
fatigue, TPU-strain, snap-retention, print or physical-operation qualification.
"""
from pathlib import Path
import hashlib
import json
import math
import FreeCAD as App
import Part
import bracelet_v6_updated as b
import assembly_v6_updated
from engineering_v6_updated import estimates

V=App.Vector
TOL=1e-5
GEAR_TOL=5e-5


def overlap(a,c):
    if a.isNull() or c.isNull() or not a.BoundBox.intersect(c.BoundBox): return 0.0
    return max(0.0,a.common(c).Volume)


def crop(shape,point,half=3.25):
    return shape.common(Part.makeBox(2*half,2*half,2*half,point-V(half,half,half)))


def dimensions(o):
    box=o.Shape.optimalBoundingBox(False)
    return dict(width=round(box.XLength,3),depth=round(box.YLength,3),height=round(box.ZLength,3),
                minimum_z=round(box.ZMin,3),maximum_z=round(box.ZMax,3))


def periodic_vertex_error(shape,angle):
    """Rotational witness for saved extruded polygon profiles and centre bore.

    Comparing coincident 900-edge solids with a Boolean is both ill-conditioned
    and unnecessarily expensive. Their saved planar profile vertices provide
    the same periodic-position witness; the concentric bore is invariant.
    """
    cell=1e-5;grid={}
    key=lambda p:tuple(math.floor(x/cell) for x in (p.x,p.y,p.z))
    points=[v.Point for v in shape.Vertexes if math.hypot(v.Point.x,v.Point.y)>5.70001]
    for p in points:
        grid.setdefault(key(p),[]).append(p)
    rotation=App.Rotation(V(0,0,1),angle);error=0.0
    for point in points:
        p=rotation.multVec(point);k=key(p);near=[]
        for x in (-1,0,1):
            for y in (-1,0,1):
                for z in (-1,0,1): near+=grid.get((k[0]+x,k[1]+y,k[2]+z),[])
        error=max(error,min(((p-q).Length for q in near),default=1e9))
    return error


def run(d,report_path=None):
    destination=Path(report_path) if report_path else b.HERE/'checks.json'
    destination.parent.mkdir(parents=True,exist_ok=True)
    m=d.Motion
    def pose(step=0,closed=True,stroke=0,returning=False):
        m.BeadSteps=step;m.StrandClosed=closed;m.CapStroke=stroke;m.CapReturning=returning;d.recompute()
    pose()
    parts={o.Name:dict(valid=o.Shape.isValid(),solids=len(o.Shape.Solids),volume_mm3=round(o.Shape.Volume,6))
           for o in d.Objects if hasattr(o,'DisplayColour')}
    invalid=[n for n,v in parts.items() if not v['valid'] or v['solids']!=1]
    worst={};witness={};errors={};notes=[]
    def record(name,a,c): worst[name]=max(worst.get(name,0),overlap(a,c))
    def put_error(name,value): errors[name]=max(errors.get(name,0),abs(value))
    hardware=['CapWasher']+[f'HousingScrew{i:02}' for i in range(len(b.CASE_MOUNTS))]
    fixed_names=['LowerBody','LowerLid','GearGuard','BeadKeeper','CentreAxle','CapRetainer',
                 'CapReturnSpring','CapFixedSpringLeg','ReturnSpringHousing','DetentAnchor']+hardware
    fixed={n:b.world(d.getObject(n)) for n in fixed_names}
    bounds={n:s.optimalBoundingBox(False) for n,s in fixed.items()}
    def against_fixed(name,shape,targets=fixed_names):
        box=shape.optimalBoundingBox(False)
        for n in targets:
            if box.intersect(bounds[n]): record(name+'/'+n,shape,fixed[n])
    print('V6 updated checks: saved RNA rack / real involute gear, both strand modes',flush=True)
    # Include both shoulder bends, beyond the short straight engagement.
    tile=Part.makeBox(50,16,8,V(-25,-38,15.6))
    gear_samples=0
    mesh_centre=round((b.route.LENGTH-b.route.JOIN_HOME)/b.RNA_PITCH)
    for closed in (True,False):
        for j in range(9):
            pose(j/24,closed)
            wheel=b.world(d.RnaDriveGear).common(tile)
            for i in b.RNA_LINKS:
                o=d.getObject(f'RnaLink{i:03}')
                if o.Placement.Base.z>14 and abs(o.Placement.Base.x)<25:
                    record('actual RNA rack / involute gear',b.world(o),wheel)
            gear_samples+=1
        print('  gear modes: '+('closed' if closed else 'open'),flush=True)
    print('V6 updated checks: actual protein solids and spherical bound through drum handoff',flush=True)
    drum=d.BeadDrum.Shape.copy();drum.Placement=App.Placement()
    keeper=fixed['BeadKeeper'];variants=[]
    for kind in range(3):
        o=next(o for o in d.Protein.Group if hasattr(o,'BeadVariant') and o.BeadVariant==kind)
        shape=o.Shape.copy();shape.Placement=App.Placement();variants.append(shape)
    outside=max(s.cut(Part.makeSphere(b.BEAD_R)).Volume for s in variants)
    handoff=0
    for j in range(9):
        distance=j*b.BEAD_PITCH/8;wheel=drum.copy()
        wheel.rotate(V(),V(0,0,1),-math.degrees(distance/b.STORE_R))
        for k,s in enumerate((distance-b.BEAD_PITCH,distance,distance+b.BEAD_PITCH)):
            centre=b.path(s);local=crop(wheel,centre)
            record('spherical protein / actual drum',Part.makeSphere(b.BEAD_R,centre),local)
            bead=b.placed_bead(variants[(j+k)%3],s,90*(j%4))
            record('actual protein / actual drum',bead,local)
            record('actual protein / keeper',bead,crop(keeper,centre));handoff+=1
        print('  handoff %d/8'%j,flush=True)
    print('V6 updated checks: continuous drum / gear / protein envelopes and external RNA trough',flush=True)
    sweeps={
        'drum':b.drum_sweep(.01),
        'RNA gear':b.annulus(3.14,b.MODULE*(b.SUN_TEETH/2+1)+.01,b.GEAR_Z-.01,b.GEAR_WIDTH+.02),
        'protein arc':Part.makeTorus(b.STORE_R,b.BEAD_R,V(0,0,b.BEAD_Z),V(0,0,1)),
        'protein straight':b.cylinder(b.BEAD_R,160,V(0,b.STORE_R,b.BEAD_Z),V(1,0,0)),
    }
    for n,s in sweeps.items():
        against_fixed(n+' continuous envelope',s)
    pose()
    for label,obj in [('drum',d.BeadDrum),('RNA gear',d.RnaDriveGear)]:
        worst[label+' outside conservative envelope']=max(0,b.world(obj).cut(sweeps[label]).Volume)
    # The analytic tube is a continuous bound of all RNA orientations. Local
    # cross-section + curvature sag certificates avoid profile-only claims.
    tube=b.return_clearance()
    record('continuous RNA tube / lower body',tube,fixed['LowerBody'])
    record('continuous open RNA tails / lower body',b.open_return_clearance(),fixed['LowerBody'])
    # Tangential span and curvature sag bound each canonical component.
    r=b.route.RADIUS
    rail_bound=math.hypot(2.28,1.15)+(b.RNA_PITCH+.3)**2/(8*r)
    base_bound=.48+max(b.RNA_BASE_LENGTHS)+.53+.53**2/(2*r)
    clasp_bound=math.hypot(1.6,2.4)+5.0**2/(2*r)
    envelope=dict(radius_mm=b.RNA_GROOVE_RADIUS,link_required_radius_mm=rail_bound,
                  base_required_radius_mm=base_bound,clasp_required_radius_mm=clasp_bound,
                  minimum_bend_radius_mm=r,nominal_path_only=True)
    for closed in (True,False):
        record('continuous base tube / lower body '+str(closed),b.base_clearance(closed),fixed['LowerBody'])
    envelope['base_bound_method']='Separate continuous outward-offset base tube'
    envelope_ok=max(rail_bound,clasp_bound)<b.RNA_GROOVE_RADIUS
    print('V6 updated checks: single central RNA channel, base slot and physical end-stop shoulders',flush=True)
    guard=fixed['GearGuard'];retention=[]
    for x in (0,):
        local=b.union([crop(guard,V(x,b.RNA_Y,b.RNA_Z),10),
                       crop(fixed['LowerLid'],V(x,b.RNA_Y,b.RNA_Z),10)])
        rail=b.rna_link_shape().copy();rail.translate(V(x,b.RNA_Y,b.RNA_Z))
        record('RNA rail nominal / guide throat',rail,local)
        for i in range(4):
            base=b.rna_base_shape(i);base.translate(V(x,b.RNA_Y,b.RNA_Z))
            record('RNA base nominal / guide throat',base,local)
        lifted=rail.copy();lifted.translate(V(0,-1.3,0))
        retention.append(dict(guide_x=x,action='forbidden side escape',overlap_mm3=overlap(lifted,local)))
        for female in (True,False):
            head=b.clasp_shape(female);head.translate(V(x,b.RNA_Y,b.RNA_Z))
            retention.append(dict(guide_x=x,action='receiver stop' if female else 'button stop',overlap_mm3=overlap(head,local)))
    retention_ok=all(v['overlap_mm3']>.001 for v in retention)
    print('V6 updated checks: native forward/reverse RNA, actual orientations and clasp mating',flush=True)
    poses=[0,.125,.25,.5,.75,1,5.5,11,16.5,21,21.5,22]
    min_clasp_clearance=1e9;min_link_lap=1e9;min_clasp_root_lap=1e9
    port_solids=[local]
    lap_indices=sorted({2+(len(b.RNA_LINKS)-2)*j//8 for j in range(9)})
    for closed in (True,False):
        for step in poses:
            pose(step,closed)
            put_error('three bases per bead',m.BasesPassed-3*step)
            put_error('RNA translation ratio mm',m.RnaTravel.Value-b.RNA_STEP*step)
            put_error('drum ratio deg',m.DrumDegrees+b.STEP_DEG*step)
            for i in b.RNA_LINKS:
                o=d.getObject(f'RnaLink{i:03}');p=b.rna_pose(i*b.RNA_PITCH,b.RNA_STEP*step,closed)
                put_error('RNA native position mm',(o.Placement.Base-p.Base).Length)
                for axis in (V(1,0,0),V(0,1,0),V(0,0,1)):
                    put_error('RNA native orientation',(o.Placement.Rotation.multVec(axis)-p.Rotation.multVec(axis)).Length)
                # Actual shoulder cells and bases must clear the whole cover
                # and lid, including the former outer-holder locations.
                for label,shape in [('RNA cell',b.world(o)),
                    ('RNA base',b.world(d.getObject(f'Base{i:03}')))]:
                    against_fixed('travelling '+label,shape,['LowerLid','GearGuard']+hardware)
            for i in range(b.BEADS):
                o=d.getObject(f'Bead{i:02}');s=b.HOME_S-i*b.BEAD_PITCH+step*b.BEAD_PITCH
                put_error('protein native position mm',(o.Placement.Base-b.path(s)).Length)
            for i in range(b.BEADS-1):
                a=d.getObject(f'Bead{i:02}').Placement.Base;c=d.getObject(f'Bead{i+1:02}').Placement.Base
                put_error('native wire length mm',d.getObject(f'Wire{i:02}').Height.Value-(c-a).Length)
            # Actual connector solids, not idealized points.
            heads=[b.world(d.ClaspReceiver),b.world(d.ClaspButton)]
            if closed: record('closed clasp rigid fit',*heads)
            for h in heads:
                against_fixed('travelling clasp',h,[n for n in fixed_names if n!='LowerBody'])
                for port in port_solids:
                    min_clasp_clearance=min(min_clasp_clearance,h.distToShape(port)[0])
                    record('actual travelling clasp / guide',h,port)
            # Adjacent cells represent one continuous TPU strip. Sample both
            # straight and tightest-curvature lap joints in the saved model.
            if step in (0,11,22):
                for head_name,link_name in [('ClaspReceiver','RnaLink002'),('ClaspButton',f'RnaLink{b.route.CELLS-2:03}')]:
                    min_clasp_root_lap=min(min_clasp_root_lap,overlap(b.world(d.getObject(head_name)),b.world(d.getObject(link_name))))
                for i in lap_indices:
                    a=b.world(d.getObject(f'RnaLink{i:03}'));c=b.world(d.getObject(f'RnaLink{i+1:03}'))
                    min_link_lap=min(min_link_lap,overlap(a,c))
            invalid += [o.Name for o in d.Objects if 'Invalid' in o.State]
        # A separate decreasing traversal checks native direct reverse with
        # the cap resting and without any release flag or release motion.
        for step in reversed(poses):
            pose(step,closed)
            for name in ['DriveCarrier']:
                record('resting '+name+' / reversing feed ratchet',b.world(d.getObject(name)),b.world(d.FeedRatchet))
        print('  native '+('closed' if closed else 'open')+' forward and direct reverse complete',flush=True)
    pose(22)
    retained=dict(hidden_beads=sum(d.getObject(f'Bead{i:02}').PathDistance<=b.MOUTH_X for i in range(b.BEADS)),
                  seated_beads=sum(d.getObject(f'Bead{i:02}').PathDistance<=0 for i in range(b.BEADS)))
    print('V6 updated checks: engaged cap stroke, conjugate cam and axial face-ramp return',flush=True)
    cap_parts=['UpperLobe','DriveCarrier','PawlBiasSpring']
    cap_pose_count=0;clearance_pose_count=0;max_flex=0.0;max_cam_lift=0.0;min_rest_gap=1e9;drive_contact=[]
    checked_cap_angles=set();checked_internal_lifts=set()
    # Integer bead positions differ by the exact rotational period of both
    # index wheels. Check that periodicity on the saved solids before reusing
    # one cycle's rigid-clearance evidence at the other two feed positions.
    for name in ('FeedRatchet','IndexWheel'):
        shape=d.getObject(name).Shape.copy();shape.Placement=App.Placement()
        put_error(name+' saved periodicity mm',periodic_vertex_error(shape,b.STEP_DEG))
    print('  saved drive/index profile periodicity checked',flush=True)
    strokes=sorted(set([j/12 for j in range(13)]+
        [(b.ENTRY_DEG+a)/b.CAP_ANGLE for a in (-.2,0,.01,.2)]+
        [(2.7+a)/b.CAP_ANGLE for a in (-.05,0,.05)]))
    for base in (0,11,21):
        for returning in (False,True):
            for j,f in enumerate(strokes):
                pose(base+1 if returning else base,True,f,returning)
                expected=base+1 if returning else base+max(0,(b.CAP_ANGLE*f-b.ENTRY_DEG)/b.STEP_DEG)
                put_error('cap drives exact feed step',m.EffectiveSteps-expected)
                put_error('cap actual protein feed mm',(d.Bead00.Placement.Base-b.path(b.HOME_S+b.BEAD_PITCH*expected)).Length)
                o=d.getObject(f'RnaLink{mesh_centre:03}');p=b.rna_pose(mesh_centre*b.RNA_PITCH,b.RNA_STEP*expected,True)
                put_error('cap actual RNA feed mm',(o.Placement.Base-p.Base).Length)
                max_flex=max(max_flex,m.CoastLift.Value);max_cam_lift=max(max_cam_lift,m.CamLift.Value)
                if base!=0:
                    cap_pose_count+=1
                    continue
                ratchet=b.world(d.FeedRatchet);cap=b.world(d.UpperLobe)
                for o in d.RnaStrand.Group:
                    if hasattr(o,'DisplayColour'):
                        record('actual RNA / upper shell',b.world(o),cap)
                angle_key=round(m.CapAngle,10);lift_key=round(m.PawlLift.Value,10)
                # Shell/fixed geometry repeats exactly at the same angle on
                # feed and return. Internal cap fits depend only on lift:
                # both shapes share the same rigid cap rotation. Reuse those
                # identical Boolean witnesses; cam/ratchet checks stay live.
                if angle_key not in checked_cap_angles:
                    against_fixed('upper shell',cap)
                for n in cap_parts[1:]:
                    shape=b.world(d.getObject(n));against_fixed(n,shape)
                    record(n+' / feed ratchet',shape,ratchet)
                    if lift_key not in checked_internal_lifts:
                        record(n+' / upper shell',shape,cap)
                for n in ['DetentTip','DetentFlexure']:
                    shape=b.world(d.getObject(n))
                    record(n+' / click wheel',shape,b.world(d.IndexWheel))
                    record(n+' / upper shell',shape,cap)
                moving_leg=b.world(d.CapMovingSpringLeg)
                if angle_key not in checked_cap_angles:
                    against_fixed('moving cap-spring terminal',moving_leg,[n for n in fixed_names if n!='CapReturnSpring'])
                    record('moving spring terminal / cap anchor',moving_leg,cap)
                    record('fixed spring terminal / moving cap',fixed['CapFixedSpringLeg'],cap)
                checked_cap_angles.add(angle_key);checked_internal_lifts.add(lift_key)
                if not returning and b.CAP_ANGLE*f>=b.ENTRY_DEG:
                    drive_contact.append(b.world(d.DriveCarrier).distToShape(ratchet)[0])
                if f==0:
                    min_rest_gap=min(min_rest_gap,b.world(d.DriveCarrier).distToShape(ratchet)[0])
                cap_pose_count+=1
                clearance_pose_count+=1
                print('  cap clearance %s %d/%d'%('return' if returning else 'feed',j,len(strokes)-1),flush=True)
            print('  upper input base %d %s'%(base,'return' if returning else 'feed'),flush=True)
    print('V6 updated checks: true travel stops and blocked extra feed at full extension',flush=True)
    pin=d.TravelPin.Shape.copy();pin.Placement=App.Placement();stops=[]
    for angle in (-2,0,b.MAX_DRUM,b.MAX_DRUM+2):
        shape=pin.copy();shape.rotate(V(),V(0,0,1),-angle)
        stops.append(dict(drum_degrees=angle,overlap_mm3=overlap(shape,fixed['LowerBody'])))
    cap_stops=[]
    cap=d.UpperLobe.Shape.copy();cap.Placement=App.Placement()
    post=b.cylinder(.85,8.5,b.polar(24,b.CAP_STOP_ANGLE,21.7))
    for angle in (-2,0,b.CAP_ANGLE,b.CAP_ANGLE+2):
        shape=cap.copy();shape.rotate(V(),V(0,0,1),-angle)
        cap_stops.append(dict(cap_degrees=angle,overlap_mm3=overlap(shape,post)))
    pose(22,True,1,False)
    end=dict(effective_steps=m.EffectiveSteps,cap_angle=m.CapAngle,allowed_entry_angle=b.ENTRY_DEG)
    attempt=b.world(d.DriveCarrier);attempt.rotate(V(),V(0,0,1),-.8)
    end['attempted_extra_drive_contact_mm3']=overlap(attempt,b.world(d.FeedRatchet))
    print('V6 updated checks: actual screw passages, bearing seats, wall witnesses and integral roots',flush=True)
    pose()
    assembly=assembly_v6_updated.run(d,overlap)
    print('  fastening audit: '+str(assembly['passed']),flush=True)
    # Fixed assembly fit. Only bounded thread zones and explicitly integral
    # features may overlap. Do not exempt an entire fastener/host pair.
    pose()
    main=[o for o in d.Objects if hasattr(o,'DisplayColour') and not o.Name.startswith(
        ('RnaLink','Base','Bead0','Bead1','Bead2','Wire','DetentLeaf'))]
    rotor_names={o.Name for o in d.Rotor.Group}
    spring_claims={'CapReturnSpring','CapFixedSpringLeg','CapMovingSpringLeg'}
    main_shapes={o.Name:b.world(o) for o in main}
    boxes={n:s.optimalBoundingBox(False) for n,s in main_shapes.items()}
    for j,a in enumerate(main):
        for c in main[j+1:]:
            if a.Name in rotor_names and c.Name in rotor_names: continue
            if a.Name in spring_claims and c.Name in spring_claims: continue
            pair={a.Name,c.Name}
            if pair in assembly_v6_updated.INTEGRAL_PAIRS: continue
            if pair in ({'DetentFlexure','DetentTip'},{'DetentFlexure','DetentAnchor'}): continue
            if not boxes[a.Name].intersect(boxes[c.Name]): continue
            sa,sc=main_shapes[a.Name],main_shapes[c.Name]
            # The fixed last web joins the pedestal only inside the actual
            # root. Keep checking any flexure/cover overlap outside that root.
            if pair=={'DetentFlexure','GearGuard'}:
                if a.Name=='DetentFlexure':sa=sa.cut(main_shapes['DetentAnchor'])
                else:sc=sc.cut(main_shapes['DetentAnchor'])
            thread=assembly_v6_updated.allowed_thread(pair)
            if thread:
                name,mask=thread
                if a.Name==name:sa=sa.cut(mask)
                else:sc=sc.cut(mask)
            record('assembly '+a.Name+'/'+c.Name,sa,sc)
    import springs_v6_updated
    spring_audit=springs_v6_updated.audit(d,overlap)
    def stop_ok(items):
        return max(items[1]['overlap_mm3'],items[2]['overlap_mm3'])<TOL and min(items[0]['overlap_mm3'],items[3]['overlap_mm3'])>.001
    failures={k:v for k,v in worst.items() if v>(GEAR_TOL if k=='actual RNA rack / involute gear' else TOL)}
    logical=dict(retention_witnesses=retention_ok,continuous_RNA_bound=envelope_ok,
        continuous_TPU_cell_laps=min_link_lap>1e-5,clasp_guides_clear=min_clasp_clearance>1,
        clasp_roots_connected=min_clasp_root_lap>1e-5,
        positive_drum_stops=stop_ok(stops),positive_cap_stops=stop_ok(cap_stops),
        cap_endpoint=m.EffectiveSteps<=22 and end['effective_steps']==22 and abs(end['cap_angle']-b.ENTRY_DEG)<1e-7,
        extra_feed_physically_blocked=end['attempted_extra_drive_contact_mm3']>.001,
        resting_cap_disengaged=min_rest_gap>.5,
        drive_face_contact=bool(drive_contact) and max(drive_contact)<1e-5,
        no_external_release=not hasattr(m,'ReverseRelease') and d.getObject('ReleaseYoke') is None,
        retained_tail=retained['hidden_beads']==4 and retained['seated_beads']>=3,
        native_accuracy=max(errors.values(),default=0)<1e-7,bead_spherical_bound=outside<TOL,
        assembly_fastening_and_roots=assembly['passed'],spring_parts_and_seats=spring_audit['passed'])
    # cap_endpoint above must use its captured endpoint, not the reset pose.
    logical['cap_endpoint']=end['effective_steps']==22 and abs(end['cap_angle']-b.ENTRY_DEG)<1e-7
    result=dict(version='6-updated',status='FOCUSED_PASS' if not invalid and not failures and all(logical.values()) else 'REVIEW',
        mechanical_status='REVIEW',functional_mechanism_established=False,
        unresolved_engineering=['Folded-detent force and holding torque',
            'Spring end treatments, terminal retention and preload installation',
            'Friction, cap return under load, print fit and physical durability'],
        runtime='.'.join(App.Version()[:3]),parts=parts,invalid_objects=sorted(set(invalid)),
        collision_failures_mm3=failures,maximum_unintended_overlap_mm3=worst,
        overlap_tolerance_mm3=TOL,involute_approximation_tolerance_mm3=GEAR_TOL,
        logical_checks=logical,native_errors=errors,
        actual_bead_handoff_samples=handoff,spherical_bead_handoff_samples=handoff,
        actual_RNA_gear_phase_samples=gear_samples,sampled_forward_poses_per_mode=len(poses),
        sampled_direct_reverse_poses_per_mode=len(poses),sampled_cap_cycle_poses=cap_pose_count,
        actual_cap_clearance_poses=clearance_pose_count,
        unique_upper_shell_fixed_clearance_angles=len(checked_cap_angles),
        unique_internal_cap_clearance_lifts=len(checked_internal_lifts),
        RNA_envelope_certificate=envelope,retention_solid_witnesses=retention,
        minimum_actual_clasp_guide_clearance_mm=min_clasp_clearance,
        minimum_same_strip_cell_lap_mm3=min_link_lap,retained_at_full_travel=retained,
        minimum_clasp_to_strip_root_lap_mm3=min_clasp_root_lap,
        drum_travel_stops=stops,cap_travel_stops=cap_stops,full_feed_cap=end,
        maximum_face_ramp_return_lift_mm=max_flex,maximum_internal_cam_lift_mm=max_cam_lift,
        minimum_resting_pawl_clearance_mm=min_rest_gap,
        maximum_feed_face_contact_gap_mm=max(drive_contact,default=-1),
        housing_dimensions_mm={n:dimensions(d.getObject(n)) for n in ('LowerBody','UpperLobe')},
        assembly_audit=assembly,
        spring_audit=spring_audit,
        housing_refinement=dict(central_RNA_capture_only=True,outer_RNA_holders=False,protruding_guide_brackets=False,
            bottom_grip_rails=False,open_underside_groove=True,
            guide_centres_x_mm=[0],straight_drive_span_mm=2*b.route.TOP_HALF,
            RNA_route_width_mm=b.route.WIDTH,RNA_route_depth_mm=b.route.HEIGHT,
            nominal_shoulder_bend_radius_mm=b.route.TOP_RADIUS,nominal_minimum_bend_radius_mm=b.route.RADIUS,
            nominal_palm_dome_minimum_z_mm=-8.1,
            RNA_route_angle_degrees=b.RNA_ROUTE_ANGLE,
            nominal_return_centre_y_mm=b.RNA_Y+b.RNA_SIDE*b.route.HEIGHT,
            nominal_return_centre_z_mm=b.RNA_Z-b.RNA_DROP*b.route.HEIGHT),
        engineering_estimates=estimates(),
        design=dict(handheld=True,wearable=False,open_or_closed_captive_RNA=True,external_open_underside_return=True,
            parking_clip=False,external_reverse_release=False,direct_RNA_reverse=True,
            RNA_bases_per_bead=3,RNA_lattice_positions=b.route.CELLS,visible_RNA_bases=len(b.RNA_LINKS),
            RNA_pitch_mm=b.RNA_PITCH,RNA_travel_mm=b.RNA_MAX,RNA_nominal_loop_length_mm=b.route.LENGTH,
            RNA_drive_teeth=b.SUN_TEETH,bead_pitch_mm=6,drum_pockets=28,protein_beads=26,
            maximum_bead_steps=22,maximum_protein_feed_mm=132,tensioned_rewind=False,automatic_curling=False,
            input_cap_entry_degrees=b.ENTRY_DEG,input_cap_total_degrees=b.CAP_ANGLE),
        intentional_connections=dict(rotor='Drum/hub/travel pin form the lower rotor; RNA gear/input sleeve/click wheel/feed wheel form the upper rotor. A D-key couples the two, with separate assembly and torque witnesses.',
            TPU='Neighboring nominal RNA cells, their base roots and clasp roots represent one continuous flexible strip.',
            flexures='One fused serpentine flexure depicts prescribed deflection; force and fatigue remain unqualified.',
            spring_studies='Native coil solid and its schematic terminals represent one metal torsion spring; their root laps are intentional. Compression spring has two explicit seat washers.',
            integral_roots='Lower-body/spindle and cover/detent-anchor features overlap and fuse to one solid each.',
            fastener='Only bounded nominal thread envelopes overlap their pilots. Coaxial passages, conical seats, clamped stack and fixed washer shoulder are checked; thread strength and preload are unqualified.'),
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (b.HERE/'bracelet_v6_updated.py',b.HERE/'rna_path.py',b.HERE/'validation_v6_updated.py',b.HERE/'assembly_v6_updated.py',b.HERE/'engineering_v6_updated.py',b.HERE/'springs_v6_updated.py')},
        validation_boundary='Focused actual bead/drum, actual rack/gear including shoulder bends, conservative continuous envelopes, central RNA captivity, reusable-clasp fit, native open/closed forward/reverse, cap feed/return, cam clearance, positive travel stops, actual screw passages/seats/wall sections, integral roots, keyed rotor fit/torque and sampled assembly insertion checks. TPU cells and flexure chords are prescribed deformation; native coupling omits physical key backlash and axial float. Springs have explicit hardware solids, anchors and seats; their properties remain unqualified. No force, click acoustics, compliance, strain, snap retention, fatigue, manufacturing, hand-fit or physical-operation qualification.',
        physical_tests_still_required=[
            'RNA TPU bending, pitch stability, mesh friction and guide escape under hand loads',
            'Clasp snap force, retention, peeling release and repeated-cycle fatigue',
            'Closed-loop clasp travel, grip clearance and open-tail handling',
            'Bidirectional detent force, audible click and long-term wear',
            'Cap follower friction, axial bias and return springs, reliable one-step engagement and face-ramp return',
            'End-of-feed force transmission and protection against pawl skip or damage under overload',
            'Direct bead capture/retraction, wire pitch fixation, buckling and bend fatigue',
            'Printed fits, fastening, material selection, assembly and durability'],
        preserved_versions=dict(V5='FOCUSED_PASS; preserved circular RNA and external-release comparison',
            V4='FOCUSED_PASS; cuff comparison',V3='INCOMPLETE_USER_STOPPED',V2='HISTORICAL_PASS_INVALIDATED'))
    destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    pose()
    print(json.dumps({k:v for k,v in result.items() if k not in ('parts','maximum_unintended_overlap_mm3')},indent=2),flush=True)
    return result
