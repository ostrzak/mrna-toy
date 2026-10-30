"""Focused V5 solid/phase/kinematic checks. No force or physical qualification."""
from pathlib import Path
import hashlib
import json
import math
import FreeCAD as App
import Part
import bracelet_v5 as b

V=App.Vector
TOL=1e-5
GEAR_TOL=5e-5  # Native Bezier involute contact approximation, not a print fit.


def overlap(a,c):
    if a.isNull() or c.isNull() or not a.BoundBox.intersect(c.BoundBox):
        return 0.0
    return max(0.0,a.common(c).Volume)


def crop(shape,centre,half=3.25):
    return shape.common(Part.makeBox(2*half,2*half,2*half,centre-V(half,half,half)))


def run(d,report_path=None):
    destination=Path(report_path) if report_path else b.HERE/'checks.json'
    destination.parent.mkdir(parents=True,exist_ok=True)
    m=d.Motion
    m.BeadSteps,m.CapStroke,m.ReverseRelease=0,0,False
    d.recompute()
    parts={o.Name:dict(valid=o.Shape.isValid(),solids=len(o.Shape.Solids),volume_mm3=round(o.Shape.Volume,5))
           for o in d.Objects if hasattr(o,'DisplayColour')}
    invalid=[name for name,info in parts.items() if not info['valid'] or info['solids']!=1]
    worst={}
    def record(name,a,c):
        worst[name]=max(worst.get(name,0),overlap(a,c))
    fixed_names=['LowerBody','LowerLid','BeadKeeper','StopRing']
    fixed={name:b.world(d.getObject(name)) for name in fixed_names}
    print('V5 checks: real involute meshes at nine sub-tooth phases',flush=True)
    tile=Part.makeBox(14,15,3.2,V(-7,-b.IDLER_R-7.5,b.GEAR_Z-.5))
    for j in range(9):
        m.BeadSteps=j/(8*3)
        d.recompute()
        sun=b.world(d.SunGear).common(tile)
        ring=b.world(d.Rna).common(tile)
        idler=b.world(d.RnaIdler)
        record('sun/idler mesh',sun,idler)
        record('RNA/idler mesh',ring,idler)
        print('  gear phase %d/8'%j,flush=True)
    print('V5 checks: actual bead solids and tangent pocket handoff',flush=True)
    drum=d.BeadDrum.Shape.copy()
    drum.Placement=App.Placement()
    keeper=b.world(d.BeadKeeper)
    variants=[]
    for kind in range(3):
        actual=next(o for o in d.Protein.Group if hasattr(o,'BeadVariant') and o.BeadVariant==kind)
        shape=actual.Shape.copy()
        shape.Placement=App.Placement()
        variants.append(shape)
    sphere=Part.makeSphere(b.BEAD_R)
    outside=max(s.cut(sphere).Volume for s in variants)
    actual_samples,envelope_samples=0,0
    for j in range(9):
        distance=j*b.BEAD_PITCH/8
        wheel=drum.copy()
        wheel.rotate(V(),V(0,0,1),-math.degrees(distance/b.STORE_R))
        for k,s in enumerate([distance-b.BEAD_PITCH,distance,distance+b.BEAD_PITCH]):
            centre=b.path(s)
            local=crop(wheel,centre)
            envelope=Part.makeSphere(b.BEAD_R,centre)
            record('spherical bead/drum handoff',envelope,local)
            envelope_samples+=1
            # The sphere test covers every variant and wire roll. Retain a
            # real saved solid witness for each position and phase as well.
            shape=variants[(j+k)%3]
            bead=b.placed_bead(shape,s,90*(j%4))
            record('actual bead/drum handoff',bead,local)
            record('actual bead/fixed keeper',bead,crop(keeper,centre))
            actual_samples+=1
        print('  bead handoff phase %d/8'%j,flush=True)
    tab_sweep=b.annulus(b.RNA_OUT-.2,b.RNA_OUT+max(b.RNA_BASE_LENGTHS)+.65,
                       b.GEAR_Z+b.GEAR_WIDTH/2-.59,1.18)
    record('RNA base sweep/lower body',tab_sweep,fixed['LowerBody'])
    print('V5 checks: conservative continuous rotational and protein envelopes',flush=True)
    sweeps={
        'drum':b.drum_sweep(.01),
        'sun':b.cylinder(b.MODULE*(b.SUN_TEETH/2+1)+.01,b.GEAR_WIDTH+.02,V(0,0,b.GEAR_Z-.01)),
        'idler':b.cylinder(b.MODULE*(b.IDLER_TEETH/2+1)+.01,b.GEAR_WIDTH+.02,V(0,-b.IDLER_R,b.GEAR_Z-.01)),
        'RNA':b.annulus(b.RNA_R-1-.01,b.RNA_OUT+.35+.01,b.GEAR_Z-.16,b.GEAR_WIDTH+.82),
        'protein arc':Part.makeTorus(b.STORE_R,b.BEAD_R,V(0,0,b.BEAD_Z),V(0,0,1)),
        'protein straight':b.cylinder(b.BEAD_R,160,V(0,b.STORE_R,b.BEAD_Z),V(1,0,0)),
    }
    # Verify that the saved rotating solids are contained in those envelopes.
    for name,obj in [('drum',d.BeadDrum),('sun',d.SunGear),('idler',d.RnaIdler),('RNA',d.Rna)]:
        m.BeadSteps=0
        d.recompute()
        worst[name+' outside declared sweep']=max(0,b.world(obj).cut(sweeps[name]).Volume)
    for label,shape in sweeps.items():
        for name in fixed_names:
            record(label+' continuous sweep/'+name,shape,fixed[name])
        print('  continuous envelope: '+label,flush=True)
    print('V5 checks: saved native motion at forward/reverse poses',flush=True)
    poses=[0,.125,.25,.5,.75,1,5.5,11,16.5,21,21.5,22]
    error,wire_error,ratio_error=0.0,0.0,0.0
    retained=[]
    preload={'drive_leaf/ratchet':0.0,'holding_leaf/ratchet':0.0}
    for step in poses:
        m.BeadSteps=step
        m.CapStroke=(step%1) if step<1 else 0
        d.recompute()
        for i in range(b.BEADS):
            bead=d.getObject(f'Bead{i:02}')
            expected=b.path(b.HOME_S-i*b.BEAD_PITCH+step*b.BEAD_PITCH)
            error=max(error,(bead.Placement.Base-expected).Length)
        for i in range(b.BEADS-1):
            wire=d.getObject(f'Wire{i:02}')
            a=d.getObject(f'Bead{i:02}').Placement.Base
            c=d.getObject(f'Bead{i+1:02}').Placement.Base
            wire_error=max(wire_error,abs(wire.Height.Value-(c-a).Length))
        ratio_error=max(ratio_error,abs(m.BasesPassed-3*step),abs(m.RnaDegrees*b.RNA_TEETH/360-3*step))
        if step in (0,.5,1):
            upper=b.world(d.UpperLobe)
            for name in fixed_names:
                record('upper/'+name,upper,fixed[name])
            record('upper/ratchet',upper,b.world(d.Ratchet))
        for key,name in [('drive_leaf/ratchet','DrivePawl'),('holding_leaf/ratchet','HoldPawl')]:
            preload[key]=max(preload[key],overlap(b.world(d.getObject(name)),b.world(d.Ratchet)))
        invalid += [o.Name for o in d.Objects if 'Invalid' in o.State]
        print('  native pose %.3f / 22'%step,flush=True)
    for step in reversed(poses):
        m.BeadSteps,m.CapStroke,m.ReverseRelease=step,0,True
        d.recompute()
        for i in range(b.BEADS):
            error=max(error,(d.getObject(f'Bead{i:02}').Placement.Base-b.path(b.HOME_S-i*b.BEAD_PITCH+step*b.BEAD_PITCH)).Length)
        for name in ('DrivePawl','HoldPawl'):
            record('released '+name+'/ratchet',b.world(d.getObject(name)),b.world(d.Ratchet))
    m.BeadSteps=b.EMIT
    d.recompute()
    hidden=[i for i in range(b.BEADS) if d.getObject(f'Bead{i:02}').PathDistance<=b.MOUTH_X]
    engaged=[i for i in range(b.BEADS) if d.getObject(f'Bead{i:02}').PathDistance<=0]
    retained=dict(hidden_beads=len(hidden),seated_beads=len(engaged),hidden_indices=hidden)
    print('V5 checks: physical travel-stop geometry, not only slider limits',flush=True)
    pin=d.TravelPin.Shape.copy()
    pin.Placement=App.Placement()
    stop=b.world(d.StopRing)
    stops=[]
    for angle in (-2,0,b.MAX_DRUM,b.MAX_DRUM+2):
        shape=pin.copy()
        shape.rotate(V(),V(0,0,1),-angle)
        stops.append(dict(drum_degrees=angle,overlap_mm3=overlap(shape,stop)))
    stops_ok=max(stops[1]['overlap_mm3'],stops[2]['overlap_mm3'])<TOL and min(stops[0]['overlap_mm3'],stops[3]['overlap_mm3'])>.001
    # All 112 bases are real saved solids on the same closed-loop placement.
    base_count=len([o for o in d.RnaLoop.Group if o.Name.startswith('Base')])
    failures={k:v for k,v in worst.items() if v>(GEAR_TOL if k in ('sun/idler mesh','RNA/idler mesh') else TOL)}
    core_ok=(not invalid and not failures and outside<TOL and error<1e-7
             and wire_error<1e-7 and ratio_error<1e-7 and stops_ok and retained['hidden_beads']==4
             and retained['seated_beads']>=3 and base_count==112)
    result=dict(version='5.0',status='FOCUSED_PASS' if core_ok else 'REVIEW',
        runtime='.'.join(App.Version()[:3]),parts=parts,invalid_objects=sorted(set(invalid)),
        maximum_unintended_overlap_mm3=worst,overlap_tolerance_mm3=TOL,
        involute_contact_approximation_tolerance_mm3=GEAR_TOL,collision_failures_mm3=failures,
        actual_bead_handoff_samples=actual_samples,spherical_envelope_handoff_samples=envelope_samples,
        sampled_gear_phases=9,sampled_forward_poses=len(poses),sampled_reverse_poses=len(poses),
        native_position_error_mm=error,native_wire_length_error_mm=wire_error,coupling_error=ratio_error,
        bead_outside_spherical_bound_mm3=outside,retained_at_full_travel=retained,travel_stops=stops,
        unloaded_ratchet_leaf_overlap_mm3=preload,
        design=dict(handheld=True,wearable=False,closed_RNA_loop=True,RNA_bases=112,RNA_bases_per_bead=3,
                    drum_pockets=28,protein_beads=26,bead_pitch_mm=6,bead_bound_mm=4.4,
                    maximum_feed_mm=132,maximum_drum_degrees=b.MAX_DRUM,drum_pitch_diameter_mm=2*b.STORE_R,
                    gear_teeth=dict(RNA=112,idler=14,sun=84),tensioned_rewind=False,automatic_curling=False),
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (b.HERE/'bracelet_v5.py',b.HERE/'validation_v5.py')},
        validation_boundary='Focused rigid solid, actual bead handoff, actual gear phase, housing, travel-stop and native prescribed motion checks. Ratchet leaves are unloaded elastic geometry; their overlaps are recorded separately. RNA shown on nominal circular path. No force, compliance, spring, manufacturing or physical qualification.',
        physical_tests_still_required=['Direct bead capture and bidirectional transfer under load',
          'Bead pitch fixation, wire bending force and fatigue','Flexible RNA engagement, low stretch and retention',
          'Click ratchet leaves, cap return spring selection and reverse-release linkage',
          'Printed fits, fastening, strength, friction, wear and handling'],
        preserved_versions=dict(V4='FOCUSED_PASS; preserved cuff comparison',V3='INCOMPLETE_USER_STOPPED',V2='HISTORICAL_PASS_INVALIDATED'))
    destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    m.BeadSteps,m.CapStroke,m.ReverseRelease=0,0,False
    d.recompute()
    print(json.dumps({k:v for k,v in result.items() if k!='parts'},indent=2),flush=True)
    return result
