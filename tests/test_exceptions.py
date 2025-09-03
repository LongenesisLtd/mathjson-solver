import sys
import os
import pytest
import re

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver, MathJSONException


def test_raises_divide():
    solver = create_solver({})
    with pytest.raises(
        MathJSONException,
        match=re.escape("Problem in Divide. ['Divide', 1, 0]. division by zero"),
    ):
        r = solver(["Divide", 1, 0])


def test_raises_outside_interpolation_range1():
    solver = create_solver({})
    with pytest.raises(
        MathJSONException,
        match=re.escape(
            "Problem in Interp. ['Interp', ['Array', 1, 2, 3], ['Array', 10, 20, 30], 0]. Target value is outside interpolation range."
        ),
    ):
        r = solver(["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 0])


def test_raises_outside_interpolation_range2():
    solver = create_solver({})
    with pytest.raises(
        MathJSONException,
        match=re.escape(
            "Problem in Interp. ['Interp', ['Array', 1, 2, 3], ['Array', 10, 20, 30], 4]. Target value is outside interpolation range."
        ),
    ):
        r = solver(["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 4])


# # Extrapolation beyond the boundaries
# (
#     {},
#     ["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 0],
#     10,
# ),
# (
#     {},
#     ["Interp", ["Array", 1, 2, 3], ["Array", 10, 20, 30], 4],
#     30,
# ),
# Non-uniformly spaced x values


# def test_raises_unsupported():
#     solver = create_solver({})
#     with pytest.raises(
#         MathJSONException,
#         match=re.escape(
#             "Problem in MathJSON. ['Unsupported', 1]. 'Unsupported' is not supported"
#         ),
#     ):
#         r = solver(["Unsupported", 1])


def test_raises_malformed():
    solver = create_solver({})
    with pytest.raises(
        MathJSONException,
        match=re.escape("Problem in Power. ['Power', 1]. list index out of range"),
    ):
        r = solver(["Power", 1])


def test_handle_exception():
    solver = create_solver({})
    try:
        r = solver(["Power", 1])
    except MathJSONException:
        assert True
    else:
        assert False
