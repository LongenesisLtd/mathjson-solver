"""
Higher-order constructs (Map, Filter, Reduce, Fold, ...) built on
`_apply_fn`, which applies a CortexJS `Function` expression or call-
template to positional arguments.
"""

from ._construct_shared import _apply_fn
from ._exceptions import MathJSONException


def Fold(f, c, solver_parameters, s):
    """
    ["Fold", function, array] or ["Fold", function, array, initial]
    The function-first form of `Reduce`'s CortexJS calling
    convention (`["Reduce", array, function, ...]`) - same
    behaviour, arguments swapped.
    """
    if len(s) == 3:
        return Reduce(f, c, solver_parameters, ["Reduce", s[2], s[1]])
    return Reduce(f, c, solver_parameters, ["Reduce", s[2], s[1], s[3]])


def Map(f, c, solver_parameters, s):
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
                retlist.append(_apply_fn(f, c, solver_parameters, s[2], [x] + s[3:]))
            except MathJSONException:
                retlist.append(x)
        return retlist


def StrictMap(f, c, solver_parameters, s):
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
            retlist.append(_apply_fn(f, c, solver_parameters, s[2], [x] + s[3:]))
        return retlist


def Filter(f, c, solver_parameters, s):
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
            if _apply_fn(f, c, solver_parameters, s[2], [x] + s[3:]):
                retlist.append(x)
        return retlist


def Reduce(f, c, solver_parameters, s):
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
            accumulator = _apply_fn(f, c, solver_parameters, fn_expr, [accumulator, x])
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
