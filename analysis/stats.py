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
