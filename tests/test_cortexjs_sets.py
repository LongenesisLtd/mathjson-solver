import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- Union: variadic, dedup, first-appearance order across args ---
        (
            {},
            ["Union", ["Array", 1, 2, 3], ["Array", 2, 3, 4]],
            ["Array", 1, 2, 3, 4],
        ),
        (
            {},
            ["Union", ["Array", 1, 2], ["Array", 2, 3], ["Array", 3, 4]],
            ["Array", 1, 2, 3, 4],
        ),
        ({}, ["Union", ["Array", 1, 1, 2]], ["Array", 1, 2]),
        # --- Intersection: variadic, dedup, order from the first array ---
        (
            {},
            ["Intersection", ["Array", 1, 2, 3], ["Array", 2, 3, 4]],
            ["Array", 2, 3],
        ),
        (
            {},
            ["Intersection", ["Array", 1, 2, 3], ["Array", 2, 3], ["Array", 3, 4]],
            ["Array", 3],
        ),
        ({}, ["Intersection", ["Array", 1, 2], ["Array", 3, 4]], ["Array"]),
        # --- SetMinus: binary, dedup, order from array1 ---
        (
            {},
            ["SetMinus", ["Array", 1, 2, 3], ["Array", 2]],
            ["Array", 1, 3],
        ),
        (
            {},
            ["SetMinus", ["Array", 1, 1, 2], ["Array", 3]],
            ["Array", 1, 2],
        ),
        # --- SymmetricDifference: binary, array1's exclusives then array2's ---
        (
            {},
            ["SymmetricDifference", ["Array", 1, 2, 3], ["Array", 2, 3, 4]],
            ["Array", 1, 4],
        ),
        (
            {},
            ["SymmetricDifference", ["Array", 1, 2], ["Array", 1, 2]],
            ["Array"],
        ),
        # --- Element / NotElement: CortexJS names for In / Not_in ---
        ({}, ["Element", 2, ["Array", 1, 2, 3]], True),
        ({}, ["Element", 9, ["Array", 1, 2, 3]], False),
        ({}, ["NotElement", 9, ["Array", 1, 2, 3]], True),
        ({}, ["NotElement", 2, ["Array", 1, 2, 3]], False),
        # --- Element / Interval: range membership, CortexJS's own
        # convention for "x in [a, b]" (ce.parse("x \\in [0, 1]").json
        # == ["Element", "x", ["Interval", 0, 1]]) - closed by default,
        # ["Open", endpoint] to exclude that endpoint ---
        ({}, ["Element", 0.5, ["Interval", 0, 1]], True),
        ({}, ["Element", 1.5, ["Interval", 0, 1]], False),
        ({}, ["Element", 1, ["Interval", 0, 1]], True),  # closed: endpoint included
        ({}, ["Element", 0, ["Interval", 0, 1]], True),  # closed: endpoint included
        ({}, ["Element", 1, ["Interval", 0, ["Open", 1]]], False),  # [0, 1): excluded
        ({}, ["Element", 0, ["Interval", ["Open", 0], 1]], False),  # (0, 1]: excluded
        ({}, ["NotElement", 5, ["Interval", 0, 1]], True),
        ({"age": 45}, ["Element", "age", ["Interval", 40, 65]], True),
        # --- Subset / SubsetEqual / Superset / SupersetEqual / NotSubset / NotSuperset ---
        ({}, ["SubsetEqual", ["Array", 1, 2], ["Array", 1, 2, 3]], True),
        ({}, ["Subset", ["Array", 1, 2], ["Array", 1, 2, 3]], True),
        ({}, ["Subset", ["Array", 1, 2, 3], ["Array", 1, 2, 3]], False),  # equal, not proper
        ({}, ["SubsetEqual", ["Array", 1, 2, 3], ["Array", 1, 2, 3]], True),
        ({}, ["Superset", ["Array", 1, 2, 3], ["Array", 1, 2]], True),
        ({}, ["Superset", ["Array", 1, 2], ["Array", 1, 2]], False),  # equal, not proper
        ({}, ["SupersetEqual", ["Array", 1, 2], ["Array", 1, 2]], True),
        ({}, ["NotSubset", ["Array", 1, 2, 3], ["Array", 1, 2, 3]], True),  # equal
        ({}, ["NotSubset", ["Array", 1, 5], ["Array", 1, 2, 3]], True),  # not a subset at all
        ({}, ["NotSuperset", ["Array", 1, 2], ["Array", 1, 2]], True),  # equal
    ],
)
def test_cortexjs_set_algebra(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_element_rejects_unrecognized_domain():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Element", 5, ["NotADomain", 1, 2]])
