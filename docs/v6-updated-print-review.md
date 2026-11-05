# V6 updated: export and hardware review

Reviewed 2026-11-06 on `version6-updated`. The user confirmed **Bambu Lab A1
mini, 0.4 mm nozzle**, ownership of the Skipping Stone BOM items, and corrected
the available filament to **Bambu TPU 90A**. Copper-wire diameter remains to
be confirmed; the current toy CAD represents a 0.36 mm core.

This is an export/manufacturing review, not a print release. V6 updated CAD,
its motion and its mechanical REVIEW boundary remain unchanged. V6, V7 and
the V4 Print package remain preserved.

## What was exported and checked

The FreeCAD 1.1.4 worker opens the saved `cad/v6-updated/RibosomeV6Updated.FCStd`
in a separate process. It groups intended physical components, excludes
metal hardware, moves each exported component to a nonnegative millimetre
coordinate system, and writes STEP and binary STL into
`build/v6-updated-print-review/`. It never saves the source document.
STL is unitless; interpret these exports as millimetres. The STEP round trip
also checks that the dimensions survive export.

Bambu Studio's CLI also accepted the unloaded fixed-cover STL and the corrected
offset-bead STL in an import-only check (return code 0). No slicing, printer
profile qualification or G-code generation was performed.

The twelve exports are eight rigid components, three bead variants and one
**reference-only** open RNA layout. Integral features are fused: the lower
housing includes its spindle; each rotor is one physical part; the fixed
cover includes the torsion cup, anchor, follower and serpentine leaf.

The cover export uses **zero prescribed leaf deflection** on the temporary
document. Printing the installed, pre-deflected leaf would not establish the
intended preload. Installation of the free leaf still needs a physical trial.

All twelve STEP files reopened as valid single solids, with dimension errors
below 0.00001 mm. All twelve final STLs passed independent edge-incidence,
orientation, degenerate-facet, finite-coordinate and positive-volume checks.
All twelve also fit the nominal 180 mm build volume in the tested coordinate
orientation. Bed placement, adhesion, supports and slicing are not qualified.

The initial offset-bead STL had two nonmanifold edges, two degenerate facets
and two mesh components. Its STEP remained valid. Reconstructing the shape
from that STEP and tessellating at 0.005 mm / 0.07 rad produced a closed,
single-component STL that passed the independent checks. The source CAD was
not changed. Finer tessellation was tested rather than assumed to repair it:
the 0.01 mm trial also failed.

`export-report.json` and `mesh-audit.json` retain the results. A closed mesh is
not evidence of successful printing, fit or operation. The open RNA export
is a fused nominal deformed pose, not an unloaded manufacturing flat pattern.
Its approximately 4.76 mm height after plane rotation illustrates why simply
exporting the animated strip is not the final flat TPU print design.

