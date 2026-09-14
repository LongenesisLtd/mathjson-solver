import numbers
import sys
from typing import Union, Any
from functools import reduce
from fractions import Fraction
import math
from copy import deepcopy
from statistics import (
    median,
    variance,
    stdev,
    pvariance,
    pstdev,
    mode,
    quantiles,
    covariance,
    correlation,
)
import datetime

NUMPY_AVAILABLE = False
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    pass

RE2_AVAILABLE = False
try:
    import re2

    RE2_AVAILABLE = True
    # No public "re2.Pattern" name is exported; derive the actual
    # compiled-pattern type at import time rather than hardcoding
    # re2's internal class path.
    _RE2_PATTERN_TYPE = type(re2.compile(""))
except ImportError:
    _RE2_PATTERN_TYPE = None

# Hard cap on the result length of string operations whose size is
# otherwise controlled directly by a user-supplied count/length
# argument (StringRepeat, PadStart, PadEnd) - closes the same
# memory/time exhaustion shape that Loop/Random/arbitrary-size Repeat
# are excluded for elsewhere in this solver, but here it's cheaply and
# exactly bounded by a single length check before any allocation.
_MAX_STRING_REPEAT_LENGTH = 100_000

# Hard cap on PolynomialFit's degree - the normal-equations system it
# builds is (degree+1) x (degree+1), solved by O(degree^3) Gaussian
# elimination, so an unbounded user-supplied degree is a compute-cost
# vector the same way an unbounded string length is above.
_MAX_POLYFIT_DEGREE = 50

NoneType = type(None)


def _try_parse_datetime(value):
    """Try to parse a string as datetime or date. Returns original value if not parseable."""
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value
    if isinstance(value, str):
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            pass
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            pass
    return value


# def find_interpolation_bounds(
#     l: list, target: int | float
# ) -> Union[Union[int, float], tuple[Union[int, float], Union[int, float]]]:
#     for i, x in enumerate(l):
#         if i == 0:
#             continue
#         if l[i - 1] <= target and target <= l[i]:
#             if target == l[i - 1] or target == l[i]:
#                 return target
#             else:
#                 return l[i - 1], l[i]
#     else:
#         raise ValueError("Target value is outside interpolation range.")


def _MultiplyByScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x * a for x in l]


def _MultiplyByArray(
    l1: list[numbers.Real], l2: list[numbers.Real]
) -> list[numbers.Real]:
    return [a * b for a, b in zip(l1, l2)]


def _AddScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x + a for x in l]


def _SubtractScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x - a for x in l]


def _AddArray(l1: list[numbers.Real], l2: list[numbers.Real]) -> list[numbers.Real]:
    return [a + b for a, b in zip(l1, l2)]


def _SubtractArray(
    l1: list[numbers.Real], l2: list[numbers.Real]
) -> list[numbers.Real]:
    return [a - b for a, b in zip(l1, l2)]


def _CumulativeProduct(l: list) -> list:
    res = []
    for i, x in enumerate(l):
        if i == 0:
            res.append(x)
        else:
            res.append(reduce(lambda a, b: a * b, l[: i + 1]))
    return res


def _CumulativeSum(l: list) -> list:
    res = []
    for i, x in enumerate(l):
        if i == 0:
            res.append(x)
        else:
            res.append(reduce(lambda a, b: a + b, l[: i + 1]))
    return res


def find_interpolation_bounds_indexes(
    l: list, target: int | float
) -> Union[Union[int, float], tuple[Union[int, float], Union[int, float]]]:
    for i, x in enumerate(l):
        if i == 0:
            continue
        if l[i - 1] <= target and target <= l[i]:
            if target == l[i - 1]:
                return i - 1
            elif target == l[i]:
                return i
            else:
                return i - 1, i
    else:
        raise ValueError("Target value is outside interpolation range.")


def find_interpolation_bounds_2indexes(
    l: list, target: int | float
) -> Union[Union[int, float], tuple[Union[int, float], Union[int, float]]]:
    for i, x in enumerate(l):
        if i == len(l) - 1:
            return i - 1, i
        if l[i] <= target and target < l[i + 1]:
            return i, i + 1
    else:
        raise ValueError("Target value is outside interpolation range.")


def linear_interpolate(x_array, y_array, target_x):
    # Find the interval where target_x falls
    # Handle edge cases (target_x outside range)
    # Apply: y = y1 + (y2 - y1) * (target_x - x1) / (x2 - x1)

    # first check if both arrays are the same length
    if len(x_array) != len(y_array) or len(x_array) < 2:
        raise ValueError(
            "Both arrays need to be the same length and with at least 2 elements."
        )
    bounds_indexes = find_interpolation_bounds_indexes(x_array, target_x)
    if isinstance(bounds_indexes, tuple):
        x1, x2 = x_array[bounds_indexes[0]], x_array[bounds_indexes[1]]
        y1, y2 = y_array[bounds_indexes[0]], y_array[bounds_indexes[1]]
        return y1 + (y2 - y1) * (target_x - x1) / (x2 - x1)
    else:
        return y_array[bounds_indexes]


class MathJSONException(Exception):
    """Exception for MathJSON processing issues"""

    def __init__(self, e, expr, *args, **kwargs):
        super().__init__(args)
        self.e = e
        self.expr = expr
        self.construct = kwargs.get("mathjson_construct", "MathJSON")

    def __str__(self):
        if hasattr(self.e, "message"):
            m = self.e.message
        else:
            m = str(self.e)
        return f"Problem in {self.construct}. {self.expr}. {m}"


# def requires_array(func):
#     def inner1(*args, **kwargs):
#         try:
#             if args[0][1][0] == "Array" and len(args[0][1]) > 0:
#                 return func(*args, **kwargs)
#             else:
#                 raise ValueError(f"'{func.__name__}' should receive a list")
#         except TypeError:
#             raise ValueError(f"'{func.__name__}' really should receive a list")

#     return inner1


def is_numeric(x):
    try:
        float(x)
    except ValueError:
        return False
    except TypeError:
        return False
    else:
        return True


def _is_prime(n) -> bool:
    n = int(n)
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    return all(n % i for i in range(3, int(n**0.5) + 1, 2))


# --- Number theory helpers -------------------------------------------
#
# _is_prime, _factor_integer and _divisors are all trial-division based
# (O(sqrt(n))) - fine for everyday inputs, but a ~15+ digit number makes
# a single call noticeably slow (empirically: ~0.3s at 10**14, and it
# grows with sqrt(n), so ~3s at 10**16, ~30s at 10**18). Every
# construct built on them below caps its integer input at
# _MAX_NUMBER_THEORY_MAGNITUDE to keep worst-case latency low.
# `IsPrime`/`_is_prime` itself predates this and has no such cap - a
# pre-existing gap, not introduced here; left alone rather than
# silently changing already-shipped behavior.
_MAX_NUMBER_THEORY_MAGNITUDE = 10**12

# NthPrime/NextPrime search forward one candidate at a time; empirically
# NthPrime(10_000) ~ 0.1s and NthPrime(100_000) ~ 3.4s, so the *count*
# of primes to advance through needs its own (smaller) cap, separate
# from the starting-value magnitude cap above.
_MAX_NTH_PRIME = 10_000

# PrimePi checks every integer up to n, so its cost scales with n
# itself (not just sqrt(n)) - empirically ~0.1s at 100_000.
_MAX_PRIME_PI = 100_000


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


def has_matching_sublist(
    *,
    my_list: list,
    required_match_count: int,
    position: int,
    contiguous: bool,
    conditions: list[bool],
) -> bool:
    if contiguous:
        # Check for contiguous matches based on position
        if position == 0:
            # Check if the beginning of the list matches
            count = sum(
                1
                for i in range(min(required_match_count, len(my_list)))
                if conditions[i]
            )
            return count == required_match_count
        elif position > 0:
            # Skip the first `position` elements
            count = sum(
                1
                for i in range(position, position + required_match_count)
                if i < len(my_list) and conditions[i]
            )
            return count == required_match_count
        elif position == -1:
            # Check if the end of the list matches
            count = sum(
                1
                for i in range(len(my_list) - required_match_count, len(my_list))
                if conditions[i]
            )
            return count == required_match_count
        elif position < -1:
            # Skip the last `abs(position)` elements
            count = sum(1 for i in range(len(my_list) + position) if conditions[i])
            return count == required_match_count
    else:
        # Check for non-contiguous matches
        count = sum(1 for i in range(len(my_list)) if conditions[i])
        return count >= required_match_count


# def has_sublist2(
#     *,
#     my_list: list,
#     required_match_count: int,
#     position: int,
#     contiguous: bool,
#     condition: callable,
# ) -> bool:
#     if contiguous:
#         # Check for contiguous matches based on position
#         if position == 0:
#             # Check if the beginning of the list matches
#             count = sum(1 for x in my_list[:required_match_count] if condition(x))
#             return count == required_match_count
#         elif position > 0:
#             # Skip the first `position` elements
#             count = sum(
#                 1
#                 for x in my_list[position : position + required_match_count]
#                 if condition(x)
#             )
#             return count == required_match_count
#         elif position == -1:
#             # Check if the end of the list matches
#             count = sum(1 for x in my_list[-required_match_count:] if condition(x))
#             return count == required_match_count
#         elif position < -1:
#             # Skip the last `abs(position)` elements
#             count = sum(1 for x in my_list[:position] if condition(x))
#             return count == required_match_count
#     else:
#         # Check for non-contiguous matches
#         count = sum(1 for x in my_list if condition(x))
#         return count >= required_match_count


def comparison_safe_converter(x):
    if type(x) in [bool, NoneType]:  # bool before int (bool IS an int in Python)
        return "1" if x else "0"
    elif type(x) in [int, float, str]:
        return f"{x}"
    return x


def comparison_safe_converter_for_pairs(
    v1, v2
) -> (Union[str, float], Union[str, float]):
    if is_numeric(v1):
        v1 = float(v1)
    if is_numeric(v2):
        v2 = float(v2)
    return v1, v2


def translate_v1_mathjson(expr):
    """
    Rewrite a MathJSON expression written for mathjson-solver < 2.0.0 so it
    evaluates to the same result on >= 2.0.0.

    The only breaking change introduced in 2.0.0 is "Log": before 2.0.0 it
    always meant natural log (`["Log", x]` == `math.log(x)`); from 2.0.0 on
    it matches CortexJS (`["Log", x]` is log base 10, `["Log", x, b]` is log
    base `b`), and natural log moved to "Ln". Since the pre-2.0.0 "Log" only
    ever took one argument, every legacy `["Log", x]` node has exactly one
    correct translation: `["Ln", x]`. This function walks the expression
    tree and applies that rewrite, leaving everything else untouched, so
    existing expressions don't need to be hand-migrated to keep working
    while still gaining access to functions added in 2.x.
    """
    if isinstance(expr, list):
        if len(expr) == 2 and expr[0] == "Log":
            return ["Ln", translate_v1_mathjson(expr[1])]
        return [translate_v1_mathjson(item) for item in expr]
    return expr


