"""Continuous nominal RNA/clasp clearance from actual saved component solids.

Endpoint distances certify full intervals using a rigid-motion speed bound;
nearby intervals subdivide. This is geometric evidence for the two prescribed
layouts, not elasticity, force, reliable feeding or automatic latch operation.
"""
import math
import FreeCAD as App
import Part
import bracelet_v7 as b

V=App.Vector


def certify(canonical,pose_at,start,end,targets,overlap,offset=0,margin=.05):
    box=canonical.BoundBox
    radius=max(V(x+offset,y,z).Length for x in (box.XMin,box.XMax)
               for y in (box.YMin,box.YMax) for z in (box.ZMin,box.ZMax))
    speed=1+radius/b.route.RADIUS
    bounds={n:t.BoundBox for n,t in targets.items()}
    distance_queries=0;box_certificates=0
    cache={};failures=[];minimum=1e9;certified=0;deepest=0
    def measure(s):
        nonlocal distance_queries,box_certificates
        if s in cache:return cache[s]
        pose=pose_at(s)
        if offset:pose.Base+=pose.Rotation.multVec(V(offset,0,0))
        shape=canonical.copy();shape.Placement=pose
        qb=shape.BoundBox;gaps=[]
        for name,target in targets.items():
            tb=bounds[name]
            lower=math.sqrt(sum(max(0,getattr(qb,k+'Min')-getattr(tb,k+'Max'),
                                     getattr(tb,k+'Min')-getattr(qb,k+'Max'))**2 for k in 'XYZ'))
            if lower>=1 or ('pose envelope' in name and lower>0):
                # Box separation is a conservative clearance bound. Refine
                # nearby actual solids, keeping distant bounds conservative.
                gaps.append(lower);box_certificates+=1
            else:
                gaps.append(shape.distToShape(target)[0]);distance_queries+=1
        gap=min(gaps)
        hits={n:overlap(shape,t) for n,t in targets.items()} if gap<1e-8 else {}
        hits={n:x for n,x in hits.items() if x>1e-5}
        cache[s]=(gap,hits)
        return gap,hits
    intervals=[(start,end,0)]
    while intervals:
        a,c,depth=intervals.pop();ga,ha=measure(a);gc,hc=measure(c)
        minimum=min(minimum,ga,gc)
        if ha or hc:
            failures.append(dict(path_parameter_mm=a if ha else c,overlaps_mm3=ha or hc));break
        # Every intermediate pose is <=speed*(c-a)/2 from an endpoint.
        # Distance to fixed material is 1-Lipschitz under that displacement.
        if min(ga,gc)-margin>speed*(c-a)/2:
            certified+=1;continue
        if depth>=24:
            failures.append(dict(unresolved_interval_mm=[a,c],endpoint_gap_mm=min(ga,gc)));break
        mid=(a+c)/2;intervals.extend([(a,mid,depth+1),(mid,c,depth+1)])
        deepest=max(deepest,depth+1)
    return dict(passed=not failures,actual_saved_solid=True,
        maximum_frame_radius_mm=radius,speed_bound_per_mm_path=speed,
        path_interval_mm=[start,end],samples=len(cache),certified_intervals=certified,
        maximum_subdivision_depth=deepest,minimum_endpoint_clearance_lower_bound_mm=minimum,
        exact_distance_queries=distance_queries,bounding_box_certificates=box_certificates,
        certified_clearance_mm=margin,failures=failures)


