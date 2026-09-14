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
        # Skewness/Kurtosis on the same shared dataset, verified against
        # scipy.stats.skew(bias=False)/kurtosis(bias=False, fisher=True).
        (
            {},
            ["Round", ["Skewness", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3],
            0.818,
        ),
        (
            {},
            ["Round", ["Kurtosis", ["Array", 2, 4, 4, 4, 5, 5, 7, 9]], 3],
            0.941,
        ),
        (
            {},
            ["LinearRegression", ["Array", 1, 2, 3, 4, 5], ["Array", 3, 5, 7, 9, 11]],
            ["Array", 2.0, 1.0],  # y = 2x + 1, exact
        ),
    ],
)
def test_cortexjs_statistics(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


@pytest.mark.parametrize(
    "x, y, degree, expected_coeffs",
    [
        # y = 2x + 1, degree 1 - matches LinearRegression above, reversed
        # coefficient order (PolynomialFit is lowest-degree-first).
        ([1, 2, 3, 4, 5], [3, 5, 7, 9, 11], 1, [1.0, 2.0]),
        # y = x^2 + 2x + 3, exact quadratic.
        ([0, 1, 2, 3, 4], [3, 6, 11, 18, 27], 2, [3.0, 2.0, 1.0]),
        # Verified independently against numpy.polyfit (reversed order).
        (
            [-2, -1, 0, 1, 2, 3, 4],
            [-10, -1, 2, 1, 6, 29, 82],
            3,
            [1.238095238095199, -2.206349206349206, -0.8809523809523798, 1.6111111111111107],
        ),
    ],
)
def test_polynomial_fit(x, y, degree, expected_coeffs):
    solver = create_solver({})
    result = solver(["PolynomialFit", ["Array"] + x, ["Array"] + y, degree])
    assert result == pytest.approx(["Array"] + expected_coeffs)


def test_skewness_requires_at_least_three_points():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Skewness", ["Array", 1, 2]])


def test_kurtosis_requires_at_least_four_points():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Kurtosis", ["Array", 1, 2, 3]])


def test_linear_regression_requires_at_least_two_points():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["LinearRegression", ["Array", 1], ["Array", 2]])


def test_linear_regression_rejects_constant_x():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["LinearRegression", ["Array", 5, 5, 5], ["Array", 1, 2, 3]])


def test_polynomial_fit_rejects_negative_degree():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["PolynomialFit", ["Array", 1, 2, 3], ["Array", 1, 2, 3], -1])


def test_polynomial_fit_rejects_excessive_degree():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["PolynomialFit", ["Array", 1, 2, 3], ["Array", 1, 2, 3], 51])


def test_polynomial_fit_requires_enough_points_for_degree():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["PolynomialFit", ["Array", 1, 2], ["Array", 1, 2], 3])


def test_covariance_requires_equal_length_arrays():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Covariance", ["Array", 1, 2, 3], ["Array", 1, 2]])


def test_covariance_requires_at_least_two_points():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Covariance", ["Array", 1], ["Array", 2]])
