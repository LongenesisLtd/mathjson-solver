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
    ],
)
def test_cortexjs_set_algebra(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