def run(d,overlap):
    targets={n:b.world(d.getObject(n)) for n in
        ['LowerLid','GearGuard','BeadKeeper','PickupRoofScrew','DetentScrew']+
        [f'HousingScrew{i:02}' for i in range(3)]}
    # These envelopes contain the checked saved drum and all spherical bead
    # bounds throughout travel. The protein bound includes the straight exit.
    targets['continuous drum envelope']=b.drum_sweep(.01)
    targets['continuous protein envelope']=b.protein_envelope(b.BEAD_R)
    # All upper members rotate about Z, and their axial motion is nonnegative.
    # The four mm allowance exceeds the latch/trip local deformation ranges.
    upper_bound=b.cylinder(80,49.1,V(0,0,20.9))
    fixed_coupling={'PickupResetRoof','PickupTripPost',
        'CapRetainer','CapWasher','DetentAnchor','DetentTip','DetentWasher'}|{
        f'DetentLeaf{i}' for i in range(8)}
    members={}
    def upper_member(o):
        if o.Name=='Clicker':return True
        return any(upper_member(p) for p in o.InList if p.TypeId=='App::Part')
    for o in d.Objects:
        if not hasattr(o,'DisplayColour') or not (upper_member(o) or o.Name in fixed_coupling):continue
        box=b.world(o).optimalBoundingBox(False)
        radial=math.hypot(max(abs(box.XMin),abs(box.XMax)),max(abs(box.YMin),abs(box.YMax)))
        members[o.Name]=dict(minimum_z_mm=box.ZMin,maximum_z_mm=box.ZMax,
            conservative_radial_bound_mm=radial,
            contained=box.ZMin>=20.9-1e-8 and box.ZMax+4<=70 and radial+4<=80)
    upper_ok=bool(members) and all(x['contained'] for x in members.values())
    targets['upper/coupling pose envelope above z20.9']=upper_bound
    shaft_bound=b.cylinder(8.01,32.55,V(0,0,1))
    pin_bound=b.cylinder(16.76,1.9,V(0,0,5.8))
    targets['coaxial shaft/hub envelope']=shaft_bound
    targets['travel-pin rotational envelope']=pin_bound
    rotor_bounds={n:overlap(b.world(d.getObject(n)),b.world(d.getObject(n)).cut(envelope))
        for n,envelope in [('CentreAxle',shaft_bound),('DriveHub',shaft_bound),
                           ('IndexSleeve',shaft_bound),('TravelPin',pin_bound)]}
    rotor_ok=all(x<1e-5 for x in rotor_bounds.values())
    rows=[]
    for closed in (True,False):
        def route_pose(s):
            p,turn=b.rna_point(s,closed)
            return App.Placement(p,App.Rotation(b.PLANE_NORMAL,-math.degrees(turn)))
        start,end=(0,b.route.LENGTH) if closed else (-b.route.LENGTH,b.route.LENGTH)
        # The full curves conservatively contain every saved cell/base pose
        # across full feed, including positions absent at the clasp joint.
        for name in ['RnaLink002']+[f'Base{i:03}' for i in range(2,6)]:
            canonical=d.getObject(name).Shape.copy();canonical.Placement=App.Placement()
            result=certify(canonical,route_pose,start,end,targets,overlap,margin=0)
            rows.append(dict(component=name,closed=closed,category='RNA',**result))
            print('  continuous travel '+name+' '+str(closed)+': '+str(result['passed'])+
                  ', '+str(result['samples'])+' interval endpoint poses',flush=True)
        for name,material,offset in [('ClaspReceiver',2.5,-2.5),('ClaspButton',b.route.LENGTH-2.5,2.5)]:
            canonical=d.getObject(name).Shape.copy();canonical.Placement=App.Placement()
            def feed_pose(feed):return b.rna_pose(0 if closed else material,feed,closed)
            result=certify(canonical,feed_pose,0,b.RNA_MAX,targets,overlap,
                           offset=offset if closed else 0)
            rows.append(dict(component=name,closed=closed,category='clasp',**result))
            print('  continuous clasp '+name+' '+str(closed)+': '+str(result['passed'])+
                  ', '+str(result['samples'])+' interval endpoint poses',flush=True)
    return dict(passed=upper_ok and rotor_ok and all(x['passed'] for x in rows),
        RNA_passed=all(x['passed'] for x in rows if x['category']=='RNA'),
        clasp_passed=all(x['passed'] for x in rows if x['category']=='clasp'),
        cases=rows,upper_pose_envelope=dict(passed=upper_ok,members=members,
            radius_mm=80,z_range_mm=[20.9,70],local_motion_allowance_mm=4),
        shaft_pin_envelopes=dict(passed=rotor_ok,saved_solids_outside_bound_mm3=rotor_bounds),
        targets=list(targets),
        proof='Rigid point speed <=1+R/r per mm path, from unit arc-length speed and angular rate <=1/r. Distance to fixed material is 1-Lipschitz; endpoint gaps certify every full interval. Remaining intervals subdivide; unresolved intervals fail.',
        body_clearance_reference='The validator separately checks continuous rail/clasp and base tubes against the actual lower body; their section/curvature certificates contain these profiles.',
        boundary='Actual saved component solids on the nominal open/closed RNA layouts. Conservative box gaps are refined by exact distance queries near fixed material. Body clearance uses separate continuous tube certificates. Protein and drum envelopes cover the checked native bead/drum positions. The upper envelope bounds prescribed poses, not mechanical causality. RNA/gear contact uses separate actual phase checks. No elastic, force, physical feed or automatic trip/reset qualification.')
