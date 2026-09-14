"""
Descriptive-statistics and regression constructs, plus probability
distributions (NormalDistribution, ..., PDF, CDF, Quantile).
"""

import math
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
from ._special_functions import _erf_inv

SCIPY_AVAILABLE = False
try:
    from scipy import special as _scipy_special

    SCIPY_AVAILABLE = True
except ImportError:
    pass


def _require_scipy():
    if not SCIPY_AVAILABLE:
        raise ImportError(
            "'CDF'/'Quantile' on a BinomialDistribution or "
            "PoissonDistribution require 'scipy' (PDF does not). "
            "Install with 'pip install scipy' (or 'pip install "
            "mathjson-solver[special-functions]')."
        )


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


# --- Probability distributions ---
#
# NormalDistribution/BinomialDistribution/PoissonDistribution/
# UniformDistribution/ExponentialDistribution are "markers", the same
# self-quoting pattern already used for Function/Hold: they just
# return their own unevaluated expression. PDF/CDF/Quantile resolve
# and dispatch on that expression themselves. This means a
# distribution's parameters (e.g. ["NormalDistribution", "mu",
# "sigma"]) are still treated as ordinary sub-expressions by
# extract_variables - unlike Head/Tail/Hold, they're meant to be
# evaluated later by whichever query function unpacks them, not held
# opaque forever, so no special-casing is needed there.


def NormalDistribution(f, c, solver_parameters, s):
    return s


def BinomialDistribution(f, c, solver_parameters, s):
    return s


def PoissonDistribution(f, c, solver_parameters, s):
    return s


def UniformDistribution(f, c, solver_parameters, s):
    return s


def ExponentialDistribution(f, c, solver_parameters, s):
    return s


def _normal_pdf(mu, sigma, x):
    if sigma <= 0:
        raise ValueError("'NormalDistribution' requires standard deviation > 0.")
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def _normal_cdf(mu, sigma, x):
    if sigma <= 0:
        raise ValueError("'NormalDistribution' requires standard deviation > 0.")
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def _normal_quantile(mu, sigma, p):
    if sigma <= 0:
        raise ValueError("'NormalDistribution' requires standard deviation > 0.")
    return mu + sigma * math.sqrt(2) * _erf_inv(2 * p - 1)


def _uniform_pdf(a, b, x):
    if not a < b:
        raise ValueError("'UniformDistribution' requires a < b.")
    return 1 / (b - a) if a <= x <= b else 0.0


def _uniform_cdf(a, b, x):
    if not a < b:
        raise ValueError("'UniformDistribution' requires a < b.")
    if x < a:
        return 0.0
    if x > b:
        return 1.0
    return (x - a) / (b - a)


def _uniform_quantile(a, b, p):
    if not a < b:
        raise ValueError("'UniformDistribution' requires a < b.")
    return a + p * (b - a)


def _exponential_pdf(lam, x):
    if lam <= 0:
        raise ValueError("'ExponentialDistribution' requires lambda > 0.")
    return lam * math.exp(-lam * x) if x >= 0 else 0.0


def _exponential_cdf(lam, x):
    if lam <= 0:
        raise ValueError("'ExponentialDistribution' requires lambda > 0.")
    return 1 - math.exp(-lam * x) if x >= 0 else 0.0


def _exponential_quantile(lam, p):
    if lam <= 0:
        raise ValueError("'ExponentialDistribution' requires lambda > 0.")
    return -math.log(1 - p) / lam


def _binomial_pdf(n, p, k):
    """
    P(X=k) for Binomial(n,p), via a log-space reformulation - the
    direct formula (math.comb(n,k) * p**k * (1-p)**(n-k)) overflows a
    float for even moderately large n (verified: n=10,000 already
    raises OverflowError converting math.comb's huge intermediate
    integer to float), well within a realistic input range.
    """
    n = int(n)
    if not (0 <= p <= 1):
        raise ValueError("'BinomialDistribution' requires 0 <= p <= 1.")
    k = int(k)
    if k < 0 or k > n:
        return 0.0
    log_pdf = (
        math.lgamma(n + 1)
        - math.lgamma(k + 1)
        - math.lgamma(n - k + 1)
        + k * math.log(p)
        + (n - k) * math.log(1 - p)
    )
    return math.exp(log_pdf)


