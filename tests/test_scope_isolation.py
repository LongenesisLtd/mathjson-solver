"""
Regression tests for `c`-scope isolation.

`f()` passes `c` through by reference rather than copying it on every
call; the handful of constructs that introduce new bindings
(`Constants`, `Reduce`'s legacy accumulator form, `TrapezoidalIntegrate`)
are responsible for copying it themselves before writing into it (see
`_apply_fn`, which has always done this for `Function`). These tests
exist specifically to catch a leak in either direction - a binding
escaping into the caller's scope, or two sibling scopes contaminating
each other - since the existing per-construct tests weren't written to
catch that failure mode.
"""

import sys
import os
import pytest

NUMPY_AVAILABLE = False
try:
    import numpy  # noqa: F401

    NUMPY_AVAILABLE = True
except ImportError:
    pass

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


def test_constants_binding_does_not_shadow_solver_parameter_afterward():
    solver = create_solver({"x": 5})
    expression = ["Add", ["Constants", ["x", 999], "x"], "x"]
    assert solver(expression) == 1004


def test_constants_binding_does_not_leak_to_sibling():
    solver = create_solver({})
    expression = ["List", ["Constants", ["temp", 1], "temp"], ["IsDefined", "temp"]]
    assert solver(expression) == ["Array", 1, False]


def test_sibling_constants_blocks_do_not_cross_contaminate():
    solver = create_solver({})
    expression = [
        "Add",
        ["Constants", ["x", 1], "x"],
        ["Constants", ["x", 2], "x"],
    ]
    assert solver(expression) == 3


def test_nested_constants_inner_binding_does_not_leak_to_outer():
    solver = create_solver({})
    expression = [
        "Constants",
        ["x", 1],
        ["Add", ["Constants", ["x", 100], "x"], "x"],
    ]
    # Inner Constants shadows x=100 for its own body (100 + 1 = 101);
    # outer x=1 is untouched by the inner block having run.
    assert solver(expression) == 101


def test_reduce_legacy_form_bindings_do_not_leak():
    solver = create_solver({})
    expression = [
        "List",
        [
            "Reduce",
            ["Array", 1, 2, 3],
            0,
            ["Add", ["Variable", "accumulator"], ["Variable", "current_item"]],
            ["Variable", "accumulator"],
            ["Variable", "current_item"],
            ["Variable", "index"],
        ],
        ["IsDefined", "accumulator"],
        ["IsDefined", "current_item"],
        ["IsDefined", "index"],
    ]
    assert solver(expression) == ["Array", 6, False, False, False]


def test_sibling_reduce_legacy_calls_do_not_cross_contaminate():
    solver = create_solver({})
    expression = [
        "Add",
        [
            "Reduce",
            ["Array", 1, 2, 3],
            0,
            ["Add", ["Variable", "accumulator"], ["Variable", "current_item"]],
            ["Variable", "accumulator"],
            ["Variable", "current_item"],
            ["Variable", "index"],
        ],
        [
            "Reduce",
            ["Array", 10, 20],
            0,
            ["Add", ["Variable", "accumulator"], ["Variable", "current_item"]],
            ["Variable", "accumulator"],
            ["Variable", "current_item"],
            ["Variable", "index"],
        ],
    ]
    assert solver(expression) == 36


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="NumPy not available")
def test_trapezoidal_integrate_variable_binding_does_not_leak():
    solver = create_solver({})
    expression = [
        "List",
        ["TrapezoidalIntegrate", ["Multiply", "t", "t"], 0, 1, 1000, ["Variable", "t"]],
        ["IsDefined", "t"],
    ]
    result = solver(expression)
    assert result[0] == "Array"
    assert abs(result[1] - 1 / 3) < 1e-3
    assert result[2] is False
