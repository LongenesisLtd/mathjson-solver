import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, ["Mode", ["Array", 1, 2, 2, 3]], 2),
        # Same dataset as the existing Variance/StandardDeviation tests,
        # contrasted with their population variants.
        (
            {},
            ["PopulationVariance", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]],
            4,
        ),
        (
            {},
            ["PopulationStandardDeviation", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]],
            2.0,
        ),
        (
            {},
            ["Quartiles", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]],
            ["Array", 4.0, 4.5, 6.5],
        ),
        (
            {},
            ["InterquartileRange", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]],
            2.5,
        ),
        (
            {},
            ["Covariance", ["Array", 1, 2, 3, 4, 5], ["Array", 2, 4, 6, 8, 10]],
            5.0,
        ),
        (
            {},
            [
                "Round",
                ["Correlation", ["Array", 1, 2, 3, 4, 5], ["Array", 2, 4, 6, 8, 10]],
                5,
            ],
            1.0,
        ),
        (
            {},
            [
                "Round",
                ["Correlation", ["Array", 1, 2, 3, 4, 5], ["Array", 5, 4, 3, 2, 1]],
                5,
            ],
            -1.0,
        ),
    ],
)
def test_cortexjs_statistics(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_covariance_requires_equal_length_arrays():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Covariance", ["Array", 1, 2, 3], ["Array", 1, 2]])


def test_covariance_requires_at_least_two_points():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Covariance", ["Array", 1], ["Array", 2]])
