# mRNA toy versions

- **[V3 — same-direction feed](v3/README.md):** current development version. The protein leaves a short tangent outlet in the same local direction as the moving RNA. A close guide holds the beads against the feeder. No protein half-turn around the shaft.
- **[V2 — opposite-direction feed](v2/README.md):** preserved comparison, including its source, model, images and historical checks. The chain makes a half-turn inside the ribosome.

Each folder is self-contained. The version macros select the model by its full path, so opening one version does not substitute the other. V2 and V3 can be open together in FreeCAD; the last macro run supplies the controls for that version.

## Observe movement in FreeCAD

1. Open **Macro → Macros…**. Set **User Macros Location** at the bottom to the project's `cad/v3` folder (the **…** button selects a directory). Select **RibosomeV3.FCMacro** in the list, then **Execute**.
2. The panel at the bottom shows the RNA angle, bases passed, bead steps and swivel angle. **Home** aligns the cuff openings. The slider covers **0–165°**.
3. **One codon** animates **7.5° of RNA travel**, one bead step and one complete swivel cycle. The lobe returns to neutral at each whole bead step. To inspect the extremes, set RNA to **1.875°** and **5.625°**; the swivel is approximately **+5.95°** and **−5.95°**.
4. **Open storage / mechanism** exposes the drive and channel. **Pose emerged protein** displays an illustrative bend. Use Home or clear that checkbox before reversing.
5. Without the macro, open `v3/RibosomeV3.FCStd`, select **V3 controls — turn RNA, reverse only after straightening** in the tree (the internal **Motion** object) and edit **DialDegrees** in the **Data** property tab. Values from 0 to 165 are the intended range. Native expressions update the assembly; the macro only adds convenient controls and animation.

The checks evaluate native shape validity, guide clearance, gear and feeder contacts, stop geometry, and swivel linkage alignment across sampled positions. CAD motion is prescribed. Friction, feed reliability, elastic cuff opening, click feel and copper-wire fatigue require physical tests.
