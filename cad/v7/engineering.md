# V7 mechanical audit

The candidate's mechanical status remains **REVIEW**. The current checkpoint is
**INCOMPLETE_CONTINUATION**, saved at the user's stop during the integrated audit;
the last completed full audit is checkpoint `5c4b2c0`. `mechanical_v7.py` separates actual-solid
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

Checkpoint `5c4b2c0` reported an upper-shell self-intersection in the extended
BOP check. The follow-up replaces only the organic upper skin with ruled
elliptical latitude sections. Six-degree spans and 0.001-relative polar caps
give a conservative surface-deviation bound below 0.067 mm. Four quadrant
edges keep each section explicitly bounded. This approximation does not alter
the drive, bearing, screw, RNA or protein profiles.
The bound applies to the ellipsoid construction before the intentional access cuts.

The rectangular anchor-access pocket created two intersecting face pairs even
with a valid skin and a valid cutter. A wider sector contains that entire
pocket and passes the extended check. The other downward access cuts clear the
carrier's projections, rather than merely subtracting its final seated shape.
The screw pads are added after those access cuts, preserving their z=33 mm
bearing planes and conical seats. Both screw axes move to y=-6 mm to clear A.

The housing also clears the keeper's tangent cheek behind the visible outlet.
Only the rear lid column returns to a 3.4 mm radius: it is away from the rack,
and the existing local-section test is retained without lowering its threshold.

## Completed CAD audit

The checkpoint `5c4b2c0` integrated FreeCAD 1.1.4 run completed with **REVIEW**. All 14 continuous
RNA/base/clasp travel cases passed on the two nominal layouts. The native
position/orientation and ratio checks passed, as did the positive track-contact,
latch-bearing and travel-stop witnesses. These results do not establish release
or reset under load.

That checkpoint retained 32 interfering feature pairs, including:

| Actual-solid observation | Result |
| --- | --- |
| Lower housing / bead keeper | 10.7818 mm³ overlap; keeper insertion fails |
| Manual pawl / upper carrier | 3.1788 mm³ overlap |
| Upper shell / manual pawl at home | 0.4866 mm³ overlap |
| Shell / carrier during insertion at +1 mm | 18.2055 mm³ overlap |
| Partial return, fixed drum, additional 0.2° | About 0.1603 mm³ pickup/track blocking overlap |
| Trip foot / post in the sampled cycle | Minimum gap 0.025 mm; no sampled closed driving contact |

The trip/latch leaves also intersected each other and the reset roof. The five
failed checkpoint assembly checks were the third housing column's section-volume screen,
keeper insertion, right shell screw clearance outside its allowed thread zone,
right shell bearing seat, and shell insertion after the reset bridge. The
column screen measures 76.10 mm³ against its existing 90 mm³ threshold; this
screen is not a strength calculation. The separate detent's radial insertion,
root bearing, washer and screw checks passed.

The follow-up's current results are in [checks.json](checks.json). The saved
coupling still uses the 3° manual entry and prescribed trip/reset; isolated
release experiments have not established a replacement mechanism.

No contact-driven trip, elastic equilibrium, transient reset, arbitrary reverse
transition or physical prototype qualification has been completed. The current
architecture therefore remains unfinished despite the completed CAD audit.

## Unpromoted release investigation

An auxiliary rotor cam was studied at radius 20.8 mm with a 0.45 mm spherical
follower. Its nominal lift is `1.5 sin²(pi * phase / pocket_pitch)` mm. A
6° manual entry would produce about 1.48 mm lift, enough to cross a proposed
1.2 mm hold-open height before A starts driving. The conjugate surface was
constructed below the envelope of the follower spheres. This is a proposed
way to distinguish manual entry from RNA pickup; it is not in the saved CAD.

A constant-length trip crank was also studied: 4 mm arm, 8 mm spring-anchor
offset and 1.2 mm fork stroke. With crank angle q, fork height would be
`0.6 + 4 sin(q)` mm and spring length `sqrt(80 - 64 cos(q))` mm. The endpoints
are q=±asin(0.15). A provisional 0.65 mm wire / 3 mm mean diameter / three-active-
turn / 7 mm free compression spring gives a first-order energy barrier of
about 5.76 N·mm. These dimensions are calculations, not selected hardware.
An isolated crank/fork trial cleared 49 sampled positions, but integration
did not clear the fixed trip cam: at the proposed 11.8° RNA stroke peak, the
trial recorded about 1.239 mm³ fork/cam and 1.008 mm³ carrier/cam overlap.

Neither study solves the complete contact sequence. A physical continuous-pull
gate, its home/engagement interlock, spring and pivot seating/retention, friction
bounds, partial endpoint states and complete insertion paths still need design
and validation. Do not promote these investigations or change the saved 3°
entry based on their isolated results. Generated experiments remain under
ignored `build/v7/`; the saved model remains the explicitly unfinished candidate.
