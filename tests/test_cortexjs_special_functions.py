import sys
import os
import math
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- stdlib-based ---
        ({}, ["Gamma", 5], 24.0),  # Gamma(n) = (n-1)!
        ({}, ["Round", ["GammaLn", 5], 6], round(math.lgamma(5), 6)),
        # --- built on Gamma ---
        (
            {},
            ["Round", ["Beta", 2, 3], 6],
            round(math.gamma(2) * math.gamma(3) / math.gamma(5), 6),
        ),
        ({}, ["Factorial2", 7], 105),  # 7*5*3*1
        ({}, ["Factorial2", 8], 384),  # 8*6*4*2
        # --- verified iterative algorithms ---
        ({}, ["Round", ["ErfInv", 0.5], 8], round(0.4769362762044699, 8)),
        ({}, ["Round", ["LambertW", 0], 10], 0.0),
        ({}, ["Round", ["LambertW", math.e], 10], 1.0),
        ({}, ["Round", ["LambertW", 1], 10], round(0.5671432904097838, 10)),
        ({}, ["Round", ["LambertW", -1 / math.e], 5], -1.0),
        ({}, ["Round", ["AGM", 1, 1], 10], 1.0),
        ({}, ["Round", ["AGM", 1, 2], 10], round(1.4567910310469068, 10)),
        ({}, ["Round", ["EllipticK", 0], 10], round(math.pi / 2, 10)),
        ({}, ["Round", ["EllipticE", 0], 10], round(math.pi / 2, 10)),
        (
            {},
            ["Round", ["EllipticK", 0.5], 10],
            round(1.8540746773013719, 10),
        ),
        (
            {},
            ["Round", ["EllipticE", 0.5], 10],
            round(1.3506438810476755, 10),
        ),
    ],
)
def test_special_functions(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_erf_inv_rejects_out_of_domain():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["ErfInv", 1])
    with pytest.raises(Exception):
        solver(["ErfInv", -1])


def test_lambert_w_rejects_below_branch_point():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["LambertW", -1])


def test_elliptic_functions_reject_out_of_domain():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["EllipticK", -0.5])
    with pytest.raises(Exception):
        solver(["EllipticK", 1.5])
