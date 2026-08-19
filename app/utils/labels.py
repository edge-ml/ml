"""Shared handling of the 'unlabeled sample' marker used across the data pipeline.

Samples that fall outside every label interval are tagged with UNLABELED_LABEL so
they can be dropped after windowing. The marker must (a) never collide with a real
class index (real indices are non-negative) and (b) never reach np.bincount as a
positive index, since bincount sizes its output array to the largest value it sees
(a huge marker would try to allocate a huge array and OOM). -1 satisfies both.

Historically the marker was written as `9*10^10`, intended as 9e10 but actually
`(9*10) ^ 10 == 80` (^ is XOR in Python). That accidental value happened to be
small enough for bincount and was used identically at the assignment and filter
sites, so it worked by luck; but a project with >=81 labels would have a real
label collide with 80. See issue #65.
"""
import numpy as np

UNLABELED_LABEL = -1


def window_majority_label(label_col):
    """Majority per-sample label of one window, treating UNLABELED_LABEL samples as
    their own bucket without passing negatives to np.bincount.

    Returns the most frequent real label, or UNLABELED_LABEL if the window has no
    real labels or the unlabeled samples are at least as many as the top real label
    (so the window is later filtered out by BaseWindower._filterLabelings)."""
    col = np.asarray(label_col).astype(int)
    labeled = col[col >= 0]
    if labeled.size == 0:
        return UNLABELED_LABEL
    counts = np.bincount(labeled)
    top = int(np.argmax(counts))
    n_unlabeled = int(np.sum(col < 0))
    return top if counts[top] >= n_unlabeled else UNLABELED_LABEL
