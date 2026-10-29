"""Bootstrap and paired-difference statistics for per-sample 0/1 metrics. Pure numpy, no I/O."""

from __future__ import annotations

import numpy as np

_CHUNK_ELEMS = 20_000_000


def stderr(x: np.ndarray) -> float:
    """Standard error of the mean (sample std, ddof=1)."""
    x = np.asarray(x, dtype=float)
    if x.size < 2:
        return float("nan")
    return float(x.std(ddof=1) / np.sqrt(x.size))


def _bootstrap_means(x: np.ndarray, n: int, seed: int) -> np.ndarray:
    """Means of n bootstrap resamples of x, drawn in chunks to bound memory."""
    rng = np.random.default_rng(seed)
    size = x.size
    rows_per_chunk = max(1, _CHUNK_ELEMS // size)
    out = np.empty(n, dtype=float)
    for start in range(0, n, rows_per_chunk):
        stop = min(n, start + rows_per_chunk)
        idx = rng.integers(0, size, size=(stop - start, size))
        out[start:stop] = x[idx].mean(axis=1)
    return out


def bootstrap_ci(
    x: np.ndarray, n: int = 10000, seed: int = 0, alpha: float = 0.05
) -> tuple[float, float, float]:
    """Percentile bootstrap CI of the mean. Returns (mean, lo, hi)."""
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return (float("nan"), float("nan"), float("nan"))
    means = _bootstrap_means(x, n, seed)
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return (float(x.mean()), float(lo), float(hi))


def _p_two_sided(boot: np.ndarray) -> float:
    """Two-sided p for H0: delta = 0, from the bootstrap distribution of delta."""
    p_le = float(np.mean(boot <= 0))
    p_ge = float(np.mean(boot >= 0))
    return min(1.0, 2 * min(p_le, p_ge))


def paired_bootstrap_delta(
    a: np.ndarray, b: np.ndarray, n: int = 10000, seed: int = 0, alpha: float = 0.05
) -> tuple[float, float, float, float]:
    """Paired bootstrap of delta = mean(a - b). a and b must be aligned by doc_id.

    Returns (delta, lo, hi, p_two_sided). Identical inputs give (0, 0, 0, 1).
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"paired arrays differ in length: {a.shape} vs {b.shape}")
    if a.size == 0:
        return (float("nan"),) * 3 + (float("nan"),)
    d = a - b
    boot = _bootstrap_means(d, n, seed)
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    return (float(d.mean()), float(lo), float(hi), _p_two_sided(boot))


def unpaired_bootstrap_delta(
    a: np.ndarray, b: np.ndarray, n: int = 10000, seed: int = 0, alpha: float = 0.05
) -> tuple[float, float, float, float]:
    """Unpaired bootstrap of delta = mean(a) - mean(b), for independent samples.

    Returns (delta, lo, hi, p_two_sided).
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        return (float("nan"),) * 3 + (float("nan"),)
    boot_a = _bootstrap_means(a, n, seed)
    boot_b = _bootstrap_means(b, n, seed + 1)
    boot = boot_a - boot_b
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    return (float(a.mean() - b.mean()), float(lo), float(hi), _p_two_sided(boot))


def _cluster_totals(x: np.ndarray, clusters: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per-cluster sum of x and per-cluster item count, clusters in sorted label order."""
    labels = np.asarray(clusters)
    if labels.shape != x.shape:
        raise ValueError(f"clusters length {labels.shape} does not match values {x.shape}")
    _, inv = np.unique(labels, return_inverse=True)
    inv = inv.reshape(-1)
    sums = np.bincount(inv, weights=x, minlength=inv.max() + 1)
    counts = np.bincount(inv, minlength=inv.max() + 1).astype(float)
    return sums, counts


def _cluster_bootstrap_means(sums: np.ndarray, counts: np.ndarray, n: int, seed: int) -> np.ndarray:
    """Resample whole clusters with replacement. Each draw's statistic is sum(x) / count over the drawn clusters."""
    rng = np.random.default_rng(seed)
    k = sums.size
    rows_per_chunk = max(1, _CHUNK_ELEMS // k)
    out = np.empty(n, dtype=float)
    for start in range(0, n, rows_per_chunk):
        stop = min(n, start + rows_per_chunk)
        idx = rng.integers(0, k, size=(stop - start, k))
        out[start:stop] = sums[idx].sum(axis=1) / counts[idx].sum(axis=1)
    return out


def cluster_bootstrap_ci(
    values: np.ndarray, clusters: np.ndarray, n_boot: int = 10000, seed: int = 0, alpha: float = 0.05
) -> tuple[float, float, float]:
    """Cluster (block) bootstrap CI of the mean: resample clusters, not items. Returns (mean, lo, hi).

    The statistic for a draw is the mean over all items in the drawn clusters, so a cluster drawn
    twice counts twice. One cluster per item reduces to the iid bootstrap in distribution.
    """
    x = np.asarray(values, dtype=float)
    if x.size == 0:
        return (float("nan"), float("nan"), float("nan"))
    sums, counts = _cluster_totals(x, clusters)
    means = _cluster_bootstrap_means(sums, counts, n_boot, seed)
    lo, hi = np.quantile(means, [alpha / 2, 1 - alpha / 2])
    return (float(x.mean()), float(lo), float(hi))


def paired_cluster_bootstrap_delta(
    a: np.ndarray, b: np.ndarray, clusters: np.ndarray, n_boot: int = 10000, seed: int = 0, alpha: float = 0.05
) -> tuple[float, float, float, float]:
    """Cluster bootstrap of delta = mean(a - b). a, b and clusters must be aligned by doc_id.

    Clusters are shared by both sides, so the same drawn clusters apply to a and b.
    Returns (delta, lo, hi, p_two_sided), same shape as paired_bootstrap_delta.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"paired arrays differ in length: {a.shape} vs {b.shape}")
    if a.size == 0:
        return (float("nan"),) * 3 + (float("nan"),)
    d = a - b
    sums, counts = _cluster_totals(d, clusters)
    boot = _cluster_bootstrap_means(sums, counts, n_boot, seed)
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    return (float(d.mean()), float(lo), float(hi), _p_two_sided(boot))


def holm(pvalues: list[float], alpha: float = 0.05) -> list[bool]:
    """Holm-Bonferroni step-down: which hypotheses are rejected at family-wise level alpha."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    reject = [False] * len(pvalues)
    m = len(pvalues)
    for rank, i in enumerate(order):
        if pvalues[i] > alpha / (m - rank):
            break
        reject[i] = True
    return reject
