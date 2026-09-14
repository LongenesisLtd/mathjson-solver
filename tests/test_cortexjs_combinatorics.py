import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, ["Choose", 5, 2], 10),  # same as the existing Binomial
        ({}, ["Binomial", 5, 2], 10),
        ({}, ["Fibonacci", 0], 0),
        ({}, ["Fibonacci", 1], 1),
        ({}, ["Fibonacci", 10], 55),
        ({}, ["Multinomial", ["Array", 2, 3, 4]], 1260),
        ({}, ["Subfactorial", 0], 1),
        ({}, ["Subfactorial", 4], 9),
        ({}, ["Subfactorial", 5], 44),
        ({}, ["BellNumber", 0], 1),
        ({}, ["BellNumber", 5], 52),
        ({}, ["BellNumber", 6], 203),
        # --- Enumeration functions (Tier 3.2): no output-size limit -
        # see test_blacklist.py for how a deployment disables these. ---
        (
            {},
            ["PowerSet", ["Array", 1, 2, 3]],
            [
                "Array",
                ["Array"],
                ["Array", 1],
                ["Array", 2],
                ["Array", 3],
                ["Array", 1, 2],
                ["Array", 1, 3],
                ["Array", 2, 3],
                ["Array", 1, 2, 3],
            ],
        ),
        ({}, ["PowerSet", ["Array"]], ["Array", ["Array"]]),
        (
            {},
            ["Permutations", ["Array", 1, 2, 3]],
            [
                "Array",
                ["Array", 1, 2, 3],
                ["Array", 1, 3, 2],
                ["Array", 2, 1, 3],
                ["Array", 2, 3, 1],
                ["Array", 3, 1, 2],
                ["Array", 3, 2, 1],
            ],
        ),
        (
            {},
            ["Permutations", ["Array", 1, 2, 3], 2],
            [
                "Array",
                ["Array", 1, 2],
                ["Array", 1, 3],
                ["Array", 2, 1],
                ["Array", 2, 3],
                ["Array", 3, 1],
                ["Array", 3, 2],
            ],
        ),
        (
            {},
            ["Combinations", ["Array", 1, 2, 3], 2],
            ["Array", ["Array", 1, 2], ["Array", 1, 3], ["Array", 2, 3]],
        ),
        (
            {},
            ["CartesianProduct", ["Array", 1, 2], ["Array", "a", "b"]],
            [
                "Array",
                ["Array", 1, "a"],
                ["Array", 1, "b"],
                ["Array", 2, "a"],
                ["Array", 2, "b"],
            ],
        ),
    ],
)
def test_combinatorics(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_subfactorial_rejects_negative():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Subfactorial", -1])


def test_bell_number_rejects_negative():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["BellNumber", -1])
