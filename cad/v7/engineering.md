# V7 mechanical audit

The candidate remains **INCOMPLETE_CONTINUATION** pending a completed integrated run. `mechanical_v7.py` separates actual-solid
contact observations, analytical necessary conditions, prescribed native poses
and missing physical evidence. It is a rejection audit, not an elasticity or
dynamics solver. No functional mechanism is claimed.

## Force assumptions and current failure

Units are N, mm and N·mm. The illustrative printed-leaf modulus is 1700 N/mm²;
steel moduli are E=200000 and G=79000 N/mm². None is measured grade/process data.
Spring envelopes are reservations, not supplier-qualified components.

| Item | Proposed dimensions / calculated result |
| --- | --- |
| Upper return spring | 0.6 mm wire, 12.1 mm mean coil diameter, 3 active turns, 22° preload |
| Upper return torque | 4.284 N·mm at home; 7.372 N·mm at full manual stroke |
| A bias spring | 0.15 mm wire, 2.5 mm mean diameter, 8 active turns, 6.5 mm free length |
| A installed length | 4.4 mm engaged; 2.4 mm lifted; approximate solid height 1.5 mm |
| Entry cam | 2 mm rise over 3° at 22 mm radius |
| Frictionless entry load | 6.263 N·mm peak; about 1.98 N·mm more than return torque at home |
| Entry load, assumed μ=0.1 / 0.2 / 0.3 | 8.016 / 10.701 / 15.331 N·mm peak |
| Latch release leaf | 7 x 0.8 x 0.4 mm; estimated radial stiffness 0.254 N/mm |
| Latch reset, before friction | 0.241 N at 0.95 mm deflection; peak ramp equivalent about 3.28 N·mm over 4° |
| Dedicated detent leaf | 12 x 1.3 x 1.0 mm; estimated stiffness 0.540 N/mm |
| Detent | Approximate peak resisting torque 3.066 N·mm; peak fibre strain 1.21% |

The frictionless entry load already rejects the current spring budget. Bearing,
latch and a future loaded gate add load. Selecting a stronger spring before
resolving the latch and partial-stroke constraint could increase backdrive and
contact loads without making the mechanism work.

## Trip, latch and reset

The trip leaf has ten chords with prescribed height and axial compression.
Its centreline is:

`y(t) = 10t + (1-t)^2 compression`

`z(t) = 26.8 + (1-t)^2 (TripLeafLift - 1.4)`

The audit integrates its actual centreline length through both cycles. The
animated length changes by several percent. Euler buckling loads for idealized
boundary conditions do not establish stable branches, a snap threshold,
available lift work or a reset path. A contact-driven, energy-consistent trip
must replace this prescription before the mechanism can be accepted.

The fork/lip bearing and reset follower are tested as solids. Correcting their
interference establishes a possible bearing arrangement; it does not supply a
force that deflects the latch at home. The report retains actual trip-foot/post,
follower/roof and latch contact gaps and overlaps.

## Continuous pulling, partial strokes and reversal

In the native cycle, RNA stops while the upper returns. There is no solid gate
imposing that pause on continuous hand input, and no qualified reset speed.
An animation clock cannot establish the sequence.

During an untripped partial manual stroke, B remains engaged. Recovering A's
3° entry clearance brings B to its drive face. The audit attempts another
0.2° of upper return with the actual drum held fixed and records the blocking
volume. Either B must lift, the drum must roll back, or the upper must remain
displaced. This kinematic conflict is independent of spring selection. Under
the illustrative assumptions, minimum upper return torque also exceeds the
detent's peak holding torque.

Home reverse native poses retain a stationary upper and a coasting B. They do
not establish a transition from every partial or latched state. `InputKind` is
a CAD study selector, not a physical reverse actuator.

## Geometry and assembly changes

- A's guide is centred at radius 14.7 mm, between A's 12.3 mm outer tooth
  radius and B's 17 mm inner tooth radius. The pin starts at z=24.5 mm above
  B's base plate. A high bridge clears the teeth; the bearing retains 3.8 mm height.
- Ellipsoids use exact rational patches separated at existing knots; round
  route bounds use analytic cylinders and tori. This avoids the original
  invalid curves on surfaces and incorrect Boolean intersections. Extended
  BOP checks cover the five structural solids.
- Spindle and screw passages are cut after upper-carrier spokes are fused.
- The fork bore is cut after its arm is fused. Its arm underside meets the
  raised-tab bearing plane instead of passing through the lip.
- The dedicated detent is 1 mm high below the pickup track and inserts radially
  after the cover. Its root has a finite seat, washer and separate screw.
- The RNA's 13.2° route keeps 248.814 mm length and 149.288 mm travel. A 3.4 mm
  groove bounds rail and clasp. A separate 2.28 mm-radius tube centred 2.23 mm
  along rotated local -Y continuously bounds the free-ended bases. The
  protected-cavity and finite far-flank wall-patch checks use actual solids.

The 110 nominal pitches retain two 22-pitch end reserves, preserving the original
phase at the front mesh. RNA travel remains 66 pitches. Continuous interval certificates use saved rack, base and clasp
solids against fixed housing, protein/drum bounds and the upper pose envelope.
The lid screw columns are reduced from 3.4 to 3.1 mm radius, retaining their
full 3.1 mm bearing seats while clearing the rack.

These are CAD design choices. The machine-readable report records which
clearance, wall, fastening and sampled insertion checks pass. Printed fits,
stiffness, screw purchase and reliable assembly remain physical qualification
work. No old-version report is substituted.

The upper shell still reports a face self-intersection in the extended BOP
check. This is a CAD defect separate from the mechanical blockers and physical
qualification. Passing basic solid validity does not erase that failure.
