"""V7 focused CAD evidence. Real saved contacts, native poses and travel stops.

Flexible layouts and leaf deflections are prescribed. No force, acoustic,
fatigue, TPU-strain, snap-retention, print or physical-operation qualification.
"""
from pathlib import Path
import hashlib
import json
import math
import FreeCAD as App
import Part
import bracelet_v7 as b
import assembly_v7
import coupling_v7 as c
from engineering_v7 import estimates

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
        m.BeadSteps=step;m.StrandClosed=closed;m.InputKind=0;m.CyclePosition=0;d.recompute()
    pose()
    parts={o.Name:dict(valid=o.Shape.isValid(),solids=len(o.Shape.Solids),volume_mm3=round(o.Shape.Volume,6))
           for o in d.Objects if hasattr(o,'DisplayColour')}
    invalid=[n for n,v in parts.items() if not v['valid'] or v['solids']!=1]
    worst={};witness={};errors={};notes=[]
    def record(name,a,c): worst[name]=max(worst.get(name,0),overlap(a,c))
    def put_error(name,value): errors[name]=max(errors.get(name,0),abs(value))
    hardware=['CapWasher']+[f'HousingScrew{i:02}' for i in range(len(b.CASE_MOUNTS))]
    fixed_names=['LowerBody','LowerLid','GearGuard','BeadKeeper','CentreAxle','CapRetainer',
                 'CapSpringEnvelope','CapFixedSpringLeg','DetentAnchor']+hardware
    fixed={n:b.world(d.getObject(n)) for n in fixed_names}
    bounds={n:s.optimalBoundingBox(False) for n,s in fixed.items()}
    def against_fixed(name,shape,targets=fixed_names):
        box=shape.optimalBoundingBox(False)
        for n in targets:
            if box.intersect(bounds[n]): record(name+'/'+n,shape,fixed[n])
    print('V7 checks: saved RNA rack / real involute gear, both strand modes',flush=True)
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
    print('V7 checks: actual protein solids and spherical bound through drum handoff',flush=True)
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
    print('V7 checks: continuous drum / gear / protein envelopes and external RNA trough',flush=True)
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
    envelope=dict(radius_mm=4.65,link_required_radius_mm=rail_bound,
                  base_required_radius_mm=base_bound,clasp_required_radius_mm=clasp_bound,
                  minimum_bend_radius_mm=r,nominal_path_only=True)
    envelope_ok=max(rail_bound,base_bound,clasp_bound)<4.65
    print('V7 checks: single central RNA channel, base slot and physical end-stop shoulders',flush=True)
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
    print('V7 checks: native forward/reverse RNA, actual orientations and clasp mating',flush=True)
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
    # Coupling, final assembly and candidate boundaries are checked by the
    # V7-specific continuation, never by the preserved V6 cap suite.
    return finish(d,destination,parts,invalid,worst,errors,record,put_error,
                  outside,handoff,gear_samples,envelope,envelope_ok,retention,
                  retention_ok,min_clasp_clearance,min_link_lap,min_clasp_root_lap,
                  retained)