def _poisson_pdf(lam, k):
    """Same log-space reasoning as `_binomial_pdf` - math.factorial(k) overflows for large k."""
    if lam <= 0:
        raise ValueError("'PoissonDistribution' requires lambda > 0.")
    k = int(k)
    if k < 0:
        return 0.0
    return math.exp(-lam + k * math.log(lam) - math.lgamma(k + 1))


def _binomial_cdf(n, p, k):
    """
    P(X<=k) for Binomial(n,p), via the regularized incomplete beta
    identity I_(1-p)(n-k, k+1) - verified against direct summation to
    machine precision, and far more numerically robust for large n
    (direct summation both overflows and is measurably slower well
    before this identity's cost grows at all).
    """
    _require_scipy()
    n = int(n)
    if not (0 <= p <= 1):
        raise ValueError("'BinomialDistribution' requires 0 <= p <= 1.")
    k = int(math.floor(k))
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return _scipy_special.betainc(n - k, k + 1, 1 - p)


def _poisson_cdf(lam, k):
    """P(X<=k) for Poisson(lambda), via Q(k+1, lambda) - see `_binomial_cdf`."""
    _require_scipy()
    if lam <= 0:
        raise ValueError("'PoissonDistribution' requires lambda > 0.")
    k = int(math.floor(k))
    if k < 0:
        return 0.0
    return _scipy_special.gammaincc(k + 1, lam)


def _discrete_quantile(cdf_fn, p):
    """
    Smallest non-negative integer k such that cdf_fn(k) >= p, via
    doubling then bisecting (same pattern as `_is_figurate` in
    _number_theory.py) - robust for arbitrarily large true quantiles
    without assuming where they'll land, unlike a linear scan from 0.
    """
    if cdf_fn(0) >= p:
        return 0
    lo, hi = 0, 1
    while cdf_fn(hi) < p:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if cdf_fn(mid) < p:
            lo = mid + 1
        else:
            hi = mid
    return lo


def PDF(f, c, solver_parameters, s):
    """["PDF", distribution, x] - probability density (or mass) function."""
    dist = f(s[1], c)
    x = f(s[2], c)
    name = dist[0]
    if name == "NormalDistribution":
        return _normal_pdf(f(dist[1], c), f(dist[2], c), x)
    if name == "UniformDistribution":
        return _uniform_pdf(f(dist[1], c), f(dist[2], c), x)
    if name == "ExponentialDistribution":
        return _exponential_pdf(f(dist[1], c), x)
    if name == "BinomialDistribution":
        return _binomial_pdf(f(dist[1], c), f(dist[2], c), x)
    if name == "PoissonDistribution":
        return _poisson_pdf(f(dist[1], c), x)
    raise ValueError(f"'PDF' does not support distribution '{name}'.")


def CDF(f, c, solver_parameters, s):
    """["CDF", distribution, x] - cumulative distribution function."""
    dist = f(s[1], c)
    x = f(s[2], c)
    name = dist[0]
    if name == "NormalDistribution":
        return _normal_cdf(f(dist[1], c), f(dist[2], c), x)
    if name == "UniformDistribution":
        return _uniform_cdf(f(dist[1], c), f(dist[2], c), x)
    if name == "ExponentialDistribution":
        return _exponential_cdf(f(dist[1], c), x)
    if name == "BinomialDistribution":
        return _binomial_cdf(f(dist[1], c), f(dist[2], c), x)
    if name == "PoissonDistribution":
        return _poisson_cdf(f(dist[1], c), x)
    raise ValueError(f"'CDF' does not support distribution '{name}'.")


def Quantile(f, c, solver_parameters, s):
    """["Quantile", distribution, p] - inverse CDF (0 <= p <= 1)."""
    dist = f(s[1], c)
    p = f(s[2], c)
    if not (0 <= p <= 1):
        raise ValueError("'Quantile' requires 0 <= p <= 1.")
    name = dist[0]
    if name == "NormalDistribution":
        return _normal_quantile(f(dist[1], c), f(dist[2], c), p)
    if name == "UniformDistribution":
        return _uniform_quantile(f(dist[1], c), f(dist[2], c), p)
    if name == "ExponentialDistribution":
        return _exponential_quantile(f(dist[1], c), p)
    if name == "BinomialDistribution":
        n, prob = f(dist[1], c), f(dist[2], c)
        return _discrete_quantile(lambda k: _binomial_cdf(n, prob, k), p)
    if name == "PoissonDistribution":
        lam = f(dist[1], c)
        return _discrete_quantile(lambda k: _poisson_cdf(lam, k), p)
    raise ValueError(f"'Quantile' does not support distribution '{name}'.")
