import sys
import os
import math
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- Tier 1: aliases ---
        ({}, ["Log", 1000], 3),
        ({}, ["Log", 8, 2], 3),
        ({}, ["Lb", 8], 3),
        ({}, ["Lg", 1000], 3),
        ({}, ["List", 1, 2, 3], ["Array", 1, 2, 3]),
        ({}, ["Mean", ["Array", 2, 4, 6]], 4),
        ({}, ["Count", ["Array", 1, 2, 3]], 3),
        ({"x": 2}, ["Which", "x", 0, [1, "a"], [2, "b"]], "b"),
        # --- Tier 2: trivial new implementations ---
        ({}, ["Chop", 1e-12], 0),
        ({}, ["Chop", 5], 5),
        ({}, ["Mod", 7, 3], 1),
        ({}, ["Mod", -7, 3], 2),
        ({}, ["Clamp", 5, 0, 3], 3),
        ({}, ["Clamp", -5, 0, 3], 0),
        ({}, ["Clamp", 1.5], 1),
        ({}, ["Round", ["LogOnePlus", 0], 3], 0),
        ({}, ["GCD", 12, 18], 6),
        ({}, ["LCM", 4, 6], 12),
        ({}, ["Xor", True, False], True),
        ({}, ["Xor", True, True], False),
        ({}, ["Nand", True, True], False),
        ({}, ["Nand", True, False], True),
        ({}, ["Nor", False, False], True),
        ({}, ["Nor", True, False], False),
        ({}, ["Implies", True, False], False),
        ({}, ["Implies", False, False], True),
        ({}, ["Equivalent", True, True], True),
        ({}, ["Equivalent", True, False], False),
        ({}, ["Max", 5, 2, -1], 5),
        ({}, ["Min", 5, 2, -1], -1),
        ({}, ["Round", ["Sinh", 0], 3], 0),
        ({}, ["Round", ["Cosh", 0], 3], 1),
        ({}, ["Round", ["Hypot", 3, 4], 3], 5),
        ({}, ["Sinc", 0], 1.0),
        ({}, ["Round", ["Degrees"], 5], round(math.pi / 180, 5)),
        ({}, ["Round", ["ExponentialE"], 5], round(math.e, 5)),
        ({}, ["Round", ["GoldenRatio"], 5], round((1 + math.sqrt(5)) / 2, 5)),
        ({}, ["Factorial", 5], 120),
        ({}, ["Binomial", 5, 2], 10),
        ({}, ["IsPrime", 7], True),
        ({}, ["IsPrime", 8], False),
        ({}, ["Round", ["StandardDeviation", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3], 2.138),
        ({}, ["Round", ["Variance", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3], 4.571),
        ({}, ["Round", ["Erf", 1], 3], 0.843),
        ({}, ["First", ["Array", 1, 2, 3]], 1),
        ({}, ["Last", ["Array", 1, 2, 3]], 3),
        ({}, ["Rest", ["Array", 1, 2, 3]], ["Array", 2, 3]),
        ({}, ["Most", ["Array", 1, 2, 3]], ["Array", 1, 2]),
        ({}, ["Reverse", ["Array", 1, 2, 3]], ["Array", 3, 2, 1]),
        ({}, ["IsEmpty", ["Array"]], True),
        ({}, ["IsEmpty", ["Array", 1]], False),
        ({}, ["Range", 5], ["Array", 1, 2, 3, 4, 5]),
        ({}, ["Range", 2, 5], ["Array", 2, 3, 4, 5]),
        ({}, ["Range", 1, 10, 2], ["Array", 1, 3, 5, 7, 9]),
        ({}, ["Join", ["Array", 1, 2], ["Array", 3, 4]], ["Array", 1, 2, 3, 4]),
        (
            {},
            ["Unique", ["Array", 1, 2, 2, 3, 1]],
            ["Array", 1, 2, 3],
        ),
        ({}, ["Sort", ["Array", 3, 1, 2]], ["Array", 1, 2, 3]),
        (
            {},
            ["Zip", ["Array", 1, 2], ["Array", "a", "b"]],
            ["Array", ["Array", 1, "a"], ["Array", 2, "b"]],
        ),
        ({}, ["At", ["Array", 10, 20, 30], 1], 10),
        ({}, ["At", ["Array", 10, 20, 30], -1], 30),
    ],
)
def test_cortexjs_compat(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
