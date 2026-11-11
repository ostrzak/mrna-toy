# V6 updated print: A1 mini prototype preparation

This package belongs to the separate
[V6 updated print candidate](../../cad/v6-updated-print/README.md) on
`version6-updated`. The original V6 updated, V6, V7 and V4 Print remain
preserved. It is a manufacturing prototype, not physical operation evidence.

Use **A1 mini / 0.4 mm**, Bambu **PETG Translucent** for functional rigid
parts, printed screws/nuts, retaining cap, spring supports and the leaf.
Bambu **TPU 90A** remains the RNA/bead trial material. Bambu **PLA Matte**
can be used for rigid appearance or dimensional comparisons.

## GitHub and cloud handoff

The [prototype ZIP](../V6-updated-print-prototype.zip) contains the saved CAD,
20 grouped STEP/STL exports with quantity/material metadata and mesh checks,
and the sliced nine-piece PETG fit-test project. Its CAD files match the
saved `cad/v6-updated-print/` candidate in this repository. Extract the ZIP
before using its relative folder paths; the sliced Bambu project is inside
`fit-plate/`.

For cloud continuation, check out **`version6-updated`** explicitly. The
repository's `main` branch does not contain this candidate. Reading the BOM
and opening package files does not require access to the original Windows
computer. Regenerating geometry requires a compatible FreeCAD runtime with
Part and fcgear; slicing requires Bambu Studio and the matching presets.
Follow `docs/development.md` for the runtime boundary. Local raw builds and
scratch outputs remain ignored; this ZIP is the published prototype handoff.

## Minimum bought components

| Component | Qty | Stock listing |
| --- | ---: | --- |
| Cap return spring | 1 | [TECH-AR MS/095P TYP2 — right-hand, 0.6 mm wire, 6.5 mm OD, 7.25 turns](https://allegro.pl/oferta/sprezyna-skretna-d-0-6-dw-5-3-dz-6-5-prawa-typ2-1-szt-18308431897) |
| Pawl bias spring | 1 | [TECH-AR MS/095L TYP1 — left-hand, 0.6 mm wire, 6.5 mm OD, 7 turns](https://allegro.pl/oferta/sprezyna-skretna-d-0-6-dw-5-3-dz-6-5-lewa-typ1-1-szt-18308566664) |
| Copper wire | One length, user-owned | Existing bead bores and 0.36 mm CAD wire reference are unchanged; the user will select a suitable wire from their supplies |

Both spring listings displayed 12 PLN each on 2026-11-06, before delivery.
They are standard stock items with long straight ends, which the seller
permits trimming. They are not interchangeable: keep the handedness and TYP
numbers above. Supplier dimensions are nominal and supplier rates are not
published. See [engineering details](../../cad/v6-updated-print/engineering.md)
for the force estimates and installation boundary.

There are no metal screws, brass inserts, washers, bearings or extra shafts
in this candidate. Three printed housing screws mate with three printed keyed
nuts. The central retaining cap and spring-retaining shafts are printed.

## Fit plate first

The small PETG test plate contains one case screw, one keyed nut, the mating
post/stack test pieces, a spindle-tip coupon, cap-bearing gauge and retaining
cap, and the two spring-retaining shaft/cup coupons. It uses the exact
installed PETG Translucent filament preset and a derived 0.12 mm Fine process
with four walls, solid infill, Arachne walls, a brim and no supports.
The small stack proxy reproduces the housing stack's 8.2 mm clamped height,
4.6 mm passage and conical head seat; it does not test housing strength.

- Assemble the case post, nut, stack and screw. The nut enters from below;
  hold it while starting the screw. Check free helical engagement and light
  hand tightening before committing to the housing print.
- Place the cap-bearing gauge over the spindle coupon and screw on the cap.
  Its roof should stop on the spindle while the gauge remains free. The CAD
  running gap is 0.25 mm; the printed result needs calibration.
- Measure the received springs before trimming. Trial the retaining tips
  and actual coil fit on the small coupons. Their split heads require elastic
  insertion and recovery, which CAD does not qualify.

The supplier's long legs are trimmed from the coil tangency point: cap spring
3.5 mm fixed / 14.5 mm moving; pawl spring 6 mm fixed / 16.7 mm moving. Deburr
the cut ends. These are prototype nominal lengths. Confirm the received end
angles and fit before making irreversible cuts.

The cap return coil sits in the fixed rear-left cup. Its moving leg pushes
the upper's rounded peg. The horizontal spring inside the upper presses the
pawl's rounded contact boss downward. Proposed home preloads are 23° and
15.5° respectively. Preload installation, access and retention require a
physical assembly trial. The stock spring bodies in CAD are conservative
annular envelopes with explicit wire terminals; do not print them.

## Export and slicing commands

Run the exporter through FreeCADCmd's Python, then check the binary STLs:

```powershell
& 'C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe' -c "import runpy; runpy.run_path('scripts/export_v6_updated_print.py',run_name='__main__')"
python scripts/check_stl_exports.py build/v6-updated-print/exports
python scripts/prepare_v6_updated_fit_plate.py --slice
```

Outputs remain under ignored `build/v6-updated-print/`. The exporter groups
integral physical pieces and includes quantity/material metadata. It exports
the cover's leaf in its unloaded state. Reference RNA layout, bead/wire grip,
full-size orientations, supports and production settings remain separate
qualification work. The new fit plate does not claim a complete sliced toy.

The fit-plate report distinguishes an unsliced source 3MF from a Bambu
project containing G-code. Review the sliced small features before printing.
The workflow never connects to a printer or dispatches a print.

On 2026-11-06, Studio 02.09.01.70 sliced all nine fit-test objects using the
A1 mini / 0.4 mm machine and exact PETG Translucent preset. The saved 3MF
contains G-code and passed archive, object-presence and settings checks.
Studio estimates 31 minutes 5 seconds and 2.13 g; these are slicer estimates.
The output is `build/v6-updated-print/fit-plate/V6-updated-PETG-fit-trials.3mf`.
All 20 grouped model-part/coupon STLs also passed the independent binary-mesh
audit. RNA remains a nominal-layout CAD reference; a new flat manufacturing
pattern is outside this export set.

Physical tests still need to establish spring rates and return under friction,
detent holding without rollback, printed fits and fastening life, bead/wire
retention, RNA pitch/clasp behavior and repeated forward/reverse feeding.
