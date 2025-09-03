import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import extract_variables


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, ["Add", 2, 4, 3], set()),
        ({}, ["Sum", 2, "a", 3], set(["a"])),
        ({"a": 5}, ["Sum", 2, "a", 3], set()),
        ({"a": 5, "b": 6}, ["Sum", 2, "a", "c"], set(["c"])),
        ({}, ["Constants", ["c", 1], ["d", ["Add", 2, "a"]], "d"], set(["a"])),
        # Now with "ugly" variables that mimic the ones used for deep referencing.
        (
            {},
            ["Add", "[slug1][0][question1]", "y", 4, "[slug1][-3:-1][question1]"],
            set(["[slug1][0][question1]", "y", "[slug1][-3:-1][question1]"]),
        ),
        (
            {},
            ["If", [["Equal", "[uzwuoy][-1][question1]", 200], 200], 1],
            set(["[uzwuoy][-1][question1]"]),
        ),
        (
            {},
            [
                "If",
                [["Equal", "[uzwuoy][-1][question1]", 200], 201],
                [["Equal", "[uzwuoy][-2][question1]", 100], 101],
                1,
            ],
            set(["[uzwuoy][-1][question1]", "[uzwuoy][-2][question1]"]),
        ),
    ],
)
def test_extract_variables(parameters, expression, expected_result):
    assert (
        extract_variables(expression, set(), set([x for x in parameters.keys()]))
        == expected_result
    )
