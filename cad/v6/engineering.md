# V6 starting force budget

These are **illustrative estimates**, separate from the focused CAD result.
They use assumed elastic moduli and idealized beam/spring formulas. They do
not establish printed material properties, strength, fatigue, sound or
reliable operation. Reproduce them with `python cad/v6/engineering_v6.py`.

The return pawl must rise over its face ramps while the symmetric detent holds
the drum at its index. RNA hand force must still overcome that detent in
either direction. The cap-return spring also has to raise the pawl onto the
rest-disengagement cam, against the axial bias spring.

| Starting quantity | Idealized estimate |
| --- | --- |
| Click leaf: 12 mm long, 1 mm radial thickness, 2 mm height | 0.492 N/mm with assumed effective modulus 1700 N/mm² |
| Click follower preload / peak displacement | About 0.29 / 0.89 mm |
| Idealized click force at those displacements | 0.143 / 0.438 N |
| Peak resisting drum torque | About 2.79 N·mm |
| Axial bias candidate: 0.15 mm wire, 2.5 mm mean coil diameter, 8 active turns, 6.5 mm free length | About 0.040 N/mm with assumed shear modulus 79000 N/mm² |
| Installed axial length / approximate solid height | 2.7–4.7 mm / 1.5 mm |
| Ideal face-ramp return torque | About 0.60 N·mm |
| Cap torsion candidate: 0.6 mm wire, 12.1 mm mean diameter, 3 active turns, 22° preload | About 4.28 N·mm at rest, 7.96 N·mm at full stroke, with assumed modulus 200000 N/mm² |
| Ideal entry-cam torque against axial bias | About 2.90 N·mm |

This gives a starting peak detent/return-torque ratio around 4.7 and a cap
restoring/entry-torque ratio around 1.5 before friction and losses. The latter
margin needs particular attention on a printed cam. The ideal leaf's peak
outer-fibre strain is about 0.93%; actual cyclic capability is unknown.

The CAD reserves spring body volumes and candidate wire-terminal routes. The
compression spring has upper/lower seats and a guide pin. The cap spring has
fixed and moving radial leg sockets outside the central cap bearing; its
reserved terminals clear the moving parts in the sampled poses. Actual coil
manufacture, terminal hooks, preload setting and retention remain unqualified.

Measure printed leaf force, cam friction and detent holding torque first.
Then test cap return without drum rollback, low-force RNA reversal, click
sound, reliable bead handoff and overload behavior. Bead/core drag, printed
anisotropy, toe torsion, impact, wear and spring variation are omitted from
this first-order calculation. No ready-to-buy spring or material grade is
specified by these numbers.
