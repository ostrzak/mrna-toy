# Printed joints and stock-spring boundary

The user authorised the printed-fastener, central-retainer and integrated-seat
changes on 2026-11-06 and specified **standard stock springs only** from
Allegro or AliExpress. A made-to-order quote is outside the selected approach.

## Printed hardware

| Part | Installed qty | Geometry |
| --- | ---: | --- |
| Housing screw | 3 | 4 mm major diameter, 1.2 mm pitch, 6 mm recessed slotted head |
| Keyed nut | 3 | 6.4 mm round bound with two flats 5.2 mm apart; 3.6 mm high; underside insertion |
| Closed spindle cap | 1 | 8.2 mm OD, coarse 6 mm / 1.5 mm pitch female thread; integral retaining flange |
| Spindle | Integral | Smooth 6 mm journal, threaded extension above the journal, flared root retained |
| Pawl spring supports | Integral | Split retaining shaft and fixed-leg socket in the upper; 0.25 mm contact base with a rounded 0.5 mm radius boss on the pawl |

Nominal thread allowance is 0.20 mm radially and 0.10 mm axially. It is a
coupon starting point, not a measured A1 mini fit. The thread flanks use
24 ruled sections per turn, with less than 0.028 mm radial faceting at the
largest tool radius. Female seams are staggered by half a section with a
matching pitch translation; their helix phase remains aligned. This avoids
an OCCT coincident-face failure that could otherwise falsely report zero
overlap during an attempted axial pullout.

The lower keyed nut pockets open through the underside. A nut is stopped
against the post's shoulder at z=12 mm; its screw clamps the keeper, lid and
cover against the lower body. The nut is replaceable without removing a
heat-set insert. Physical holding during screw starting and print tolerances
need a trial. Do not treat the nut as a metal-strength replacement.

The central cap bottoms its closed roof against the fixed spindle tip at
z=36.65 mm. Its retaining flange starts at z=33.65 mm, above the upper's
z=33.4 mm bearing face. The 37.85 mm top keeps the retainer close to the shell;
nominal thread engagement is 3 mm. Tightening must preserve the proposed 0.25 mm gap.
The legacy inspection feature `CapWasher` is the **integral printed flange**;
fuse it with `CapRetainer` when exporting the physical cap.

## Standard stock springs

Both parts are standard Allegro items from seller `arkadiusc`, identified on
2026-11-06. They have nominal 0.6 mm stainless wire, 6.5 mm OD, 5.3 mm ID and
5 mm coil bodies. Supplier rates are not published. The seller permits
trimming/forming the approximately 50 mm straight-leg configuration.

| Role | Qty | Exact selected item | Proposed leg trimming from coil tangency |
| --- | ---: | --- | --- |
| Cap return | 1 | [TECH-AR MS/095P TYP2, right-hand, 7.25 turns](https://allegro.pl/oferta/sprezyna-skretna-d-0-6-dw-5-3-dz-6-5-prawa-typ2-1-szt-18308431897) | 3.5 mm fixed leg; 14.5 mm moving leg |
| Pawl bias | 1 | [TECH-AR MS/095L TYP1, left-hand, 7 turns](https://allegro.pl/oferta/sprezyna-skretna-d-0-6-dw-5-3-dz-6-5-lewa-typ1-1-szt-18308566664) | 6 mm fixed leg; 16.7 mm moving leg |

Each listing displayed 12 PLN before delivery. Check the exact handedness and
TYP number at checkout; these are different parts. Do not substitute the
1.0 mm / 14 mm OD spring considered earlier. The two selected parts are stock
items; no made-to-order pair is required. Measure the received wire, body,
leg angle and usable straight lengths before cutting. Deburr clipped ends.

The cap spring sits in a cover-integral cup near the rear left, with a fixed
split mandrel. Its short fixed leg reacts into a cup socket. The longer leg
slides against a rounded peg on the rocking upper. The peg lies on the
loaded side of the leg: clockwise feed increases spring strain, and the leg
then pushes the upper counterclockwise. The proposed home preload is 23°.
The spring returns the upper; it does not rewind protein.

The pawl spring lies horizontally inside the upper. Its fixed leg reacts into
an upper-integral socket; its longer free leg presses a rounded boss on the
sliding pawl. A roughly 16 mm lever arm converts the torsion spring into the
small downward force previously proposed for the compression spring. The
vertical guide pin and V6 cam/feed/return law remain. Proposed home preload
is 15.5°. The printed boss has a rounded contact rather than a broad flat
seat, so the tilted wire can press it without passing through the pawl.

Both printed spring shafts have split retaining tips. Nominal free coil ID
5.3 mm versus a 5.5 mm head implies approximately 0.1 mm inward movement per
side during insertion. This is an installation candidate, not a qualified
snap fit. Verify fit and elastic recovery on a coupon before loading the
complete upper. Spring preload installation and tool access need a physical
assembly trial.

Coil bodies are displayed as conservative annular envelopes: 6.54 mm OD,
5.10 mm ID and the nominal body length plus prescribed winding growth. Their
native helix centrelines are hidden construction references. Explicit fixed
and moving wire legs show the contacts and reaction paths. The envelopes
cover the nominal wire coil and estimated loaded contraction; they are not
wire-accurate spring solids or stress simulation. They must not be printed.
This representation avoids unreliable coincident helical-end Booleans while
keeping occupied-space checks conservative.

The fixed cup's outer wall ends at z=31.3 mm. A 0.3 mm trim clears the upper
at the end of its stroke; the floor, fixed-leg socket and split retaining
mandrel are unchanged. The follow-up audit proves that only this material
was removed, checks the retained root, and repeats the affected clearance
sweep and spring audit against the complete prior validation record.

Run `python cad/v6-updated-print/engineering_v6_updated_print.py` for the
first-order estimates. They assume a 193 GPa modulus and treat the seller's
total turn counts as active turns. Estimated home return torque is around
3.8 N mm, and pawl bias is around 0.09–0.16 N. The ideal return/entry-cam torque
ratio remains only around 1.24 before friction. The folded detent's holding
force and fatigue are unqualified; spring/detent balance and no rollback
must be tested together. Neither supplier dimensions nor a CAD clearance
check establishes dependable operation.

The minimum purchased-hardware target is the two listed stock springs plus
copper wire. There are no metal screws, brass inserts, bearings, washers or
additional shafts in this manufacturing candidate. Printed thread and snap
fits, spring rates, preload, feeding, wire retention and durability still
need physical tests.
