"""First-order stock spring estimates; supplier dimensions, assumed modulus.

Counts listed as total turns are used as active turns for this estimate.
Force, preload installation, printed holding torque and friction need tests.
"""
import json
import math


def estimates():
    E=193000.0
    wire,mean=.6,5.9
    k_right=E*wire**4/(64*mean*7.25)
    k_left=E*wire**4/(64*mean*7)
    centre=(-16.,16.)
    peg=(-11.5/math.sqrt(2),11.5/math.sqrt(2))
    offset=2.95-.6-.3
    def cap_phi(a):
        qx=peg[0]*math.cos(a)+peg[1]*math.sin(a)-centre[0]
        qy=-peg[0]*math.sin(a)+peg[1]*math.cos(a)-centre[1]
        return math.atan2(qy,qx)-math.asin(offset/math.hypot(qx,qy))
    home=cap_phi(0)
    cap_rows=[]
    for j in range(21):
        a=math.radians((6+360/28)*j/20);eps=1e-6
        strain=math.radians(23)+cap_phi(a)-home
        gain=(cap_phi(a+eps)-cap_phi(a-eps))/(2*eps)
        cap_rows.append(dict(cap_degrees=math.degrees(a),spring_strain_degrees=math.degrees(strain),
            d_spring_angle_per_cap_angle=gain,return_torque_Nmm=k_right*strain*gain))
    rest_angle=math.atan2(1.25,16.2)-math.asin(3.75/math.hypot(16.2,1.25))
    pawl_rows=[]
    for lift in (0,.5,1,1.5,2):
        h=3.25-lift;distance=math.hypot(16.2,h)
        phi=math.atan2(h,16.2)-math.asin(3.75/distance)
        strain=rest_angle+math.radians(15.5)-phi
        derivative=16.2/distance**2+3.75*h/(distance**3*math.sqrt(1-(3.75/distance)**2))
        pawl_rows.append(dict(pawl_lift_mm=lift,spring_strain_degrees=math.degrees(strain),
            downward_force_N=k_left*strain*derivative))
    home_force=pawl_rows[-1]['downward_force_N']
    entry=home_force*2/math.radians(6)
    return dict(status='STOCK_SPRING_ESTIMATES_DETENT_FORCE_UNRESOLVED',units='N, mm, N mm, radians',
        assumptions=dict(elastic_modulus_N_per_mm2=E,total_turns_used_as_active=True,
            friction_included=False,printed_anisotropy_included=False,dynamics_included=False,
            supplier_rates_provided=False),
        cap_return_stock=dict(code='TECH-AR MS/095P TYP2',wire_mm=wire,free_OD_mm=6.5,
            free_ID_mm=5.3,nominal_body_length_mm=5,total_turns=7.25,winding='right',
            rate_Nmm_per_rad=k_right,proposed_preload_degrees=23,trim_fixed_leg_mm=3.5,
            trim_moving_leg_mm=14.5,sampled_force_budget=cap_rows),
        pawl_bias_stock=dict(code='TECH-AR MS/095L TYP1',wire_mm=wire,free_OD_mm=6.5,
            free_ID_mm=5.3,nominal_body_length_mm=5,total_turns=7,winding='left',
            rate_Nmm_per_rad=k_left,proposed_home_preload_degrees=15.5,
            trim_fixed_leg_mm=6,trim_moving_leg_mm=16.7,sampled_force_budget=pawl_rows),
        necessary_conditions=dict(cap_energy_increases_on_feed=all(r['d_spring_angle_per_cap_angle']>0 for r in cap_rows),
            pawl_downward_force_remains_positive=all(r['downward_force_N']>0 for r in pawl_rows),
            return_to_ideal_entry_torque_ratio=cap_rows[0]['return_torque_Nmm']/entry,
            minimum_cap_return_torque_Nmm=min(r['return_torque_Nmm'] for r in cap_rows)),
        detent=dict(geometry='Seven 0.9 mm webs, six 1 mm centre-radius U bends, 2 mm print height',
            force_and_fatigue='UNQUALIFIED: no straight-cantilever force claim for the folded beam'),
        boundary='Supplier nominal sizes and first-order estimates only. Measure actual rates, end angles and leg lengths before trimming. Physical cap return, no rollback, split-tip installation, friction, fatigue and operation remain unqualified.')


if __name__=='__main__':
    print(json.dumps(estimates(),indent=2))
