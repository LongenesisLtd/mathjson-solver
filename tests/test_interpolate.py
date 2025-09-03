import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


def _create_Interpolate_test_cases():
    """Create test cases for Interpolate function."""
    test_cases = [
        # Basic linear interpolation
        (
            {},
            ["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 2.5],
            25,
        ),
        # Interpolation at the boundaries
        (
            {},
            ["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 1],
            10,
        ),
        (
            {},
            ["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 3],
            30,
        ),
        # # Extrapolation beyond the boundaries
        # (
        #     {},
        #     ["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 0],
        #     10,
        # ),
        # (
        #     {},
        #     ["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 4],
        #     30,
        # ),
        # Non-uniformly spaced x values
        (
            {},
            ["Interp", ["Array", 1, 3, 4], ["Array", 10, 30, 40], 2],
            20,
        ),
        # Interpolation with negative x values
        (
            {},
            ["Interp", ["Array", -1, 0, 1], ["Array", -10, 0, 10], -0.5],
            -5,
        ),
        # Interpolation with negative y values
        (
            {},
            ["Interp", ["Array", -1, 0, 1], ["Array", -10, -20, -30], -0.5],
            -15,
        ),
        # Interpolation with floating-point precision
        (
            {},
            [
                "Interp",
                ["Array", 0.1, 0.2, 0.3],
                ["Array", 1.1, 2.2, 3.3],
                0.25,
            ],
            2.75,
        ),
        # Interpolation with unsorted x values (should raise an error)
    ]
    return test_cases


@pytest.mark.parametrize(
    "parameters, expression, expected_result", _create_Interpolate_test_cases()
)
def test_interpolation(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
