import sys
import os
import math
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver, translate_v1_mathjson


@pytest.mark.parametrize(
    "expression, expected_translation",
    [
        # The only rewrite: legacy 1-arg ["Log", x] -> ["Ln", x].
        (["Log", 8], ["Ln", 8]),
        (["Log", "x"], ["Ln", "x"]),
        # Nested occurrences are rewritten too.
        (["Add", ["Log", 8], 1], ["Add", ["Ln", 8], 1]),
        (["Log", ["Log", 8]], ["Ln", ["Ln", 8]]),
        # The 2.x 2-arg form is left alone (it never existed pre-2.0.0, so a
        # legacy expression can never contain it).
        (["Log", 8, 2], ["Log", 8, 2]),
        # Everything else passes through unchanged.
        (["Add", 1, 2], ["Add", 1, 2]),
        (5, 5),
        ("x", "x"),
        ([], []),
    ],
)
def test_translate_v1_mathjson(expression, expected_translation):
    assert translate_v1_mathjson(expression) == expected_translation


def test_translate_v1_mathjson_does_not_mutate_input():
    expression = ["Add", ["Log", 8], 1]
    original = ["Add", ["Log", 8], 1]
    translate_v1_mathjson(expression)
    assert expression == original


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, ["Log", 8], math.log(8)),
        ({}, ["Add", ["Log", 8], 1], math.log(8) + 1),
        # New (2.x-only) functions remain usable alongside legacy expressions.
        ({}, ["Product", ["Array", 2, 3, 4]], 24),
    ],
)
def test_create_solver_legacy_v1_mode(parameters, expression, expected_result):
    solver = create_solver(parameters, legacy_v1=True)
    assert solver(expression) == pytest.approx(expected_result)


def test_create_solver_legacy_v1_mode_matches_pre_2_0_0_log_semantics():
    # Pre-2.0.0, ["Log", x] was always natural log - the exact behavior
    # legacy_v1=True must reproduce for existing expressions.
    solver = create_solver({}, legacy_v1=True)
    assert solver(["Log", 8]) == pytest.approx(math.log(8))


def test_create_solver_non_legacy_v1_mode_uses_2_x_log_semantics():
    # Without legacy_v1=True, current (2.x) semantics apply: base 10.
    solver = create_solver({})
    assert solver(["Log", 1000]) == pytest.approx(3)


def test_create_solver_legacy_v1_mode_with_parameter_reference():
    # The translation happens on the whole expression tree up front, so a
    # ["Log", x] whose argument is a solver parameter (not a literal) is
    # rewritten and resolved correctly too.
    solver = create_solver({"x": 8}, legacy_v1=True)
    assert solver(["Log", "x"]) == pytest.approx(math.log(8))
