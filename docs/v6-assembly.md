# V6 fastening and compact RNA review

The current V6 removes both outer RNA holders. Only the short capture channel
at the drive peak remains. A nominal 226.195 mm strip crosses the curved flank
at a 38-degree inclination and returns through the open underside groove. The
drive span is 18 mm, the shoulder radii are 33 mm, and the lower bends are 10 mm.
The side-route adjustment retains the fastening and drive geometry. The route
is a prescribed flexible pose; actual sag, friction and stretch need testing.

[Housing screw section](../cad/v6/fasteners.png) ·
[Spindle section](../cad/v6/spindle.png) · [Side route](../cad/v6/side.png) · [Current checks](../cad/v6/checks.json)

## Defects found in the preceding V6

The preceding saved model had valid individual solids and passed its motion
and clearance checks, but those checks did not establish a fastenable assembly.
An actual-solid audit of model SHA-256
`e55ef6432b4b189d9f2c8471f7c8e4f0e14805a78ef01f35ceb1fa271faa1430`
found the following:

| Audit | Measured result | Correction |
| --- | --- | --- |
| Intended housing screw shafts through lid | 12.811, 12.811 and 8.489 mm³ of obstruction | One shared screw pattern through the entire stack. |
| Fixed axle attachment to body | No overlap; 0.150 mm radial gap | Flared spindle root joined into the lower-body floor. |
| Retainer head against fixed axle | 0.550 mm gap | Fixed spindle shoulder reaches the washer underside. |
| Lid against keeper mounting pads | 0.200 mm gap | Positive bearing planes at the mounting pads. |
| Vertical assembly over complete rotor | Lid/cover openings could not pass its larger wheels | Two keyed rotor parts and a larger concealed cover opening. |

The new assembly audit supplements the previous motion checks. It does not
reinterpret the old report as proof of assembly or physical operation.

The lid now uses a 2.2 mm analytic ellipse-edged plate with integral screw
columns. Local box sections and annular material witnesses must preserve the
expected solid volume. This avoids relying on the basic validity flag of a
thin spline skin when assessing the fastening regions.

## Current screw stack

Three proposed **M2 × 12 countersunk screws** share axes at X/Y
(-32, -14), (32, -14) and (-23, 26) mm. They pass through the cover, lid
columns and keeper pads into blind lower-body pilots. Shafts and heads are
modeled; hex sockets and conical seats are present.

| Interface | Nominal Z plane |
| --- | --- |
| Lower-body seat / keeper pad | 13.50 mm |
| Keeper pad / lid column | 14.60 mm |
| Lid column / cover boss | 20.25 mm |
| Recessed screw-head top | 21.30 mm |
| Cover top | 21.70 mm |

Nominal pilots are 1.70 mm diameter, with 4.2 mm thread engagement and 0.4 mm
bottom clearance. Passages are 2.30 mm diameter. The report checks real shaft
clearance, annular material around the pilots and cover seats, finite bearing
areas on both sides of each interface, conical head seating and vertical driver
access with the upper subunit removed.

Threads are represented by major-diameter envelopes. Only their bounded pilot
zones may overlap their hosts. A whole screw/host pair is never excluded from
collision checking. Screw dimensions are proposed envelopes, not a selected
supplier standard or a qualified printed-thread specification.

The cap uses a proposed **M2 × 4 screw and separate 8 mm washer**. The washer
seats on the fixed spindle at Z 33.55 mm; its head seats on the washer. The
moving cap retains 0.15 mm nominal axial endplay. The click-leaf root is
integral with the cover, eliminating its unsupported fastening hole.

## Physical parts and insertion sequence

The lower shell and its spindle are one physical part, shown as separate
features for inspection. Likewise, the cover, click-leaf root and prescribed
leaf chords represent one flexible printed part. Their connections must have
positive volume and fuse to one connected solid.

The rotor has two connected physical parts. The lower part comprises the bead
drum, hollow spindle with D key, thrust flange and travel pin. The upper part
comprises the RNA gear, input sleeve, click wheel and face ratchet. Their D
profiles fit without rigid overlap and block attempted relative rotation in
both directions. Nominal radial key clearance is 0.12 mm. Native animation
prescribes their shared rotation; actual backlash and axial float need fit tests.

1. Insert the lower rotor over the fixed spindle, with the travel pin aligned
   to the home end of its slot. Load the connected protein strand.
2. Lower the bead keeper onto its three seats.
3. Lower the lid over the rotor's 6 mm radius thrust flange through its
   6.2 mm radius opening.
4. Lower the keyed upper rotor onto that flange. The D key fixes its phase.
5. Place RNA into the exposed central channel and lower the cover. Its 15 mm
   radius opening passes the 14.4 mm click wheel. Install the three housing
   screws while the upper subunit is off.
6. Install the upper subunit with its input pawl lifted, then its washer and
   retaining screw. The two input springs remain engineering space claims.

The report checks ten vertical insertion poses for each rigid stage, including
the actual cover and its integral click leaf. Verified conservative drum/gear
envelopes bound the complex profiles; the D-key fit uses its actual solids.
These are sampled geometric
witnesses. They do not simulate hand assembly, flexible strand loading, spring
installation, friction or manufacturing tolerances.

## Qualification still required

Print pilot and D-key fit samples first. Confirm fastener selection, seating,
preload, stripping resistance, leaf material, shoulder friction, key backlash
and retention under load. Test RNA bending and pitch stability, clasp retention,
bead feeding and the full two-handed interaction. V6 remains a mechanical CAD
prototype, not a released print package.
