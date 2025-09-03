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
            ["Slice", "test_array", 2, 4],
            ["Array", 30, 40],
        ),
        (
            {"test_array": ["Array", 10, 20, 30, 40, 50, 60]},
            ["Slice", "test_array", 2, 5],
            ["Array", 30, 40, 50],
        ),
        (
            {"test_array": ["Array", 10, 20, 30, 40, 50, 60]},
            ["Length", ["Slice", "test_array", 2, 5]],
            3,
        ),
        (
            {"test_array": ["Array", 10, 20, 30, 40, 50, 60]},
            ["Sum", ["Slice", "test_array", 2, 5]],
            120,
        ),
    ],
)
def test_slice1(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
