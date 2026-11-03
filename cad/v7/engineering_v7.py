"""First-order force and causal audit; assumptions, not qualification.

N, mm, radians. Printed material properties, friction and real spring
characteristics must be measured. This calculation is deliberately separate
from the focused CAD PASS and cannot establish physical operation.
"""
import json
import math


def estimates():
    leaf_E=1700.0  # Assumed effective elastic modulus, N/mm², not grade data.
    leaf_length,leaf_thickness,leaf_height=12.0,1.3,1.0
    inertia=leaf_height*leaf_thickness**3/12
    leaf_k=3*leaf_E*inertia/leaf_length**3
    # Idealized radial cantilever with a 0.55 mm roller; approximate its
    # conjugate contact correction while retaining the CAD's running gap.
    def deflection(phase):
        r=14.1-.3*math.cos(phase)
        slope=.3*28*math.sin(phase)/r
        return r+.55*math.sqrt(1+slope*slope)+.04-14.1
    leaf_torque=0.0
    for j in range(2001):
        p=2*math.pi*j/2000;eps=1e-5
        rate=(deflection(p+eps)-deflection(p-eps))/(2*eps)*28
        leaf_torque=max(leaf_torque,abs(leaf_k*deflection(p)*rate))
    steel_G,steel_E=79000.0,200000.0  # Assumptions, not a supplier selection.
    wire,diameter,turns,free=.15,2.5,8,6.5
    axial_k=steel_G*wire**4/(8*diameter**3*turns)
    installed_min,installed_max=2.4,4.4
    axial_rest_force=axial_k*(free-installed_min)
    coast_lift=.89;coast_force=axial_k*(free-(installed_max-coast_lift))
    step=2*math.pi/28
    coast_torque=coast_force*1.25/step
    entry_torque=axial_rest_force*2/math.radians(3)
    torsion_wire,torsion_diameter,torsion_turns=.6,12.1,3
    torsion_k=steel_E*torsion_wire**4/(64*torsion_diameter*torsion_turns)
    torsion_preload=math.radians(22)
    cap_angle=math.radians(3+360/28)
    result = dict(status='INCOMPLETE_V7_FORCE_BUDGET',units='N, mm, N·mm, radians',
        missing_V7_terms=['Pickup pawl bias, snap-leaf compression and stored energy',
            'Hold-open latch and reset-roof friction/torque',
            'Continuous-pull reset coordination and reverse coast load'],
        assumptions=dict(leaf_effective_modulus_N_per_mm2=leaf_E,
            spring_shear_modulus_N_per_mm2=steel_G,spring_elastic_modulus_N_per_mm2=steel_E,
            friction_included=False,printed_anisotropy_included=False,dynamics_included=False),
        detent=dict(length_mm=leaf_length,radial_thickness_mm=leaf_thickness,height_mm=leaf_height,
            stiffness_N_per_mm=leaf_k,approx_preload_deflection_mm=.29,approx_peak_deflection_mm=.89,
            preload_force_N=.29*leaf_k,peak_force_N=.89*leaf_k,
            peak_resisting_torque_Nmm=leaf_torque,
            approximate_peak_outer_fibre_strain=1.5*leaf_thickness*.89/leaf_length**2),
        axial_bias_candidate=dict(wire_mm=wire,mean_coil_diameter_mm=diameter,active_turns=turns,
            free_length_mm=free,stiffness_N_per_mm=axial_k,
            installed_length_range_mm=[installed_min,installed_max],
            approximate_solid_height_mm=(turns+2)*wire,resting_force_N=axial_rest_force,
            maximum_coast_return_force_N=coast_force),
        cap_return_candidate=dict(wire_mm=torsion_wire,mean_coil_diameter_mm=torsion_diameter,
            active_turns=torsion_turns,preload_degrees=22,
            rate_Nmm_per_rad=torsion_k,resting_torque_Nmm=torsion_k*torsion_preload,
            full_stroke_torque_Nmm=torsion_k*(torsion_preload+cap_angle),
            coil_stack_height_mm=torsion_turns*torsion_wire),
        comparisons=dict(ideal_face_ramp_return_torque_Nmm=coast_torque,
            ideal_rest_entry_cam_torque_Nmm=entry_torque,
            detent_peak_to_return_torque_ratio=leaf_torque/coast_torque,
            cap_restoring_to_entry_torque_ratio=torsion_k*torsion_preload/entry_torque,
            ideal_RNA_force_to_overcome_detent_N=leaf_torque/30.24),
        boundary='Starting dimensions and force-order checks only. Spring legs/anchors, real grades, friction, printed leaf behavior, wear and dynamic return require design review and physical measurement. No strength, fatigue, acoustic, retention or reliable-feed qualification.')
    result['return_load_audit'] = return_loads(axial_k, free, torsion_k, torsion_preload)
    result['trip_leaf_audit'] = trip_leaf()
    result['coupled_partial_release'] = dict(
        status='FAIL',minimum_upper_return_torque_Nmm=torsion_k*torsion_preload,
        proposed_detent_peak_holding_torque_Nmm=leaf_torque,
        upper_to_detent_peak_torque_ratio=torsion_k*torsion_preload/leaf_torque,
        reason='An engaged B imposes equal upper/drum angular displacement. After A entry clearance is recovered, either the drum rolls back or the upper cannot return. Changing spring strength alone cannot satisfy return with zero drum motion.')
    result['functional_mechanism_established'] = False
    result['status'] = 'REVIEW'
    return result


