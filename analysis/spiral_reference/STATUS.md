# Spiral reference work: final status (2026-11-23)

Branch: analysis/spiral-130mm-reference, branched from main at 3928795. This directory is experimental. Nothing here is connected to the photo-saving workflow, and main, photos and workflows are untouched.

## What is done

- Primary size reference: user-confirmed outer diameter of a full spiral turn, 130 mm (green marks). The earlier 12 mm wire diameter is not used. Red marks fix the bare conductor silhouette in pixels. See reference.json, mark_endpoints.csv, digitize_marks.py.
- Upper-conductor windows 1-3 were reviewed and approved by the user on four frames: 2026-11-20 15:01, 2026-11-23 09:01, 10:01 and 11:01. Widths are in approved_upper_wire_measurements.csv, approved_10_01_sections.csv and approved_11_01_sections.csv. The first file also holds provisional millimetre estimates.
- Conditional suppression of a dark stripe inside a bright frost layer fixed 23 November windows 2-3 (conditional_gap.py, DARK_STRIPE_REVIEW.md). Windows 1-2 of 20 November remain unresolved.
- Frozen regression replays: replay_control.py (six sections) and temporal_replay.py (09:01 to 10:01 transfer plus widths). They test replay, not accuracy.

## What is not done

- No automatic acceptance or visibility criterion. Stability under changed smoothing was tested and rejected: the two wrong sections were also stable. Automatic measurements in poorly visible areas must return no numeric thickness, never zero.
- The metric scale is a local approximation. Green and red marks are at nearby, not identical, positions; each green scale was applied to its own red window. No scale is defined for the lower conductor. No interpolation between windows. Millimetre values are provisional and carry no stated accuracy.
- Frame-to-frame transfer is validated only for neighbouring hourly frames. Direct 09:01 to 11:01 matching was unreliable. Chaining through an intermediate frame is not independently validated.
- Axes for the target dates were reconstructed from an earlier manual diagnostic image. No general axis finder exists.
- Symmetric thickness is half the apparent diameter increase, not a one-sided thickness, asymmetric layer or mass.

## Provenance correction

Earlier records mention a hash mismatch only for 10:01 and 11:01. The check was later run for all five attached frames and every one differs from the same-named file in photos on main, in size and in Git blob hash:

| Frame | Attachment bytes | Archive bytes | Ratio |
|---|---:|---:|---:|
| 2026-11-20_15-01-35 | 399449 | 290977 | 1.37 |
| 2026-11-22_09-01-29 | 442617 | 312187 | 1.42 |
| 2026-11-23_09-01-27 | 425907 | 301678 | 1.41 |
| 2026-11-23_10-01-55 | 452559 | 310566 | 1.46 |
| 2026-11-23_11-01-54 | 473317 | 317992 | 1.49 |

Dimensions of the attachments are 1280x720. The user states they are the same photographs. Byte equality does not hold, and pixel equivalence has not been tested because the archive bytes were not available for pixel comparison. Cause unknown; re-encoding on upload is a hypothesis only. All coordinates, widths and approvals here refer to the attachments identified by the SHA-256 values in the CSV files and replay scripts. Reproducing them on archive files requires either a pixel comparison or recomputation and re-approval.

## Suggested next steps

1. Compare pixels of one attachment with an archive copy downloaded directly from GitHub, then recompute control widths on archive files.
2. Design and validate a visibility gate on more frames, with deliberate negative examples.
3. Validate the local scale assumption with additional green marks nearer to each red window.
4. Only then consider integrating anything into the main workflow.
