"""
Pure number-theory helpers, backing the Number Theory batch of
constructs (FactorInteger, Divisors, ExtendedGCD, BernoulliB, ...).

_is_prime, _factor_integer and _divisors are all trial-division based
(O(sqrt(n))) - fine for everyday inputs, but a ~15+ digit number makes
a single call noticeably slow (empirically: ~0.3s at 10**14, and it
grows with sqrt(n), so ~3s at 10**16, ~30s at 10**18). Every construct
built on them caps its integer input at _MAX_NUMBER_THEORY_MAGNITUDE to
keep worst-case latency low. `IsPrime`/`_is_prime` itself predates this
and has no such cap - a pre-existing gap, not introduced here; left
alone rather than silently changing already-shipped behavior.
"""

import math
from fractions import Fraction

_MAX_NUMBER_THEORY_MAGNITUDE = 10**12

# NthPrime/NextPrime search forward one candidate at a time; empirically
# NthPrime(10_000) ~ 0.1s and NthPrime(100_000) ~ 3.4s, so the *count*
# of primes to advance through needs its own (smaller) cap, separate
# from the starting-value magnitude cap above.
_MAX_NTH_PRIME = 10_000

# PrimePi checks every integer up to n, so its cost scales with n
# itself (not just sqrt(n)) - empirically ~0.1s at 100_000.
_MAX_PRIME_PI = 100_000


def _is_prime(n) -> bool:
    n = int(n)
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    return all(n % i for i in range(3, int(n**0.5) + 1, 2))


def _factor_integer(n):
    n = int(n)
    if n < 1:
        raise ValueError("Factorization requires a positive integer.")
    if n > _MAX_NUMBER_THEORY_MAGNITUDE:
        raise ValueError(
            f"Factorization is limited to integers up to "
            f"{_MAX_NUMBER_THEORY_MAGNITUDE} (trial division is too slow "
            f"beyond that)."
        )
    factors = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            exp = 0
            while n % d == 0:
                n //= d
                exp += 1
            factors.append((d, exp))
        d += 1
    if n > 1:
        factors.append((n, 1))
    return factors


