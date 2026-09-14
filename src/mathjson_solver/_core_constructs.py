"""
Core structural-introspection constructs (Head, Tail, Hold, Type, IsSame) -
these inspect or return expressions without evaluating them the way most
constructs do.
"""

import numbers

# --- Core: structural introspection ---
#
# Unlike almost everything else on CortexJS's Core reference
# page (CAS functions, mutable state, LaTeX serialization -
# all out of scope, see docs), these don't need a type
# system or a rendering surface: they work directly on the
# raw, unevaluated MathJSON tree every construct already
# receives as `s`, the same mechanism RegExp already uses to
# peek at its pattern argument without evaluating it.


def Head(f, c, solver_parameters, s):
    expr = s[1]
    return expr[0] if isinstance(expr, list) and expr else None


def Tail(f, c, solver_parameters, s):
    expr = s[1]
    return ["Array"] + expr[1:] if isinstance(expr, list) else ["Array"]


def Hold(f, c, solver_parameters, s):
    return s[1]


def Type(f, c, solver_parameters, s):
    value = f(s[1], c)
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, numbers.Number):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list) and value and value[0] == "Array":
        return "array"
    if value is None:
        return "nothing"
    return type(value).__name__


def IsSame(f, c, solver_parameters, s):
    """
    ["IsSame", expr1, expr2]
    Whether expr1 and expr2 are structurally identical *as
    written* - same shape, literals, and order - compared
    without evaluating either side. Distinct from `Equal`/
    `StrictEqual` (which compare evaluated *values*) and
    from `IdenticallyEqual` (a stricter same-type
    `StrictEqual`, also over evaluated values): this is a
    pre-evaluation, syntactic check. CortexJS distinguishes
    `IsSame` from `Same` by canonical-form normalization
    (e.g. treating `x+y` and `y+x` as the same); this solver
    has no such canonicalization step, so both map to the
    same plain structural comparison here.
    """
    return s[1] == s[2]