From the repository root, run with FreeCAD's command-line executable:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe' -c "import runpy; runpy.run_path('scripts/export_v6_updated_review.py',run_name='__main__')"
python scripts/check_stl_exports.py build/v6-updated-print-review
python scripts/check_repo.py
```

The executable path is a local example. Provision FreeCAD with Part, Mesh,
MeshPart and bundled fcgear elsewhere. Existing FreeCAD exports work; a new
MCP integration is not required for this stage.

## Material and hardware direction

These are proposed prototype choices, not qualified materials or final
procurement specifications.

| Component | Proposed direction | Decision before manufacturing |
| --- | --- | --- |
| Housing, lid, keeper and rocking upper | PETG for the first functional prototype; PLA for fit/appearance studies | Choose orientations and accessible supports; inspect bearing and guide surfaces |
| Drum and upper drive rotor | PETG candidate; PLA can be a dimensional comparison | Check teeth, 0.65 mm fork levels, supports, friction and wear |
| Fixed cover and integral serpentine leaf | PETG candidate, printed as one component | Test the leaf's free-state force, preload, holding torque and fatigue; TPU is not a substitute for this geometry |
| RNA | User-owned TPU 90A trial | Make a flat manufacturing layout and short rack/channel/clasp test; check pitch under hand loads and reverse pushing |
| Protein beads | TPU 90A trial | Add bed-contact geometry, choose bore and fixation to the actual wire, and retain 6 mm pitch |
| Two return/bias springs | Purchased metal springs | Match rate, force/torque, travel, OD/ID, end treatment and installation; adapt seats to selected hardware |
| Housing and cap screws | Purchased steel/stainless screws | Select actual head drawings and a fastening method before changing pockets |
| Retaining washer and spring-seat shims | Purchased/cut metal | Match real dimensions and preserve endplay and spring working lengths |
| 1.5 mm pawl guide pin | Printed PETG prototype or later retained metal pin | A metal pin requires a seating/retention redesign; the current pin is integral with the upper |
| Cam contact | Manufacturing change or a tested printed prototype | The current 1 mm ball has a 0.5 mm neck; review a wider printed feature or properly retained metal contact |
| Main 6 mm integral spindle | Retain the printed PETG candidate for initial tests | Do not substitute a plain metal shaft without redesigning its root, bearings, shoulder and screw retention |

## Screws and washers: current CAD facts

The CAD uses major-diameter thread envelopes, not working printed threads or
supplier-qualified screw geometry.

| Item | Qty | Current nominal CAD |
| --- | --- | --- |
| Housing fastener | 3 | M2 x 12, countersunk; nominal 90-degree seat and 3.8 mm head envelope |
| Central cap retainer | 1 | M2 x 4 nominal, hex socket/pan-like head envelope; actual head family remains unselected |
| Cap retaining washer | 1 | 2.2 mm ID, 8 mm OD, 0.6 mm thickness |
| Pawl spring-seat washer | 2 | 1.7 mm ID, 3.3 mm OD, 0.15 mm thickness |
| Housing screw pilots | 3 | 1.7 mm diameter, approximately 4.2 mm nominal engagement |
| Cap screw pilot | 1 | 1.7 mm diameter in the integral spindle, approximately 3.4 mm engagement |

The washer dimensions are not a claim that generic M2 washers will fit. In
particular the 0.15 mm spring seats are metal shim geometry, not useful
single-layer printed parts. Choose available hardware and update the seats
and screw stack to suit it.

For repeated disassembly, my preference is metal machine screws with properly
designed brass heat-set inserts or captive nuts where accessible. **The current
1.7 mm pilots are not insert pockets.** This requires a manufacturing
derivative with the selected insert's hole, depth and surrounding material.
A specified plastic thread-forming screw with tested pilots is an alternative
for a simpler first prototype. Do not treat these two methods as interchangeable.
SPIROL's [insert guidance](https://www.spirol.com/resources/white-papers/how-to-design-the-proper-hole-for-heat-ultrasonic-inserts/)
explains why the selected insert determines the hole and wall requirements.

## Spring sourcing targets, not an order list

- Torsion candidate: 0.6 mm wire, 13.5 mm mean diameter, three nominal active
  turns and 22 degrees installed preload. The illustrative rate is
  10 N mm/rad, about 0.175 N mm/degree. Leg shape and free angle are schematic.
- Compression candidate: 0.15 mm wire, 2.5 mm mean diameter, eight nominal
  active turns and 6.5 mm free length. The proposed working space between
  seats is approximately 2.4–4.4 mm, with an illustrative 0.040 N/mm rate.

These estimates omit friction and measured printed-leaf holding force. The
ideal home return/entry-cam torque ratio is only about 1.23. Select and test
the detent and metal springs together; a larger return spring alone is not
a demonstrated solution. Use catalog drawings and rates to choose real parts,
then adjust spring anchors, seats and working travel in the print derivative.

## Reusing the Skipping Stone inventory

The read source was `Skipping Stone/agentic-documentation/bom.md`; the user
confirmed its items are owned. The listed dimensions remain nominal until
measured.

PETG/TPU supplies and measurement tools can help directly. The 3 mm shafts,
3 x 8 x 5 collars, MR63ZZ 3 x 6 x 2.5 radial bearings and F3 thrust bearings
do not directly fit the toy's 6 mm integral-spindle arrangement. Keep these
as possible future redesign inputs. The rotary seal, Dyneema line and ballast
have no role in the current toy mechanism. Existing threadlocker/adhesive
grades have not been selected for the printed joints or bead fixation.

## Bambu Studio path

The installed Bambu profile `Bambu TPU 90A @BBL A1M` (setting `GFSU03_05`)
explicitly lists `Bambu Lab A1 mini 0.4 nozzle`. Bambu's
[TPU 90A data sheet](https://store.bblcdn.com/s6/default/62f87cb83a1e47a58c73c73240f8410a/Bambu_TPU_90A_Technical_Data_Sheet_582bf8f6-1f0a-474c-aeda-9e72af3689dc.pdf)
also lists a 0.4 mm nozzle. Use the external spool for ordinary flexible TPU;
the AMS lite feed path is not the selected route.

STL/STEP review exports are the starting point. The eventual deliverable can
be a Bambu Studio `.3mf` project with named physical parts, separate PETG and
TPU plates, A1 mini/0.4 settings, orientations and support choices. A geometry
3MF is distinct from a sliced/checked print job; neither proves assembly or
durability. Bambu documents project generation in its
[Studio CLI guide](https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage).

First qualify small tests: wire/bead retention, an RNA rack/channel/clasp
segment, the PETG detent and spring return, and the fastener/shaft fits.
Then prepare the full manufacturing derivative and reviewed Bambu project.