def _divisors(n):
    n = int(n)
    if n < 1:
        raise ValueError("Divisors requires a positive integer.")
    if n > _MAX_NUMBER_THEORY_MAGNITUDE:
        raise ValueError(
            f"Divisors is limited to integers up to "
            f"{_MAX_NUMBER_THEORY_MAGNITUDE} (trial division is too slow "
            f"beyond that)."
        )
    small, large = [], []
    d = 1
    while d * d <= n:
        if n % d == 0:
            small.append(d)
            if d != n // d:
                large.append(n // d)
        d += 1
    return sorted(small + large)


def _totient(n):
    n = int(n)
    if n < 1:
        raise ValueError("'Totient' requires a positive integer.")
    result = n
    for p, _ in _factor_integer(n):
        result -= result // p
    return result


def _integer_nth_root(n, k):
    """Exact integer k-th root of n via binary search (no float error)."""
    if n < 0:
        raise ValueError("Integer root requires a non-negative integer.")
    if n == 0:
        return 0
    lo, hi = 0, 1
    while hi**k <= n:
        hi *= 2
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid**k <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo


def _is_perfect_power(n):
    n = int(n)
    if n < 2:
        return False
    for k in range(2, n.bit_length() + 1):
        root = _integer_nth_root(n, k)
        if root >= 2 and root**k == n:
            return True
    return False


def _extended_gcd(a, b):
    old_r, r = int(a), int(b)
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t  # (gcd, x, y) such that a*x + b*y = gcd(a, b)


def _carmichael_lambda(n):
    n = int(n)
    if n < 1:
        raise ValueError("'CarmichaelLambda' requires a positive integer.")
    if n == 1:
        return 1

    def prime_power_lambda(p, e):
        if p == 2 and e >= 3:
            return 2 ** (e - 2)
        return (p - 1) * p ** (e - 1)

    result = 1
    for p, e in _factor_integer(n):
        result = math.lcm(result, prime_power_lambda(p, e))
    return result


def _jacobi_symbol(a, n):
    n = int(n)
    if n <= 0 or n % 2 == 0:
        raise ValueError("requires an odd, positive modulus")
    a = int(a) % n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def _multiplicative_order(a, n):
    a, n = int(a), int(n)
    if math.gcd(a, n) != 1:
        raise ValueError("'MultiplicativeOrder' requires gcd(a, n) = 1.")
    k, val = 1, a % n
    while val != 1:
        val = (val * a) % n
        k += 1
    return k


def _primitive_root(n):
    n = int(n)
    phi = sum(1 for k in range(1, n) if math.gcd(k, n) == 1)
    for g in range(1, n):
        if math.gcd(g, n) == 1 and _multiplicative_order(g, n) == phi:
            return g
    raise ValueError(f"No primitive root exists modulo {n}.")


def _chinese_remainder(remainders, moduli):
    total_modulus = math.prod(moduli)
    result = 0
    for r, m in zip(remainders, moduli):
        Mi = total_modulus // m
        result += r * Mi * pow(Mi, -1, m)
    return result % total_modulus


def _lucas_l(n):
    a, b = 2, 1
    for _ in range(int(n)):
        a, b = b, a + b
    return a


def _bernoulli(n):
    """
    Exact n-th Bernoulli number via the Akiyama-Tanigawa algorithm, using
    the modern B1 = -1/2 convention (matching Mathematica and most
    contemporary sources - the alternative B1 = +1/2 convention exists
    too, differing only at n=1; the algorithm below naturally produces
    +1/2, flipped here to match the more common convention).
    """
    n = int(n)
    if n < 0:
        raise ValueError("'BernoulliB' requires a non-negative integer.")
    A = [Fraction(1, m + 1) for m in range(n + 1)]
    for m in range(n + 1):
        for j in range(m, 0, -1):
            A[j - 1] = j * (A[j - 1] - A[j])
    result = A[0]
    return -result if n == 1 else result


def _continued_fraction(x, max_terms=20, blowup_threshold=1e6):
    """
    Continued-fraction expansion of `x`. `blowup_threshold` guards
    against floating-point noise: past a certain number of terms, a
    double's finite precision is exhausted and further terms become
    numerically meaningless (huge, essentially random integers) rather
    than real information about `x` - detected here as an implausibly
    large next term, and the expansion stopped there instead of
    emitting garbage.

    Note: a finite continued fraction has two equally valid
    representations differing only in the last term (`[..., a]` and
    `[..., a - 1, 1]` are the same value) - which one comes out depends
    on where the expansion happens to terminate, not a bug.
    """
    terms = []
    for _ in range(max_terms):
        if abs(x) > blowup_threshold:
            break
        a = math.floor(x)
        terms.append(a)
        frac = x - a
        if abs(frac) < 1e-12:
            break
        x = 1 / frac
    return terms


def _from_continued_fraction(terms):
    result = Fraction(int(terms[-1]))
    for a in reversed(terms[:-1]):
        result = int(a) + 1 / result
    return result


def _digits_in_base(n, base):
    n = abs(int(n))
    base = int(base)
    if base < 2:
        raise ValueError("Base must be at least 2.")
    if n == 0:
        return [0]
    digits = []
    while n:
        n, rem = divmod(n, base)
        digits.append(rem)
    return list(reversed(digits))


def _is_figurate(n, formula, k_min=0):
    """
    Whether `n` equals `formula(k)` for some integer `k >= k_min`.
    `formula` must be non-decreasing for `k >= k_min`. Uses binary
    search rather than solving `formula` symbolically, so it works for
    any such formula without per-shape algebra.
    """
    n = int(n)
    if n < formula(k_min):
        return False
    lo, hi = k_min, k_min + 1
    while formula(hi) < n:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if formula(mid) < n:
            lo = mid + 1
        else:
            hi = mid
    return formula(lo) == n
