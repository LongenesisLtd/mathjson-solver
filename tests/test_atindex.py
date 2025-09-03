import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        (
            {"test_array": ["Array", 10, 20, 30, 40, 50, 60]},
            ["AtIndex", "test_array", 2],
            30,
        ),
        (
            {"test_array": ["Array", 10, 20, ["Sum", 30, 1], 40, 50, 60]},
            ["AtIndex", "test_array", 2],
            31,
        ),
    ],
)
def test_atindex1(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
