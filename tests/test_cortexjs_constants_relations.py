import sys
import os
import math
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- Constants ---
        ({}, ["MachineEpsilon"], sys.float_info.epsilon),
        ({}, ["Round", ["CatalanConstant"], 5], 0.91597),
        ({}, ["Round", ["EulerGamma"], 5], 0.57722),
        # --- IdenticallyEqual: same type *and* same value ---
        ({}, ["IdenticallyEqual", 1, 1], True),
        ({}, ["IdenticallyEqual", 1, 1.0], False),
        ({}, ["IdenticallyEqual", "a", "a"], True),
        ({}, ["IdenticallyEqual", "1", 1], False),
        # --- StrictEqual doesn't care about type, for contrast ---
        ({}, ["StrictEqual", 1, 1.0], True),
        # --- Congruent: a ≡ b (mod m) ---
        ({}, ["Congruent", 7, 2, 5], True),
        ({}, ["Congruent", 7, 3, 5], False),
        ({}, ["Congruent", -1, 4, 5], True),
        # --- Rational: evaluates like Divide ---
        ({}, ["Rational", 3, 4], 0.75),
        ({}, ["Round", ["Rational", 1, 3], 5], 0.33333),
        # --- Numerator/Denominator: exact when reading a Rational node directly ---
        ({}, ["Numerator", ["Rational", 3, 4]], 3),
        ({}, ["Denominator", ["Rational", 3, 4]], 4),
        ({}, ["Numerator", ["Rational", 6, 8]], 6),  # not reduced - read verbatim
        ({}, ["Denominator", ["Rational", 6, 8]], 8),
        # --- Numerator/Denominator: plain integers have denominator 1 ---
        ({}, ["Numerator", 5], 5),
        ({}, ["Denominator", 5], 1),
        # --- Numerator/Denominator: best-effort reconstruction from a float ---
        ({}, ["Numerator", 0.75], 3),
        ({}, ["Denominator", 0.75], 4),
    ],
)
def test_cortexjs_constants_and_relations(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
