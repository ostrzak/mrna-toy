"""Audit causal necessities of the saved V7 coupling, separately from animation.

This is a rejection/requirements audit, not a dynamics solver. A prescribed
trajectory, valid solids and a force estimate cannot establish an automatic
mechanism. In particular, unavailable evidence must never be treated as PASS.
"""
import FreeCAD as App
import Part
import bracelet_v7 as b
from engineering_v7 import estimates, trip_arc_length

V=App.Vector


def run(d,overlap):
    m=d.Motion
    state=(m.BeadSteps,m.CyclePosition,m.InputKind,m.StrandClosed)
    contacts=[];lengths=[];partial=[];reverse=[]
    try:
        for mode in (0,1):
            m.InputKind=mode;m.BeadSteps=11;m.StrandClosed=True
            for p in (0,.2,.35,.395,.4,.425,.45,.5,.7,.9,.99,1):
                m.CyclePosition=p;d.recompute()
                foot=b.world(d.PickupTripFoot);post=b.world(d.PickupTripPost)
                fork=b.world(d.PickupFork);lip=b.world(d.PickupLatchTip)
                B=b.world(d.PickupPawl);track=b.world(d.PickupRatchet)
                roof=b.world(d.PickupResetRoof)
                # The follower is the actual .45 mm sphere on the fork.
                # Shape.rotate() is retained in the feature Placement. The
                # local sphere centre must not receive B_ANGLE a second time.
                centre=d.PickupFork.getGlobalPlacement().multVec(V(28.8,0,25.8))
                sphere=Part.makeSphere(.45,centre)
                contacts.append(dict(input=mode,cycle=p,feed_steps=m.EffectiveSteps,
                    upper_degrees=m.CapAngle,
                    prescribed_trip_compression_mm=m.TripCompression.Value,
                    trip_foot_to_post_gap_mm=foot.distToShape(post)[0],
                    trip_foot_post_overlap_mm3=overlap(foot,post),
                    fork_to_latch_gap_mm=fork.distToShape(lip)[0],
                    fork_latch_overlap_mm3=overlap(fork,lip),
                    fork_follower_to_roof_gap_mm=sphere.distToShape(roof)[0],
                    pickup_to_track_gap_mm=B.distToShape(track)[0]))
                arc=trip_arc_length(m.TripCompression.Value,m.TripLeafLift.Value-1.4)
                lengths.append(dict(input=mode,cycle=p,centreline_length_mm=arc))
            for fraction in (.1,.25,.5,.75,.9):
                m.CyclePosition=.4*fraction;d.recompute()
                # With A driving, B's gap is ENTRY_DEG. Once that is taken
                # up on return, an unlifted B blocks further upper return.
                engaged_B=m.PickupForkLift.Value<1.25
                trapped_angle=max(0,m.CapAngle-b.ENTRY_DEG) if mode==1 else m.CapAngle
                block={}
                if engaged_B and trapped_angle>0:
                    free_return=b.ENTRY_DEG if mode==1 else 0
                    q=b.world(d.PickupPawl)
                    # At the blocking face the reverse-coast lift has fallen
                    # to zero. Recover A's entry clearance, then try to return
                    # .2 degrees farther with the actual drum held fixed.
                    q.translate(V(0,0,-m.PickupPawlLift.Value))
                    q.rotate(V(),V(0,0,1),free_return)
                    track=b.world(d.PickupRatchet)
                    gap=q.distToShape(track)[0]
                    q.rotate(V(),V(0,0,1),.2)
                    block=dict(after_entry_recovery_gap_mm=gap,
                        attempted_additional_upper_return_degrees=.2,
                        attempted_return_blocking_overlap_mm3=overlap(q,track))
                partial.append(dict(input=mode,driven_fraction=fraction,
                    feed_steps=m.EffectiveSteps,upper_degrees=m.CapAngle,
                    fork_lift_mm=m.PickupForkLift.Value,
                    pickup_held_clear=m.PickupForkLift.Value>=1.25,
                    upper_may_remain_coupled_to_drum_on_release=engaged_B and trapped_angle>0,
                    approximate_upper_angle_after_free_A_entry_return_degrees=trapped_angle,
                    actual_pawl_return_witness=block))
        m.InputKind=2;m.BeadSteps=11
        for p in (0,.125,.25,.5,.75,.875,1):
            m.CyclePosition=p;d.recompute()
            reverse.append(dict(cycle=p,feed=m.EffectiveSteps,upper=m.CapAngle,
                pickup_lift_mm=m.PickupPawlLift.Value,
                pickup_to_track_gap_mm=b.world(d.PickupPawl).distToShape(b.world(d.PickupRatchet))[0]))
    finally:
        m.BeadSteps,m.CyclePosition,m.InputKind,m.StrandClosed=state;d.recompute()
    force=estimates()
    rest=trip_arc_length(0,-1.4)
    for row in lengths:row['strain_relative_to_initial_CAD']=(row['centreline_length_mm']-rest)/rest
    requirements={
        'return_spring_overcomes_entry_and_reset':False,
        'trip_contact_and_stored_energy_established':False,
        'continuous_pull_mechanically_gated_or_reset_rate_qualified':False,
        'partial_manual_release_returns_without_rolling_drum_back':False,
        'arbitrary_partial_stroke_and_reverse_transitions_established':False,
        'separate_bidirectional_detent_present':bool(d.getObject('DetentTip') and d.getObject('IndexWheel')),
        'reverse_home_native_pose_exists':all(abs(r['upper'])<1e-8 for r in reverse),
    }
    return dict(status='REVIEW',functional_mechanism_established=False,
        required_mechanical_checks=requirements,
        evaluation_status=dict(return_load='FAIL_ANALYTICAL_NECESSARY_CONDITION',
            trip_snap='NO_ELASTIC_OR_ENERGY_SOLUTION',continuous_pull_gate='NOT_IMPLEMENTED',
            partial_return='FAIL_COUPLED_CONTACT_CONSTRAINT',
            arbitrary_reverse_transition='NO_CONTACT_DRIVEN_STATE_SOLUTION',
            bidirectional_detent='GEOMETRY_PRESENT; material/force/fatigue unqualified',
            home_reverse='PRESCRIBED_NATIVE_POSES_ONLY'),
        actual_solid_contact_samples=contacts,trip_centreline_samples=lengths,
        partial_stroke_audit=partial,native_reverse_samples=reverse,force_budget=force,
        blockers=[
            'Return spring is weaker than the frictionless entry-cam load, before reset/latch/bearing loads.',
            'Trip displacement and snap branch are prescribed; a contact-driven elastic equilibrium and energy release have not been established.',
            'No physical interlock holds continuous forward RNA during return/reset. The GUI pause cannot enforce that in hardware.',
            'Before the end trip, B is not held open during partial manual return; after A entry is recovered, B can backdrive the drum or hold the upper away from home.',
            'InputKind changes prescribe a new state. They do not establish accessible mid-stroke reverse transitions.'
        ],
        boundary='Actual contact gaps and necessary analytical conditions can reject this candidate. These checks do not solve nonlinear elasticity, frictional contact, rate-dependent reset or physical feeding, and cannot establish a functional PASS.')
