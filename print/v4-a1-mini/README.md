# V4 Print - A1 mini prototype package

Prepared for **Bambu Lab A1 mini, standard 0.4 mm nozzle, 180 x 180 x 180 mm bed**, using PETG, PLA and TPU. Dimensions are millimetres. No physical print or assembly has been tested. Calibration parts are supplied for the uncertain fits.

**Saved at the user's request before export qualification finished.** See [handoff status](handoff.json). Cuff STL mesh-edge checks need review. Open the geometry **3MFs in `plates/`** in Bambu Studio, load the supplied profiles, inspect/repair meshes and slice before printing. Any files in `sliced/` are provisional offline results; check [slicer status](slicer-checks.json). `plates/` contains plain geometry 3MFs, `stl/` individually oriented parts, and `profiles/` the flattened slicer settings. The [manifest](manifest.json) maps parts to plates, materials, quantities and orientations. The [CAD](../../cad/v4-print/RibosomeV4Print.FCStd) is the assembly reference.

## Print order

1. **00-TPU-bore-tests:** three bead shapes at each bore of 0.4, 0.5, 0.6 and 0.8 mm, followed by three axle plugs. Groups are ordered by increasing bore; shape order follows the manifest. Keep parts identified when removing them. Ordinary TPU uses an **external spool, not AMS lite**. The profile assumes approximately 95A TPU, 230 C nozzle, 30 C textured plate, 0.12 mm layers and slow 20 mm/s walls. Check the spool's temperature range, dry it as its maker specifies, and use an appropriate release layer for TPU on your plate.
2. **01-PETG-fits-and-feeder-test:** fit gauge, three leaves and two short feeder-fixture halves. Circular holes left to right: 1.05, 1.10, 1.20, 2.20, 2.30 and 2.40 mm. Hex pockets: 4.2, 4.4 and 4.6 mm across flats. Main CAD uses 2.3 mm axle clearance, 4.4 mm nut pockets and a 1.05 mm stop seat. Select leaf force on the bench.
3. **13-PLA-mechanism** and **14-PLA-chain-pitch-jig:** test three beads with the actual feeder halves, drive shaft and axle in the short fixture first. Two extra M2 x 14 screws and nuts clamp it. Turn the exposed pinion by hand. Check straightened-chain feeding both ways, stop clearance and bead fixation. Do not force a jam.
4. Once those tests work, print **10-PETG-cuff-front**, **11-PETG-cuff-rear**, **12-PETG-RNA**, and **15-TPU-production-beads**. Production has the **0.6 mm candidate bore**, 26 beads plus three spares, and a 4.35 mm candidate plug. If calibration selects another bore or plug, substitute and duplicate the matching test STL; do not scale the whole bead.

A 0.4 mm nozzle is not a 0.4 mm drill. The 0.4 mm test bore may close or require clearing. Begin with the 0.6 mm candidate and actual deburred wire; select the smallest bore that threads without tearing or force. If necessary clear a test hole carefully with a suitable pin or pin vise, holding the bead securely with a tool.

## Materials and supports

| Material | Parts | Candidate setup |
| --- | --- | --- |
| PETG | Cuff halves, RNA, leaf, test fixture, fit gauge | Installed Generic PETG A1 mini temperatures; 0.12 mm layers, four walls, 30% infill. Check temperatures against your spool. |
| PLA | Drive/pinion, two feeder halves, cam, slider, lever/post, upper lobe, retainer cap, jig | Installed Generic PLA A1 mini temperatures; 0.12 mm layers, four walls, 95% infill. |
| TPU | Beads and axle plug | Assumed 95A; 230/30 C, 0.12 mm layers, three walls, 95% infill, maximum flow 1.2 mm3/s. External spool. |

STLs have their lowest point at Z=0. Cuff halves rest on the mating seam; RNA rests on the concealed gear face with bases upwards; feeder halves rest on their fork faces with hubs upwards; beads have a flat sole and vertical bore. The leaf's broad face lies flat so its beam bends in the layer plane.

PETG and PLA plates use removable build-plate tree supports where needed. Remove supports from open mating faces and clean the channel, cam groove, pinion, axle bores and swivel pocket. Inspect the enclosed rear bearing and slider pin particularly carefully. No support belongs inside a bead bore. RNA prints in one material colour; the CAD base colours are illustrative. Tune brims and support contacts after the small trial. Offline slicing does not prove clean support removal.

## Hardware

