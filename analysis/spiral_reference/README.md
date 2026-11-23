# Experimental spiral reference

Primary reference: user-confirmed outer diameter of a full spiral turn, 130 mm.
The former 12 mm wire diameter is not used. Red marks fix the bare silhouette
in pixels. Upper/lower refer to the annotation, not previous wire numbering.

Values in reference.json are rounded digitized distances reported during analysis.
They are not raw endpoint coordinates. Recovering and storing exact endpoints,
image hashes and extraction code remains a follow-up task.

This package only calculates from an externally supplied contour width. It does
not detect frost, align images or validate geometry. Widths must be normal to
the conductor and expressed in reference-image pixels after registration.

Green and red marks lie at nearby but different positions. Local scale transfer
must be checked before enabling local_geometry_verified. That argument is a
caller assertion, not an automatic test. No scale is assigned to the lower
conductor. No interpolation or cross-window scale transfer is implemented.

Formula: delta_D = (outer_width_px - bare_width_px) * 130 / green_width_px.
Half delta_D is a symmetric equivalent, not true asymmetric thickness or mass.
Negative results are retained and flagged, never clamped to zero.
All positive results remain experimental. No production accuracy is claimed.

Run tests from this directory: python -m unittest test_fixed_reference.py
No dependencies beyond Python standard library. No workflow or photo changes.
