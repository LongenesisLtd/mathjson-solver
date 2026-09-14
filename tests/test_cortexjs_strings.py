import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

from mathjson_solver import create_solver

RE2_AVAILABLE = False
try:
    import re2

    RE2_AVAILABLE = True
except ImportError:
    pass


@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        # --- String / StringJoin ---
        ({}, ["String", "a", 1, "b"], "a1b"),
        ({}, ["StringJoin", ["Array", "a", "b", "c"]], "abc"),
        ({}, ["StringJoin", ["Array", "a", "b", "c"], "-"], "a-b-c"),
        # --- Case / trim ---
        ({}, ["ToUpperCase", "hello"], "HELLO"),
        ({}, ["ToLowerCase", "HELLO"], "hello"),
        ({}, ["CaseFold", "STRASSE"], "strasse"),
        ({}, ["Trim", "  hi  "], "hi"),
        ({}, ["TrimStart", "  hi  "], "hi  "),
        ({}, ["TrimEnd", "  hi  "], "  hi"),
        # --- Split / replace / compare ---
        ({}, ["StringSplit", "a b  c"], ["Array", "a", "b", "c"]),
        ({}, ["StringSplit", "a,b,c", ","], ["Array", "a", "b", "c"]),
        ({}, ["StringReplace", "foo bar foo", "foo", "baz"], "baz bar baz"),
        ({}, ["StringCompare", "abc", "abd"], -1),
        ({}, ["StringCompare", "abc", "abc"], 0),
        ({}, ["StringCompare", "abd", "abc"], 1),
        # --- Repeat / pad ---
        ({}, ["StringRepeat", "ab", 3], "ababab"),
        ({}, ["StringRepeat", "x", 0], ""),
        ({}, ["PadStart", "7", 3, "0"], "007"),
        ({}, ["PadEnd", "7", 3, "0"], "700"),
        ({}, ["PadStart", "hello", 3], "hello"),  # already long enough
        # --- Characters / GraphemeClusters ---
        ({}, ["Characters", "abc"], ["Array", "a", "b", "c"]),
        ({}, ["GraphemeClusters", "abc"], ["Array", "a", "b", "c"]),
        # --- Encoding round-trips ---
        ({}, ["Utf8", "hi"], ["Array", 104, 105]),
        ({}, ["Utf16", "hi"], ["Array", 104, 105]),
        ({}, ["UnicodeScalars", "hi"], ["Array", 104, 105]),
        ({}, ["StringFrom", ["Array", 104, 105], "utf-8"], "hi"),
        ({}, ["StringFrom", ["Array", 104, 105], "utf-16"], "hi"),
        ({}, ["StringFrom", ["Array", 104, 105], "unicode-scalars"], "hi"),
        # --- Base conversion ---
        ({}, ["IntegerString", 255, 16], "ff"),
        ({}, ["IntegerString", -255, 16], "-ff"),
        ({}, ["IntegerString", 255], "255"),
        ({}, ["DigitsFrom", "ff", 16], 255),
        ({}, ["DigitsFrom", "255"], 255),
        # --- NumberFrom ---
        ({}, ["NumberFrom", "42"], 42),
        ({}, ["NumberFrom", "3.14e2"], 314.0),
    ],
)
def test_cortexjs_strings(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


def test_string_repeat_rejects_negative_count():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["StringRepeat", "x", -1])


def test_string_repeat_enforces_length_cap():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["StringRepeat", "x", 10**9])


def test_pad_enforces_length_cap():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["PadStart", "x", 10**9])


def test_string_from_rejects_unknown_encoding():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["StringFrom", ["Array", 1, 2], "made-up-encoding"])


# --- Regex (RE2-backed): IsMatch, StringMatch, StringMatchAll, RegExp ---


@pytest.mark.skipif(not RE2_AVAILABLE, reason="google-re2 not available")
@pytest.mark.parametrize(
    "parameters, expression, expected_result",
    [
        ({}, ["IsMatch", "hello world", "wor.d"], True),
        ({}, ["IsMatch", "hello world", "xyz"], False),
        ({}, ["IsMatch", "HELLO", ["RegExp", "hello", "i"]], True),
        ({}, ["IsMatch", "HELLO", "hello"], False),
        (
            {},
            ["StringMatch", "contact: alice@example", r"(\w+)@(\w+)"],
            ["Array", "alice@example", 10, 22, ["Array", "alice", "example"]],
        ),
        ({}, ["StringMatch", "no email here", r"\w+@\w+"], None),
        (
            {},
            ["StringMatchAll", "a1 b22 c333", r"\d+"],
            [
                "Array",
                ["Array", "1", 2, 2, ["Array"]],
                ["Array", "22", 5, 6, ["Array"]],
                ["Array", "333", 9, 11, ["Array"]],
            ],
        ),
    ],
)
def test_cortexjs_regex(parameters, expression, expected_result):
    solver = create_solver(parameters)
    assert solver(expression) == expected_result


@pytest.mark.skipif(not RE2_AVAILABLE, reason="google-re2 not available")
def test_regex_rejects_backreferences():
    # RE2 cannot support backreferences (no linear-time equivalent) -
    # this must fail cleanly, not hang or crash unhandled.
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["RegExp", r"(a)\1"])


@pytest.mark.skipif(not RE2_AVAILABLE, reason="google-re2 not available")
def test_regex_rejects_lookahead():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["RegExp", r"foo(?=bar)"])


@pytest.mark.skipif(not RE2_AVAILABLE, reason="google-re2 not available")
def test_regex_rejects_unsupported_flags():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["RegExp", "abc", "z"])


@pytest.mark.skipif(not RE2_AVAILABLE, reason="google-re2 not available")
def test_regex_is_immune_to_catastrophic_backtracking():
    # The whole point of using RE2: this classic ReDoS pattern must
    # resolve near-instantly, not hang, against an adversarial input
    # that would be exponential for a backtracking engine.
    import time

    solver = create_solver({})
    adversarial = "a" * 40 + "c"
    start = time.time()
    result = solver(["IsMatch", adversarial, "(a+)+b"])
    elapsed = time.time() - start
    assert result is False
    assert elapsed < 1.0


@pytest.mark.skipif(RE2_AVAILABLE, reason="test requires google-re2 to be ABSENT")
def test_regex_functions_raise_clear_error_without_re2():
    solver = create_solver({})
    with pytest.raises(Exception):
        solver(["IsMatch", "hello", "h.*o"])
