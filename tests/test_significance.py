from rojak.eval.significance import bootstrap_ci, compare, mcnemar_p


def test_mcnemar_no_disagreement_is_one():
    assert mcnemar_p(0, 0) == 1.0


def test_mcnemar_strong_asymmetry_is_significant():
    assert mcnemar_p(10, 0) < 0.05
    assert mcnemar_p(5, 5) == 1.0


def test_compare_binary_uses_mcnemar():
    a = {f"i{i}": 1.0 for i in range(10)}
    b = {f"i{i}": (0.0 if i < 8 else 1.0) for i in range(10)}
    r = compare("intent", a, b)
    assert r["n"] == 10 and r["significant"] and "mcnemar_p" in r


def test_compare_continuous_ci_excludes_zero_for_clear_gap():
    a = {f"i{i}": 0.9 for i in range(20)}
    b = {f"i{i}": 0.1 for i in range(20)}
    r = compare("normalize", a, b)
    assert r["significant"] and r["ci_lo"] > 0


def test_bootstrap_ci_covers_zero_for_identical():
    lo, hi = bootstrap_ci([0.0] * 30)
    assert lo <= 0 <= hi
