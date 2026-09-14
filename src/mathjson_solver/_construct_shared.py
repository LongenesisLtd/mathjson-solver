"""
Shared, `f`/`c`-dependent utility functions called from constructs in more
than one topic module (unlike the pure helpers in _common.py etc., these
need to recursively evaluate MathJSON sub-expressions via `f`).
"""


def _arr_vals(f, c, solver_parameters, s):
    lst = f(s[1], c)
    if not (isinstance(lst, list) and lst[0] == "Array"):
        raise ValueError("Parameter 1 must be an array.")
    return [f(x, c) for x in lst[1:]]


def _arr_vals_of(f, c, solver_parameters, expr):
    """
    Like `_arr_vals`, but for an arbitrary expression instead
    of assuming the array is at `s[1]` - needed by the
    variadic set operations below.
    """
    lst = f(expr, c)
    if not (isinstance(lst, list) and lst[0] == "Array"):
        raise ValueError("Parameter must be an array.")
    return [f(x, c) for x in lst[1:]]


def _apply_fn(f, c, solver_parameters, fn_expr, args):
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
