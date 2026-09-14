"""
Descriptive-statistics and regression constructs.
"""

from statistics import (
    correlation,
    covariance,
    mode,
    pstdev,
    pvariance,
    quantiles,
    stdev,
    variance,
)
from ._construct_shared import _arr_vals, _arr_vals_of

# Hard cap on PolynomialFit's degree - the normal-equations system it
# builds is (degree+1) x (degree+1), solved by O(degree^3) Gaussian
# elimination, so an unbounded user-supplied degree is a compute-cost
# vector the same way an unbounded string length is above.
_MAX_POLYFIT_DEGREE = 50


def Variance(f, c, solver_parameters, s):
    return variance(_arr_vals(f, c, solver_parameters, s))


def StandardDeviation(f, c, solver_parameters, s):
    return stdev(_arr_vals(f, c, solver_parameters, s))


def PopulationVariance(f, c, solver_parameters, s):
    return pvariance(_arr_vals(f, c, solver_parameters, s))


def PopulationStandardDeviation(f, c, solver_parameters, s):
    return pstdev(_arr_vals(f, c, solver_parameters, s))


def Mode(f, c, solver_parameters, s):
    """
    ["Mode", array]
    The most frequently occurring value. Ties go to whichever
    value appears first in `array` (matching Python's
    `statistics.mode`).
    """
    return mode(_arr_vals(f, c, solver_parameters, s))


def Quartiles(f, c, solver_parameters, s):
    """
    ["Quartiles", array]
    The three points (Q1, Q2/median, Q3) that divide `array`
    into four equal-sized groups, using
    `statistics.quantiles`' default ("exclusive") method.
    """
    return ["Array"] + quantiles(_arr_vals(f, c, solver_parameters, s), n=4)


def InterquartileRange(f, c, solver_parameters, s):
    """
    ["InterquartileRange", array]
    Q3 - Q1.
    """
    q1, _, q3 = quantiles(_arr_vals(f, c, solver_parameters, s), n=4)
    return q3 - q1


def Covariance(f, c, solver_parameters, s):
    """
    ["Covariance", array1, array2]
    Sample covariance of two equal-length collections.
    """
    return covariance(
        _arr_vals_of(f, c, solver_parameters, s[1]),
        _arr_vals_of(f, c, solver_parameters, s[2]),
    )


def Correlation(f, c, solver_parameters, s):
    """
    ["Correlation", array1, array2]
    The Pearson correlation coefficient of two equal-length
    collections.
    """
    return correlation(
        _arr_vals_of(f, c, solver_parameters, s[1]),
        _arr_vals_of(f, c, solver_parameters, s[2]),
    )


def Skewness(f, c, solver_parameters, s):
    """
    ["Skewness", array]
    Sample skewness (the adjusted Fisher-Pearson standardized
    moment coefficient - matches Excel's SKEW and
    scipy.stats.skew(..., bias=False)): a measure of the
    asymmetry of the data's distribution. Requires at least
    3 data points.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    n = len(vals)
    if n < 3:
        raise ValueError("'Skewness' requires at least 3 data points.")
    m = sum(vals) / n
    s_dev = stdev(vals)
    if s_dev == 0:
        raise ValueError("'Skewness' is undefined when all values are equal.")
    m3 = sum((x - m) ** 3 for x in vals) / n
    return (n**2 / ((n - 1) * (n - 2))) * m3 / s_dev**3


def Kurtosis(f, c, solver_parameters, s):
    """
    ["Kurtosis", array]
    Sample excess kurtosis (the adjusted Fisher-Pearson
    estimator - matches Excel's KURT and
    scipy.stats.kurtosis(..., bias=False, fisher=True)): a
    measure of the "tailedness" of the data's distribution
    (0 for a normal distribution). Requires at least 4 data
    points.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    n = len(vals)
    if n < 4:
        raise ValueError("'Kurtosis' requires at least 4 data points.")
    m = sum(vals) / n
    m2 = sum((x - m) ** 2 for x in vals) / n
    m4 = sum((x - m) ** 4 for x in vals) / n
    if m2 == 0:
        raise ValueError("'Kurtosis' is undefined when all values are equal.")
    g2 = m4 / m2**2 - 3
    return ((n - 1) / ((n - 2) * (n - 3))) * ((n + 1) * g2 + 6)


