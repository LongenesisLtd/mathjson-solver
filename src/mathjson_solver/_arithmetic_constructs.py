"""
Basic arithmetic and numeric-conversion constructs: variadic
add/subtract/multiply-style reducers, rounding/truncation, and rational-
number construction.
"""

from fractions import Fraction
import datetime
import math
from functools import reduce
from statistics import median
from ._common import (
    _try_parse_datetime,
    is_numeric,
)


def Add(f, c, solver_parameters, s):
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


def Sum(f, c, solver_parameters, s):
    l_res = ["Array"]
    for x in s[1:]:
        res = f(x, c)
        if isinstance(res, list):
            l_res.append(
                Add(f, c, solver_parameters, ["Array"] + [xx for xx in res[1:]])
            )
        else:
            l_res.append(res)
    return Add(f, c, solver_parameters, l_res)


def Subtract(f, c, solver_parameters, s):
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


def Max(f, c, solver_parameters, s):
    args = s[1:]
    if len(args) == 1:
        if isinstance(args[0], str):
            return max([f(x, c) for x in f(args[0], c) if is_numeric(f(x, c))])
        else:
            return max([f(x, c) for x in args[0][1:] if is_numeric(f(x, c))])
    else:
        # CortexJS-style variadic form: ["Max", a, b, c, ...]
        return max([f(x, c) for x in args])


def Min(f, c, solver_parameters, s):
    args = s[1:]
    if len(args) == 1:
        if isinstance(args[0], str):
            return min([f(x, c) for x in f(args[0], c) if is_numeric(f(x, c))])
        else:
            return min([f(x, c) for x in args[0][1:] if is_numeric(f(x, c))])
    else:
        # CortexJS-style variadic form: ["Min", a, b, c, ...]
        return min([f(x, c) for x in args])


def Average(f, c, solver_parameters, s):
    if isinstance(s[1], str):
        # A reference to "answer" has been passed
        s_ = [float(f(x, c)) for x in f(s[1], c) if is_numeric(f(x, c))]
    else:
        s_ = [float(f(x, c)) for x in s[1][1:] if is_numeric(f(x, c))]
    try:
        return sum(s_) / len(s_)
    except ZeroDivisionError:
        return None


def Median(f, c, solver_parameters, s):
    if isinstance(s[1], str):
        return median([f(x, c) for x in f(s[1], c) if is_numeric(f(x, c))])
    else:
        return median([f(x, c) for x in s[1][1:] if is_numeric(f(x, c))])


def Clamp(f, c, solver_parameters, s):
    """
    ["Clamp", value] or ["Clamp", value, lower, upper]
    Bounds `value` between `lower` (default -1) and `upper` (default 1),
    matching CortexJS `Clamp`.
    """
    value = f(s[1], c)
    lower = f(s[2], c) if len(s) > 2 else -1
    upper = f(s[3], c) if len(s) > 3 else 1
    return max(lower, min(upper, value))


def Int(f, c, solver_parameters, s):
    try:
        return int(f(s[1], c))
    except ValueError:
        return int(float(f(s[1], c)))


def Float(f, c, solver_parameters, s):
    return float(f(s[1], c))


def Floor(f, c, solver_parameters, s):
    return math.floor(f(s[1], c))


def Ceil(f, c, solver_parameters, s):
    return math.ceil(f(s[1], c))


def _rational_parts(f, c, solver_parameters, s):
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
    if isinstance(expr, list) and len(expr) == 3 and expr[0] == "Rational":
        return int(f(expr[1], c)), int(f(expr[2], c))
    value = f(expr, c)
    if isinstance(value, int):
        return value, 1
    frac = Fraction(value).limit_denominator(10**6)
    return frac.numerator, frac.denominator


def Numerator(f, c, solver_parameters, s):
    return _rational_parts(f, c, solver_parameters, s)[0]


def Denominator(f, c, solver_parameters, s):
    return _rational_parts(f, c, solver_parameters, s)[1]


def Rational(f, c, solver_parameters, s):
    """
    ["Rational", numerator, denominator]
    Evaluates to `numerator / denominator` as a plain float -
    there's no exact rational-number type carried through
    arithmetic in this solver, so precision beyond a float is
    only preserved when `Numerator`/`Denominator` read this
    expression directly, rather than its evaluated value.
    """
    return f(s[1], c) / f(s[2], c)


def Product(f, c, solver_parameters, s):
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
