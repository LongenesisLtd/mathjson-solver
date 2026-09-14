import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


def test_no_blacklist_by_default():
    solver = create_solver({})
    assert solver(["Add", 1, 2]) == 3.0


def test_blacklisted_construct_raises():
    solver = create_solver({}, blacklist=["Add"])
    with pytest.raises(Exception):
        solver(["Add", 1, 2])


def test_non_blacklisted_constructs_still_work():
    solver = create_solver({}, blacklist=["Add"])
    assert solver(["Multiply", 2, 3]) == 6.0
    assert solver(["Subtract", 5, 2]) == 3


def test_blacklist_multiple_constructs():
    solver = create_solver({}, blacklist=["PowerSet", "Permutations", "Combinations", "CartesianProduct"])
    for expr in [
        ["PowerSet", ["Array", 1, 2, 3]],
        ["Permutations", ["Array", 1, 2, 3]],
        ["Combinations", ["Array", 1, 2, 3], 2],
        ["CartesianProduct", ["Array", 1], ["Array", 2]],
    ]:
        with pytest.raises(Exception):
            solver(expr)
    # Unrelated constructs unaffected.
    assert solver(["Add", 1, 2]) == 3.0


def test_blacklisting_unknown_name_has_no_effect():
    # Not validated against the known-construct list - a typo silently
    # does nothing, by design (see create_mathjson_solver's docstring).
    solver = create_solver({}, blacklist=["Addd"])
    assert solver(["Add", 1, 2]) == 3.0


def test_blacklist_empty_iterable_same_as_none():
    solver = create_solver({}, blacklist=[])
    assert solver(["Add", 1, 2]) == 3.0


def test_blacklist_with_solver_parameters():
    solver = create_solver({"x": 5}, blacklist=["Multiply"])
    assert solver(["Add", "x", 1]) == 6.0
    with pytest.raises(Exception):
        solver(["Multiply", "x", 2])


def test_blacklist_with_legacy_v1():
    solver = create_solver({}, legacy_v1=True, blacklist=["Multiply"])
    # legacy_v1's Log->Ln rewrite still applies.
    import math

    assert solver(["Log", 1000]) == pytest.approx(math.log(1000))
    with pytest.raises(Exception):
        solver(["Multiply", 2, 3])


def test_blacklist_error_message_names_the_construct():
    solver = create_solver({}, blacklist=["Add"])
    with pytest.raises(Exception) as exc_info:
        solver(["Add", 1, 2])
    assert "Add" in str(exc_info.value)
