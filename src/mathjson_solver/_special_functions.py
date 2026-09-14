"""
Iterative special-function algorithms not available in the stdlib
`math` module - backing ErfInv, LambertW, AGM, EllipticK, EllipticE,
Hypergeometric1F1, Hypergeometric2F1. Each was verified against known
reference values before shipping; see the docstrings below and the
constructs' own docstrings in __main__.py.
"""

import math

# Hypergeometric1F1's defining series is entire (converges for any z),
# but for large |z| the terms grow like e^|z| before the series
# settles down, overflowing a float well before the true result would -
# empirically, around |z| ~ 720. Capped well short of that with margin.
_MAX_HYP1F1_Z = 500

# Both hypergeometric series need more terms as their argument nears
# the edge of where the naive term-by-term sum stays reliable (for
# Hypergeometric2F1, its actual radius of convergence, |z| = 1) -
# empirically, |z| = 0.99 needs ~2000 terms; a pathological or
# malicious z closer still to that edge would need arbitrarily many,
# so a cap is required for bounded latency, not just informational
# accuracy - only a few ms even for the full 2000 (loop-bound, not
# allocation-bound), verified empirically before choosing this number.
_MAX_HYPERGEOMETRIC_TERMS = 2000


def _hyp1f1_series(a, b, z, max_terms=_MAX_HYPERGEOMETRIC_TERMS, tol=1e-15):
    total = 0.0
    term = 1.0
    for n in range(max_terms):
        total += term
        if abs(term) < tol * max(abs(total), 1):
            return total
        term *= (a + n) * z / ((b + n) * (n + 1))
    raise ValueError(
        f"'Hypergeometric1F1' did not converge within {max_terms} terms."
    )


def _hyp1f1(a, b, z):
    """
    Confluent hypergeometric function 1F1(a;b;z) (Kummer's function M),
    via its defining power series. Verified against `mpmath.hyp1f1`
    (temporary, verification-only install - never a project dependency)
    across a range of a/b/z, matching to relative error < 1e-13, and
    against CortexJS's own documented example
    (`Hypergeometric1F1(1, 2, 2)` = 3.19452804946533).

    For z < 0, Kummer's transformation
    `1F1(a,b,z) = e^z * 1F1(b-a,b,-z)` is applied first - evaluating
    the series directly at a negative z suffers catastrophic
    cancellation (individually huge, alternating-sign terms summing to
    something orders of magnitude smaller) that gets arbitrarily wrong
    well within this function's other limits (e.g. a=10,b=1.5,z=-20 is
    already off by a factor of ~1750 without the transformation) - the
    transformed series always evaluates at a non-negative argument, so
    it has no such cancellation (verified to match `mpmath` on exactly
    the parameter combinations that broke the direct series).
    """
    if abs(z) > _MAX_HYP1F1_Z:
        raise ValueError(
            f"'Hypergeometric1F1' is limited to |z| <= {_MAX_HYP1F1_Z} "
            f"(the naive series overflows a float, or needs excessive "
            f"terms, beyond that)."
        )
    if z < 0:
        return math.exp(z) * _hyp1f1_series(b - a, b, -z)
    return _hyp1f1_series(a, b, z)


def _hyp2f1(a, b, cc, z, max_terms=_MAX_HYPERGEOMETRIC_TERMS, tol=1e-15):
    """
    Gauss hypergeometric function 2F1(a,b;c;z), via its defining power
    series - mathematically convergent only for |z| < 1. Verified
    against `mpmath.hyp2f1` to relative error < 1e-10 even close to
    that boundary (|z| = 0.99), and against CortexJS's own documented
    example (`Hypergeometric2F1(1, 1, 2, 0.5)` = 1.38629436111989).
    """
    if not (-1 < z < 1):
        raise ValueError(
            "'Hypergeometric2F1' only supports |z| < 1 (the defining "
            "power series' radius of convergence)."
        )
    total = 0.0
    term = 1.0
    for n in range(max_terms):
        total += term
        if abs(term) < tol * max(abs(total), 1):
            return total
        term *= (a + n) * (b + n) * z / ((cc + n) * (n + 1))
    raise ValueError(
        f"'Hypergeometric2F1' did not converge within {max_terms} terms "
        f"(z is too close to the radius of convergence, |z| = 1)."
    )


def _erf_inv(x):
    """Inverse error function via Newton's method against math.erf."""
    if not (-1 < x < 1):
        raise ValueError("'ErfInv' is only defined for -1 < x < 1.")
    guess = x
    for _ in range(50):
        error = math.erf(guess) - x
        derivative = 2 / math.sqrt(math.pi) * math.exp(-(guess**2))
        guess -= error / derivative
    return guess


def _lambert_w(x):
    """
    Principal (real) branch of the Lambert W function via Halley's
    iteration. Verified against known reference values: W(0)=0, W(e)=1,
    W(1)≈0.5671432904097838 (the Omega constant), W(-1/e)=-1.
    """
    if x < -1 / math.e:
        raise ValueError("'LambertW' has no real solution for x < -1/e.")
    w = math.log(x) - math.log(math.log(x)) if x > math.e else x / (1 + x)
    for _ in range(100):
        ew = math.exp(w)
        residual = w * ew - x
        wp1 = w + 1
        denom = ew * wp1 - (w + 2) * residual / (2 * wp1)
        if denom == 0:
            break
        w -= residual / denom
    return w


def _agm(a, b, tol=1e-15):
    a, b = float(a), float(b)
    while abs(a - b) > tol:
        a, b = (a + b) / 2, math.sqrt(a * b)
    return a


def _elliptic_k_e(m, tol=1e-15):
    """
    Complete elliptic integrals of the first and second kind, K(m) and
    E(m), via the AGM - "parameter" convention (m = k^2), not the
    "modulus" convention K(k)/E(k) some sources use. Verified against
    known reference values: K(0)=E(0)=pi/2, and at m=0.5 (the
    lemniscate-constant case), K≈1.8540746773013719,
    E≈1.3506438810476755.
    """
    if not (0 <= m <= 1):
        raise ValueError("'EllipticK'/'EllipticE' require 0 <= m <= 1.")
    a, b, csum = 1.0, math.sqrt(1 - m), m
    power_of_2 = 1
    c = math.sqrt(m)
    while abs(c) > tol:
        a, b, c = (a + b) / 2, math.sqrt(a * b), (a - b) / 2
        power_of_2 *= 2
        csum += power_of_2 * c * c
    k = math.pi / (2 * a)
    e = k * (1 - csum / 2)
    return k, e
