# Image provenance

## V6 updated

[v6-updated-flexure-reference.png](v6-updated-flexure-reference.png) is the
user's supplied photo, retained for the two circled serpentine flexure shapes.
Other mechanisms visible in it are not requirements or geometry references.
The images in [cad/v6-updated](../../cad/v6-updated/README.md) are captures of
that candidate's FreeCAD solids. Springs, seats and the folded detent are
geometric candidates; the views do not establish force or physical operation.

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

## V7 routing request and mechanism concept

[v7-routing-request.png](v7-routing-request.png) is the user's annotated V6
CAD screenshot supplied on 2026-11-02. The red line asks for the RNA loop to
cross farther over the body midline and close along the far flank, snug in a
groove. It is qualitative routing guidance, not a dimensioned curve.

[v7-coupling-concept.png](v7-coupling-concept.png) was generated in this
conversation using the built-in image-generation tool. It illustrates two
opposing pawls on separate tracks of one rotor, with a pickup release latch.
It is **not current V7 CAD, a manufacturing drawing or proof of operation**.
The contacts and exaggerated component shapes must not replace actual solids.

Actual V7 review views are in [cad/v7](../../cad/v7/README.md), captured from
the saved solids in cloud FreeCAD 1.1.4, including joined and open RNA and
the higher 13.2-degree far-flank route. They are CAD evidence, not generated
illustrations or proof of physical operation. The report retains rigid and
mechanical failures; reset timing and physical qualification remain unfinished.
See [the continuation record](../v7-cloud-handoff.md).

## Preserved wearable concept illustration

[toy-concept.png](toy-concept.png) was regenerated on 2026-10-27 with the built-in imagegen tool, using the [V3 CAD screenshot](../../cad/v3/bracelet.png) as its structural reference. The [exact prompt](toy-concept.prompt.txt) is retained for reproducibility.

That reference was the screenshot before the bead/outlet revision, preserved in Git commit `0ab02ecf1417fc804089969797e7930fe316d605`. The linked screenshot now shows the newer CAD.

This replaces the early on-wrist illustration at the same filename. That early image is superseded; it must not guide the cuff, RNA routing, protein storage or ribosome mounting. This illustration also predates the subsequent 2026-10-27 CAD revision introducing lobed beads and a cleft between lobe contours. Its spherical beads and round projecting outlet are outdated.

The image illustrates the overall architecture: a separate structural C cuff and RNA C dial, fixed ribosome, concealed waiting chain and direct protein outlet. It is AI concept art, not a CAD render, dimensioned specification, manufacturing drawing or evidence of a working prototype. Use the [current V4 CAD view](../../cad/v4/bracelet.png), saved V3 model and source for the implemented bead and outlet geometry. The AI image has been retained with its original prompt and has not been repainted to imply CAD changes.
