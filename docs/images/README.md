# Image provenance

## V6 actual CAD

`cad/v6/handheld.png`, `open.png`, `underside.png`, `mechanism.png`,
`cap-input.png` and `home.png` are captures of the V6 FreeCAD geometry.
They show the captive open/closed RNA and its external underside return.
The current captures show the short central RNA channel with both outer holders
removed and a longer route across the curved flank and underneath. `side.png`
shows the side crossing. `fasteners.png` and
`spindle.png` are actual solid sections of the saved model, not idealized bolt
illustrations. Their source checks that no expected component is lost by the
section Boolean. See the [assembly review](../v6-assembly.md).
RNA cells, open-tail layouts and flexure chords are prescribed kinematic
geometry. The views do not demonstrate physical operation, click sound,
TPU strain, clasp retention or print qualification.

The conversation's generated routing boards are exploratory illustrations.
They motivated the V6 interaction and are not geometry, clearance or
manufacturing references. The CAD views and report define the implemented
design boundary.

## V5 actual CAD

`cad/v5/handheld.png`, `mechanism.png`, `drum.png`, `home.png` and `grip.png` are captures of
the saved V5 FreeCAD geometry. They depict the handheld design, not the earlier
cuff. The source, saved model and focused report define the engineering scope.
The protein core segments and unloaded click leaves are kinematic geometry;
images do not demonstrate physical operation or manufacturing qualification.
The 2026-10-30 captures include the revised asymmetric upper and fixed palm
swell. `grip.png` is a CAD side view, not a photograph or a demonstrated hand fit.

Conversation-generated bead-mechanism sketches are concept art only. They are
not dimensioned references or validation evidence and are not substituted for
the actual CAD captures.

## Preserved wearable concept illustration

[toy-concept.png](toy-concept.png) was regenerated on 2026-10-27 with the built-in imagegen tool, using the [V3 CAD screenshot](../../cad/v3/bracelet.png) as its structural reference. The [exact prompt](toy-concept.prompt.txt) is retained for reproducibility.

That reference was the screenshot before the bead/outlet revision, preserved in Git commit `0ab02ecf1417fc804089969797e7930fe316d605`. The linked screenshot now shows the newer CAD.

This replaces the early on-wrist illustration at the same filename. That early image is superseded; it must not guide the cuff, RNA routing, protein storage or ribosome mounting. This illustration also predates the subsequent 2026-10-27 CAD revision introducing lobed beads and a cleft between lobe contours. Its spherical beads and round projecting outlet are outdated.

The image illustrates the overall architecture: a separate structural C cuff and RNA C dial, fixed ribosome, concealed waiting chain and direct protein outlet. It is AI concept art, not a CAD render, dimensioned specification, manufacturing drawing or evidence of a working prototype. Use the [current V4 CAD view](../../cad/v4/bracelet.png), saved V3 model and source for the implemented bead and outlet geometry. The AI image has been retained with its original prompt and has not been repainted to imply CAD changes.