def coupling_checks(d,record,put_error):
    m=d.Motion;contacts=[];poses=[];latch_witness=[];stop_witness=[]
    rotor={o.Name for o in d.Rotor.Group}
    cover={'GearGuard','DetentAnchor','DetentTip','PickupTripPost'}|{f'DetentLeaf{i}' for i in range(8)}
    frame={'UpperCarrier','PickupLatchTip','PickupTripFoot'}|{
        f'PickupLatchLeaf{i}' for i in range(8)}|{f'PickupTripLeaf{i}' for i in range(10)}
    pair_cache=set()
    studied=[o for o in d.Objects if hasattr(o,'DisplayColour') and
        o.Name not in ('RnaDriveGear','BeadDrum') and
        not o.Name.startswith(('RnaLink','Base','Bead0','Bead1','Bead2','Wire')) and
        not getattr(o,'GeometryRole','').startswith('SPACE_CLAIM_ONLY')]
    def mask_thread(a,n,shape):
        pair={a,n}
        if pair=={'PickupRoofScrew','GearGuard'}:
            tool=b.cylinder(1.001,3.30001,c.ROOF_MOUNT+V(0,0,18.4))
            return shape.cut(tool) if a=='PickupRoofScrew' else shape
        if 'UpperCarrier' in pair and any(k.startswith('UpperShellScrew') for k in pair):
            name=next(k for k in pair if k.startswith('UpperShellScrew'))
            x=-14 if name.endswith('Left') else 14
            tool=b.cylinder(1.001,3.20001,V(x,-2,29.8));tool.rotate(V(),V(0,0,1),-m.CapAngle)
            return shape.cut(tool) if a==name else shape
        allowed=assembly_v7.allowed_thread(pair)
        if allowed and a==allowed[0]:return shape.cut(allowed[1])
        return shape
    def actual_pairs():
        shapes={o.Name:b.world(o) for o in studied}
        boxes={n:s.optimalBoundingBox(False) for n,s in shapes.items()}
        for j,a in enumerate(studied):
            for q in studied[j+1:]:
                names={a.Name,q.Name}
                if names<=rotor or names<=cover or names<=frame:continue
                if names=={'LowerBody','CentreAxle'}:continue
                if not boxes[a.Name].intersect(boxes[q.Name]):continue
                relative=a.getGlobalPlacement().inverse().multiply(q.getGlobalPlacement())
                values=(relative.Base.x,relative.Base.y,relative.Base.z)+relative.Rotation.Q
                key=(a.Name,q.Name,round(shapes[a.Name].Volume,7),round(shapes[q.Name].Volume,7))+tuple(round(x,8) for x in values)
                if key in pair_cache:continue
                pair_cache.add(key)
                sa=mask_thread(a.Name,q.Name,shapes[a.Name]);sq=mask_thread(q.Name,a.Name,shapes[q.Name])
                print('    pair '+a.Name+'/'+q.Name,flush=True)
                record('assembly '+a.Name+'/'+q.Name,sa,sq)
    print('V7 checks: opposite face tracks, forward pickup and manual drive',flush=True)
    for name in ('FeedRatchet','PickupRatchet','IndexWheel'):
        shape=d.getObject(name).Shape.copy();shape.Placement=App.Placement()
        put_error(name+' periodicity mm',periodic_vertex_error(shape,b.STEP_DEG))
    samples=sorted(set([j/20 for j in range(21)]+[.075,.225,.395,.4,.425,.449,.45,.475,.5,.844,.9,.95,.999]))
    # Actual clearance geometry repeats after one full index on all three
    # rotor profiles. Native coordinates are also checked at mid/end feed.
    for mode in (0,1,2):
        m.InputKind=mode;m.BeadSteps=11
        for p in samples:
            print('  cycle '+str(mode)+' '+str(p),flush=True)
            m.CyclePosition=p;d.recompute()
            invalid=[o.Name for o in d.Objects if 'Invalid' in o.State]
            if invalid:raise RuntimeError('Invalid V7 cycle expressions: '+str(invalid))
            if mode==2:
                expected=11-p;cap=0
            else:
                f=min(1,p/.4);r=max(0,min(1,(p-.5)/.5));cap=(b.STEP_DEG if mode==0 else b.CAP_ANGLE)*f*(1-r)
                advance=f if mode==0 else max(0,(b.CAP_ANGLE*f-b.ENTRY_DEG)/b.STEP_DEG)
                expected=11+advance
            put_error('V7 cycle feed',m.EffectiveSteps-expected)
            put_error('V7 cycle cap',m.CapAngle-cap)
            for i in (0,7,25):
                put_error('cycle actual bead mm',(d.getObject(f'Bead{i:02}').Placement.Base-b.path(b.HOME_S-i*b.BEAD_PITCH+b.BEAD_PITCH*expected)).Length)
            ia=round((b.route.LENGTH-b.route.JOIN_HOME)/b.RNA_PITCH)
            o=d.getObject(f'RnaLink{ia:03}');pose=b.rna_pose(ia*b.RNA_PITCH,b.RNA_STEP*expected,True)
            put_error('cycle actual RNA mm',(o.Placement.Base-pose.Base).Length)
            A=b.world(d.DriveCarrier);B=b.world(d.PickupPawl)
            ta=b.world(d.FeedRatchet);tb=b.world(d.PickupRatchet)
            record('A actual pawl / its track',A,ta);record('B actual pawl / its track',B,tb)
            record('A actual pawl / pickup track',A,tb);record('B actual pawl / manual track',B,ta)
            active=mode in (0,1) and p>.095 and p<=.4
            if active:
                name,pa,track=('B',B,tb) if mode==0 else ('A',A,ta)
                attempt=pa.copy();attempt.rotate(V(),V(0,0,1),-.2 if name=='A' else .2)
                contacts.append(dict(input=mode,cycle=p,pawl=name,gap_mm=pa.distToShape(track)[0],
                    attempted_wrong_relative_rotation_overlap_mm3=overlap(attempt,track)))
            # A retained hold-open tab must actually block a downward
            # attempt, rather than merely occupying the expected coordinates.
            if mode==0 and abs(p-.5)<1e-9:
                fork=b.world(d.PickupFork);lip=b.world(d.PickupLatchTip)
                down=fork.copy();down.translate(V(0,0,-.2))
                latch_witness.append(dict(seated_gap_mm=fork.distToShape(lip)[0],
                    downward_attempt_overlap_mm3=overlap(down,lip)))
            if p in (0,.2,.4,.45,.5,.7,.9,.95,1):actual_pairs()
            poses.append(dict(input=mode,cycle=p,feed=m.EffectiveSteps,upper_degrees=m.CapAngle,
                A_lift_mm=m.PawlLift.Value,B_lift_mm=m.PickupPawlLift.Value,
                fork_lift_mm=m.PickupForkLift.Value,latch_flex_mm=m.LatchDeflection.Value))
        print('  input '+str(mode)+' complete',flush=True)
    m.InputKind=0;m.BeadSteps=0;m.CyclePosition=0;d.recompute()
    pin=d.TravelPin.Shape.copy();pin.Placement=App.Placement()
    for angle in (-2,0,b.MAX_DRUM,b.MAX_DRUM+2):
        q=pin.copy();q.rotate(V(),V(0,0,1),-angle)
        stop_witness.append(dict(degrees=angle,overlap_mm3=overlap(q,b.world(d.LowerBody))))
    cap=d.UpperCarrier.Shape.copy();cap.Placement=App.Placement()
    post=b.cylinder(.85,8.5,b.polar(24,b.CAP_STOP_ANGLE,21.7));cap_stops=[]
    for angle in (-2,0,b.CAP_ANGLE,b.CAP_ANGLE+2):
        q=cap.copy();q.rotate(V(),V(0,0,1),-angle)
        cap_stops.append(dict(degrees=angle,overlap_mm3=overlap(q,post)))
    def stop_ok(items):return max(items[1]['overlap_mm3'],items[2]['overlap_mm3'])<TOL and min(items[0]['overlap_mm3'],items[3]['overlap_mm3'])>.001
    m.BeadSteps=22;m.InputKind=1;m.CyclePosition=.4;d.recompute()
    endpoint=dict(feed=m.EffectiveSteps,upper_degrees=m.CapAngle)
    attempt=b.world(d.DriveCarrier);attempt.rotate(V(),V(0,0,1),-.2)
    endpoint['attempted_extra_feed_overlap_mm3']=overlap(attempt,b.world(d.FeedRatchet))
    logic=dict(opposite_track_contacts=bool(contacts) and max(x['gap_mm'] for x in contacts)<1e-6,
        positive_torque_contacts=bool(contacts) and min(x['attempted_wrong_relative_rotation_overlap_mm3'] for x in contacts)>.0001,
        latch_holds_fork=bool(latch_witness) and all(x['seated_gap_mm']<1e-6 and x['downward_attempt_overlap_mm3']>.001 for x in latch_witness),
        positive_drum_stops=stop_ok(stop_witness),positive_upper_stops=stop_ok(cap_stops),
        endpoint_feed_blocked=endpoint['feed']==22 and abs(endpoint['upper_degrees']-b.ENTRY_DEG)<1e-8 and endpoint['attempted_extra_feed_overlap_mm3']>.001)
    m.InputKind=0;m.BeadSteps=0;m.CyclePosition=0;d.recompute()
    return dict(logic=logic,contacts=contacts,cycle_poses=poses,latch=latch_witness,
        drum_stops=stop_witness,upper_stops=cap_stops,endpoint=endpoint)


