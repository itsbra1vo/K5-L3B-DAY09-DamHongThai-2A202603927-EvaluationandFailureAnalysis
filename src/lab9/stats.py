"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy.stats import bootstrap

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge):
        raise ValueError("human and judge labels must have the same length")

    counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
    for actual, predicted in zip(human, judge):
        if actual not in ("PASS", POS) or predicted not in ("PASS", POS):
            raise ValueError("labels must be 'PASS' or 'FAIL'")
        if actual == POS and predicted == POS:
            counts["tp"] += 1
        elif actual != POS and predicted == POS:
            counts["fp"] += 1
        elif actual == POS and predicted != POS:
            counts["fn"] += 1
        else:
            counts["tn"] += 1
    return counts


def precision_recall(human: Sequence[str], judge: Sequence[str]) -> tuple[float, float]:
    counts = confusion(human, judge)
    predicted_positive = counts["tp"] + counts["fp"]
    actual_positive = counts["tp"] + counts["fn"]
    precision = counts["tp"] / predicted_positive if predicted_positive else 0.0
    recall = counts["tp"] / actual_positive if actual_positive else 0.0
    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """kappa = (p_o - p_e) / (1 - p_e). Raise ValueError when undefined (p_e == 1):
    a constant judge has no signal and must FAIL calibration, not pass on a technicality."""
    counts = confusion(human, judge)
    n = len(human)
    if n == 0:
        raise ValueError("Cohen's kappa is undefined for empty labels")

    observed_agreement = (counts["tp"] + counts["tn"]) / n
    human_fail_rate = (counts["tp"] + counts["fn"]) / n
    judge_fail_rate = (counts["tp"] + counts["fp"]) / n
    expected_agreement = (
        human_fail_rate * judge_fail_rate
        + (1 - human_fail_rate) * (1 - judge_fail_rate)
    )
    if expected_agreement == 1:
        raise ValueError("Cohen's kappa is undefined when expected agreement is 1")
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)


def rogan_gladen(observed_rate: float, sensitivity: float, specificity: float) -> float:
    """Correct an observed failure rate for judge error; clip to [0, 1]."""
    if any(not 0 <= rate <= 1 for rate in (observed_rate, sensitivity, specificity)):
        raise ValueError("observed rate, sensitivity, and specificity must be in [0, 1]")
    denominator = sensitivity + specificity - 1
    if denominator == 0:
        raise ValueError("Rogan-Gladen correction is undefined when sensitivity + specificity = 1")
    corrected_rate = (observed_rate + specificity - 1) / denominator
    return min(1.0, max(0.0, corrected_rate))


def paired_bootstrap(a: Sequence[float], b: Sequence[float], *, n_resamples: int = 1000,
                     rng: int = 2027, confidence: float = 0.95) -> tuple[float, float, float]:
    """a[i], b[i] = per-item mean over seeds, SAME items, SAME order.
    Return (mean(a)-mean(b), lo, hi) with scipy.stats.bootstrap(paired=True, method="percentile",
    rng=numpy.random.default_rng(rng)). If a == b everywhere return (0.0, 0.0, 0.0)."""
    if len(a) != len(b):
        raise ValueError("paired samples must have the same length")
    if len(a) == 0:
        raise ValueError("paired samples must not be empty")
    if n_resamples < 1:
        raise ValueError("n_resamples must be positive")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    sample_a, sample_b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if not np.all(np.isfinite(sample_a)) or not np.all(np.isfinite(sample_b)):
        raise ValueError("paired samples must contain only finite values")
    if np.array_equal(sample_a, sample_b):
        return 0.0, 0.0, 0.0

    result = bootstrap(
        (sample_a, sample_b),
        lambda x, y, axis: np.mean(x - y, axis=axis),
        paired=True,
        vectorized=True,
        n_resamples=n_resamples,
        confidence_level=confidence,
        method="percentile",
        rng=np.random.default_rng(rng),
    )
    return (
        float(np.mean(sample_a - sample_b)),
        float(result.confidence_interval.low),
        float(result.confidence_interval.high),
    )


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    if n < 0 or c < 0 or k < 0:
        raise ValueError("n, c, and k must be non-negative")
    if c > n:
        raise ValueError("c cannot exceed n")
    if k > n:
        raise ValueError("k cannot exceed n")
    if k == 0:
        raise ValueError("k must be positive")
    import math
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    if n < 0 or c < 0 or k < 0:
        raise ValueError("n, c, and k must be non-negative")
    if c > n:
        raise ValueError("c cannot exceed n")
    if k > n:
        raise ValueError("k cannot exceed n")
    if k == 0:
        raise ValueError("k must be positive")
    import math
    return math.comb(c, k) / math.comb(n, k)
