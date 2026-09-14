import sys
import os
import math
import pytest

SCIPY_AVAILABLE = False
try:
    import scipy  # noqa: F401

    SCIPY_AVAILABLE = True
except ImportError:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver, extract_variables


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- verified against CortexJS's own documented examples ---
        (
            {},
            ["PDF", ["BinomialDistribution", 4, ["Rational", 1, 2]], 2],
            0.375,
        ),
        (
            {},
            ["Round", ["CDF", ["NormalDistribution", 0, 1], 1], 10],
            round(0.8413447460685429, 10),
        ),
        # --- Normal: PDF/CDF/Quantile are mutual inverses, no scipy needed ---
        ({}, ["Round", ["PDF", ["NormalDistribution", 0, 1], 0], 6], round(1 / math.sqrt(2 * math.pi), 6)),
        (
            {},
            ["Round", ["CDF", ["NormalDistribution", 0, 1], ["Quantile", ["NormalDistribution", 0, 1], 0.9]], 6],
            0.9,
        ),
        # --- Uniform: closed forms ---
        ({}, ["CDF", ["UniformDistribution", 0, 10], 3], 0.3),
        ({}, ["PDF", ["UniformDistribution", 0, 10], 15], 0.0),
        ({}, ["Quantile", ["UniformDistribution", 0, 10], 0.5], 5.0),
        # --- Exponential: closed forms ---
        ({}, ["Round", ["CDF", ["ExponentialDistribution", 2], 1], 6], round(1 - math.exp(-2), 6)),
        (
            {},
            ["Round", ["Quantile", ["ExponentialDistribution", 2], ["CDF", ["ExponentialDistribution", 2], 3]], 6],
            3.0,
        ),
        # --- distribution referenced via a solver parameter, not inline ---
        ({"my_dist": ["NormalDistribution", 5, 2]}, ["CDF", "my_dist", 5], 0.5),
    ],
)
def test_distributions(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_distribution_domain_errors():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["PDF", ["NormalDistribution", 0, -1], 0])
    with pytest.raises(Exception):
        solver(["CDF", ["UniformDistribution", 5, 5], 0])
    with pytest.raises(Exception):
        solver(["Quantile", ["ExponentialDistribution", 0], 0.5])
    with pytest.raises(Exception):
        solver(["Quantile", ["NormalDistribution", 0, 1], 1.5])  # p out of [0,1]
    with pytest.raises(Exception):
        solver(["PDF", ["NotADistribution", 1, 2], 0])


def test_extract_variables_recurses_into_distribution_parameters():
    # Unlike Head/Tail/Hold, a distribution's own parameters are meant
    # to be evaluated later (by PDF/CDF/Quantile) - they should be
    # reported as free variables, not treated as opaque syntax.
    result = extract_variables(
        ["PDF", ["NormalDistribution", "mu", "sigma"], "x"], set(), set()
    )
    assert result == {"mu", "sigma", "x"}


@pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not available")
@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- CortexJS's own documented example ---
        ({}, ["Quantile", ["PoissonDistribution", 9], 0.95], 14),
        # --- discrete PDF/CDF, closed-form cross-checks ---
        ({}, ["Round", ["PDF", ["PoissonDistribution", 3], 2], 8], round(math.exp(-3) * 3**2 / 2, 8)),
        (
            {},
            ["Round", ["CDF", ["BinomialDistribution", 10, 0.3], 3], 8],
            round(sum(math.comb(10, i) * 0.3**i * 0.7 ** (10 - i) for i in range(4)), 8),
        ),
        # --- large n/k: the naive formula overflows a float here; the
        # log-space/regularized-incomplete-function implementation
        # must not ---
        ({}, ["Round", ["PDF", ["BinomialDistribution", 10000, 0.5], 5000], 6], 0.007979),
        ({}, ["Round", ["CDF", ["BinomialDistribution", 10000, 0.5], 5000], 6], 0.503989),
    ],
)
def test_scipy_gated_discrete_distributions(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


@pytest.mark.skipif(not SCIPY_AVAILABLE, reason="scipy not available")
def test_discrete_pdf_works_without_scipy_but_cdf_and_quantile_do_not():
    import mathjson_solver._statistics_constructs as stats_mod

    original = stats_mod.SCIPY_AVAILABLE
    try:
        stats_mod.SCIPY_AVAILABLE = False
        solver = create_solver({})
        # PDF has no scipy dependency at all - must still work.
        assert solver(["PDF", ["BinomialDistribution", 10, 0.3], 3]) == pytest.approx(
            math.comb(10, 3) * 0.3**3 * 0.7**7
        )
        with pytest.raises(Exception):
            solver(["CDF", ["BinomialDistribution", 10, 0.3], 3])
        with pytest.raises(Exception):
            solver(["Quantile", ["PoissonDistribution", 9], 0.95])
    finally:
        stats_mod.SCIPY_AVAILABLE = original