def create_mathjson_solver(solver_parameters, legacy_v1=False):
    def f(s, *args):
        if args:
            c = deepcopy(args[0])
        else:
            c = {}
        #         c = deepcopy(kwargs.get("c", {}))
        if isinstance(s, numbers.Number):
            return s
        # CortexJS represents the boolean literals as the bare symbols
        # "True" and "False" (as opposed to native JSON `true`/`false`,
        # which already arrive here as Python bool - itself a `numbers.Number`
        # subtype, so it's handled by the check above). Resolve them to
        # actual booleans unconditionally, the same way numeric literals
        # are resolved above, so they can't be shadowed by a same-named
        # solver parameter or local variable.
        if s == "True" or s == "False":
            return s == "True"
        if isinstance(s, list):

            def Arr(s):
                return s

            def Add(s):
                l_res = []
                tmp = 0
                for i, x in enumerate(s[1:]):
                    res = f(x, c)
                    if is_numeric(res):
                        res = float(res)
                    if i == 0:
                        tmp = res
                    else:
                        # Handle datetime string + timedelta
                        if isinstance(res, datetime.timedelta):
                            tmp = _try_parse_datetime(tmp)
                        elif isinstance(tmp, datetime.timedelta):
                            res = _try_parse_datetime(res)
                        try:
                            tmp = tmp + res
                        except TypeError:
                            pass

                # Convert datetime result back to string
                if isinstance(tmp, (datetime.datetime, datetime.date)):
                    return tmp.isoformat()
                return tmp

                # tmp = 0
                # for i, x in enumerate(l):
                #     if i == 0:
                #         tmp = x
                #     else:
                #         tmp = tmp + x
                # return tmp

            # def Sum(s):
            #     l_res = []
            #     for x in s[1:]:
            #         res = f(x, c)
            #         if isinstance(res, list):
            #             l_res.append(sum([xx for xx in res[1:]]))
            #         else:
            #             l_res.append(res)
            #     return sum(l_res)

            def Sum(s):
                l_res = ["Array"]
                for x in s[1:]:
                    res = f(x, c)
                    if isinstance(res, list):
                        l_res.append(Add(["Array"] + [xx for xx in res[1:]]))
                    else:
                        l_res.append(res)
                return Add(l_res)

            def Subtract(s):
                values = [f(x, c) for x in s[1:]]
                # Convert datetime strings if we're dealing with timedelta
                converted = []
                for i, v in enumerate(values):
                    if isinstance(v, datetime.timedelta):
                        converted.append(v)
                    elif any(isinstance(other, datetime.timedelta) for other in values):
                        converted.append(_try_parse_datetime(v))
                    else:
                        converted.append(v)
                result = reduce(lambda a, b: a - b, converted)
                if isinstance(result, (datetime.datetime, datetime.date)):
                    return result.isoformat()
                return result

            def Max(s):
                args = s[1:]
                if len(args) == 1:
                    if isinstance(args[0], str):
                        return max(
                            [f(x, c) for x in f(args[0], c) if is_numeric(f(x, c))]
                        )
                    else:
                        return max(
                            [f(x, c) for x in args[0][1:] if is_numeric(f(x, c))]
                        )
                else:
                    # CortexJS-style variadic form: ["Max", a, b, c, ...]
                    return max([f(x, c) for x in args])

            def Min(s):
                args = s[1:]
                if len(args) == 1:
                    if isinstance(args[0], str):
                        return min(
                            [f(x, c) for x in f(args[0], c) if is_numeric(f(x, c))]
                        )
                    else:
                        return min(
                            [f(x, c) for x in args[0][1:] if is_numeric(f(x, c))]
                        )
                else:
                    # CortexJS-style variadic form: ["Min", a, b, c, ...]
                    return min([f(x, c) for x in args])

            def Average(s):
                if isinstance(s[1], str):
                    # A reference to "answer" has been passed
                    s_ = [float(f(x, c)) for x in f(s[1], c) if is_numeric(f(x, c))]
                else:
                    s_ = [float(f(x, c)) for x in s[1][1:] if is_numeric(f(x, c))]
                try:
                    return sum(s_) / len(s_)
                except ZeroDivisionError:
                    return None

            def Median(s):
                if isinstance(s[1], str):
                    return median([f(x, c) for x in f(s[1], c) if is_numeric(f(x, c))])
                else:
                    return median([f(x, c) for x in s[1][1:] if is_numeric(f(x, c))])

            def Length(s):
                if isinstance(s[1], str):
                    return len([x for x in f(s[1], c)][1:])
                else:
                    return len([x for x in s[1][1:]])

            def Clamp(s):
                """
                ["Clamp", value] or ["Clamp", value, lower, upper]
                Bounds `value` between `lower` (default -1) and `upper` (default 1),
                matching CortexJS `Clamp`.
                """
                value = f(s[1], c)
                lower = f(s[2], c) if len(s) > 2 else -1
                upper = f(s[3], c) if len(s) > 3 else 1
                return max(lower, min(upper, value))

            def _arr_vals(s):
                lst = f(s[1], c)
                if not (isinstance(lst, list) and lst[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                return [f(x, c) for x in lst[1:]]

            def First(s):
                return _arr_vals(s)[0]

            def Second(s):
                return _arr_vals(s)[1]

            def Third(s):
                return _arr_vals(s)[2]

            def Last(s):
                return _arr_vals(s)[-1]

            def Rest(s):
                return ["Array"] + _arr_vals(s)[1:]

            def Most(s):
                return ["Array"] + _arr_vals(s)[:-1]

            def Reverse(s):
                return ["Array"] + list(reversed(_arr_vals(s)))

            def Sort(s):
                return ["Array"] + sorted(_arr_vals(s))

            def IsEmpty(s):
                lst = f(s[1], c)
                if not (isinstance(lst, list) and lst[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                return len(lst) <= 1

            def Range(s):
                """
                CortexJS-compatible `Range`:
                ["Range", upper]                -> 1..upper (inclusive)
                ["Range", lower, upper]         -> lower..upper (inclusive)
                ["Range", lower, upper, step]   -> lower..upper (inclusive), stepped
                Distinct from `GenerateRange`, which is 0-indexed and exclusive at
                the upper end.
                """
                if len(s) == 2:
                    return ["Array"] + list(range(1, int(f(s[1], c)) + 1))
                elif len(s) == 3:
                    lo, hi = int(f(s[1], c)), int(f(s[2], c))
                    return ["Array"] + list(range(lo, hi + 1))
                else:
                    lo, hi, step = (
                        int(f(s[1], c)),
                        int(f(s[2], c)),
                        int(f(s[3], c)),
                    )
                    return ["Array"] + list(
                        range(lo, hi + 1 if step > 0 else hi - 1, step)
                    )

            def Join(s):
                """
                ["Join", array1, array2, ...]
                Concatenates the given arrays.
                """
                result = ["Array"]
                for arg in s[1:]:
                    lst = f(arg, c)
                    if not (isinstance(lst, list) and lst[0] == "Array"):
                        raise ValueError("All parameters must be arrays.")
                    result += [f(x, c) for x in lst[1:]]
                return result

            def Unique(s):
                seen = []
                for x in _arr_vals(s):
                    if x not in seen:
                        seen.append(x)
                return ["Array"] + seen

            def Zip(s):
                lists = [[f(x, c) for x in f(arg, c)[1:]] for arg in s[1:]]
                return ["Array"] + [["Array", a, b] for a, b in zip(*lists)]

            def At(s):
                """
                ["At", array, index]
                1-indexed element access (CortexJS `At`), with negative indexes
                counting from the end.
                """
                vals = _arr_vals(s)
                idx = int(f(s[2], c))
                if idx > 0:
                    return vals[idx - 1]
                else:
                    return vals[idx]

            def Take(s):
                """
                ["Take", array, n]
                First `n` elements if n >= 0; last `n` elements if n < 0.
                Distinct from `Slice`, which takes an explicit [start, end)
                range instead of a count.
                """
                vals = _arr_vals(s)
                n = int(f(s[2], c))
                if n >= 0:
                    return ["Array"] + vals[:n]
                return ["Array"] + vals[n:]

            def Drop(s):
                """
                ["Drop", array, n]
                All elements except the first `n` if n >= 0; except the
                last `n` if n < 0.
                """
                vals = _arr_vals(s)
                n = int(f(s[2], c))
                if n >= 0:
                    return ["Array"] + vals[n:]
                return ["Array"] + vals[:n]

            def TakeWhile(s):
                """
                ["TakeWhile", array, predicate]
                Elements from the start, up to (excluding) the first one
                for which `predicate` is false.
                """
                result = []
                for v in _arr_vals(s):
                    if not _apply_fn(s[2], [v]):
                        break
                    result.append(v)
                return ["Array"] + result

            def DropWhile(s):
                """
                ["DropWhile", array, predicate]
                Remaining elements from (and including) the first one for
                which `predicate` is false.
                """
                vals = _arr_vals(s)
                i = 0
                while i < len(vals) and _apply_fn(s[2], [vals[i]]):
                    i += 1
                return ["Array"] + vals[i:]

            def Contains(s):
                """
                ["Contains", array, value]
                Whether `value` occurs in `array`. CortexJS argument order
                (collection first) - the existing `In` takes them the
                other way round (`["In", value, collection]`).
                """
                return f(s[2], c) in _arr_vals(s)

            def IndexOf(s):
                """
                ["IndexOf", array, value]
                1-indexed position of the first occurrence of `value`, or
                None if it doesn't occur.
                """
                vals = _arr_vals(s)
                value = f(s[2], c)
                try:
                    return vals.index(value) + 1
                except ValueError:
                    return None

            def IndexWhere(s):
                """
                ["IndexWhere", array, predicate]
                1-indexed position of the first element for which
                `predicate` is true, or None if none match.
                """
                for i, v in enumerate(_arr_vals(s)):
                    if _apply_fn(s[2], [v]):
                        return i + 1
                return None

            def Find(s):
                """
                ["Find", array, predicate]
                The first element for which `predicate` is true, or None
                if none match.
                """
                for v in _arr_vals(s):
                    if _apply_fn(s[2], [v]):
                        return v
                return None

            def CountIf(s):
                """
                ["CountIf", array, predicate]
                Count of elements for which `predicate` is true.
                """
                return sum(1 for v in _arr_vals(s) if _apply_fn(s[2], [v]))

            def Position(s):
                """
                ["Position", array, predicate]
                Array of the 1-indexed positions of every element for
                which `predicate` is true.
                """
                return ["Array"] + [
                    i + 1
                    for i, v in enumerate(_arr_vals(s))
                    if _apply_fn(s[2], [v])
                ]

            def RotateLeft(s):
                """
                ["RotateLeft", array, n]
                Circularly shifts `array` left by `n` positions.
                """
                vals = _arr_vals(s)
                if not vals:
                    return ["Array"]
                n = int(f(s[2], c)) % len(vals)
                return ["Array"] + vals[n:] + vals[:n]

            def RotateRight(s):
                """
                ["RotateRight", array, n]
                Circularly shifts `array` right by `n` positions.
                """
                vals = _arr_vals(s)
                if not vals:
                    return ["Array"]
                n = int(f(s[2], c)) % len(vals)
                if n == 0:
                    return ["Array"] + vals
                return ["Array"] + vals[-n:] + vals[:-n]

            def MaxBy(s):
                """
                ["MaxBy", array, function]
                The element of `array` for which `function(element)` is
                largest.
                """
                return max(_arr_vals(s), key=lambda v: _apply_fn(s[2], [v]))

            def MinBy(s):
                """
                ["MinBy", array, function]
                The element of `array` for which `function(element)` is
                smallest.
                """
                return min(_arr_vals(s), key=lambda v: _apply_fn(s[2], [v]))

            def ArgMax(s):
                """
                ["ArgMax", array]
                1-indexed position of the largest element.
                """
                vals = _arr_vals(s)
                return max(range(len(vals)), key=lambda i: vals[i]) + 1

            def ArgMin(s):
                """
                ["ArgMin", array]
                1-indexed position of the smallest element.
                """
                vals = _arr_vals(s)
                return min(range(len(vals)), key=lambda i: vals[i]) + 1

            def Ordering(s):
                """
                ["Ordering", array]
                Array of the 1-indexed positions that would put `array`
                in ascending order.
                """
                vals = _arr_vals(s)
                return ["Array"] + [
                    i + 1 for i in sorted(range(len(vals)), key=lambda i: vals[i])
                ]

            def FlatMap(s):
                """
                ["FlatMap", array, function]
                Applies `function` to each element (as with `Map`) and
                flattens one level of the results - each result that is
                itself an array is spliced in, others are kept as-is -
                into a single array.
                """
                result = ["Array"]
                for v in _arr_vals(s):
                    mapped = _apply_fn(s[2], [v])
                    if isinstance(mapped, list) and mapped and mapped[0] == "Array":
                        result += mapped[1:]
                    else:
                        result.append(mapped)
                return result

            def Scan(s):
                """
                ["Scan", array, function] or ["Scan", array, function, initial]
                Like `Reduce`'s CortexJS form (`function` applied as
                `function(accumulator, current)`), but returns an array of
                every intermediate accumulator value, including the seed,
                instead of just the final one.
                """
                vals = _arr_vals(s)
                fn_expr = s[2]
                if len(s) == 4:
                    acc = f(s[3], c)
                    remaining = vals
                else:
                    if not vals:
                        raise ValueError(
                            "'Scan' on an empty collection requires an initial value."
                        )
                    acc = vals[0]
                    remaining = vals[1:]
                result = ["Array", acc]
                for v in remaining:
                    acc = _apply_fn(fn_expr, [acc, v])
                    result.append(acc)
                return result

            def Differences(s):
                """
                ["Differences", array]
                Array of successive differences: element[i+1] - element[i].
                """
                vals = _arr_vals(s)
                return ["Array"] + [b - a for a, b in zip(vals, vals[1:])]

            def Fold(s):
                """
                ["Fold", function, array] or ["Fold", function, array, initial]
                The function-first form of `Reduce`'s CortexJS calling
                convention (`["Reduce", array, function, ...]`) - same
                behaviour, arguments swapped.
                """
                if len(s) == 3:
                    return Reduce(["Reduce", s[2], s[1]])
                return Reduce(["Reduce", s[2], s[1], s[3]])

            def Dedup(s):
                """
                ["Dedup", array]
                Removes only *consecutive* duplicate elements - distinct
                from `Unique`, which removes every duplicate regardless of
                position.
                """
                result = []
                for v in _arr_vals(s):
                    if not result or result[-1] != v:
                        result.append(v)
                return ["Array"] + result

            def Insert(s):
                """
                ["Insert", array, index, value]
                Inserts `value` at the 1-indexed `index` (CortexJS
                convention, matching `At`); negative indexes count from
                the end.
                """
                vals = _arr_vals(s)
                idx = int(f(s[2], c))
                value = f(s[3], c)
                vals.insert(idx - 1 if idx > 0 else idx, value)
                return ["Array"] + vals

            def DeleteAt(s):
                """
                ["DeleteAt", array, index]
                Removes the element at the 1-indexed `index`; negative
                indexes count from the end.
                """
                vals = _arr_vals(s)
                idx = int(f(s[2], c))
                del vals[idx - 1 if idx > 0 else idx]
                return ["Array"] + vals

            def ReplaceAt(s):
                """
                ["ReplaceAt", array, index, value]
                Replaces the element at the 1-indexed `index` with
                `value`; negative indexes count from the end.
                """
                vals = _arr_vals(s)
                idx = int(f(s[2], c))
                value = f(s[3], c)
                vals[idx - 1 if idx > 0 else idx] = value
                return ["Array"] + vals

            def Partition(s):
                """
                ["Partition", array, size]
                Splits `array` into consecutive chunks of length `size`
                (the last chunk may be shorter). Distinct from `Chunk`,
                which instead takes the number of groups to split into.
                """
                vals = _arr_vals(s)
                size = int(f(s[2], c))
                if size <= 0:
                    raise ValueError("'Partition' size must be a positive integer.")
                return ["Array"] + [
                    ["Array"] + vals[i : i + size] for i in range(0, len(vals), size)
                ]

            def Chunk(s):
                """
                ["Chunk", array, n]
                Splits `array` into `n` roughly equal-sized consecutive
                groups.
                """
                vals = _arr_vals(s)
                n = int(f(s[2], c))
                if n <= 0:
                    raise ValueError("'Chunk' group count must be a positive integer.")
                base, extra = divmod(len(vals), n)
                result, start = [], 0
                for i in range(n):
                    size = base + (1 if i < extra else 0)
                    result.append(["Array"] + vals[start : start + size])
                    start += size
                return ["Array"] + result

            def GroupBy(s):
                """
                ["GroupBy", array, function]
                Groups elements of `array` by `function(element)`, in
                order of first appearance of each key. Returns an array of
                [key, group] pairs - there's no dedicated `Dictionary`
                type in this solver.
                """
                order = []
                groups = {}
                for v in _arr_vals(s):
                    k = _apply_fn(s[2], [v])
                    hk = tuple(k) if isinstance(k, list) else k
                    if hk not in groups:
                        order.append((hk, k))
                        groups[hk] = []
                    groups[hk].append(v)
                return ["Array"] + [
                    ["Array", k, ["Array"] + groups[hk]] for hk, k in order
                ]

            def ChunkBy(s):
                """
                ["ChunkBy", array, function]
                Splits `array` into consecutive runs sharing the same
                `function(element)` key - unlike `GroupBy`, runs are not
                merged across non-adjacent occurrences of the same key.
                """
                vals = _arr_vals(s)
                if not vals:
                    return ["Array"]
                result = []
                current = [vals[0]]
                current_key = _apply_fn(s[2], [vals[0]])
                for v in vals[1:]:
                    k = _apply_fn(s[2], [v])
                    if k == current_key:
                        current.append(v)
                    else:
                        result.append(["Array"] + current)
                        current, current_key = [v], k
                result.append(["Array"] + current)
                return ["Array"] + result

            def Tally(s):
                """
                ["Tally", array]
                Counts occurrences of each distinct element, in order of
                first appearance. Returns an array of [value, count]
                pairs.
                """
                order = []
                counts = {}
                for v in _arr_vals(s):
                    hv = tuple(v) if isinstance(v, list) else v
                    if hv not in counts:
                        order.append((hv, v))
                        counts[hv] = 0
                    counts[hv] += 1
                return ["Array"] + [["Array", v, counts[hv]] for hv, v in order]

            def _arr_vals_of(expr):
                """
                Like `_arr_vals`, but for an arbitrary expression instead
                of assuming the array is at `s[1]` - needed by the
                variadic set operations below.
                """
                lst = f(expr, c)
                if not (isinstance(lst, list) and lst[0] == "Array"):
                    raise ValueError("Parameter must be an array.")
                return [f(x, c) for x in lst[1:]]

            def Union(s):
                """
                ["Union", array1, array2, ...]
                Distinct elements appearing in any of the given arrays, in
                order of first appearance across the arguments
                (left to right). Arrays stand in for CortexJS's `Set`
                here - there's no dedicated set type in this solver.
                """
                result = []
                for arg in s[1:]:
                    for v in _arr_vals_of(arg):
                        if v not in result:
                            result.append(v)
                return ["Array"] + result

            def Intersection(s):
                """
                ["Intersection", array1, array2, ...]
                Distinct elements common to every given array, in the
                order they first appear in `array1`.
                """
                arrays = [_arr_vals_of(arg) for arg in s[1:]]
                if not arrays:
                    return ["Array"]
                result = []
                for v in arrays[0]:
                    if v not in result and all(v in arr for arr in arrays[1:]):
                        result.append(v)
                return ["Array"] + result

            def SetMinus(s):
                """
                ["SetMinus", array1, array2]
                Distinct elements of `array1` that don't occur in
                `array2`.
                """
                a = _arr_vals_of(s[1])
                b = _arr_vals_of(s[2])
                result = []
                for v in a:
                    if v not in b and v not in result:
                        result.append(v)
                return ["Array"] + result

            def SymmetricDifference(s):
                """
                ["SymmetricDifference", array1, array2]
                Distinct elements that occur in exactly one of
                `array1`/`array2`: `array1`'s exclusive elements first
                (in `array1`'s order), then `array2`'s (in `array2`'s
                order).
                """
                a = _arr_vals_of(s[1])
                b = _arr_vals_of(s[2])
                result = []
                for v in a:
                    if v not in b and v not in result:
                        result.append(v)
                for v in b:
                    if v not in a and v not in result:
                        result.append(v)
                return ["Array"] + result

            def IsPrime(s):
                return _is_prime(f(s[1], c))

            # --- Number theory ---

            def FactorInteger(s):
                return ["Array"] + [
                    ["Array", p, e] for p, e in _factor_integer(f(s[1], c))
                ]

            def PrimeFactors(s):
                return ["Array"] + [p for p, _ in _factor_integer(f(s[1], c))]

            def PrimeNu(s):
                return len(_factor_integer(f(s[1], c)))

            def PrimeOmega(s):
                return sum(e for _, e in _factor_integer(f(s[1], c)))

            def Radical(s):
                return math.prod(p for p, _ in _factor_integer(f(s[1], c)))

            def IsSquareFree(s):
                return all(e == 1 for _, e in _factor_integer(f(s[1], c)))

            def Divisors(s):
                return ["Array"] + _divisors(f(s[1], c))

            def Sigma0(s):
                return len(_divisors(f(s[1], c)))

            def Sigma1(s):
                return sum(_divisors(f(s[1], c)))

            def SigmaMinus1(s):
                return sum(Fraction(1, d) for d in _divisors(f(s[1], c)))

            def DivisorSigma(s):
                k = int(f(s[2], c))
                return sum(d**k for d in _divisors(f(s[1], c)))

            def Totient(s):
                return _totient(f(s[1], c))

            def IsPerfectPower(s):
                return _is_perfect_power(f(s[1], c))

            def NthPrime(s):
                """
                ["NthPrime", n]
                The n-th prime number (1-indexed: NthPrime(1) = 2).
                Capped at _MAX_NTH_PRIME - a naive forward search gets
                slow well before Python's own integer limits do.
                """
                n = int(f(s[1], c))
                if not (1 <= n <= _MAX_NTH_PRIME):
                    raise ValueError(
                        f"'NthPrime' n must be between 1 and {_MAX_NTH_PRIME}."
                    )
                count, candidate = 0, 1
                while count < n:
                    candidate += 1
                    if _is_prime(candidate):
                        count += 1
                return candidate

            def NextPrime(s):
                """
                ["NextPrime", n] or ["NextPrime", n, k]
                The smallest prime greater than n, or the k-th such
                prime. Both the starting value's magnitude and k are
                capped, for the same reason as NthPrime.
                """
                start = int(f(s[1], c))
                k = int(f(s[2], c)) if len(s) > 2 else 1
                if abs(start) > _MAX_NUMBER_THEORY_MAGNITUDE:
                    raise ValueError(
                        f"'NextPrime' starting value is limited to "
                        f"{_MAX_NUMBER_THEORY_MAGNITUDE} in absolute value."
                    )
                if not (1 <= k <= _MAX_NTH_PRIME):
                    raise ValueError(
                        f"'NextPrime' k must be between 1 and {_MAX_NTH_PRIME}."
                    )
                count, candidate = 0, start
                while count < k:
                    candidate += 1
                    if _is_prime(candidate):
                        count += 1
                return candidate

            def PrimePi(s):
                """
                ["PrimePi", n]
                pi(n): the count of primes <= n. Capped at
                _MAX_PRIME_PI - cost scales with n itself, not sqrt(n).
                """
                n = int(f(s[1], c))
                if not (0 <= n <= _MAX_PRIME_PI):
                    raise ValueError(
                        f"'PrimePi' n must be between 0 and {_MAX_PRIME_PI}."
                    )
                return sum(1 for k in range(2, n + 1) if _is_prime(k))

            def ExtendedGCD(s):
                return ["Array"] + list(
                    _extended_gcd(int(f(s[1], c)), int(f(s[2], c)))
                )

            def ChineseRemainder(s):
                """
                ["ChineseRemainder", remainders, moduli]
                Solves the system x = remainders[i] (mod moduli[i]) via
                the Chinese Remainder Theorem. Moduli must be pairwise
                coprime.
                """
                remainders = _arr_vals_of(s[1])
                moduli = _arr_vals_of(s[2])
                return _chinese_remainder(remainders, moduli)

            def CarmichaelLambda(s):
                return _carmichael_lambda(f(s[1], c))

            def JacobiSymbol(s):
                return _jacobi_symbol(f(s[1], c), f(s[2], c))

            def MultiplicativeOrder(s):
                return _multiplicative_order(f(s[1], c), f(s[2], c))

            def PrimitiveRoot(s):
                return _primitive_root(f(s[1], c))

            def LucasL(s):
                return _lucas_l(f(s[1], c))

            def BernoulliB(s):
                return _bernoulli(f(s[1], c))

            def ContinuedFraction(s):
                x = f(s[1], c)
                max_terms = int(f(s[2], c)) if len(s) > 2 else 20
                return ["Array"] + _continued_fraction(x, max_terms)

            def FromContinuedFraction(s):
                return _from_continued_fraction(_arr_vals(s))

            def IntegerDigits(s):
                base = int(f(s[2], c)) if len(s) > 2 else 10
                return ["Array"] + _digits_in_base(f(s[1], c), base)

            def DigitCount(s):
                base = int(f(s[2], c)) if len(s) > 2 else 10
                return len(_digits_in_base(f(s[1], c), base))

            def DigitSum(s):
                base = int(f(s[2], c)) if len(s) > 2 else 10
                return sum(_digits_in_base(f(s[1], c), base))

            def FromDigits(s):
                digits = _arr_vals(s)
                base = int(f(s[2], c)) if len(s) > 2 else 10
                result = 0
                for d in digits:
                    result = result * base + int(d)
                return result

            def IsSquare(s):
                n = int(f(s[1], c))
                return n >= 0 and math.isqrt(n) ** 2 == n

            def IsTriangular(s):
                return _is_figurate(f(s[1], c), lambda k: k * (k + 1) // 2, 0)

            def IsPentagonal(s):
                return _is_figurate(f(s[1], c), lambda k: k * (3 * k - 1) // 2, 1)

            def IsOctahedral(s):
                return _is_figurate(
                    f(s[1], c), lambda k: k * (2 * k * k + 1) // 3, 1
                )

            def IsCenteredSquare(s):
                return _is_figurate(f(s[1], c), lambda k: 2 * k * (k - 1) + 1, 1)

            def IsPerfect(s):
                n = f(s[1], c)
                return sum(_divisors(n)[:-1]) == n

            def IsAbundant(s):
                n = f(s[1], c)
                return sum(_divisors(n)[:-1]) > n

            def IsHappy(s):
                n = int(f(s[1], c))
                seen = set()
                while n != 1 and n not in seen:
                    seen.add(n)
                    n = sum(int(d) ** 2 for d in str(n))
                return n == 1

            def Variance(s):
                return variance(_arr_vals(s))

            def StandardDeviation(s):
                return stdev(_arr_vals(s))

            def PopulationVariance(s):
                return pvariance(_arr_vals(s))

            def PopulationStandardDeviation(s):
                return pstdev(_arr_vals(s))

            def Mode(s):
                """
                ["Mode", array]
                The most frequently occurring value. Ties go to whichever
                value appears first in `array` (matching Python's
                `statistics.mode`).
                """
                return mode(_arr_vals(s))

            def Quartiles(s):
                """
                ["Quartiles", array]
                The three points (Q1, Q2/median, Q3) that divide `array`
                into four equal-sized groups, using
                `statistics.quantiles`' default ("exclusive") method.
                """
                return ["Array"] + quantiles(_arr_vals(s), n=4)

            def InterquartileRange(s):
                """
                ["InterquartileRange", array]
                Q3 - Q1.
                """
                q1, _, q3 = quantiles(_arr_vals(s), n=4)
                return q3 - q1

            def Covariance(s):
                """
                ["Covariance", array1, array2]
                Sample covariance of two equal-length collections.
                """
                return covariance(_arr_vals_of(s[1]), _arr_vals_of(s[2]))

            def Correlation(s):
                """
                ["Correlation", array1, array2]
                The Pearson correlation coefficient of two equal-length
                collections.
                """
                return correlation(_arr_vals_of(s[1]), _arr_vals_of(s[2]))

            def Skewness(s):
                """
                ["Skewness", array]
                Sample skewness (the adjusted Fisher-Pearson standardized
                moment coefficient - matches Excel's SKEW and
                scipy.stats.skew(..., bias=False)): a measure of the
                asymmetry of the data's distribution. Requires at least
                3 data points.
                """
                vals = _arr_vals(s)
                n = len(vals)
                if n < 3:
                    raise ValueError("'Skewness' requires at least 3 data points.")
                m = sum(vals) / n
                s_dev = stdev(vals)
                if s_dev == 0:
                    raise ValueError(
                        "'Skewness' is undefined when all values are equal."
                    )
                m3 = sum((x - m) ** 3 for x in vals) / n
                return (n**2 / ((n - 1) * (n - 2))) * m3 / s_dev**3

            def Kurtosis(s):
                """
                ["Kurtosis", array]
                Sample excess kurtosis (the adjusted Fisher-Pearson
                estimator - matches Excel's KURT and
                scipy.stats.kurtosis(..., bias=False, fisher=True)): a
                measure of the "tailedness" of the data's distribution
                (0 for a normal distribution). Requires at least 4 data
                points.
                """
                vals = _arr_vals(s)
                n = len(vals)
                if n < 4:
                    raise ValueError("'Kurtosis' requires at least 4 data points.")
                m = sum(vals) / n
                m2 = sum((x - m) ** 2 for x in vals) / n
                m4 = sum((x - m) ** 4 for x in vals) / n
                if m2 == 0:
                    raise ValueError(
                        "'Kurtosis' is undefined when all values are equal."
                    )
                g2 = m4 / m2**2 - 3
                return ((n - 1) / ((n - 2) * (n - 3))) * ((n + 1) * g2 + 6)

            def LinearRegression(s):
                """
                ["LinearRegression", x_array, y_array]
                The least-squares linear fit y = slope*x + intercept,
                returned as ["Array", slope, intercept].
                """
                x = _arr_vals_of(s[1])
                y = _arr_vals_of(s[2])
                if len(x) != len(y):
                    raise ValueError("Both arrays must be of the same length.")
                n = len(x)
                if n < 2:
                    raise ValueError(
                        "'LinearRegression' requires at least 2 data points."
                    )
                mx, my = sum(x) / n, sum(y) / n
                sxy = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
                sxx = sum((xi - mx) ** 2 for xi in x)
                if sxx == 0:
                    raise ValueError(
                        "'LinearRegression' is undefined when all x values are equal."
                    )
                slope = sxy / sxx
                intercept = my - slope * mx
                return ["Array", slope, intercept]

            def _solve_linear_system(matrix, vector):
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

            def PolynomialFit(s):
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
                x = _arr_vals_of(s[1])
                y = _arr_vals_of(s[2])
                if len(x) != len(y):
                    raise ValueError("Both arrays must be of the same length.")
                degree = int(f(s[3], c))
                if not (0 <= degree <= _MAX_POLYFIT_DEGREE):
                    raise ValueError(
                        f"'PolynomialFit' degree must be between 0 and "
                        f"{_MAX_POLYFIT_DEGREE}."
                    )
                if len(x) < degree + 1:
                    raise ValueError(
                        "'PolynomialFit' needs at least degree + 1 data points."
                    )
                power_sums = [sum(xi**k for xi in x) for k in range(2 * degree + 1)]
                matrix = [
                    [power_sums[i + j] for j in range(degree + 1)]
                    for i in range(degree + 1)
                ]
                vector = [
                    sum((xi**k) * yi for xi, yi in zip(x, y))
                    for k in range(degree + 1)
                ]
                return ["Array"] + _solve_linear_system(matrix, vector)

            def Any(s):
                evaluated = f(s[1], c)
                if isinstance(evaluated, list) and evaluated[0] == "Array":
                    return any([f(x, c) for x in evaluated[1:]])
                raise ValueError("Parameter 1 must be an array.")

            def All(s):
                evaluated = f(s[1], c)
                if isinstance(evaluated, list) and evaluated[0] == "Array":
                    return all([f(x, c) for x in evaluated[1:]])
                raise ValueError("Parameter 1 must be an array.")

            def Int(s):
                try:
                    return int(f(s[1], c))
                except ValueError:
                    return int(float(f(s[1], c)))

            def Float(s):
                return float(f(s[1], c))

            def Floor(s):
                return math.floor(f(s[1], c))

            def Ceil(s):
                return math.ceil(f(s[1], c))

            def Constants(s):
                for x in s[1:-1]:
                    try:
                        c[x[0]] = f(x[1], c)
                    except Exception:
                        c[x[0]] = None
                return f(s[-1], c)

            def Switch(s):
                expression = f(s[1], c)
                for x in s[3:]:
                    if len(x) != 2:
                        raise ValueError(
                            "Case of 'Switch' should have exactly two parameters"
                        )
                    if comparison_safe_converter(
                        expression
                    ) == comparison_safe_converter(f(x[0], c)):
                        return f(x[1], c)
                else:
                    return f(s[2], c)

            def StrictSwitch(s):
                expression = f(s[1], c)
                for x in s[3:]:
                    if len(x) != 2:
                        raise ValueError(
                            "Case of 'StrictSwitch' should have exactly two parameters"
                        )
                    if expression == f(x[0], c):
                        return f(x[1], c)
                else:
                    return f(s[2], c)

            def If(s):
                if len(s) < 3:
                    raise ValueError("Wrong parameters for 'If'")

                # Detect the CortexJS flat form: ["If", cond, then] or
                # ["If", cond, then, else]. In the Python pair-form below,
                # s[1] is always a [condition, value] pair whose first
                # element (the condition) is itself a MathJSON construct
                # call, e.g. ["Equal", 1, 0]. A CortexJS flat condition is
                # either not a list at all, or is itself such a construct
                # call (its own first element is a *known construct name*).
                # Requiring a known name - rather than any string - keeps a
                # Python-form condition that is a bare parameter reference,
                # e.g. ["If", ["my_flag", "yes"], "no"], from being
                # misdetected as CortexJS form.
                is_cortexjs_form = not isinstance(s[1], list) or (
                    bool(s[1]) and isinstance(s[1][0], str) and s[1][0] in constructs
                )

                if is_cortexjs_form:
                    if len(s) not in (3, 4):
                        raise ValueError("Wrong parameters for 'If'")
                    if f(s[1], c):
                        return f(s[2], c)
                    elif len(s) == 4:
                        return f(s[3], c)
                    else:
                        return None  # CortexJS: Nothing, no else and condition false

                for x in s[1:-1]:
                    if len(x) != 2:
                        raise ValueError("Wrong if or elif in 'If'")
                    try:
                        if f(x[0], c):
                            try:
                                return f(x[1], c)
                            except MathJSONException:
                                # Branch failed, try next condition
                                continue
                    except MathJSONException:
                        return f(s[-1], c)  # return default value (else)

                return f(s[-1], c)

            def Which(s):
                """
                ["Which", cond1, expr1, cond2, expr2, ..., condN, exprN]
                CortexJS multi-branch conditional: evaluates each `cond` in
                order and returns the `expr` paired with the first truthy
                one. Unlike 'Switch' (Python's value-equality dispatch),
                each `cond` here is itself a boolean expression, not a
                value to compare against - and unlike `If`'s pair form,
                the pairs are flat (cond, expr as separate arguments, not
                nested as [cond, expr]). Returns None (CortexJS `Nothing`)
                if no condition matches.
                """
                args = s[1:]
                if len(args) % 2 != 0:
                    raise ValueError(
                        "'Which' requires an even number of parameters "
                        "(condition, value, ...)"
                    )
                for i in range(0, len(args), 2):
                    if f(args[i], c):
                        return f(args[i + 1], c)
                return None

            def In(s):
                if len(s) != 3:
                    raise ValueError("Wrong parameters for 'In'")
                if isinstance(s[2], list) and s[2][0] == "Array":
                    return f(s[1], c) in [f(x, c) for x in s[2][1:]]

                elif isinstance(s[2], str):
                    return f(s[1], c) in f(s[2], c)
                else:
                    raise ValueError(
                        "Wrong parameters for 'In'. Parameter 2 must be a list."
                    )

            def Not_in(s):
                return not In(s)

            def Contains_any_of(s):
                if isinstance(s[1], list) and s[1][0] == "Array":
                    list1 = [f(x, c) for x in s[1][1:]]
                elif isinstance(s[1], str):
                    list1 = f(s[1], c)

                if isinstance(s[2], list) and s[2][0] == "Array":
                    list2 = [f(x, c) for x in s[2][1:]]
                elif isinstance(s[2], str):
                    list2 = f(s[2], c)

                if any(x in list1 for x in list2):
                    return True
                return False

            def Contains_all_of(s):
                if isinstance(s[1], list) and s[1][0] == "Array":
                    list1 = [f(x, c) for x in s[1][1:]]
                elif isinstance(s[1], str):
                    list1 = f(s[1], c)

                if isinstance(s[2], list) and s[2][0] == "Array":
                    list2 = [f(x, c) for x in s[2][1:]]
                elif isinstance(s[2], str):
                    list2 = f(s[2], c)

                if all(x in list1 for x in list2):
                    return True
                return False

            def Contains_none_of(s):
                return not Contains_any_of(s)

            def Str(s):
                if len(s) < 2:
                    raise ValueError("Wrong parameters for 'Str'")
                return f"{f(s[1])}"

            def String(s):
                """
                ["String", value1, value2, ...]
                Concatenates the default string representation of each
                argument. Distinct from `Str` (single argument) and from
                `StringJoin` (joins the elements of a single array).
                """
                return "".join(str(f(x, c)) for x in s[1:])

            def StringJoin(s):
                """
                ["StringJoin", array] or ["StringJoin", array, separator]
                Joins the (stringified) elements of `array` with
                `separator` (default ""). Distinct from `Join`, which
                concatenates multiple arrays together.
                """
                values = [str(v) for v in _arr_vals(s)]
                separator = f(s[2], c) if len(s) > 2 else ""
                return separator.join(values)

            def Utf8(s):
                """
                ["Utf8", string]
                List of UTF-8 byte values representing `string`.
                """
                return ["Array"] + list(f(s[1], c).encode("utf-8"))

            def Utf16(s):
                """
                ["Utf16", string]
                List of UTF-16 code units representing `string` (one
                array element per 16-bit code unit, matching how
                JavaScript/CortexJS model a string).
                """
                encoded = f(s[1], c).encode("utf-16-le")
                return ["Array"] + [
                    encoded[i] | (encoded[i + 1] << 8)
                    for i in range(0, len(encoded), 2)
                ]

            def UnicodeScalars(s):
                """
                ["UnicodeScalars", string]
                List of Unicode scalar (code point) values in `string`.
                """
                return ["Array"] + [ord(ch) for ch in f(s[1], c)]

            def StringFrom(s):
                """
                ["StringFrom", array, encoding]
                Converts `array` (a list of code units, as produced by
                `Utf8`/`Utf16`/`UnicodeScalars`) back into a string.
                `encoding` is one of "utf-8", "utf-16", "unicode-scalars".
                """
                values = _arr_vals(s)
                encoding = f(s[2], c)
                if encoding == "utf-8":
                    return bytes(int(v) for v in values).decode("utf-8")
                elif encoding == "utf-16":
                    raw = b"".join(int(v).to_bytes(2, "little") for v in values)
                    return raw.decode("utf-16-le")
                elif encoding == "unicode-scalars":
                    return "".join(chr(int(v)) for v in values)
                else:
                    raise ValueError(f"Unknown encoding: {encoding!r}")

            def Characters(s):
                """
                ["Characters", string]
                Splits `string` into a list of its characters. Approximated
                at the Unicode code-point level (Python `str` iteration)
                rather than true extended grapheme clusters (Unicode
                Annex #29), which would need a dependency this solver
                doesn't otherwise require - a multi-codepoint grapheme
                (e.g. an emoji with a modifier) is split into its
                constituent code points rather than kept whole.
                """
                return ["Array"] + list(f(s[1], c))

            def StringSplit(s):
                """
                ["StringSplit", string] or ["StringSplit", string, separator]
                Splits on whitespace if no `separator` is given, else on
                the literal `separator` string.
                """
                string = f(s[1], c)
                if len(s) > 2:
                    return ["Array"] + string.split(f(s[2], c))
                return ["Array"] + string.split()

            def StringReplace(s):
                """
                ["StringReplace", string, target, replacement]
                Replaces every occurrence of the literal substring
                `target` with `replacement` (not pattern-based - see
                `IsMatch`/`StringMatch` for pattern matching).
                """
                return f(s[1], c).replace(f(s[2], c), f(s[3], c))

            def StringCompare(s):
                """
                ["StringCompare", string1, string2]
                -1, 0, or 1 depending on whether `string1` sorts before,
                equal to, or after `string2` by code-point sequence.
                """
                a, b = f(s[1], c), f(s[2], c)
                return (a > b) - (a < b)

            def IntegerString(s):
                """
                ["IntegerString", integer] or ["IntegerString", integer, base]
                String representation of `integer` in `base` (default 10,
                2-36).
                """
                value = int(f(s[1], c))
                base = int(f(s[2], c)) if len(s) > 2 else 10
                if base == 10:
                    return str(value)
                if not (2 <= base <= 36):
                    raise ValueError(
                        "'IntegerString' base must be between 2 and 36."
                    )
                digits = "0123456789abcdefghijklmnopqrstuvwxyz"
                negative = value < 0
                value = abs(value)
                if value == 0:
                    digits_out = "0"
                else:
                    digits_out = ""
                    while value:
                        value, rem = divmod(value, base)
                        digits_out = digits[rem] + digits_out
                return ("-" if negative else "") + digits_out

            def DigitsFrom(s):
                """
                ["DigitsFrom", string] or ["DigitsFrom", string, base]
                Parses `string` as an integer in `base` (default 10).
                """
                string = f(s[1], c)
                base = int(f(s[2], c)) if len(s) > 2 else 10
                return int(string, base)

            def NumberFrom(s):
                """
                ["NumberFrom", string]
                Parses `string` as a number - integer, decimal, or
                scientific notation.
                """
                string = f(s[1], c).strip()
                try:
                    return int(string)
                except ValueError:
                    return float(string)

            def StringRepeat(s):
                """
                ["StringRepeat", string, n]
                Concatenates `n` copies of `string`. Capped at
                `_MAX_STRING_REPEAT_LENGTH` characters, since `n` is a
                user-controlled value that would otherwise make this an
                unbounded memory-exhaustion primitive.
                """
                string = f(s[1], c)
                n = int(f(s[2], c))
                if n < 0:
                    raise ValueError("'StringRepeat' count must be non-negative.")
                if len(string) * n > _MAX_STRING_REPEAT_LENGTH:
                    raise ValueError(
                        f"'StringRepeat' result would exceed the "
                        f"{_MAX_STRING_REPEAT_LENGTH}-character limit."
                    )
                return string * n

            def _pad(string, length, pad, prepend):
                if length > _MAX_STRING_REPEAT_LENGTH:
                    raise ValueError(
                        f"Pad length must not exceed "
                        f"{_MAX_STRING_REPEAT_LENGTH} characters."
                    )
                if len(string) >= length or not pad:
                    return string
                needed = length - len(string)
                full_pad = (pad * (needed // len(pad) + 1))[:needed]
                return full_pad + string if prepend else string + full_pad

            def PadStart(s):
                """
                ["PadStart", string, length] or
                ["PadStart", string, length, pad]
                Pads `string` on the left to `length` characters using
                `pad` (default a single space), truncating `pad` as
                needed to fit exactly.
                """
                pad = f(s[3], c) if len(s) > 3 else " "
                return _pad(f(s[1], c), int(f(s[2], c)), pad, prepend=True)

            def PadEnd(s):
                """
                ["PadEnd", string, length] or ["PadEnd", string, length, pad]
                Pads `string` on the right to `length` characters using
                `pad` (default a single space), truncating `pad` as
                needed to fit exactly.
                """
                pad = f(s[3], c) if len(s) > 3 else " "
                return _pad(f(s[1], c), int(f(s[2], c)), pad, prepend=False)

            _VALID_REGEX_FLAGS = set("ims")

            def _require_re2():
                if not RE2_AVAILABLE:
                    raise ImportError(
                        "RegExp/IsMatch/StringMatch/StringMatchAll require "
                        "'google-re2'. Install with "
                        "'pip install mathjson-solver[regex]' "
                        "(or 'pip install google-re2')."
                    )

            def _compile_regex(pattern_str, flags_str=""):
                if not set(flags_str) <= _VALID_REGEX_FLAGS:
                    raise ValueError(
                        f"Unsupported regex flag(s) in {flags_str!r}; only "
                        f"'i', 'm', 's' are supported."
                    )
                prefixed = f"(?{flags_str})" + pattern_str if flags_str else pattern_str
                try:
                    return re2.compile(prefixed)
                except re2.error as e:
                    raise ValueError(f"Invalid pattern {pattern_str!r}: {e}") from e

            def _resolve_pattern(expr):
                """
                Evaluates `expr` and returns a compiled RE2 pattern -
                unchanged if it's already one (e.g. produced by a nested
                `RegExp` call), else compiled fresh (no flags) if it's a
                plain string.

                Uses RE2 rather than Python's `re`: RE2 guarantees
                linear-time matching (no catastrophic backtracking is
                possible, by construction of the engine), at the cost of
                not supporting backreferences or lookaround - a
                deliberate trade-off for a solver that evaluates
                untrusted expressions with no execution budget of its own.
                """
                _require_re2()
                value = f(expr, c)
                if isinstance(value, _RE2_PATTERN_TYPE):
                    return value
                if isinstance(value, str):
                    return _compile_regex(value)
                raise ValueError(
                    "Expected a pattern string or a RegExp value."
                )

            def RegExp(s):
                """
                ["RegExp", pattern] or ["RegExp", pattern, flags]
                Compiles `pattern` (RE2 syntax - see `_resolve_pattern`)
                into a reusable pattern value, for passing to
                `IsMatch`/`StringMatch`/`StringMatchAll`. `flags` is a
                string made up of "i" (case-insensitive), "m" (multiline
                anchors), "s" (dot matches newline).
                """
                _require_re2()
                pattern_str = f(s[1], c)
                flags_str = f(s[2], c) if len(s) > 2 else ""
                return _compile_regex(pattern_str, flags_str)

            def IsMatch(s):
                """
                ["IsMatch", string, pattern]
                Whether `string` contains a match for `pattern` (a plain
                pattern string, or a `RegExp` value) anywhere within it.
                """
                pattern = _resolve_pattern(s[2])
                return pattern.search(f(s[1], c)) is not None

            def _match_record(m):
                return [
                    "Array",
                    m.group(0),
                    m.start() + 1,  # 1-indexed, matching this solver's
                    m.end(),        # other CortexJS-compat index
                                    # conventions (At, Range, ...)
                    ["Array"] + list(m.groups()),
                ]

            def StringMatch(s):
                """
                ["StringMatch", string, pattern]
                The first match of `pattern` in `string`, as
                ["Array", matched_text, start, end, ["Array", group1, ...]]
                (1-indexed `start`, exclusive `end`), or None if there's
                no match.
                """
                pattern = _resolve_pattern(s[2])
                m = pattern.search(f(s[1], c))
                return _match_record(m) if m else None

            def StringMatchAll(s):
                """
                ["StringMatchAll", string, pattern]
                All non-overlapping matches of `pattern` in `string`,
                each in the same shape as `StringMatch`.
                """
                pattern = _resolve_pattern(s[2])
                return ["Array"] + [
                    _match_record(m) for m in pattern.finditer(f(s[1], c))
                ]

            def Not(s):
                return not f(s[1])

            def _apply_fn(fn_expr, args):
                """
                Apply a "function" argument (as used by Map, Filter, and the
                CortexJS form of Reduce) to positional `args`. Supports two
                conventions:

                - CortexJS `["Function", body, param1, param2, ...]`. If no
                  parameter names are given, `args` are bound to the
                  anonymous placeholders "_" (only when there is a single
                  argument) and "_1", "_2", ... (always), for use inside
                  `body`.
                - The existing "call template" convention:
                  `[function_name, ...]`, applied as
                  `f([function_name] + args, c)`.
                """
                if isinstance(fn_expr, list) and fn_expr and fn_expr[0] == "Function":
                    body = fn_expr[1]
                    params = fn_expr[2:]
                    local_c = dict(c)
                    if params:
                        for name, value in zip(params, args):
                            local_c[name] = value
                    else:
                        if len(args) == 1:
                            local_c["_"] = args[0]
                        for i, value in enumerate(args, start=1):
                            local_c[f"_{i}"] = value
                    return f(body, local_c)
                elif isinstance(fn_expr, list) and fn_expr:
                    function_name = fn_expr[0]
                    return f([function_name] + list(args), c)
                else:
                    raise ValueError(
                        "Wrong function parameter: expected a call template "
                        "(e.g. ['Square']) or a ['Function', body, ...] expression."
                    )

            def Map(s):
                """
                ["Map", list, function, more parameters]
                The `function` must accept at least one parameter. That is for the current loop element.
                The `more parameters` are for any additional parameters that function might have.
                `function` can also be a CortexJS ["Function", body, ...params] expression.
                """
                z = f(s[1], c)
                if isinstance(z, list):
                    retlist = ["Array"]
                    for x in z[1:]:
                        try:
                            retlist.append(_apply_fn(s[2], [x] + s[3:]))
                        except MathJSONException:
                            retlist.append(x)
                    return retlist

            def StrictMap(s):
                """
                ["Map", list, function, more parameters]
                The `function` must accept at least one parameter. That is for the current loop element.
                The `more parameters` are for any additional parameters that function might have.
                `function` can also be a CortexJS ["Function", body, ...params] expression.
                """
                z = f(s[1], c)
                if isinstance(z, list):
                    retlist = ["Array"]
                    for x in z[1:]:
                        retlist.append(_apply_fn(s[2], [x] + s[3:]))
                    return retlist

            def Filter(s):
                """
                ["Filter", list, function, more parameters]
                The `function` must accept at least one parameter. That is for the current loop element.
                The `more parameters` are for any additional parameters that function might have.
                `function` can also be a CortexJS ["Function", body, ...params] expression.
                """
                z = f(s[1], c)
                if isinstance(z, list):
                    retlist = ["Array"]
                    for x in z[1:]:
                        if _apply_fn(s[2], [x] + s[3:]):
                            retlist.append(x)
                    return retlist

            def HasMatchingSublist(s):
                """
                ["HasMatchingSublist", list, required_match_count, position, contiguous, function, more parameters]
                """
                the_list = f(s[1], c)[1:]
                required_match_count = f(s[2], c)
                position = f(s[3], c)
                contiguous = f(s[4], c)
                conditions = []

                for i, x in enumerate(the_list):
                    the_function_name = s[5][0]
                    ss = [the_function_name, x] + s[6:]
                    conditions.append(f(ss, c))
                    pass

                return has_matching_sublist(
                    my_list=the_list,
                    required_match_count=required_match_count,
                    position=position,
                    contiguous=contiguous,
                    conditions=conditions,
                )

            def Strptime(s):
                datetime_str = f(s[1], c)
                parameters = f(s[2], c)
                return datetime.datetime.strptime(datetime_str, parameters).isoformat()

            def Strftime(s):
                dt = _try_parse_datetime(f(s[1], c))
                if not isinstance(dt, (datetime.datetime, datetime.date)):
                    raise ValueError(f"Strftime: could not parse input as datetime: {dt!r}")
                parameters = f(s[2], c)
                return dt.strftime(parameters)

            def Now(s):
                return datetime.datetime.now().isoformat()

            def Today(s):
                return datetime.date.today().isoformat()

            def TimeDeltaDays(s):
                return datetime.timedelta(days=f(s[1], c))

            def TimeDeltaMinutes(s):
                return datetime.timedelta(minutes=f(s[1], c))

            def TimeDeltaHours(s):
                return datetime.timedelta(hours=f(s[1], c))

            def TimeDeltaWeeks(s):
                return datetime.timedelta(weeks=f(s[1], c))

            # def Equal(s):
            #     a = comparison_safe_converter(f(s[1], c))
            #     b = comparison_safe_converter(f(s[2], c))
            #     return a == b
            #     if type(a) in [int, float, str]:
            #         a = f"{a}"
            #     elif type(a) in [bool, NoneType]:
            #         if a:
            #             a = True
            #         else:
            #             a = None

            #     if is_numeric(a):

            #     lambda s: f"{f(s[1], c)}" == f"{f(s[2], c)}",

            def IsDefined(s):
                return s[1] in solver_parameters or s[1] in c

            def IsUndefined(s):
                return not IsDefined(s)

            def Greater(s):
                v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
                try:
                    return v1 > v2
                except TypeError:
                    return False

            def GreaterEqual(s):
                v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
                try:
                    return v1 >= v2
                except TypeError:
                    return False

            def Less(s):
                v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
                try:
                    return v1 < v2
                except TypeError:
                    return False

            def LessEqual(s):
                v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
                try:
                    return v1 <= v2
                except TypeError:
                    return False

            def IdenticallyEqual(s):
                """
                ["IdenticallyEqual", a, b]
                Stricter than `StrictEqual`: true only if `a` and `b` have
                the same Python type *and* are equal - e.g. `1` and `1.0`
                are `StrictEqual` but not `IdenticallyEqual`.
                """
                a = f(s[1], c)
                b = f(s[2], c)
                return type(a) == type(b) and a == b

            def Congruent(s):
                """
                ["Congruent", a, b, modulus]
                Whether `a` and `b` are congruent modulo `modulus`, i.e.
                `(a - b) % modulus == 0`.
                """
                a = f(s[1], c)
                b = f(s[2], c)
                modulus = f(s[3], c)
                return (a - b) % modulus == 0

            def _rational_parts(s):
                """
                Numerator/denominator pair for `s[1]`. If `s[1]` is itself
                an unevaluated `["Rational", n, d]` expression, its
                declared `n`/`d` are used exactly. Otherwise, the
                evaluated value is reconstructed as the closest fraction
                with a bounded denominator - a best-effort approximation,
                not exact/symbolic, since this solver has no dedicated
                rational-number type carried through arithmetic (see
                `Rational`'s docstring).
                """
                expr = s[1]
                if (
                    isinstance(expr, list)
                    and len(expr) == 3
                    and expr[0] == "Rational"
                ):
                    return int(f(expr[1], c)), int(f(expr[2], c))
                value = f(expr, c)
                if isinstance(value, int):
                    return value, 1
                frac = Fraction(value).limit_denominator(10**6)
                return frac.numerator, frac.denominator

            def Numerator(s):
                return _rational_parts(s)[0]

            def Denominator(s):
                return _rational_parts(s)[1]

            def Rational(s):
                """
                ["Rational", numerator, denominator]
                Evaluates to `numerator / denominator` as a plain float -
                there's no exact rational-number type carried through
                arithmetic in this solver, so precision beyond a float is
                only preserved when `Numerator`/`Denominator` read this
                expression directly, rather than its evaluated value.
                """
                return f(s[1], c) / f(s[2], c)

            def BooleanAnd(s):
                """
                Boolean AND operation.
                ["And", condition1, condition2, ...]
                """
                for x in s[1:]:
                    if not f(x, c):
                        return False
                return True

            def BooleanOr(s):
                """
                Boolean OR operation.
                ["Or", condition1, condition2, ...]
                """
                for x in s[1:]:
                    if f(x, c):
                        return True
                return False

            # sin, cos, tan, arcsin, arccos, arctan
            def Sin(s):
                return math.sin(f(s[1], c))

            def Arcsin(s):
                return math.asin(f(s[1], c))

            def Cos(s):
                return math.cos(f(s[1], c))

            def Arccos(s):
                return math.acos(f(s[1], c))

            def Tan(s):
                return math.tan(f(s[1], c))

            def Arctan(s):
                return math.atan(f(s[1], c))

            def Pi(s):
                return math.pi

            def Variable(s):
                """
                ["Variable", variable_name]
                The `variable_name` must be a string.
                """
                variable_name = s[1]
                if variable_name in c:
                    return f(c[variable_name], c)
                else:
                    raise KeyError(f"Variable '{variable_name}' is not defined")

            def Function(s):
                """
                ["Function", body_expression, param_name1, param_name2, ...]
                Defines a CortexJS-style lambda: `body_expression` is evaluated
                with the given parameter names bound to whatever arguments it
                is called with. `Function` expressions are meant to be passed
                as the `function` argument of Map, Filter, and Reduce; if no
                parameter names are given, the anonymous placeholders "_",
                "_1", "_2", ... are used instead (see those functions).
                Evaluating a ["Function", ...] expression outside of such a
                context just returns it unevaluated.
                """
                return s

            def MultiplyByScalar(s):
                """
                ["MultiplyByScalar", array, scalar]
                The `array` must be an array of numeric values.
                The `scalar` is the number to multiply each element by.
                """
                array = f(s[1], c)
                scalar = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _MultiplyByScalar(array, scalar)

            def MultiplyByArray(s):
                """
                ["MultiplyByArray", array1, array2]
                The `array1` and `array2` must be arrays of the same length.
                """
                array1 = f(s[1], c)
                array2 = f(s[2], c)
                if not (isinstance(array1, list) and array1[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                if not (isinstance(array2, list) and array2[0] == "Array"):
                    raise ValueError("Parameter 2 must be an array.")
                array1 = [f(x, c) for x in array1[1:]]
                array2 = [f(x, c) for x in array2[1:]]
                if len(array1) != len(array2):
                    raise ValueError("Both arrays must be of the same length.")
                return ["Array"] + _MultiplyByArray(array1, array2)

            def AddScalar(s):
                """
                ["AddScalar", array, scalar]
                The `array` must be an array of numeric values.
                The `scalar` is the number to add to each element.
                """
                array = f(s[1], c)
                scalar = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _AddScalar(array, scalar)

            def SubtractScalar(s):
                """
                ["SubtractScalar", array, scalar]
                The `array` must be an array of numeric values.
                The `scalar` is the number to subtract from each element.
                """
                array = f(s[1], c)
                scalar = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _SubtractScalar(array, scalar)

            def AddArray(s):
                """
                ["AddArray", array1, array2]
                The `array1` and `array2` must be arrays of the same length.
                """
                array1 = f(s[1], c)
                array2 = f(s[2], c)
                if not (isinstance(array1, list) and array1[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                if not (isinstance(array2, list) and array2[0] == "Array"):
                    raise ValueError("Parameter 2 must be an array.")
                array1 = [f(x, c) for x in array1[1:]]
                array2 = [f(x, c) for x in array2[1:]]
                if len(array1) != len(array2):
                    raise ValueError("Both arrays must be of the same length.")
                return ["Array"] + _AddArray(array1, array2)

            def SubtractArray(s):
                """
                ["SubtractArray", array1, array2]
                The `array1` and `array2` must be arrays of the same length.
                """
                array1 = f(s[1], c)
                array2 = f(s[2], c)
                if not (isinstance(array1, list) and array1[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                if not (isinstance(array2, list) and array2[0] == "Array"):
                    raise ValueError("Parameter 2 must be an array.")
                array1 = [f(x, c) for x in array1[1:]]
                array2 = [f(x, c) for x in array2[1:]]
                if len(array1) != len(array2):
                    raise ValueError("Both arrays must be of the same length.")
                return ["Array"] + _SubtractArray(array1, array2)

            def GenerateRange(s):
                """
                ["GenerateRange", end]
                or
                ["GenerateRange", start, end, step]
                The `start`, `end`, and `step` are numeric values.
                """
                if len(s) == 2:
                    end = f(s[1], c)
                    start = 0
                    step = 1
                elif len(s) == 4:
                    start = f(s[1], c)
                    end = f(s[2], c)
                    step = f(s[3], c)
                else:
                    raise ValueError(
                        "GenerateRange requires either 1 or 3 parameters (end or start, end, step)."
                    )
                if step == 0:
                    raise ValueError("Step cannot be zero.")
                if (start < end and step < 0) or (start > end and step > 0):
                    raise ValueError("Step direction is incorrect for the given range.")
                result = ["Array"]
                if start < end:
                    current = start
                    while current < end:
                        result.append(current)
                        current += step
                else:
                    current = start
                    while current > end:
                        result.append(current)
                        current += step
                return result

            def AtIndex(s):
                """
                ["AtIndex", array, index]
                The `array` must be an array of values.
                The `index` is the index of the element to retrieve.
                """
                array = f(s[1], c)
                index = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                # array = [f(x, c) for x in array[1:]]
                # return array[index]
                array = [x for x in array[1:]]
                return f(array[index], c)

            def Slice(s):
                """
                ["Slice", array, start, end]
                The `array` must be an array of values.
                The `start` and `end` are the slice indices.
                """
                array = f(s[1], c)
                start = f(s[2], c)
                end = f(s[3], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + array[start:end]

            def CumulativeProduct(s):
                """
                ["CumulativeProduct", array]
                The `array` must be an array of numeric values.
                """
                array = f(s[1], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _CumulativeProduct(array)
                # return _CumulativeProduct(array)

            def CumulativeSum(s):
                """
                ["CumulativeSum", array]
                The `array` must be an array of numeric values.
                """
                array = f(s[1], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _CumulativeSum(array)
                # return

            def Interp(s):
                """
                ["Interp", x_array, y_array, target_x]
                The `x_array` and `y_array` must be arrays of the same length.
                The `target_x` is the x value to interpolate for.
                """
                x_array = f(s[1], c)
                y_array = f(s[2], c)
                target_x = f(s[3], c)
                if not (isinstance(x_array, list) and x_array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                if not (isinstance(y_array, list) and y_array[0] == "Array"):
                    raise ValueError("Parameter 2 must be an array.")
                x_array = [f(x, c) for x in x_array[1:]]
                y_array = [f(y, c) for y in y_array[1:]]
                return linear_interpolate(x_array, y_array, target_x)

            def FindIntervalIndex(s):
                """
                ["FindIntervalIndex", array, target_value]
                The `array` must be an array of numeric values.
                The `target_value` is the value to find the interval index for.
                """
                array = f(s[1], c)
                target_value = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                zz = find_interpolation_bounds_2indexes(array, target_value)
                return zz[0]

            def TrapezoidalIntegrate(s):
                """
                ["TrapezoidalIntegrate", function_expression, start, end, n, variable]
                """
                if not NUMPY_AVAILABLE:
                    raise ImportError(
                        "TrapezoidalIntegrate requires 'numpy'. Install with 'pip install numpy'."
                    )
                function_expression = s[1]
                start = f(s[2], c)
                end = f(s[3], c)
                n = f(s[4], c)
                variable = s[5]

                t = np.linspace(start, end, n + 1)

                # Calculate the integral using the trapezoidal rule

                values = []
                for x in t:
                    variable_name = variable[1]
                    variable_value = x
                    c[variable_name] = variable_value
                    values.append(f(function_expression, c))
                h = (end - start) / n
                return h * (0.5 * values[0] + np.sum(values[1:-1]) + 0.5 * values[-1])

                # return total_area

            def Reduce(s):
                """
                Two calling conventions, disambiguated by argument count:

                CortexJS form (3 or 4 arguments):
                ["Reduce", list, function]
                ["Reduce", list, function, initial_value]
                `function` is applied as `function(accumulator, current_item)`
                on each element; without `initial_value`, the first element
                seeds the accumulator. `function` can be a call template
                (e.g. ["Add"]) or a ["Function", body, ...params] expression
                (see `_apply_fn`).

                Original Python form (6 arguments):
                ["Reduce", list, initial_value, function, str_name_of_accumulator, str_name_of_current, str_name_of_index]
                """
                if len(s) <= 4:
                    the_list = f(s[1], c)
                    if not (isinstance(the_list, list) and the_list[0] == "Array"):
                        raise ValueError("Parameter 1 must be an array.")
                    elements = the_list[1:]
                    fn_expr = s[2]

                    if len(s) == 4:
                        accumulator = f(s[3], c)
                        remaining = elements
                    else:
                        if not elements:
                            raise ValueError(
                                "'Reduce' on an empty collection requires an initial value."
                            )
                        accumulator = f(elements[0], c)
                        remaining = elements[1:]

                    for x in remaining:
                        accumulator = _apply_fn(fn_expr, [accumulator, x])
                    return accumulator

                the_list = f(s[1], c)[1:]
                initial_value = f(s[2], c)
                function_expression = s[3]

                _accumulator = s[4]
                name_accumulator = _accumulator[1]

                _current = s[5]
                name_current = _current[1]

                _index = s[6]
                name_index = _index[1]

                c[name_accumulator] = initial_value

                for i, x in enumerate(the_list):
                    c[name_current] = x
                    c[name_index] = i
                    c[name_accumulator] = f(function_expression, c)

                return c[name_accumulator]

            def Product(s):
                """
                ["Product", array]
                Multiplies together the numeric elements of `array`.
                """
                the_list = f(s[1], c)
                if not (isinstance(the_list, list) and the_list[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                result = 1
                for x in the_list[1:]:
                    result *= f(x, c)
                return result

            def Appended(s):
                """
                ["Appended", array, value]
                The `array` must be an array of values.
                The `value` is the value to append to the array.
                """
                array = f(s[1], c)

                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")

                value = f(s[2], c)

                array = [x for x in array[1:]]
                array.append(value)
                return ["Array"] + array

            constructs = {
                "Sum": Sum,
                "Add": Add,
                "Subtract": Subtract,
                "Constants": Constants,
                "Switch": Switch,
                "StrictSwitch": StrictSwitch,
                "If": If,
                "Multiply": lambda s: reduce(
                    lambda a, b: float(a) * float(b), [f(x, c) for x in s[1:]]
                ),
                "Divide": lambda s: f(s[1], c) / f(s[2], c),
                "Negate": lambda s: -f(s[1], c),
                "Power": lambda s: pow(f(s[1], c), f(s[2], c)),
                "Root": lambda s: pow(f(s[1], c), 1.0 / f(s[2], c)),
                "Sqrt": lambda s: pow(f(s[1], c), 1.0 / 2),
                "Square": lambda s: pow(f(s[1], c), 2),
                "Exp": lambda s: math.exp(f(s[1], c)),
                # CortexJS-compatible: ["Log", x] is log base 10; ["Log", x, b] is
                # log base b. Use "Ln" for natural log. (BREAKING as of 2.0.0 -
                # "Log" previously meant natural log.)
                "Log": lambda s: (
                    math.log10(f(s[1], c))
                    if len(s) == 2
                    else math.log(f(s[1], c), f(s[2], c))
                ),
                "Log2": lambda s: math.log2(f(s[1], c)),
                "Log10": lambda s: math.log10(f(s[1], c)),
                "Ln": lambda s: math.log(f(s[1], c)),
                "Lb": lambda s: math.log2(f(s[1], c)),  # CortexJS name for Log2
                "Lg": lambda s: math.log10(f(s[1], c)),  # CortexJS name for Log10
                "LogOnePlus": lambda s: math.log1p(f(s[1], c)),
                # "Equal": lambda s: f"{f(s[1], c)}" == f"{f(s[2], c)}",
                "Equal": lambda s: comparison_safe_converter(f(s[1], c))
                == comparison_safe_converter(f(s[2], c)),
                "IsTrue": lambda s: bool(f(s[1], c)),
                "IsFalse": lambda s: not bool(f(s[1], c)),
                "StrictEqual": lambda s: f(s[1], c) == f(s[2], c),
                "IdenticallyEqual": IdenticallyEqual,
                "Congruent": Congruent,
                # "Greater": lambda s: f(s[1], c) > f(s[2], c),
                "Greater": Greater,
                # "GreaterEqual": lambda s: f(s[1], c) >= f(s[2], c),
                "GreaterEqual": GreaterEqual,
                # "Less": lambda s: f(s[1], c) < f(s[2], c),
                "Less": Less,
                # "LessEqual": lambda s: f(s[1], c) <= f(s[2], c),
                "LessEqual": LessEqual,
                # "NotEqual": lambda s: f(s[1], c) != f(s[2], c),
                "NotEqual": lambda s: comparison_safe_converter(f(s[1], c))
                != comparison_safe_converter(f(s[2], c)),
                "And": BooleanAnd,
                "Or": BooleanOr,
                "Abs": lambda s: abs(f(s[1], c)),
                "Round": lambda s: (
                    round(f(s[1], c), f(s[2], c))
                    if len(s) == 3
                    else int(round(f(s[1], c)))
                ),
                "Max": Max,
                "Min": Min,
                "Average": Average,
                "Mean": Average,  # CortexJS name for Average
                "Median": Median,
                "Length": Length,
                "Count": Length,  # CortexJS name for Length
                "Any": Any,
                "All": All,
                "Array": Arr,
                "List": lambda s: ["Array"] + [f(x, c) for x in s[1:]],  # CortexJS name for Array
                "In": In,
                "Not_in": Not_in,
                "Element": In,  # CortexJS name for In (["Element", value, set])
                "NotElement": Not_in,  # CortexJS name for Not_in
                "Contains_any_of": Contains_any_of,
                "Contains_all_of": Contains_all_of,
                "Contains_none_of": Contains_none_of,
                "NotIn": Not_in,
                "ContainsAnyOf": Contains_any_of,
                "ContainsAllOf": Contains_all_of,
                "ContainsNoneOf": Contains_none_of,
                "Int": Int,
                "Float": Float,
                "Floor": Floor,
                "Ceil": Ceil,
                "Str": Str,
                # --- Strings ---
                "String": String,
                "StringJoin": StringJoin,
                "ToUpperCase": lambda s: f(s[1], c).upper(),
                "ToLowerCase": lambda s: f(s[1], c).lower(),
                "CaseFold": lambda s: f(s[1], c).casefold(),
                "Trim": lambda s: f(s[1], c).strip(),
                "TrimStart": lambda s: f(s[1], c).lstrip(),
                "TrimEnd": lambda s: f(s[1], c).rstrip(),
                "StringSplit": StringSplit,
                "StringReplace": StringReplace,
                "StringCompare": StringCompare,
                "StringRepeat": StringRepeat,
                "PadStart": PadStart,
                "PadEnd": PadEnd,
                "Characters": Characters,
                "GraphemeClusters": Characters,  # CortexJS synonym for Characters
                "Utf8": Utf8,
                "Utf16": Utf16,
                "UnicodeScalars": UnicodeScalars,
                "StringFrom": StringFrom,
                "IntegerString": IntegerString,
                "DigitsFrom": DigitsFrom,
                "NumberFrom": NumberFrom,
                "RegExp": RegExp,
                "IsMatch": IsMatch,
                "StringMatch": StringMatch,
                "StringMatchAll": StringMatchAll,
                "Not": Not,
                # "IsDefined": lambda s: s[1] in c,
                "IsDefined": IsDefined,
                "IsUndefined": IsUndefined,
                "Map": Map,
                "StrictMap": StrictMap,
                "Filter": Filter,
                "HasMatchingSublist": HasMatchingSublist,
                "Strptime": Strptime,
                "Strftime": Strftime,
                "Today": Today,
                "Now": Now,
                "TimeDeltaWeeks": TimeDeltaWeeks,
                "TimeDeltaHours": TimeDeltaHours,
                "TimeDeltaMinutes": TimeDeltaMinutes,
                "TimeDeltaDays": TimeDeltaDays,
                "Function": Function,
                "Variable": Variable,
                "MultiplyByScalar": MultiplyByScalar,
                "MultiplyByArray": MultiplyByArray,
                "AddScalar": AddScalar,
                "SubtractScalar": SubtractScalar,
                "AddArray": AddArray,
                "SubtractArray": SubtractArray,
                "GenerateRange": GenerateRange,
                "AtIndex": AtIndex,
                "Slice": Slice,
                "CumulativeProduct": CumulativeProduct,
                "CumulativeSum": CumulativeSum,
                "Interp": Interp,
                "FindIntervalIndex": FindIntervalIndex,
                "TrapezoidalIntegrate": TrapezoidalIntegrate,
                "Reduce": Reduce,
                "Product": Product,
                "Appended": Appended,
                "Sin": Sin,
                "Cos": Cos,
                "Tan": Tan,
                "Arcsin": Arcsin,
                "Arccos": Arccos,
                "Arctan": Arctan,
                "Arctan2": lambda s: math.atan2(f(s[1], c), f(s[2], c)),
                "Pi": Pi,
                "Which": Which,  # CortexJS multi-branch conditional (not Switch - see Which's docstring)
                # --- Trigonometric: reciprocal, hyperbolic, area-hyperbolic ---
                "Cot": lambda s: 1 / math.tan(f(s[1], c)),
                "Sec": lambda s: 1 / math.cos(f(s[1], c)),
                "Csc": lambda s: 1 / math.sin(f(s[1], c)),
                "Arccot": lambda s: math.atan(1 / f(s[1], c)),
                "Arcsec": lambda s: math.acos(1 / f(s[1], c)),
                "Arccsc": lambda s: math.asin(1 / f(s[1], c)),
                "Sinh": lambda s: math.sinh(f(s[1], c)),
                "Cosh": lambda s: math.cosh(f(s[1], c)),
                "Tanh": lambda s: math.tanh(f(s[1], c)),
                "Coth": lambda s: 1 / math.tanh(f(s[1], c)),
                "Sech": lambda s: 1 / math.cosh(f(s[1], c)),
                "Csch": lambda s: 1 / math.sinh(f(s[1], c)),
                "Arsinh": lambda s: math.asinh(f(s[1], c)),
                "Arcosh": lambda s: math.acosh(f(s[1], c)),
                "Artanh": lambda s: math.atanh(f(s[1], c)),
                "Arcoth": lambda s: math.atanh(1 / f(s[1], c)),
                "Arsech": lambda s: math.acosh(1 / f(s[1], c)),
                "Arcsch": lambda s: math.asinh(1 / f(s[1], c)),
                "Hypot": lambda s: math.hypot(f(s[1], c), f(s[2], c)),
                "Sinc": lambda s: (
                    1.0 if f(s[1], c) == 0 else math.sin(f(s[1], c)) / f(s[1], c)
                ),
                # --- Constants ---
                "Degrees": lambda s: math.pi / 180,
                "ExponentialE": lambda s: math.e,
                "GoldenRatio": lambda s: (1 + math.sqrt(5)) / 2,
                "MachineEpsilon": lambda s: sys.float_info.epsilon,
                "CatalanConstant": lambda s: 0.915965594177219015054603514932384110774,
                "EulerGamma": lambda s: 0.5772156649015328606065120900824024310421,
                "Rational": Rational,
                "Numerator": Numerator,
                "Denominator": Denominator,
                # --- Number theory / special functions ---
                "Chop": lambda s: 0 if abs(f(s[1], c)) < 1e-10 else f(s[1], c),
                "Mod": lambda s: f(s[1], c) % f(s[2], c),
                "Clamp": Clamp,
                "GCD": lambda s: math.gcd(int(f(s[1], c)), int(f(s[2], c))),
                "LCM": lambda s: math.lcm(int(f(s[1], c)), int(f(s[2], c))),
                "Factorial": lambda s: math.factorial(int(f(s[1], c))),
                "Binomial": lambda s: math.comb(int(f(s[1], c)), int(f(s[2], c))),
                "IsPrime": IsPrime,
                "Erf": lambda s: math.erf(f(s[1], c)),
                "Erfc": lambda s: math.erfc(f(s[1], c)),
                # --- Number theory ---
                "PowerMod": lambda s: pow(
                    int(f(s[1], c)), int(f(s[2], c)), int(f(s[3], c))
                ),
                "ModularInverse": lambda s: pow(
                    int(f(s[1], c)), -1, int(f(s[2], c))
                ),
                "IntegerSqrt": lambda s: math.isqrt(int(f(s[1], c))),
                "FactorInteger": FactorInteger,
                "PrimeFactors": PrimeFactors,
                "PrimeNu": PrimeNu,
                "PrimeOmega": PrimeOmega,
                "Radical": Radical,
                "IsSquareFree": IsSquareFree,
                "Divisors": Divisors,
                "Sigma0": Sigma0,
                "Sigma1": Sigma1,
                "SigmaMinus1": SigmaMinus1,
                "DivisorSigma": DivisorSigma,
                "Divides": lambda s: f(s[2], c) % f(s[1], c) == 0,
                "Totient": Totient,
                "IsPerfectPower": IsPerfectPower,
                "NthPrime": NthPrime,
                "NextPrime": NextPrime,
                "PrimePi": PrimePi,
                "ExtendedGCD": ExtendedGCD,
                "ChineseRemainder": ChineseRemainder,
                "CarmichaelLambda": CarmichaelLambda,
                "JacobiSymbol": JacobiSymbol,
                "LegendreSymbol": JacobiSymbol,  # same algorithm when n is prime
                "MultiplicativeOrder": MultiplicativeOrder,
                "PrimitiveRoot": PrimitiveRoot,
                "LucasL": LucasL,
                "CatalanNumber": lambda s: math.comb(
                    2 * int(f(s[1], c)), int(f(s[1], c))
                )
                // (int(f(s[1], c)) + 1),
                "BernoulliB": BernoulliB,
                "ContinuedFraction": ContinuedFraction,
                "FromContinuedFraction": FromContinuedFraction,
                "IntegerDigits": IntegerDigits,
                "DigitCount": DigitCount,
                "DigitSum": DigitSum,
                "FromDigits": FromDigits,
                "IsSquare": IsSquare,
                "IsTriangular": IsTriangular,
                "IsPentagonal": IsPentagonal,
                "IsOctahedral": IsOctahedral,
                "IsCenteredSquare": IsCenteredSquare,
                "IsPerfect": IsPerfect,
                "IsAbundant": IsAbundant,
                "IsHappy": IsHappy,
                # --- Boolean logic ---
                "Xor": lambda s: bool(f(s[1], c)) ^ bool(f(s[2], c)),
                "Nand": lambda s: not all(f(x, c) for x in s[1:]),
                "Nor": lambda s: not any(f(x, c) for x in s[1:]),
                "Implies": lambda s: (not f(s[1], c)) or bool(f(s[2], c)),
                "Equivalent": lambda s: bool(f(s[1], c)) == bool(f(s[2], c)),
                # --- Statistics ---
                "Variance": Variance,
                "StandardDeviation": StandardDeviation,
                "PopulationVariance": PopulationVariance,
                "PopulationStandardDeviation": PopulationStandardDeviation,
                "Mode": Mode,
                "Quartiles": Quartiles,
                "InterquartileRange": InterquartileRange,
                "Covariance": Covariance,
                "Correlation": Correlation,
                "Skewness": Skewness,
                "Kurtosis": Kurtosis,
                "LinearRegression": LinearRegression,
                "PolynomialFit": PolynomialFit,
                # --- Collections ---
                "First": First,
                "Second": Second,
                "Third": Third,
                "Last": Last,
                "Rest": Rest,
                "Most": Most,
                "Reverse": Reverse,
                "Sort": Sort,
                "IsEmpty": IsEmpty,
                "Range": Range,
                "Join": Join,
                "Unique": Unique,
                "Zip": Zip,
                "At": At,
                "Take": Take,
                "Drop": Drop,
                "TakeWhile": TakeWhile,
                "DropWhile": DropWhile,
                "Contains": Contains,
                "IndexOf": IndexOf,
                "IndexWhere": IndexWhere,
                "Find": Find,
                "CountIf": CountIf,
                "Position": Position,
                "RotateLeft": RotateLeft,
                "RotateRight": RotateRight,
                "MaxBy": MaxBy,
                "MinBy": MinBy,
                "ArgMax": ArgMax,
                "ArgMin": ArgMin,
                "Ordering": Ordering,
                "FlatMap": FlatMap,
                "Scan": Scan,
                "Differences": Differences,
                "Fold": Fold,
                "Dedup": Dedup,
                "Append": Appended,  # CortexJS name for Appended
                "Insert": Insert,
                "DeleteAt": DeleteAt,
                "ReplaceAt": ReplaceAt,
                "Partition": Partition,
                "Chunk": Chunk,
                "GroupBy": GroupBy,
                "ChunkBy": ChunkBy,
                "Tally": Tally,
                # --- Set algebra (over Array - no dedicated Set type) ---
                "Union": Union,
                "Intersection": Intersection,
                "SetMinus": SetMinus,
                "SymmetricDifference": SymmetricDifference,
            }
            if not s:
                # Empty equation given - []
                return None
            if s[0] in constructs:
                try:
                    return constructs[s[0]](s)

                # except RecursionError:
                #     return s[0]
                # except Exception as e:
                except TypeError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0]) from e
                except ValueError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0]) from e
                except IndexError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0]) from e
                except ZeroDivisionError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0]) from e
            else:
                # raise MathJSONException(
                #     NotImplementedError(f"'{s[0]}' is not supported"), s
                # )
                return s
        elif s in c:
            # Local scope (Constants, Reduce accumulator/current/index,
            # Function parameters, ...) shadows top-level solver parameters
            # of the same name, matching normal lexical scoping.
            return f(c[s], c)
        elif s in solver_parameters:
            try:
                return f(solver_parameters[s], c)
            except RecursionError:
                return solver_parameters[s]
        else:
            # raise KeyError(f"Parameter '{s}' is not defined")
            return s

    if legacy_v1:

        def legacy_v1_f(s, *args):
            return f(translate_v1_mathjson(s), *args)

        return legacy_v1_f

    return f


def extract_variables(s: Union[list, int, float, str], li: set, ignore_list: set):
    constructs = [
        "Add",
        "Sum",
        "Subtract",
        "Constants",
        "Switch",
        "If",
        "Multiply",
        "Divide",
        "Negate",
        "Power",
        "Root",
        "Sqrt",
        "Square",
        "Exp",
        "Log",
        "Log2",
        "Log10",
        "Ln",
        "Equal",
        "IsTrue",
        "IsFalse",
        "Greater",
        "GreaterEqual",
        "Less",
        "LessEqual",
        "NotEqual",
        "And",
        "Or",
        "Abs",
        "Round",
        "Max",
        "Min",
        "Average",
        "Median",
        "Length",
        "Any",
        "All",
        "Array",
        "In",
        "Not_in",
        "Contains_any_of",
        "Contains_all_of",
        "Contains_none_of",
        "NotIn",
        "ContainsAnyOf",
        "ContainsAllOf",
        "ContainsNoneOf",
        "Element",
        "NotElement",
        "Int",
        "Float",
        "Floor",
        "Ceil",
        "Str",
        "String",
        "StringJoin",
        "ToUpperCase",
        "ToLowerCase",
        "CaseFold",
        "Trim",
        "TrimStart",
        "TrimEnd",
        "StringSplit",
        "StringReplace",
        "StringCompare",
        "StringRepeat",
        "PadStart",
        "PadEnd",
        "Characters",
        "GraphemeClusters",
        "Utf8",
        "Utf16",
        "UnicodeScalars",
        "StringFrom",
        "IntegerString",
        "DigitsFrom",
        "NumberFrom",
        "RegExp",
        "IsMatch",
        "StringMatch",
        "StringMatchAll",
        "Not",
        "IsDefined",
        "IsUndefined",
        "StrictEqual",
        "IdenticallyEqual",
        "Congruent",
        "NotEqual",
        "StrictSwitch",
        "Map",
        "StrictMap",
        "Filter",
        "HasMatchingSublist",
        "Strptime",
        "Strftime",
        "Today",
        "Now",
        "TimeDeltaWeeks",
        "TimeDeltaHours",
        "TimeDeltaMinutes",
        "TimeDeltaDays",
        "Function",
        "Variable",
        "MultiplyByScalar",
        "MultiplyByArray",
        "AddScalar",
        "SubtractScalar",
        "AddArray",
        "SubtractArray",
        "GenerateRange",
        "AtIndex",
        "Slice",
        "CumulativeProduct",
        "CumulativeSum",
        "Interp",
        "FindIntervalIndex",
        "TrapezoidalIntegrate",
        "TrapezoidalIntegrate",
        "Reduce",
        "Product",
        "Appended",
        "Sin",
        "Cos",
        "Tan",
        "Arcsin",
        "Arccos",
        "Arctan",
        "Arctan2",
        "Pi",
        "Which",
        "Lb",
        "Lg",
        "LogOnePlus",
        "Mean",
        "Count",
        "List",
        "Cot",
        "Sec",
        "Csc",
        "Arccot",
        "Arcsec",
        "Arccsc",
        "Sinh",
        "Cosh",
        "Tanh",
        "Coth",
        "Sech",
        "Csch",
        "Arsinh",
        "Arcosh",
        "Artanh",
        "Arcoth",
        "Arsech",
        "Arcsch",
        "Hypot",
        "Sinc",
        "Degrees",
        "ExponentialE",
        "GoldenRatio",
        "MachineEpsilon",
        "CatalanConstant",
        "EulerGamma",
        "Rational",
        "Numerator",
        "Denominator",
        "Chop",
        "Mod",
        "Clamp",
        "GCD",
        "LCM",
        "Factorial",
        "Binomial",
        "IsPrime",
        "Erf",
        "Erfc",
        "PowerMod",
        "ModularInverse",
        "IntegerSqrt",
        "FactorInteger",
        "PrimeFactors",
        "PrimeNu",
        "PrimeOmega",
        "Radical",
        "IsSquareFree",
        "Divisors",
        "Sigma0",
        "Sigma1",
        "SigmaMinus1",
        "DivisorSigma",
        "Divides",
        "Totient",
        "IsPerfectPower",
        "NthPrime",
        "NextPrime",
        "PrimePi",
        "ExtendedGCD",
        "ChineseRemainder",
        "CarmichaelLambda",
        "JacobiSymbol",
        "LegendreSymbol",
        "MultiplicativeOrder",
        "PrimitiveRoot",
        "LucasL",
        "CatalanNumber",
        "BernoulliB",
        "ContinuedFraction",
        "FromContinuedFraction",
        "IntegerDigits",
        "DigitCount",
        "DigitSum",
        "FromDigits",
        "IsSquare",
        "IsTriangular",
        "IsPentagonal",
        "IsOctahedral",
        "IsCenteredSquare",
        "IsPerfect",
        "IsAbundant",
        "IsHappy",
        "Xor",
        "Nand",
        "Nor",
        "Implies",
        "Equivalent",
        "Variance",
        "StandardDeviation",
        "PopulationVariance",
        "PopulationStandardDeviation",
        "Mode",
        "Quartiles",
        "InterquartileRange",
        "Covariance",
        "Correlation",
        "Skewness",
        "Kurtosis",
        "LinearRegression",
        "PolynomialFit",
        "First",
        "Second",
        "Third",
        "Last",
        "Rest",
        "Most",
        "Reverse",
        "Sort",
        "IsEmpty",
        "Range",
        "Join",
        "Unique",
        "Zip",
        "At",
        "Take",
        "Drop",
        "TakeWhile",
        "DropWhile",
        "Contains",
        "IndexOf",
        "IndexWhere",
        "Find",
        "CountIf",
        "Position",
        "RotateLeft",
        "RotateRight",
        "MaxBy",
        "MinBy",
        "ArgMax",
        "ArgMin",
        "Ordering",
        "FlatMap",
        "Scan",
        "Differences",
        "Fold",
        "Dedup",
        "Append",
        "Insert",
        "DeleteAt",
        "ReplaceAt",
        "Partition",
        "Chunk",
        "GroupBy",
        "ChunkBy",
        "Tally",
        "Union",
        "Intersection",
        "SetMinus",
        "SymmetricDifference",
    ]
    if isinstance(s, str):
        if s in ignore_list:
            return li
        # "True"/"False" are boolean literals (see `f`'s handling of them),
        # not solver-parameter references, so they're never free variables.
        if s not in constructs and s not in ("True", "False"):
            li.add(s)
        return li
    elif isinstance(s, list):
        if s[0] == "Constants":
            for x in s[1:-1]:
                ignore_list.add(x[0])
                li.update(extract_variables(x[1], li, ignore_list))
            li.update(extract_variables(s[-1], li, ignore_list))
        elif s[0] == "If":
            # Mirror the calling-convention detection used by the solver's
            # own `If` (see its docstring / comments): CortexJS flat form
            # ["If", cond, then[, else]] vs. the Python pair form
            # ["If", [cond, val], ..., else_val].
            is_cortexjs_form = len(s) > 1 and (
                not isinstance(s[1], list)
                or (
                    bool(s[1])
                    and isinstance(s[1][0], str)
                    and s[1][0] in constructs
                )
            )
            if is_cortexjs_form:
                for x in s[1:]:
                    li.update(extract_variables(x, li, ignore_list))
            else:
                for elif_block in s[1:-1]:  # s[1] is list
                    for x in elif_block:
                        li.update(extract_variables(x, li, ignore_list))
                li.update(extract_variables(s[-1], li, ignore_list))
        elif s[0] == "Function":
            # ["Function", body, param1, param2, ...]: parameter names (and
            # the anonymous placeholders "_", "_1", "_2", ...) are bound
            # locally, not free variables.
            for p in s[2:]:
                if isinstance(p, str):
                    ignore_list.add(p)
            ignore_list.update({f"_{i}" for i in range(1, 10)})
            ignore_list.add("_")
            if len(s) > 1:
                li.update(extract_variables(s[1], li, ignore_list))
        elif s[0] not in constructs:
            # Unrecognized construct (e.g. "Color", "Quantity" - anything
            # this solver doesn't implement): f() never evaluates or
            # substitutes into such expressions either (its fallback for
            # an unknown head is to return the whole list unchanged), so
            # none of its arguments are free variables to supply. Treat
            # the whole thing as opaque data rather than recursing into
            # it, so a decorative/unrelated subtree (e.g. a color literal
            # meant for something else downstream) doesn't get reported
            # as a required parameter.
            pass
        else:
            for x in s[1:]:
                li.update(extract_variables(x, li, ignore_list))
        return li
    else:
        return li
