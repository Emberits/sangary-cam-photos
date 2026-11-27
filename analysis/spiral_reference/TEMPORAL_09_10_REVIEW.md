# Temporal test: 09:01 to 10:01 on 23 November

The user approved all three cyan/orange pairs in the lower row of temporal_09_10_contour_review.png at 15:43 +09 on 2026-11-23. Approval applies to the uploaded 2026-11-23_10-01-55.jpg attachment, upper conductor only. No previous baseline is replaced.

Source attachment: 1280x720, 452559 bytes. SHA-256: 074e36e86224ccd20890ff3c4166cbf48d757abb2a45c38be8a9ddf74d044fa1. Computed Git blob SHA-1: adda60c1bbeec9387812cfdfeb59b0c74770995f. The GitHub connector reports e4c2c57a48692afd4f481883b1df64a631611728 for photos/2026-11-23_10-01-55.jpg on main. These do not match. Cause is unknown and pixel equivalence has not been tested. Do not substitute the repository image by filename alone or claim these widths replay on it. The attachment is not added by this commit.

Source frame 09:01 SHA-256: 3ddb069f5825cdc30a504eabb1d7f2723ddb312d7f71fc73a914290a049ee688. Its three widths replayed as 3.625, 4.500 and 4.500 px.

Temporal localisation used high-pass normalised cross-correlation in local wire coordinates. Templates extended 12 px along the conductor and 4, 6 or 10 px either side of the axis. Search margin was 8 px in both directions, on a 0.5 px grid. All nine forward tests selected zero displacement; reverse matches also selected zero displacement. Forward correlation was approximately 0.93-0.95. This does not prove subpixel immobility or correct contour selection: templates contain both wire and background.

The three 10:01 widths were independently extracted using the reviewed gradient rule, not copied from 09:01: 3.750, 4.375 and 4.500 px. Signed offsets in the CSV are normal to the transferred 09:01 axes, not image y coordinates. Those source axes were reconstructed from the earlier manual diagnostic.

No frost-growth inference is made from differences of 0.125 px. No new millimetre estimates, visibility classifier, general temporal tracker or production integration are introduced. The matching code and control PNG are not included in this commit; this is a provenance and approval record, not a complete replay package. Existing code, calibration, main, photos and workflows remain unchanged.
