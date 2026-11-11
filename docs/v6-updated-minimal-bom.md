# V6 updated: minimal purchased-parts proposal

Implementation: the separate [V6 updated print candidate](../cad/v6-updated-print/README.md)
now contains the printed fasteners and mounts for two selected stock Allegro
springs. Use its [current BOM and fit-test guide](../print/v6-updated-a1-mini/README.md).
The proposal below records the earlier recommendations for the preserved baseline.

Proposed 2026-11-06, following the user's preference for printed screws and
inserts. This changes the recommended manufacturing direction, not the saved
CAD. The present model still contains M2 fastener envelopes and metal washers.
Preserve V6 updated and make a separate manufacturing derivative if this
proposal is implemented.

The user owns Bambu Lab TPU 90A, PETG Translucent and PLA Matte and uses an
A1 mini with a 0.4 mm nozzle. All three installed `@BBL A1M` filament presets
explicitly include that printer/nozzle combination. No Bambu MCP server is
needed to prepare, slice or save local Studio projects. Studio's
[official CLI](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage)
supports printer/process/filament settings, slicing and project 3MF export.
No print has been sent and no new sliced project was made for this proposal.

## Purchased BOM target

Quantities are installed quantities per toy. **This is a design target, not
an order-ready BOM for the present model.** Neither spring has a selected
supplier part number. Do not order by outside diameter alone.

| Item | Qty | Current engineering starting point | Procurement decision still needed |
| --- | ---: | --- | --- |
| Metal torsion return spring | 1 | Approximately 14.1 mm OD / 12.9 mm ID, 0.6 mm wire, nominal 3 active turns; illustrative rate 0.175 N mm/degree; intended torque about 3.84–7.13 N mm | Match rated torque, usable deflection, winding, free leg angle, leg geometry and axial growth; adapt the cup, mandrel and anchors to a stock part |
| Metal compression pawl spring | 1 | Approximately 2.65 mm OD / 2.35 mm ID, 6.5 mm free length, 0.15 mm wire; illustrative rate 0.040 N/mm; present working length 2.4–4.4 mm | Check actual end coils, solid height, permitted working length and force; adapt printed seats and guide clearance |
| Soft bare copper wire, if not already owned | 1 length | Present CAD represents 0.36 mm diameter; about 0.2 m allows for the 26-bead chain and finishing | Confirm the actual wire diameter, then test bead grip, shaping and repeated reversal; a small 1 m pack provides trial material |

The target requires **zero purchased screws, brass inserts, washers, bearings,
shaft collars or extra metal shafts**. Printed joints and bead retention must
pass small physical trials before treating that target as achieved. Springs
remain metal; the printed serpentine detent remains a separate PETG feature.

The current spring estimates are not measured requirements. In particular,
the ideal return/entry-cam torque ratio is only about 1.23 before friction,
and folded-leaf holding torque is unknown. Select the two springs and detent
together. A stronger return spring alone may increase rollback or wear.

Supplier drawings must include more than coil diameters. Century Spring's
[selection guide](https://www.centuryspring.com/resources/select-torsion-spring)
explains that a torsion spring contracts in diameter and grows axially when
loaded in its preferred direction. Its leg geometry and mandrel clearance
therefore need to be represented in the manufacturing model. The present
radial terminal stubs are schematic, not a catalog end shape.

## Proposed model changes

1. **Three printed housing fasteners and replaceable printed nuts.** Use a
   coarse custom thread with a broad tool recess or finger head, rather than
   trying to print the present M2 envelopes. A roughly 4–5 mm thread is a
   starting study, not a selected standard size. Current front lid columns
   are only 6.2 mm OD and run close to the moving RNA rack. Decide the nut
   pockets, wall sections and screw locations through a clearance/assembly
   check; simply enlarging the existing holes is not sufficient. Replaceable
   nuts let a stripped thread be replaced without reprinting the housing.
2. **A printed flanged spindle cap.** Extend the fixed spindle tip above its
   running journal and use a coarse external thread with a printed closed
   cap. Its flange replaces the central M2 screw and retaining washer. A
   positive stop against the fixed spindle must set the flange height so
   tightening cannot clamp the moving upper. The present approximately
   0.15 mm axial gap needs print-fit calibration. Keep threads off the bearing
   surface; check access inside the upper's existing 8.7 mm recess.
3. **Integral PETG spring seats.** Replace the two 0.15 mm metal shims with
   substantial annular seating surfaces on the carrier and pawl, and adjust
   their spacing to the selected spring. Printing the thin washer envelopes
   directly would not be the proposed solution. Confirm the pawl can still
   move freely and that its spring ends cannot slip past the seats.
4. **Real spring installation geometry.** Adapt both spring mounts to selected
   stock springs, including the torsion legs, preload access, winding and cup
   clearances. Verify pawl return and detent holding with friction before
   committing to the whole housing print.
5. **Manufacturing details for small moving parts.** Add a stronger neck/root
   beneath the present 1 mm cam follower where clearance permits; retain the
   printed 1.5 mm pawl guide pin for the initial trial. Prepare a flat RNA
   layout and printable bead bed contacts/grip features for the actual wire.
   Avoid adding crimps or adhesive to the BOM unless the retention trial
   shows they are needed. Preserve bead shoulders, 6 mm pitch and drive phase.

The folded leaf should first be tested in its unloaded print state, rather
than thickened on the assumption that more material is better. The existing
export worker already uses that unloaded state. Its force and fatigue, and
the thin rotor forks, remain physical manufacturing questions.

## Use the owned filaments

| Filament | Initial assignment |
| --- | --- |
| Bambu PETG Translucent | Functional housing, rotors, cover/leaf, printed fasteners, nuts, seats and spindle cap; fit and fatigue trials first |
| Bambu TPU 90A | RNA and protein beads; test pitch stability and wire retention |
| Bambu PLA Matte | Rigid fit/appearance prototypes or later shell alternatives; retain PETG as the initial flexure material |

These assignments are prototype choices, not qualified strength or life
claims. Prepare separate material plates in Bambu Studio with their exact
presets and inspect the sliced small features, supports and bearing surfaces.
The current closed STL meshes can be printed for trials; mesh validity alone
does not resolve the proposed fasteners or purchased-spring fit.

The owned Skipping Stone shaft and bearings are 3 mm nominal, whereas this
toy uses a 6 mm integral printed spindle. Introducing them would require a
different spindle/retention design and is not needed for this minimum BOM.

Implementation order: select documented stock spring candidates; make the
fastener, spring/leaf, RNA and bead/wire test pieces; update a manufacturing
derivative after those fits are established; then prepare the full Bambu
Studio project. Keep CAD checks, sliced results and physical results distinct.
