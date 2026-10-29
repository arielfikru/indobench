import numpy as np
import pytest

from stats import (
    bootstrap_ci,
    cluster_bootstrap_ci,
    paired_bootstrap_delta,
    paired_cluster_bootstrap_delta,
    stderr,
    unpaired_bootstrap_delta,
)


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


def test_holm_step_down():
    from stats import holm
    # m=3: thresholds 0.0167, 0.025, 0.05 in p order
    assert holm([0.01, 0.02, 0.04]) == [True, True, True]
    assert holm([0.01, 0.03, 0.04]) == [True, False, False]
    assert holm([0.2, 0.001]) == [False, True]


def test_cluster_one_item_per_cluster_matches_iid_in_distribution():
    x = _bernoulli(0.3, 2000, seed=11)
    ids = np.arange(x.size)
    m_iid, lo_iid, hi_iid = bootstrap_ci(x, n=10000, seed=0)
    m_cl, lo_cl, hi_cl = cluster_bootstrap_ci(x, ids, n_boot=10000, seed=0)
    assert m_cl == pytest.approx(m_iid)
    assert (hi_cl - lo_cl) / (hi_iid - lo_iid) == pytest.approx(1.0, abs=0.05)
    assert lo_cl == pytest.approx(lo_iid, abs=0.005)
    assert hi_cl == pytest.approx(hi_iid, abs=0.005)


def test_cluster_correlated_items_give_wider_ci():
    # 40 clusters of 50 items; every item in a cluster shares the same outcome,
    # so the effective sample size is 40, not 2000.
    rng = np.random.default_rng(12)
    cluster_outcome = (rng.random(40) < 0.3).astype(float)
    clusters = np.repeat(np.arange(40), 50)
    x = cluster_outcome[clusters]
    _, lo_iid, hi_iid = bootstrap_ci(x, n=10000, seed=0)
    mean, lo_cl, hi_cl = cluster_bootstrap_ci(x, clusters, n_boot=10000, seed=0)
    assert mean == pytest.approx(x.mean())
    assert (hi_cl - lo_cl) > 2 * (hi_iid - lo_iid)
    assert lo_cl <= x.mean() <= hi_cl


def test_cluster_statistic_weights_by_item_count():
    # Unequal cluster sizes: the point estimate is the item-level mean, not the mean of cluster means.
    x = np.array([1.0] * 9 + [0.0])
    clusters = np.array(["big"] * 9 + ["small"])
    mean, _, _ = cluster_bootstrap_ci(x, clusters, n_boot=500, seed=0)
    assert mean == pytest.approx(0.9)


def test_cluster_length_mismatch_raises():
    with pytest.raises(ValueError):
        cluster_bootstrap_ci(np.zeros(3), np.zeros(4), n_boot=10)


def test_cluster_paired_identical_arrays_is_zero():
    a = _bernoulli(0.5, 300, seed=13)
    clusters = np.arange(300) // 10
    assert paired_cluster_bootstrap_delta(a, a.copy(), clusters, n_boot=2000) == (0.0, 0.0, 0.0, 1.0)


def test_cluster_paired_widens_and_keeps_delta():
    b = _bernoulli(0.5, 1000, seed=14)
    a = b.copy()
    flip = np.flatnonzero(b == 0)[:200]
    a[flip] = 1.0
    clusters = np.arange(1000) // 50
    delta_iid, lo_iid, hi_iid, _ = paired_bootstrap_delta(a, b, n=10000, seed=0)
    delta, lo, hi, p = paired_cluster_bootstrap_delta(a, b, clusters, n_boot=10000, seed=0)
    assert delta == pytest.approx(delta_iid)
    assert (hi - lo) > (hi_iid - lo_iid)
    assert 0 <= p <= 1


def test_cluster_seed_determinism():
    x = _bernoulli(0.4, 200, seed=15)
    clusters = np.arange(200) // 20
    assert cluster_bootstrap_ci(x, clusters, seed=7) == cluster_bootstrap_ci(x, clusters, seed=7)
    assert cluster_bootstrap_ci(x, clusters, seed=7) != cluster_bootstrap_ci(x, clusters, seed=8)
