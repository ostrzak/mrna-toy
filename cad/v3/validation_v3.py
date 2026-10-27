"""Independent geometric acceptance checks for the current cuff mechanism.

Use conservative swept envelopes for guide clearance and actual local solids
for the gear mesh, cam pin and swivel. No friction or elastic simulation.
"""
import json
import math
import FreeCAD as App
import Part
import bracelet_v3 as b

V = App.Vector


def overlap(a, c):
    bb, cb = a.BoundBox, c.BoundBox
    if not bb.intersect(cb):
        return 0.0
    # Crop large cuff/gear solids to the local moving component before booleans.
    x0, x1 = max(bb.XMin, cb.XMin)-.01, min(bb.XMax, cb.XMax)+.01
    y0, y1 = max(bb.YMin, cb.YMin)-.01, min(bb.YMax, cb.YMax)+.01
    z0, z1 = max(bb.ZMin, cb.ZMin)-.01, min(bb.ZMax, cb.ZMax)+.01
    clip = Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0, y0, z0))
    if len(a.Faces) > 200:
        a = a.common(clip)
    if len(c.Faces) > 200:
        c = c.common(clip)
    return a.common(c).Volume


def annulus(inner, outer, y, width):
    return b.cylinder(outer, width, V(0, y, 0)).cut(b.cylinder(inner, width+2, V(0, y-1, 0)))


