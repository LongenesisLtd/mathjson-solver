"""
Control-flow constructs (Constants, Switch, StrictSwitch, Which) plus
Variable/Function, which share their scoping concerns. `If` itself stays in
__main__.py - it inspects the module-level `constructs` dict directly to
detect CortexJS vs. Python calling convention, and moving it here would
create a circular import back to __main__.
"""

from ._common import (
    comparison_safe_converter,
)


def Constants(f, c, solver_parameters, s):
    # Bind into a copy, not the caller's `c` - these bindings must be
    # visible to the rest of this Constants block but not leak back out
    # once it returns (see `f`'s own comment on this convention).
    c = dict(c)
    for x in s[1:-1]:
        try:
            c[x[0]] = f(x[1], c)
        except Exception:
            c[x[0]] = None
    return f(s[-1], c)


def Switch(f, c, solver_parameters, s):
    expression = f(s[1], c)
    for x in s[3:]:
        if len(x) != 2:
            raise ValueError("Case of 'Switch' should have exactly two parameters")
        if comparison_safe_converter(expression) == comparison_safe_converter(
            f(x[0], c)
        ):
            return f(x[1], c)
    else:
        return f(s[2], c)


def StrictSwitch(f, c, solver_parameters, s):
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


def Which(f, c, solver_parameters, s):
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
            "'Which' requires an even number of parameters " "(condition, value, ...)"
        )
    for i in range(0, len(args), 2):
        if f(args[i], c):
            return f(args[i + 1], c)
    return None


def Variable(f, c, solver_parameters, s):
    """
    ["Variable", variable_name]
    The `variable_name` must be a string.
    """
    variable_name = s[1]
    if variable_name in c:
        return f(c[variable_name], c)
    else:
        raise KeyError(f"Variable '{variable_name}' is not defined")


def Function(f, c, solver_parameters, s):
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
