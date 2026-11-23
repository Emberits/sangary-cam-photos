# Conditional dark-stripe suppression: visual review

On 2026-11-23 at 14:57 +09 the user accepted the result after a targeted request to review new cyan/orange boundaries in windows 2 and 3 of 2026-11-23_09-01-27.jpg in conditional_dark_gap_review.png. The user reported that remaining failures occur where nothing is discernible. This is visual feedback, not an independently validated visibility classifier.

Experiment: fill narrow dark valleys only when flanked by bright shoulders and supported along the conductor, then run paired-boundary tracking. Common thresholds were used for both control frames. The approved width table was used for evaluation, not per-window method selection.

Widths in original-image pixels:

| Image date | Window | Earlier approved baseline | Raw paired search | Conditional suppression |
|---|---:|---:|---:|---:|
| 2026-11-23 | 1 | 3.625 | 3.750 | 3.750 |
| 2026-11-23 | 2 | 4.500 | 1.250 | 4.250 |
| 2026-11-23 | 3 | 4.500 | 1.500 | 4.375 |
| 2026-11-20 | 1 | 2.375 | 1.625 | 1.625 |
| 2026-11-20 | 2 | 3.625 | 6.500 | 6.500 |
| 2026-11-20 | 3 | 8.375 | 8.250 | 8.250 |

Four of six conditional widths are within 0.25 px of the earlier baseline, versus two of six raw widths. Mean absolute differences are 0.708333 and 1.687500 px respectively. These are development-set comparisons, not independent accuracy estimates. The 0.25 px threshold is a comparison tolerance, not claimed physical accuracy. The remaining discrepancies in 20 November windows 1-2 are unresolved; their exact optical cause has not been established.

Proposed next step: distinguish found contour, ambiguous contour and insufficient visibility. Ambiguous or insufficient-visibility automatic measurements should have no numeric thickness, not zero or an interpolated result. An automatic rejection criterion has not yet been implemented or validated. This does not revoke the previous manual approvals.

This commit records review only. It does not add the experimental suppression code, image artifacts, automatic visibility gate or production integration. Existing approved measurements, the 130 mm reference, replay code, main and workflows are unchanged.
