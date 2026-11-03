# mRNA toy versions

**[V7 review](v7/README.md)** is an unfinished two-pawl/latch and flank-route
candidate. Its cloud CAD checks and independent mechanical audit retain
explicit failures. Read [the continuation record](../docs/v7-cloud-handoff.md).
It is not a functional PASS; V6 remains the launcher default.

Start with the [project overview](../README.md) for purpose and current status. This page covers viewing and operating the saved CAD.

- **[V6 — captive open/closed RNA](v6/README.md):** current design, with joined external underside return or open tails, direct RNA reversal, bidirectional detent and rest-disengaged cap input. [Open model](v6/RibosomeV6.FCStd), or run its adjacent macro.
- **[V5 — handheld ribosome](v5/README.md):** preserved circular-loop comparison, with direct bead-storage drum, upper rocker and external reverse release. [Open model](v5/RibosomeV5.FCStd).
- **[V4 Print - A1 mini](v4-print/README.md):** preserved cuff manufacturing prototype with TPU beads and calibration parts; physical tests pending. It is not a V5 print package.
- **[V4 — exposed RNA strand](v4/README.md):** preserved cuff comparison, with a covered mechanism, recessed cuff edge and free-ended bases.
- **[V3 — same-direction feed](v3/README.md):** preserved comparison with incomplete full validation. Compact lobed beads leave a shallow cleft between lobe contours, in the same local direction as the moving RNA. A close internal guide holds the beads against the feeder. No protein half-turn around the shaft.
- **[V2 — opposite-direction feed](v2/README.md):** preserved comparison, including its source, model, images and historical checks. The chain makes a half-turn inside the ribosome.

Each folder is self-contained. The version macros select the model by its full path, so opening one version does not substitute the other. V2 and V3 can be open together in FreeCAD; the last macro run supplies the controls for that version.

## Observe V6 movement

Run [RibosomeV6.FCMacro](v6/RibosomeV6.FCMacro). Slide RNA in either direction,
or use **Rock upper subunit** and **RNA backward — one bead**. **Clasp joined**
selects the closed external return or two captive open tails. **Open mechanism**
reveals the shared drum, rack gear, symmetric detent and internal lift cam.
Straighten the protein before reversing. No release checkbox is required.

Without the macro, edit `Motion.BeadSteps`, `Motion.StrandClosed` and
`Motion.CapStroke`; saved native expressions preserve geometry. See the
[V6 guide](v6/README.md) for cap-cycle bookkeeping and the check boundary.

## Observe preserved V5 movement

Run [RibosomeV5.FCMacro](v5/RibosomeV5.FCMacro). Use the RNA travel slider or
**Click upper subunit**. Enable **Open lower body** to see the drum, keeper,
gears and click leaves. **Return one bead** requires **Release for reverse**;
straighten the real strand first. **Reset view / home** resets the CAD study.
Without the macro, `Motion.BeadSteps` from 0 to 22 drives saved native expressions.
The [V5 guide](v5/README.md) distinguishes the checked rigid geometry from the
unqualified flexible RNA, ratchet leaves, spring space claim and physical feed.

## Observe preserved V4 movement in FreeCAD

1. Open **Macro → Macros…**. Set **User Macros Location** at the bottom to the project's `cad/v4` folder (the **…** button selects a directory). Select **RibosomeV4.FCMacro** in the list, then **Execute**.
2. The panel at the bottom shows the RNA angle, bases passed, bead steps and swivel angle. **Home** aligns the cuff openings. The slider covers **0–165°**.
3. **One codon** animates **7.5° of RNA travel**, one bead step and one complete swivel cycle. The lobe returns to neutral at each whole bead step. To inspect the extremes, set RNA to **1.875°** and **5.625°**; the swivel is approximately **+5.95°** and **−5.95°**.
4. **Open storage / mechanism** exposes the drive and channel. In V3 and V4, **Example hand-shaped chain** displays an illustrative manual pose; V2 retains **Pose emerged protein**. Use Home or clear that checkbox before reversing. Neither view models automatic curling.
5. Without the macro, open `v4/RibosomeV4.FCStd`, select **V4 controls — turn RNA, reverse only after straightening** in the tree (the internal **Motion** object) and edit **DialDegrees** in the **Data** property tab. Values from 0 to 165 are the intended range. Native expressions update the assembly; the macro only adds convenient controls and animation.

The checks evaluate native shape validity, guide clearance, gear and feeder contacts, stop geometry, and swivel linkage alignment across sampled positions. CAD motion is prescribed. Friction, feed reliability, elastic cuff opening, click feel and copper-wire fatigue require physical tests.
