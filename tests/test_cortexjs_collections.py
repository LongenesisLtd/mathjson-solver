import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- Take / Drop / TakeWhile / DropWhile ---
        ({}, ["Take", ["Array", 1, 2, 3, 4, 5], 3], ["Array", 1, 2, 3]),
        ({}, ["Take", ["Array", 1, 2, 3, 4, 5], -2], ["Array", 4, 5]),
        ({}, ["Drop", ["Array", 1, 2, 3, 4, 5], 2], ["Array", 3, 4, 5]),
        ({}, ["Drop", ["Array", 1, 2, 3, 4, 5], -2], ["Array", 1, 2, 3]),
        (
            {},
            ["TakeWhile", ["Array", 1, 2, 3, 10, 4], ["Function", ["Less", "_", 5]]],
            ["Array", 1, 2, 3],
        ),
        (
            {},
            ["DropWhile", ["Array", 1, 2, 3, 10, 4], ["Function", ["Less", "_", 5]]],
            ["Array", 10, 4],
        ),
        # --- Searching / testing ---
        ({}, ["Contains", ["Array", 1, 2, 3], 2], True),
        ({}, ["Contains", ["Array", 1, 2, 3], 9], False),
        ({}, ["IndexOf", ["Array", "a", "b", "c"], "b"], 2),
        ({}, ["IndexOf", ["Array", "a", "b", "c"], "z"], None),
        (
            {},
            ["IndexWhere", ["Array", 1, 2, 3, 4], ["Function", ["Greater", "_", 2]]],
            3,
        ),
        (
            {},
            ["Find", ["Array", 1, 2, 3, 4], ["Function", ["Greater", "_", 2]]],
            3,
        ),
        (
            {},
            ["CountIf", ["Array", 1, 2, 3, 4, 5], ["Function", ["Greater", "_", 2]]],
            3,
        ),
        (
            {},
            ["Position", ["Array", 1, 2, 3, 4, 5], ["Function", ["Greater", "_", 2]]],
            ["Array", 3, 4, 5],
        ),
        # --- Reordering ---
        ({}, ["RotateLeft", ["Array", 1, 2, 3, 4, 5], 2], ["Array", 3, 4, 5, 1, 2]),
        ({}, ["RotateRight", ["Array", 1, 2, 3, 4, 5], 2], ["Array", 4, 5, 1, 2, 3]),
        ({}, ["RotateLeft", ["Array"], 3], ["Array"]),
        (
            {},
            ["MaxBy", ["Array", -5, 3, -2], ["Function", ["Abs", "_"]]],
            -5,
        ),
        (
            {},
            ["MinBy", ["Array", -5, 3, -2], ["Function", ["Abs", "_"]]],
            -2,
        ),
        ({}, ["ArgMax", ["Array", 3, 7, 2]], 2),
        ({}, ["ArgMin", ["Array", 3, 7, 2]], 3),
        ({}, ["Ordering", ["Array", 30, 10, 20]], ["Array", 2, 3, 1]),
        # --- Transformation ---
        (
            {},
            ["FlatMap", ["Array", 1, 2, 3], ["Function", ["Range", "_"]]],
            ["Array", 1, 1, 2, 1, 2, 3],
        ),
        (
            {},
            ["Scan", ["Array", 1, 2, 3, 4], ["Add"]],
            ["Array", 1, 3.0, 6.0, 10.0],
        ),
        (
            {},
            ["Scan", ["Array", 1, 2, 3], ["Add"], 10],
            ["Array", 10, 11.0, 13.0, 16.0],
        ),
        ({}, ["Differences", ["Array", 1, 3, 6, 10]], ["Array", 2, 3, 4]),
        ({}, ["Fold", ["Add"], ["Array", 1, 2, 3, 4]], 10.0),
        ({}, ["Fold", ["Add"], ["Array", 1, 2, 3], 10], 16.0),
        (
            {},
            ["Dedup", ["Array", 1, 1, 2, 2, 2, 1, 3, 3]],
            ["Array", 1, 2, 1, 3],
        ),
        ({}, ["Append", ["Array", 1, 2], 3], ["Array", 1, 2, 3]),
        ({}, ["Insert", ["Array", 1, 2, 4], 3, 3], ["Array", 1, 2, 3, 4]),
        ({}, ["Insert", ["Array", 1, 2, 4], -1, 99], ["Array", 1, 2, 99, 4]),
        ({}, ["DeleteAt", ["Array", 1, 2, 3, 4], 2], ["Array", 1, 3, 4]),
        ({}, ["DeleteAt", ["Array", 1, 2, 3, 4], -1], ["Array", 1, 2, 3]),
        ({}, ["ReplaceAt", ["Array", 1, 2, 3], 2, 99], ["Array", 1, 99, 3]),
        (
            {},
            ["Partition", ["Array", 1, 2, 3, 4, 5], 2],
            ["Array", ["Array", 1, 2], ["Array", 3, 4], ["Array", 5]],
        ),
        (
            {},
            ["Chunk", ["Array", 1, 2, 3, 4, 5], 2],
            ["Array", ["Array", 1, 2, 3], ["Array", 4, 5]],
        ),
        (
            {},
            ["GroupBy", ["Array", 1, 2, 3, 4, 5, 6], ["Function", ["Mod", "_", 2]]],
            [
                "Array",
                ["Array", 1, ["Array", 1, 3, 5]],
                ["Array", 0, ["Array", 2, 4, 6]],
            ],
        ),
        (
            {},
            ["ChunkBy", ["Array", 1, 1, 2, 2, 1, 1], ["Function", "_"]],
            ["Array", ["Array", 1, 1], ["Array", 2, 2], ["Array", 1, 1]],
        ),
        (
            {},
            ["Tally", ["Array", "a", "b", "a", "c", "b", "a"]],
            [
                "Array",
                ["Array", "a", 3],
                ["Array", "b", 2],
                ["Array", "c", 1],
            ],
        ),
    ],
)
def test_cortexjs_collections(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_partition_requires_positive_size():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Partition", ["Array", 1, 2, 3], 0])


def test_chunk_requires_positive_count():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Chunk", ["Array", 1, 2, 3], 0])


def test_scan_on_empty_collection_requires_initial():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["Scan", ["Array"], ["Add"]])
