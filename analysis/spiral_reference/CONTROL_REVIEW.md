# Control-image review

On 2026-11-23 at 14:28 +09 the user confirmed all cyan/orange pairs in the two lower rows of upper_wire_spiral_control.png shown in the conversation. This applies to upper-conductor windows 1-3 on 2026-11-23_09-01-27.jpg and 2026-11-20_15-01-35.jpg, six pairs total. It does not approve arbitrary future detections or lower-conductor measurements.

Primary reference is the user-specified 130 mm full spiral diameter. The old nominal 12 mm wire diameter is not used. Bare widths come from red marks. Green and red marks are at nearby, not identical, positions; using each green scale for its corresponding red window remains a local-scale approximation, not independently verified geometry.

The CSV records delta_D = (outer_width_px - bare_width_px) * 130 / spiral_width_px, and symmetric_equivalent = delta_D / 2. Values are provisional apparent-width estimates, not true one-sided thickness or mass. Output digits do not represent measurement accuracy.

Axis shifts were reconstructed from the earlier diagnostic green axes. Contour widths are taken from the last control-image calculation in the conversation. The control PNG, raw source photos and full contour-extraction code are not included in this commit; this is an approval/results record, not yet an end-to-end reproducible pipeline.

The lower apparent widths on 20 November in windows 1-2 are retained as measured, without enforcing a whole-frame thin/thick ordering. Existing geometry gates, code, main branch and workflows remain unchanged.
