import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        (
            {
                "age_bounds": [
                    "Array",
                    0,
                    20,
                    25,
                    30,
                    35,
                    40,
                    45,
                    50,
                    55,
                    60,
                    65,
                    70,
                    75,
                    80,
                ]
            },
            ["FindIntervalIndex", "age_bounds", 42.5],
            5,
        ),
        (
            {
                "age_bounds": [
                    "Array",
                    0,
                    20,
                    25,
                    30,
                    35,
                    40,
                    45,
                    50,
                    55,
                    60,
                    65,
                    70,
                    75,
                    80,
                ]
            },
            ["FindIntervalIndex", "age_bounds", 20],
            1,
        ),
        (
            {
                "age_bounds": [
                    "Array",
                    0,
                    20,
                    25,
                    30,
                    35,
                    40,
                    45,
                    50,
                    55,
                    60,
                    65,
                    70,
                    75,
                    80,
                ]
            },
            ["FindIntervalIndex", "age_bounds", 39.9],
            4,
        ),
        (
            {
                "age_bounds": [
                    "Array",
                    0,
                    20,
                    25,
                    30,
                    35,
                    40,
                    45,
                    50,
                    55,
                    60,
                    65,
                    70,
                    75,
                    80,
                ]
            },
            ["FindIntervalIndex", "age_bounds", 80],
            12,
        ),
        (
            {
                "age_bounds": [
                    "Array",
                    0,
                    20,
                    25,
                    30,
                    35,
                    40,
                    45,
                    50,
                    55,
                    60,
                    65,
                    70,
                    75,
                    80,
                ]
            },
            ["FindIntervalIndex", "age_bounds", 75],
            12,
        ),
        (
            {
                "age_bounds": [
                    "Array",
                    0,
                    20,
                    25,
                    30,
                    35,
                    40,
                    45,
                    50,
                    55,
                    60,
                    65,
                    70,
                    75,
                    80,
                ]
            },
            ["FindIntervalIndex", "age_bounds", 40],
            5,
        ),
    ],
)
def test_solver_FindIntervalIndex(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
