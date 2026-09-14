"""
Iterative special-function algorithms not available in the stdlib
`math` module - backing ErfInv, LambertW, AGM, EllipticK, EllipticE.
Each was verified against known reference values before shipping; see
the docstrings below and the constructs' own docstrings in __main__.py.
"""

import math


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
