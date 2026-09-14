"""
Comparison, equality, definedness, and boolean-logic constructs.
"""

from ._common import (
    comparison_safe_converter_for_pairs,
)


def Not(f, c, solver_parameters, s):
    return not f(s[1])


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


def IsDefined(f, c, solver_parameters, s):
    return s[1] in solver_parameters or s[1] in c


def IsUndefined(f, c, solver_parameters, s):
    return not IsDefined(f, c, solver_parameters, s)


def Greater(f, c, solver_parameters, s):
    v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
    try:
        return v1 > v2
    except TypeError:
        return False


def GreaterEqual(f, c, solver_parameters, s):
    v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
    try:
        return v1 >= v2
    except TypeError:
        return False


def Less(f, c, solver_parameters, s):
    v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
    try:
        return v1 < v2
    except TypeError:
        return False


def LessEqual(f, c, solver_parameters, s):
    v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
    try:
        return v1 <= v2
    except TypeError:
        return False


def IdenticallyEqual(f, c, solver_parameters, s):
    """
    ["IdenticallyEqual", a, b]
    Stricter than `StrictEqual`: true only if `a` and `b` have
    the same Python type *and* are equal - e.g. `1` and `1.0`
    are `StrictEqual` but not `IdenticallyEqual`.
    """
    a = f(s[1], c)
    b = f(s[2], c)
    return type(a) == type(b) and a == b


def Congruent(f, c, solver_parameters, s):
    """
    ["Congruent", a, b, modulus]
    Whether `a` and `b` are congruent modulo `modulus`, i.e.
    `(a - b) % modulus == 0`.
    """
    a = f(s[1], c)
    b = f(s[2], c)
    modulus = f(s[3], c)
    return (a - b) % modulus == 0


def BooleanAnd(f, c, solver_parameters, s):
    """
    Boolean AND operation.
    ["And", condition1, condition2, ...]
    """
    for x in s[1:]:
        if not f(x, c):
            return False
    return True


def BooleanOr(f, c, solver_parameters, s):
    """
    Boolean OR operation.
    ["Or", condition1, condition2, ...]
    """
    for x in s[1:]:
        if f(x, c):
            return True
    return False
