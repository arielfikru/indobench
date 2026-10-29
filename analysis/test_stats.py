import numpy as np
import pytest

from stats import bootstrap_ci, paired_bootstrap_delta, stderr, unpaired_bootstrap_delta


def _bernoulli(p: float, n: int, seed: int) -> np.ndarray:
    return (np.random.default_rng(seed).random(n) < p).astype(float)


def test_bootstrap_ci_covers_true_mean():
    x = _bernoulli(0.3, 2000, seed=1)
    mean, lo, hi = bootstrap_ci(x)
    assert mean == pytest.approx(x.mean())
    assert lo <= 0.3 <= hi
    assert lo < mean < hi


def test_stderr_matches_formula():
    x = np.array([0.0, 1.0, 1.0, 0.0])
    assert stderr(x) == pytest.approx(np.sqrt(1 / 3) / 2)


def test_paired_identical_arrays_is_zero():
    a = _bernoulli(0.5, 300, seed=2)
    assert paired_bootstrap_delta(a, a.copy()) == (0.0, 0.0, 0.0, 1.0)


def test_paired_known_shift_detected():
    b = _bernoulli(0.5, 400, seed=3)
    a = b.copy()
    zeros = np.flatnonzero(b == 0)[:80]
    a[zeros] = 1.0  # exactly 80 docs flip 0 -> 1, so delta = 80 / 400 = 0.2
    delta, lo, hi, p = paired_bootstrap_delta(a, b)
    assert delta == pytest.approx(0.2)
    assert lo > 0
    assert p < 0.05


def test_paired_length_mismatch_raises():
    with pytest.raises(ValueError):
        paired_bootstrap_delta(np.zeros(3), np.zeros(4))


def test_unpaired_separated_groups_detected():
    delta, lo, hi, p = unpaired_bootstrap_delta(np.ones(50), np.zeros(50))
    assert delta == pytest.approx(1.0)
    assert lo > 0 and p < 0.05


def test_seed_determinism():
    x = _bernoulli(0.4, 200, seed=4)
    y = _bernoulli(0.6, 200, seed=5)
    assert bootstrap_ci(x, seed=7) == bootstrap_ci(x, seed=7)
    assert paired_bootstrap_delta(x, y, seed=7) == paired_bootstrap_delta(x, y, seed=7)
    assert bootstrap_ci(x, seed=7) != bootstrap_ci(x, seed=8)