def finish(d,destination,parts,invalid,worst,errors,record,put_error,
           outside,handoff,gear_samples,envelope,envelope_ok,retention,
           retention_ok,min_clasp_clearance,min_link_lap,min_clasp_root_lap,retained):
    coupling=coupling_checks(d,record,put_error)
    print('V7 checks: assembly and source boundaries',flush=True)
    assembly=assembly_v7.run(d,overlap)
    logical=dict(retention_witnesses=retention_ok,continuous_RNA_bound=envelope_ok,
        continuous_TPU_cell_laps=min_link_lap>1e-5,clasp_guides_clear=min_clasp_clearance>1,
        clasp_roots_connected=min_clasp_root_lap>1e-5,
        retained_tail=retained['hidden_beads']==4 and retained['seated_beads']>=3,
        bead_spherical_bound=outside<TOL,native_accuracy=max(errors.values(),default=0)<1e-7,
        assembly_audit=assembly['passed'],**coupling['logic'])
    failures={k:v for k,v in worst.items() if v>(GEAR_TOL if k=='actual RNA rack / involute gear' else TOL)}
    source_names=('bracelet_v7.py','rna_path.py','coupling_v7.py','validation_v7.py','assembly_v7.py','engineering_v7.py')
    result=dict(version='7.0',status='FOCUSED_PASS' if not invalid and not failures and all(logical.values()) else 'REVIEW',
        mechanism_maturity='KINEMATIC_CANDIDATE; trip snap and continuous-pull reset unqualified',
        runtime='.'.join(App.Version()[:3]),parts=parts,invalid_objects=sorted(set(invalid)),
        collision_failures_mm3=failures,maximum_unintended_overlap_mm3=worst,
        logical_checks=logical,native_errors=errors,overlap_tolerance_mm3=TOL,
        actual_bead_handoff_samples=handoff,actual_RNA_gear_phase_samples=gear_samples,
        retained_at_full_travel=retained,RNA_envelope_certificate=envelope,
        retention_solid_witnesses=retention,minimum_clasp_guide_clearance_mm=min_clasp_clearance,
        minimum_strip_cell_lap_mm3=min_link_lap,minimum_clasp_root_lap_mm3=min_clasp_root_lap,
        coupling=coupling,assembly_audit=assembly,
        routing=dict(route_angle_degrees=b.RNA_ROUTE_ANGLE,material_length_mm=b.route.LENGTH,
            top_bend_radius_mm=b.route.TOP_RADIUS,return_bend_radius_mm=b.route.BOTTOM_RADIUS,
            return_centre_y_mm=b.RNA_Y+b.RNA_SIDE*b.route.HEIGHT,
            return_centre_z_mm=b.RNA_Z-b.RNA_DROP*b.route.HEIGHT,
            retained_front_drive_span_mm=2*b.route.TOP_HALF,
            open_or_closed=True,nominal_inextensible_layout=True),
        design=dict(forward_RNA_rocks_upper=True,upper_input_advances_RNA=True,
            direct_RNA_reverse_with_upper_home=True,two_opposite_tracks=True,
            dedicated_bidirectional_detent=True,three_bases_per_bead=True,
            no_user_operated_release=True,no_rewind_spring=True,manual_entry_degrees=b.ENTRY_DEG,
            manual_upper_stroke_degrees=b.CAP_ANGLE,RNA_pickup_stroke_degrees=b.STEP_DEG,
            prescribed_pause_for_reset=True,mechanical_continuous_pull_gate_implemented=False),
        source_sha256={n:hashlib.sha256((b.HERE/n).read_bytes()).hexdigest() for n in source_names},
        validation_boundary='Actual saved contacts, opposing torque-blocking witnesses, nominal forward/trip/return/reverse poses, latch hold-open geometry, RNA/protein handoff and route, stops, rigid fit and sampled assembly. Flexible leaf, trip snap, TPU layout and spring-driven motion are prescribed CAD states, not an elastic or dynamic solution. No claim of reliable full-rate feeding, printed operation or physical qualification.',
        engineering_still_required=[
            'Trip spring buckling/energy, trigger preload, latch release force and repeatable snap direction',
            'Continuous RNA pull: a mechanical gate or measured reset-speed limit; animation pause is not physical gating',
            'Partial strokes, mid-stroke direction changes and externally restrained upper subunit',
            'Spring selection and preload, friction, backlash, TPU tooth stability, clasp retention and fatigue'],
        physical_tests_still_required=['Printed fit, assembly, feed/retraction, upper return, force, click sound, wear, durability and hand comfort'],
        preserved_versions=dict(V6='Preserved; its own report and GUI evidence remain unchanged',V5='Preserved',V4='Preserved',V3='INCOMPLETE_USER_STOPPED',V2='HISTORICAL_PASS_INVALIDATED'))
    destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],collision_failures=failures,logical_checks=logical),indent=2),flush=True)
    return result
