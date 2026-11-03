# Spring installation and evidence boundary

The two metal springs are explicit parts in this candidate. They are not
intended to be printed. Their dimensions remain proposed hardware, with
assumed steel properties and no supplier qualification. The printed folded
detent is a separate elastic part.

| Part | Nominal geometry | Reaction path |
| --- | --- | --- |
| Upper torsion spring | 0.6 mm wire; 13.5 mm mean diameter; three nominal turns; 22° installed preload | Moving upper terminal → coil → fixed lower terminal → fixed cover post |
| Torsion housing | 0.8 mm floor/walls; floor top at z=27.5 mm; inner mandrel, slotted outer cup and cover bridge | Coil location and containment; cover carries terminal reaction |
| Pawl compression spring | 0.15 mm wire; 2.5 mm mean diameter; eight nominal active turns | Upper carrier → upper washer → coil → lower washer → sliding pawl |
| Compression installed length | Approximately 2.4–4.4 mm between washer seats | Pawl lift reduces the space by 2 mm |
| Printed detent | Seven 0.9 mm webs; six 1 mm centre-radius bends; 2 mm height | Index profile → rounded follower → folded beam → fixed cover root |

The torsion helix winds with upper rotation and contracts slightly to retain
its nominal centreline length. Its terminal roots overlap the coil, and the
upper terminal moves with the upper. These are native geometric relationships.
They do not calculate spring stress, contact pressure, terminal bending or
friction. End-coil shapes and terminal bends need fabrication review. The
compression coil changes pitch between its washers; its end turns are not
ground/closed supplier geometry.

The 22° preload means the unloaded moving terminal would lie 22° ahead of its
home socket. Installing it in the home socket stores return torque. Actual
assembly access, tooling, terminal retention under load and hardware selection
must be resolved and tested before manufacturing. The current CAD audit keeps
these distinct from nominal coil and seat clearance.

Run `python cad/v6-updated/engineering_v6_updated.py` for illustrative metal
spring estimates. The straight-leaf calculation inherited from V6 is explicitly
removed from the reported detent result. It does not apply to the folded
geometry. Until its holding torque is measured or properly analysed, return
without drum rollback and the RNA click force remain unqualified.

The source validator reports CAD results separately from these estimates.
No CAD pose or geometric PASS proves dependable physical feeding, cap return,
printed strength or fatigue. V7's incomplete pickup/reset evidence is neither
used nor solved by this candidate.
