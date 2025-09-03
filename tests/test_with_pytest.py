import sys
import os
import pytest


sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # ({"a": 12}, ["IsDefined", "a"], True),
        ({"a": 12}, ["IsDefined", "b"], False),
        ({}, ["Abs", -3.5], 3.5),
        ({}, ["Round", -5.123456, 2], -5.12),
        ({}, ["Round", -5.123456, 0], -5),
        ({}, ["Round", 5.4], 5),
        ({}, ["Round", 5.5], 6),
        ({}, ["Constants", ["a", 1], ["b", 2], "a"], 1),
        ({}, ["Constants", ["a", 1], ["b", 2], ["c", 100], ["Sum", "a", "b"]], 3),
        ({}, ["Constants", ["a", 1], ["b", ["Add", 2, "a"]], "b"], 3),
        ({"x": 1}, ["Add", 2, "x"], 3),
        ({"value": 1}, ["Switch", "value", 0, [1, 11], [2, 22]], 11),
        ({"value": 3}, ["Switch", "value", 0, [1, 11], [2, 22]], 0),
        (
            {"[uzwuoy][-1][14]": 1},
            ["Switch", "[uzwuoy][-1][14]", 0, [1, 11], [2, 22]],
            11,
        ),
        ({"14": 1}, ["Switch", "14", 0, [1, 11], [2, 22]], 11),
        ({"14": "1"}, ["Switch", "14", 0, ["0", 0], ["1", 1], ["2", 2]], 1),
        ({"29": "1"}, ["Switch", "29", 0, ["0", 0], ["1", 1], ["2", 2]], 1),
        ({"29": "2"}, ["Switch", "29", 0, ["0", 0], ["1", 1], ["2", 2]], 2),
        ({"a": "a"}, ["Switch", "a", 0, ["0", 0], ["1", 1], ["2", 2]], 0),
        (
            {"14": "1", "29": "1"},
            [
                "Add",
                ["Switch", "14", 0, ["0", 0], ["1", 1], ["2", 2]],
                ["Switch", "29", 0, ["0", 0], ["1", 1], ["2", 2]],
            ],
            2,
        ),
        ({}, ["Switch", "14", 6, ["0", 0], ["1", 1], ["2", 2]], 6),
        ({}, ["Switch", "1", 6, ["0", 0], ["1", 1], ["2", 2]], 1),  # BKUS
        (
            {"1": "2"},
            ["Switch", "1", 6, ["0", 0], ["1", 1], ["2", 2]],
            1,
        ),  # Because all "1"s become "2"
        (
            {"1": "3"},
            ["Switch", "1", 6, ["0", 0], ["1", 1], ["2", 2]],
            1,
        ),  # Because string "1" is equal string "1"
        # The following test works.
        # It is commented out because otherwise black auto-formatter would expand it to 100+ lines
        # (
        #     {"14": "1", "29": "1", "30": "1", "31": "1", "32": "1", "33": "1", "35": "1", "45": "1", "50": "1", "52": "1", "71": "1", "91": "1", "112": "1"},
        #     ["Add",
        #       ["Switch","14",0,["0",0],["1",1],["2",2]],
        #       ["Switch","29",0,["0",0],["1",1],["2",2]],
        #       ["Switch","30",0,["0",0],["1",1],["2",2]],
        #       ["Switch","31",0,["0",0],["1",1],["2",2]],
        #       ["Switch","32",0,["0",0],["1",1],["2",2]],
        #       ["Switch","33",0,["0",0],["1",1],["2",2]],
        #       ["Switch","35",0,["0",0],["1",1],["2",2]],
        #       ["Switch","45",0,["0",0],["1",1],["2",2]],
        #       ["Switch","50",0,["0",0],["1",1],["2",2]],
        #       ["Switch","52",0,["0",0],["1",1],["2",2]],
        #       ["Switch","71",0,["0",0],["1",1],["2",2]],
        #       ["Switch","91",0,["0",0],["1",1],["2",2]],
        #       ["Switch","112",0,["0",0],["1",1],["2",2]]
        #     ],
        #     13
        # ),
        # The next tests check the type-forgiving nature of Switch.
        ({"value": 2}, ["Switch", "value", 0, ["1", 11], ["2", 22]], 22),
        ({"value": "2"}, ["Switch", "value", 0, [1, 11], [2, 22]], 22),
        # The next tests verify that the StrictSwitch is not forgiving.
        ({"value": 2}, ["StrictSwitch", "value", 0, ["1", 11], ["2", 22]], 0),
        ({"value": "2"}, ["StrictSwitch", "value", 0, [1, 11], [2, 22]], 0),
        ({"color": "red"}, ["Switch", "color", 0, ["blue", 10], ["red", 30]], 30),
        ({"color": "green"}, ["Switch", "color", 0, ["blue", 10], ["red", 30]], 0),
        ({"color": "green"}, ["Switch", "undefined", 0, ["blue", 10], ["red", 30]], 0),
        ({}, ["If", [["Equal", 1, 0], 10], [["Equal", 2, 2], 20], 9000], 20),
        # # The following tests that If don't fail on incompatible data types
        # ({}, ["If", [["Equal", 1, "1"], 10], [["Equal", "1", "1"], 20], -1], 20),
        # ({"a": 1}, ["If", [["Equal", "a", "1"], 10], [["Equal", "a", 1], 20], -1], 20),
        # ({"a": 1}, ["If", [["Equal", "a", 1], 10], [["Equal", "a", "1"], 20], -1], 10),
        ({"a": 10, "b": 10}, ["If", [["Equal", "a", "b"], 10], 9000], 10),
        ({"a": 10, "b": 20}, ["If", [["Equal", "a", "b"], 10], 9000], 9000),
        ({"a": 10}, ["If", [["Equal", "a", "b"], 10], 9000], 9000),
        # The following test checks if Sum failure (1+"b") is handled correctly in If.
        ({"a": 10}, ["If", [["Equal", "a", ["Sum", 1, "b"]], 10], 9000], 9000),
        ({}, ["Array", 1, 2, 3, 5, 2], ["Array", 1, 2, 3, 5, 2]),
        ({}, ["Max", ["Array", 1, 2, 3, 5, 2]], 5),
        ({}, ["Max", ["Array", 1, 2, ["Sum", 2, 4, 3], 5, 2]], 9),
        ({"a": ["Array", 1, 2, 3, 5, 2]}, ["Max", "a"], 5),
        ({}, ["Min", ["Array", 1, 2, 3, 5, 2]], 1),
        ({"a": ["Array", 2, 1, 3, 5, 2]}, ["Min", "a"], 1),
        ({}, ["Median", ["Array", 1, 2, 3, 5, 2]], 2),
        ({"a": ["Array", 1, 2, 3, 5, 2]}, ["Median", "a"], 2),
        ({}, ["Average", ["Array", 2, "three", 4, "6"]], 4),
        ({}, ["Average", ["Array", 1, 2, 3, 5, 2]], 2.6),
        (
            {},
            [
                "Average",
                [
                    "Array",
                    "-2",
                    -1,
                    "0",
                    1,
                    "2",
                    "3",
                    4,
                    5,
                    6,
                    "seven",
                    8,
                    "9",
                    "10",
                    15,
                    10,
                ],
            ],
            5.0,
        ),
        ({}, ["Average", ["Array"]], None),
        ({"a": ["Array", 2, 8]}, ["Average", "a"], 5),
        ({"a": 10, "b": 20}, ["Average", ["Array", "a", "b"]], 15),
        ({}, ["Length", ["Array", 1, 2, 3, 5, 2, 9]], 6),
        ({}, ["Length", ["Array", 1, 2, 3, None]], 4),
        ({"a": ["Array", 1, 2, 3, 5, 2, 9]}, ["Length", "a"], 6),
        ({}, ["Length", ["Array"]], 0),
        # Next test illustrates an invalid formula, where 'Length' receives an invalid array.
        ({}, ["Length", ["Greater", ["Array", 3, 5, 6, 4, 8, 1, 0, 1], 5]], 2),
        ({}, ["Sum", ["Array", True, False, True, False, False]], 2),
        ({}, ["Int", "12"], 12),
        ({}, ["Int", "12.2"], 12),
        ({}, ["Float", "12.2"], 12.2),
        ({}, ["Any", ["Array", 0, 0, False, 0, 0]], False),
        ({}, ["Any", ["Array", 0, 1, False, 0, 0]], True),
        ({}, ["All", ["Array", 0, 1, False, 0, 0]], False),
        ({}, ["All", ["Array", 0, 1, False, "", 0]], False),
        ({}, ["All", ["Array", 2, 1, True, "zz", 2]], True),
        ({}, ["Str", 12], "12"),
        ({}, ["Str", "12"], "12"),
        ({}, ["Str", "aabb"], "aabb"),
        ({}, "aabb", "aabb"),
        ({}, 11, 11),
        ({}, True, True),
        ({}, False, False),
        ({}, ["Not", True], False),
        ({}, ["Not", 0], True),
        ({}, ["Not", ["In", 2, ["Array", 1, 2, 3]]], False),
        ({}, ["Array", 2, 4, 3], ["Array", 2, 4, 3]),
        ({}, ["StrictMap", ["Array", 1, 2, 3], ["Square"]], ["Array", 1, 4, 9]),
        ({}, ["Filter", ["Array", 1, 2, 3], ["LessEqual"], 2], ["Array", 1, 2]),
        ({}, ["Filter", ["Array", 1, 2, 3, "None"], ["LessEqual"], 2], ["Array", 1, 2]),
        ({}, ["Map", ["Array", 1, 2, 3], ["Square"]], ["Array", 1, 4, 9]),
        (
            {},
            ["Map", ["Array", 1, 2, 3, None, "a"], ["Square"]],
            ["Array", 1, 4, 9, None, "a"],
        ),
        ({}, ["Map", ["Array", 1, 2, 3], ["Power"], 2], ["Array", 1, 4, 9]),
        (
            {},
            ["Map", ["Array", 1, 2, 3], ["GreaterEqual"], 2],
            ["Array", False, True, True],
        ),
        (
            {},
            ["Sum", ["Map", ["Array", 1, 2, 3, 4, 1, 1, 0, 1], ["GreaterEqual"], 2]],
            3,
        ),
        ({}, ["Sum", ["Array", True, False, True, False, False]], 2),
        # ["HasMatchingSublist", list, required_match_count, position, contiguous, function, more parameters]
        (
            {},
            [
                "HasMatchingSublist",
                ["Array", 1, 2, 3, 4, 5, 6],
                3,
                0,
                True,
                ["GreaterEqual"],
                1,
            ],
            True,  # first 3 elements are greater than 3
        ),
        (
            {},
            [
                "HasMatchingSublist",
                ["Array", 1, 2, 3, 4, 5, 6],
                3,
                0,
                True,
                ["GreaterEqual"],
                2,
            ],
            False,  # first 3 elements are greater than 3 - False
        ),
        (
            {},
            [
                "HasMatchingSublist",
                ["Array", 1, 2, 3, 4, 5, 6],
                3,
                0,
                False,  # anywhere
                ["GreaterEqual"],
                4,
            ],
            True,
        ),
        (
            {},
            [
                "HasMatchingSublist",
                ["Array", 1, 2, 3, 4, 5, 6],
                4,
                0,
                False,  # anywhere
                ["GreaterEqual"],
                4,
            ],
            False,
        ),
        (
            {},
            [
                "HasMatchingSublist",
                ["Array", 1, 2, 3, 4, 5, 6],
                3,
                -1,
                True,
                ["GreaterEqual"],
                4,
            ],
            True,
        ),
        (
            {},
            [
                "HasMatchingSublist",
                ["Array", 1, 2, 3, 4, 5, 6],
                5,
                -1,
                True,
                ["GreaterEqual"],
                4,
            ],
            False,
        ),
        (
            {},
            ["Strftime", ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"], "%Y"],
            "2025",
        ),
        ({}, ["Strftime", ["Today"], "%Y"], "2025"),
        ({}, ["Strftime", ["Now"], "%Y"], "2025"),
        (
            {},
            [
                "Strftime",
                [
                    "Add",
                    ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"],
                    ["TimeDeltaDays", 3],
                ],
                "%d",
            ],
            "13",
        ),
        (
            {},
            [
                "Strftime",
                [
                    "Subtract",
                    ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"],
                    ["TimeDeltaDays", 3],
                ],
                "%d",
            ],
            "07",
        ),
        (
            {},
            [
                "Strftime",
                [
                    "Add",
                    ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"],
                    ["TimeDeltaMinutes", 5],
                ],
                "%M",
            ],
            "10",
        ),
        (
            {},
            [
                "Strftime",
                [
                    "Add",
                    ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"],
                    ["TimeDeltaHours", 2],
                ],
                "%H",
            ],
            "12",
        ),
        (
            {},
            [
                "Strftime",
                [
                    "Add",
                    ["Strptime", "2025-01-10T10:05", "%Y-%m-%dT%H:%M"],
                    ["TimeDeltaWeeks", 1],
                ],
                "%d",
            ],
            "17",
        ),
    ],
)
def test_solver_simple(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result