def LinearRegression(f, c, solver_parameters, s):
    """
    ["LinearRegression", x_array, y_array]
    The least-squares linear fit y = slope*x + intercept,
    returned as ["Array", slope, intercept].
    """
    x = _arr_vals_of(f, c, solver_parameters, s[1])
    y = _arr_vals_of(f, c, solver_parameters, s[2])
    if len(x) != len(y):
        raise ValueError("Both arrays must be of the same length.")
    n = len(x)
    if n < 2:
        raise ValueError("'LinearRegression' requires at least 2 data points.")
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    sxx = sum((xi - mx) ** 2 for xi in x)
    if sxx == 0:
        raise ValueError("'LinearRegression' is undefined when all x values are equal.")
    slope = sxy / sxx
    intercept = my - slope * mx
    return ["Array", slope, intercept]


def _solve_linear_system(f, c, solver_parameters, matrix, vector):
    """
    Solves `matrix @ x = vector` via Gaussian elimination
    with partial pivoting - a pure-Python solver (no numpy
    dependency) for the small, dense normal-equations system
    `PolynomialFit` builds. Less numerically stable than a
    QR-based solver for high degrees or badly-scaled data,
    but exact enough for the modest degrees this is capped
    at. Raises ValueError if the system is singular.
    """
    n = len(matrix)
    rows = [list(row) + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(rows[r][col]))
        if abs(rows[pivot][col]) < 1e-12:
            raise ValueError(
                "System is singular - check for duplicate x values "
                "or too few distinct points for the requested degree."
            )
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for r in range(n):
            if r != col:
                factor = rows[r][col] / rows[col][col]
                for cc in range(col, n + 1):
                    rows[r][cc] -= factor * rows[col][cc]
    return [rows[i][n] / rows[i][i] for i in range(n)]


def PolynomialFit(f, c, solver_parameters, s):
    """
    ["PolynomialFit", x_array, y_array, degree]
    The least-squares polynomial fit of the given `degree`
    (0 to _MAX_POLYFIT_DEGREE), via the normal equations
    solved with Gaussian elimination - no numpy dependency,
    but less numerically stable for high degrees or
    badly-scaled x values than a QR-based solver (e.g.
    numpy.polyfit) would be; keep degrees modest for
    well-conditioned results. Returns
    ["Array", c0, c1, ..., cd] representing
    `c0 + c1*x + c2*x^2 + ... + cd*x^d` (lowest degree
    first - the opposite order from numpy.polyfit).
    """
    x = _arr_vals_of(f, c, solver_parameters, s[1])
    y = _arr_vals_of(f, c, solver_parameters, s[2])
    if len(x) != len(y):
        raise ValueError("Both arrays must be of the same length.")
    degree = int(f(s[3], c))
    if not (0 <= degree <= _MAX_POLYFIT_DEGREE):
        raise ValueError(
            f"'PolynomialFit' degree must be between 0 and " f"{_MAX_POLYFIT_DEGREE}."
        )
    if len(x) < degree + 1:
        raise ValueError("'PolynomialFit' needs at least degree + 1 data points.")
    power_sums = [sum(xi**k for xi in x) for k in range(2 * degree + 1)]
    matrix = [[power_sums[i + j] for j in range(degree + 1)] for i in range(degree + 1)]
    vector = [sum((xi**k) * yi for xi, yi in zip(x, y)) for k in range(degree + 1)]
    return ["Array"] + _solve_linear_system(f, c, solver_parameters, matrix, vector)