def profile_clearance():
    """Signed 2D distance from the spherical fork sections to the actual polygon."""
    outline = b.feed_outline()
    edges = [(outline[i], outline[(i+1) % len(outline)]) for i in range(len(outline))]
    section_r = math.sqrt(b.BEAD_R**2-.85**2)
    low, high = 1e9, -1e9
    count = 0
    for j in range(321):
        s = -11+22*j/320
        p = b.path(s)-V(0, 0, b.SHAFT_Z)
        theta = -s/b.FEED_R
        x = p.x*math.cos(theta)-p.z*math.sin(theta)
        z = p.x*math.sin(theta)+p.z*math.cos(theta)
        if math.hypot(x, z) > 9.4+section_r:
            continue
        dsq = 1e9
        for (ax, az), (cx, cz) in edges:
            dx, dz = cx-ax, cz-az
            t = max(0, min(1, ((x-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz)))
            dsq = min(dsq, (x-ax-t*dx)**2+(z-az-t*dz)**2)
        ray = (math.atan2(x, z) % b.TAU)/b.TAU*len(outline)
        idx = int(ray) % len(outline)
        a, c = outline[idx], outline[(idx+1) % len(outline)]
        rr = (1-(ray-int(ray)))*math.hypot(*a)+(ray-int(ray))*math.hypot(*c)
        signed = math.sqrt(dsq)*(1 if math.hypot(x, z) >= rr else -1)
        gap = signed-section_r
        low, high = min(low, gap), max(high, gap)
        count += 1
    return {'samples': count, 'minimum_mm': low, 'maximum_mm': high,
            'boundary': 'Actual sampled polygon, conservative maximum bead section in either fork lane.'}


def run(d):
    print('V3 checks: validity and continuous swept envelopes', flush=True)
    m = d.Motion
    m.PoseProtein, m.DialDegrees = False, 0
    d.recompute()
    parts = {o.Name: {'valid': o.Shape.isValid(), 'solids': len(o.Shape.Solids),
                     'volume_mm3': round(o.Shape.Volume, 4)}
             for o in d.Objects if hasattr(o, 'Shape') and hasattr(o, 'DisplayColour')}
    bodies = [b.world(d.CuffFrame), b.world(d.CuffRear)]
    peg = b.cylinder(.45, 2.8, b.radial(b.STOP_R, 0, -3.2))
    # Each envelope covers all phases. The fixed travel-stop pin is checked separately.
    rna_sweep = b.union([annulus(35.1, 36.45, -9, 1.4),
                         annulus(35.25, 36.55, -7.8, 4.35),
                         annulus(35.1, 35.55, -3.65, .5),
                         annulus(32.8, b.RNA_R+b.MODULE, -3.35, 1.5)])
    drive_sweep = b.union([b.cylinder(b.MODULE*(b.PINION_TEETH/2+1), 1.5, V(0, -3.35, b.SHAFT_Z)),
                           b.cylinder(2.4, 14.45, V(0, -3.35, b.SHAFT_Z)),
                           b.cylinder(math.sqrt(2)*2.2, 3.4, V(0, 2.6, b.SHAFT_Z)),
                           b.cylinder(math.sqrt(2)*2.2, 2, V(0, 9.1, b.SHAFT_Z)),
                           b.cylinder(4.12, 1.1, V(0, -.35, b.SHAFT_Z))])
    feed_sweep = b.cylinder(9.4, 3.2, V(0, 2.8, b.SHAFT_Z))
    cam_sweep = b.cylinder(7.5, 1.9, V(0, 9.2, b.SHAFT_Z))
    bead_sweep = b.union([b.storage_tube(b.BEAD_R),
                          b.output_tube(b.BEAD_R, 160)])
    worst = {}
    for suffix, body in zip(['frame', 'rear'], bodies):
        for name, shape in [('RNA sweep', rna_sweep), ('drive sweep', drive_sweep),
                            ('feeder sweep', feed_sweep), ('cam sweep', cam_sweep),
                            ('protein swept path', bead_sweep)]:
            if name == 'RNA sweep':
                body_test = body.cut(peg)
            else:
                body_test = body
            worst[name+'/'+suffix] = overlap(shape, body_test)
    print('  envelope overlaps', {k: round(v, 5) for k, v in worst.items()}, flush=True)
    # Crop the RNA to the readout station: the other 300 degrees cannot touch the pinion.
    local_mesh = Part.makeBox(15, 2.0, 7.0, V(-7.5, -3.5, 33.5))
    mesh_max = 0.0
    for j in range(9):
        m.DialDegrees = j*2.5/8
        d.recompute()
        mesh_max = max(mesh_max, overlap(b.world(d.Rna).common(local_mesh), b.world(d.InputDrive)))
    worst['RNA/input mesh'] = mesh_max
    print('  RNA gear mesh max overlap', mesh_max, flush=True)
    samples = sorted(set([0, 37.5, 82.5, 120, b.MAX_DIAL]+[7.5*j/16 for j in range(17)]))
    position_error, slot_error = 0.0, 0.0
    gaps, invalid, cam_gaps = [], [], []
    for key in ['cam/follower', 'slider/frame', 'slider/rear', 'lever/frame', 'lever/rear',
                'lobe/frame', 'lobe/rear', 'lobe/slider', 'lobe/lever', 'slider/lever', 'wire/bead', 'bead/feeder actual', 'leaf/frame', 'leaf/rear']:
        worst[key] = 0.0
    for index, angle in enumerate(samples):
        m.DialDegrees = angle
        d.recompute()
        invalid += [o.Name for o in d.Objects if 'Invalid' in o.State]
        slider, lever, lobe, cam, feeder = [b.world(d.getObject(n)) for n in ['FollowerSlider', 'LeverPost', 'UpperLobe', 'SwivelCam', 'BeadWheel']]
        worst['cam/follower'] = max(worst['cam/follower'], overlap(cam, slider))
        # Test lobe extrema and intermediate quarter-cycle poses against the actual cases.
        if index <= 16 or angle == b.MAX_DIAL:
            for name, shape in [('slider', slider), ('lever', lever), ('lobe', lobe)]:
                for suffix, body in zip(['frame', 'rear'], bodies):
                    worst[name+'/'+suffix] = max(worst[name+'/'+suffix], overlap(shape, body))
            worst['lobe/slider'] = max(worst['lobe/slider'], overlap(lobe, slider))
            worst['lobe/lever'] = max(worst['lobe/lever'], overlap(lobe, lever))
            worst['slider/lever'] = max(worst['slider/lever'], overlap(slider, lever))
        pin = V(b.PIVOT.x+m.FollowerShift.Value, 12.8, b.SHAFT_Z+1.3)
        local = d.Swivel.Placement.inverse().multVec(pin)
        slot_error = max(slot_error, abs(local.x))
        for i in range(b.BEADS):
            o = d.getObject(f'Bead{i:02}')
            expected = b.path(b.HOME_S-i*b.BEAD_PITCH+m.FeedDistance.Value)
            position_error = max(position_error, (o.Placement.Base-expected).Length)
            if i:
                gaps.append((o.Placement.Base-d.getObject(f'Bead{i-1:02}').Placement.Base).Length)
                # Test the actual saved bead phase, including entry and exit.
                if abs(o.PathDistance) <= 10:
                    wire = b.world(d.getObject(f'Wire{i-1:02}'))
                    worst['wire/bead'] = max(worst['wire/bead'], overlap(wire, b.world(o)), overlap(wire, b.world(d.getObject(f'Bead{i-1:02}'))))
            if abs(o.PathDistance) <= 9 and angle in [0, 1.875, 3.75, 5.625, 7.5, b.MAX_DIAL]:
                worst['bead/feeder actual'] = max(worst['bead/feeder actual'], overlap(b.world(o), feeder))
        print('  coupled pose %.4g deg / swivel %.3g deg' % (angle, m.SwivelDegrees), flush=True)
    leaf = b.world(d.DetentLeaf)
    for suffix, body in zip(['frame', 'rear'], bodies):
        worst['leaf/'+suffix] = overlap(leaf, body)
    stops = []
    for angle in [-1, 0, b.MAX_DIAL, b.MAX_DIAL+1]:
        rna = d.Rna.Shape.copy()
        rna.rotate(V(), V(0, 1, 0), angle)
        stops.append({'dial_degrees': angle, 'pin_overlap_mm3': overlap(rna, peg)})
    m.DialDegrees, m.PoseProtein = b.MAX_DIAL, True
    d.recompute()
    posed_error = max((d.getObject(f'Bead{i:02}').Placement.Base-b.path(b.HOME_S-i*6+b.EMIT*6, True)).Length for i in range(b.BEADS))
    posed_overlap = max(overlap(b.world(d.getObject(f'Bead{i:02}')), body)
                        for i in range(b.BEADS) for body in bodies+[b.world(d.UpperLobe)])
    invalid += [o.Name for o in d.Objects if 'Invalid' in o.State]
    profile = profile_clearance()
    all_valid = all(p['valid'] and p['solids'] == 1 for p in parts.values()) and not invalid
    collisions_ok = max(worst.values()) < 1e-5 and posed_overlap < 1e-5
    stops_ok = min(stops[0]['pin_overlap_mm3'], stops[3]['pin_overlap_mm3']) > .001 and max(t['pin_overlap_mm3'] for t in stops[1:3]) < 1e-5
    result = {
        'version': '3.0',
        'status': 'PASS' if all_valid and collisions_ok and stops_ok and position_error < 1e-7 and posed_error < 1e-7 and slot_error < 1e-7 and profile['minimum_mm'] > .05 else 'REVIEW',
        'parts': parts, 'invalid_objects': sorted(set(invalid)), 'sampled_coupled_poses': len(samples),
        'overlap_tolerance_mm3': 1e-5,
        'sampled_gear_phases': 9, 'maximum_unintended_overlap_mm3': worst,
        'position_expression_error_mm': position_error, 'posed_expression_error_mm': posed_error,
        'lever_slot_centreline_error_mm': slot_error, 'posed_protein_lobe_overlap_mm3': posed_overlap,
        'bead_pocket_profile_clearance': profile, 'stop_tests': stops,
        'minimum_bead_centre_spacing_mm': min(gaps), 'maximum_bead_centre_spacing_mm': max(gaps),
        'minimum_wire_to_fork_axial_clearance_mm': .85-b.WIRE_R,
        'wire_to_hub_radial_clearance_lower_bound_mm': b.FEED_R-b.WIRE_R-5.35,
        'kinematics': {'rna_bases_per_bead': 3, 'rna_full_circle_base_pitch_count': b.BASES,
            'visible_bases_on_C_arc': 128, 'pinion_teeth': 24, 'feeder_pockets': 8,
            'dial_degrees_per_bead': 7.5, 'maximum_dial_degrees': b.MAX_DIAL,
            'protein_feed_mm': b.EMIT*b.BEAD_PITCH, 'total_beads': b.BEADS,
            'nominal_emitted_beads': b.EMIT, 'retained_beads': b.BEADS-b.EMIT,
            'swivel_degrees_each_way': b.SWIVEL_MAX, 'swivel_cycles_per_bead': 1,
            'rna_readout_direction': '+X', 'protein_outlet_direction': '+X',
            'half_turn_in_protein_path': False, 'minimum_feed_path_bend_radius_mm': b.STORE_R,
            'bead_phase_at_home_in_pitches': b.HOME_S/b.BEAD_PITCH},
        'dimensions_mm': {'cuff_inner_diameter': 2*b.CUFF_IN, 'cuff_outer_diameter': 2*b.CUFF_OUT,
            'cuff_width': 19.6, 'bead_diameter': 2*b.BEAD_R, 'channel_diameter': 2*b.CHANNEL_R,
            'copper_core_diameter': 2*b.WIRE_R, 'keeper_diameter': 2*b.KEEPER_R,
            'rna_base_arc_pitch': b.TAU*b.RNA_R/b.BASES},
        'physical_tests_still_required': [
            'Spread cuff and RNA arc together at home: force, strain, fatigue and track retention',
            'Reverse feed into curved storage: wire buckling, bead fixation and friction',
            'Bidirectional bead handoff with the close guide; rounded bore fit and wire fatigue',
            'Printed pinion, groove cam and slider fits; wear and drive torque',
            'Detent preload, elastic deflection, click sound and flexure life',
            'Comfort, pinch clearances, end retention and final assembly fasteners'],
        'validation_boundary': 'Native prescribed kinematics, sampled actual contacts and conservative rigid swept envelopes. No elastic, stress, friction or gravity simulation.'}
    (b.HERE/'checks.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    m.PoseProtein, m.DialDegrees = False, 0
    d.recompute()
    print(json.dumps({k: result[k] for k in ['status', 'maximum_unintended_overlap_mm3', 'stop_tests', 'bead_pocket_profile_clearance', 'position_expression_error_mm', 'posed_expression_error_mm']}, indent=2), flush=True)
    return result

