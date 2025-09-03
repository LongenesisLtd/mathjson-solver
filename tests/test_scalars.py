import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        (
            {"test_array": ["Array", 2, 3, 4]},
            ["MultiplyByScalar", "test_array", 5],
            ["Array", 10, 15, 20],
        ),
        (
            {"l1": ["Array", 2, 3, 4], "l2": ["Array", 1, 2, 3]},
            ["MultiplyByArray", "l1", "l2"],
            ["Array", 2, 6, 12],
        ),
        (
            {"test_array": ["Array", 2, 3, 4]},
            ["AddScalar", "test_array", 1],
            ["Array", 3, 4, 5],
        ),
        (
            {"test_array": ["Array", 2, 3, 4]},
            ["SubtractScalar", "test_array", 1],
            ["Array", 1, 2, 3],
        ),
        (
            {"l1": ["Array", 2, 3, 4], "l2": ["Array", 1, 2, 3]},
            ["AddArray", "l1", "l2"],
            ["Array", 3, 5, 7],
        ),
        (
            {"l1": ["Array", 2, 3, 4], "l2": ["Array", 1, 2, 7]},
            ["SubtractArray", "l1", "l2"],
            ["Array", 1, 1, -3],
        ),

    ],
)
def test_scalars1(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
