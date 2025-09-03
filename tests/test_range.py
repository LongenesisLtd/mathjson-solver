import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        (
            {},
            ["GenerateRange", 3],
            ["Array", 0, 1, 2],
        ),
        (
            {},
            ["GenerateRange", 0],
            ["Array"],
        ),
        (
            {},
            ["GenerateRange", 0, 3, 1],
            ["Array", 0, 1, 2],
        ),
        (
            {},
            ["GenerateRange", 0, 10, 2],
            ["Array", 0, 2, 4, 6, 8],
        ),

    ],
)
def test_scalars1(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