def return_loads(axial_k, axial_free, torsion_k, preload):
    """Bound the entry ramp with sliding friction, including the latch reset.

    This is a local wedge approximation, not the conjugate-cam contact solve.
    A frictionless necessary-condition failure already rules out a force PASS.
    No friction coefficient here is a measured material property.
    """
    r, entry, lift = 22.0, math.radians(3), 2.0
    slope = lift/(r*entry)
    rows = []
    for mu in (0.0, .1, .2, .3):
        peak = 0.0
        minimum_margin = float('inf')
        for j in range(301):
            angle = entry*j/300
            pawl_lift = lift*(1-angle/entry)
            force = axial_k*(axial_free-(4.4-pawl_lift))
            torque = force*r*(slope+mu)/(1-mu*slope)
            available = torsion_k*(preload+angle)
            peak = max(peak, torque)
            minimum_margin = min(minimum_margin, available-torque)
        rows.append(dict(assumed_sliding_friction=mu,
            peak_entry_cam_torque_Nmm=peak,
            minimum_available_minus_entry_load_Nmm=minimum_margin,
            entry_alone_has_positive_margin=minimum_margin>0))
    # Latch is 7 x .8 x .4 mm, deflected radially by .95 mm.
    latch_k = 3*1700*(.4*.8**3/12)/7**3
    latch_force = latch_k*.95
    return dict(status='FAIL',
        reason='The current return spring fails the frictionless entry-cam necessary condition; latch, bearing and fork reset add load.',
        cam_rise_mm=lift,cam_radius_mm=r,cam_angle_degrees=3,
        assumed_friction_cases=rows,latch_stiffness_N_per_mm=latch_k,
        latch_release_force_without_friction_N=latch_force,
        latch_peak_reset_torque_without_friction_Nmm=latch_force*.95/math.radians(4),
        upper_restoring_torque_at_home_Nmm=torsion_k*preload,
        bearing_friction_and_gate_load_included=False,
        scope='Analytical necessary conditions; no measured spring, friction, fatigue or dynamic qualification.')


def trip_arc_length(compression, free_tip_delta_z, n=2000):
    """Length of the CAD trip centreline, independent of rectangular laps.

    CAD uses y=10*t+(1-t)^2*compression and
    z=26.8+(1-t)^2*(TripLeafLift-1.4). The root is t=1.
    """
    def speed(t):
        dy=10-2*(1-t)*compression
        dz=-2*(1-t)*free_tip_delta_z
        return math.hypot(dy,dz)
    return sum((speed(j/n)+4*speed((j+.5)/n)+speed((j+1)/n))/(6*n)
               for j in range(n))


def trip_leaf():
    E, length, width, thickness=1700.,10.,2.2,.4
    I=width*thickness**3/12
    rest=trip_arc_length(0,-1.4)
    poses=[]
    # Compression varies with carrier angle; bound the advertised .58 mm.
    for compression in (0,.29,.58):
        for lift in (0,1.8,2.6):
            arc=trip_arc_length(compression,lift-1.4)
            strain=(arc-rest)/rest
            poses.append(dict(compression_mm=compression,tip_lift_mm=lift,
                centreline_length_mm=arc,strain_relative_to_rest=strain,
                linear_axial_force_if_length_error_is_elastic_N=E*width*thickness*strain))
    return dict(status='UNRESOLVED',
        initial_CAD_centreline_length_mm=rest,
        Euler_fixed_free_buckling_load_N=math.pi**2*E*I/(4*length**2),
        Euler_pinned_pinned_buckling_load_N=math.pi**2*E*I/length**2,
        length_sensitivity=poses,
        actual_boundary_conditions_known=False,
        snap_direction_selected_by_geometry=False,
        potential_energy_landscape_solved=False,
        reason='The prescribed chords change centreline length. Buckling load alone does not establish the two stable states, trip threshold, available work or reset path.')


if __name__=='__main__': print(json.dumps(estimates(),indent=2))