| Item | Quantity | Specification |
| --- | --- | --- |
| Annealed solid copper wire | About 180 mm before trimming | **0.25 mm candidate**; compare 0.20/0.30 mm for hand shaping if useful. No automatic curling. |
| Micro crimp tubes | 52 plus spares | No. 1 candidate: nominal 0.8 ID x 1.3 OD x 1.2 long. Correct micro-crimping pliers. Finished folded envelope at most 1.5 OD x 1.2 long. Test grip on solid copper. |
| Steel axle | 1 | Diameter 2 x 21.1, square and deburred. |
| Steel stop pin | 1 | Diameter 1 x 5.4, deburred. |
| M2 socket cap screws | 6 | Four x 10 long for case; one x 6 for leaf; one x 8 for swivel. Nominal head 3.8 OD x 2 high. |
| M2 nuts | 6 | Nominal 4 across flats x 1.6 thick. |
| Extra fixture hardware | 2 screws + 2 nuts | M2 x 14, only for short feeder fixture. |

Metal CAD items are envelopes, not printed parts. Use the supplied 11 mm printed swivel cap; an ordinary small M2 washer would fall through the square-key opening. Physically test the TPU axle plug's retention.

## Assemble and test the chain

Each bead end has a 2 mm recess for a crimp stop. The central web keeps the selected small bore. Stop centres are about 1.6 mm either side of a bead centre, with bead centres at 6 mm pitch. Recess the crimps fully and keep the shared drive shoulders clear.

Test **one bead** first. Crimp a stop on actual copper with the correct pliers and check for slipping while pulling and bending by hand. Check that the TPU bead can stretch over a rounded folded stop without splitting or permanent damage. The proposed method forms each stop pair in the open, then stretches the bead over its near stop into position. If that fails, try the larger-bore sample and repeat grip and feeding tests before making 26 beads. This assembly method has not been physically demonstrated.

The jig registers **bead centres**, not stop grip. Work from one wire end. The CAD family sequence repeats `(0,1,2,1,0,2,2)` for 26 beads; counts are in the manifest. Trim and tuck wire tips inside the end-bead recesses. Neither tip nor a loose stop should protrude. Keep the emerged chain straight for initial reverse tests. Copper pose retention and repeated-bend life are unmeasured.

## Assemble the bracelet

1. Remove all supports and test hardware fit by hand. Do not pull warped halves together using screws. Fit four case nuts in the rear pockets and the leaf nut in its pocket.
2. Clamp the selected PETG leaf with M2 x 6. Fit the metal travel stop into its seat, with its front end at nominal CAD Y=-3.2, and engage the RNA's closed stop groove. At home the RNA and cuff openings align. Check that the RNA slides while remaining captured by the ledges.
3. Install InputDrive on the 2 mm axle. Slide on the two feeder halves, matching square holes and tooth phase; hub faces meet at the wire plane. Fit the cam with its groove towards the slider. Use the home CAD position for pocket/chain phase; do not offset one fork by a tooth.
4. Load the chain into the open channel, with its leading bead at the shallow outlet as shown in CAD and the feeder bead seated in a pocket. Preserve the four-bead hidden tail at full travel.
5. Seat the slider in its guide, lower pin in the wave groove and upper pin in the lever slot. Insert the M2 nut into the lever key's side pocket. Seat the post in its fixed bearing and the upper lobe on the square key. Fit the printed retainer cap and M2 x 8 screw without binding the swivel.
6. Close the rear half with four M2 x 10 screws, checking that the RNA, chain, slider and axle stay seated. Fit and check the TPU axle plug. Keep all hardware accessible for reopening.
7. Turn through one codon first, then progressively through travel. A 7.5-degree dial step passes three bases and feeds one bead; the lobe cycles once per bead. Straighten the emerged chain before reversing. Return home before opening the cuff for wearing.

These are proposed assembly steps, not a recorded successful build. Record bore, spool hardness, fit corrections, stop grip, feed failures, leaf force and copper damage before calling the prototype functional. Cuff opening strain, comfort and fatigue remain untested; inspect and test on the bench first.

## Evidence and references

[CAD checks](../../cad/v4-print/checks.json) and [offline slicer checks](slicer-checks.json) cover different boundaries. Solids and toolpaths do not prove printing, assembly, feeding or strength. V3's full baseline suite remains incomplete.

Printer/nozzle/material support: [official A1 mini guide](https://cdn1.bambulab.com/documentation/quick-start-f507128172bdf/Quick%20start%20guide%20-%20A1%20mini-EN.pdf). TPU routing: [official Combo guide](https://cdn1.bambulab.com/documentation/Quick%20Start%20Guide%20for%20A1%20mini%20Combo.pdf). Crimp dimensions: [Beadalon catalogue](https://www.beadalon.com/uploads/findings%2036.pdf). Its [wire/crimp chart](https://www.beadalon.com/content/match_up_proper_wire_crimp_bead_or_tube_diameters.asp) concerns jewellery wire, not proven grip on this solid copper. Slicing: [official Bambu Studio CLI](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage).
