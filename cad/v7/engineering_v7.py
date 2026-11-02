"""Illustrative first-order force budget; assumptions, not qualification.

N, mm, radians. Printed material properties, friction and real spring
characteristics must be measured. This calculation is deliberately separate
from the focused CAD PASS and cannot establish physical operation.
"""
import json
import math


def estimates():
    leaf_E=1700.0  # Assumed effective elastic modulus, N/mm², not grade data.
    leaf_length,leaf_thickness,leaf_height=12.0,1.0,2.0
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
    installed_min,installed_max=2.7,4.7
    axial_rest_force=axial_k*(free-installed_min)
    coast_lift=.89;coast_force=axial_k*(free-(installed_max-coast_lift))
    step=2*math.pi/28
    coast_torque=coast_force*1.25/step
    entry_torque=axial_rest_force*2/math.radians(3)
    torsion_wire,torsion_diameter,torsion_turns=.6,12.1,3
    torsion_k=steel_E*torsion_wire**4/(64*torsion_diameter*torsion_turns)
    torsion_preload=math.radians(22)
    cap_angle=math.radians(3+360/28)
    return dict(status='INCOMPLETE_V7_FORCE_BUDGET',units='N, mm, N·mm, radians',
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


if __name__=='__main__': print(json.dumps(estimates(),indent=2))
