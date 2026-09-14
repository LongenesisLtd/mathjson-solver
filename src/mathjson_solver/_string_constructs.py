"""
String and regex (RE2-backed) constructs.
"""

from ._construct_shared import _arr_vals

RE2_AVAILABLE = False
try:
    import re2

    RE2_AVAILABLE = True
    # No public "re2.Pattern" name is exported; derive the actual
    # compiled-pattern type at import time rather than hardcoding
    # re2's internal class path.
    _RE2_PATTERN_TYPE = type(re2.compile(""))
except ImportError:
    _RE2_PATTERN_TYPE = None


# Hard cap on the result length of string operations whose size is
# otherwise controlled directly by a user-supplied count/length
# argument (StringRepeat, PadStart, PadEnd) - closes the same
# memory/time exhaustion shape that Loop/Random/arbitrary-size Repeat
# are excluded for elsewhere in this solver, but here it's cheaply and
# exactly bounded by a single length check before any allocation.
_MAX_STRING_REPEAT_LENGTH = 100_000


_VALID_REGEX_FLAGS = set("ims")


def Str(f, c, solver_parameters, s):
    if len(s) < 2:
        raise ValueError("Wrong parameters for 'Str'")
    return f"{f(s[1])}"


def String(f, c, solver_parameters, s):
    """
    ["String", value1, value2, ...]
    Concatenates the default string representation of each
    argument. Distinct from `Str` (single argument) and from
    `StringJoin` (joins the elements of a single array).
    """
    return "".join(str(f(x, c)) for x in s[1:])


def StringJoin(f, c, solver_parameters, s):
    """
    ["StringJoin", array] or ["StringJoin", array, separator]
    Joins the (stringified) elements of `array` with
    `separator` (default ""). Distinct from `Join`, which
    concatenates multiple arrays together.
    """
    values = [str(v) for v in _arr_vals(f, c, solver_parameters, s)]
    separator = f(s[2], c) if len(s) > 2 else ""
    return separator.join(values)


def Utf8(f, c, solver_parameters, s):
    """
    ["Utf8", string]
    List of UTF-8 byte values representing `string`.
    """
    return ["Array"] + list(f(s[1], c).encode("utf-8"))


def Utf16(f, c, solver_parameters, s):
    """
    ["Utf16", string]
    List of UTF-16 code units representing `string` (one
    array element per 16-bit code unit, matching how
    JavaScript/CortexJS model a string).
    """
    encoded = f(s[1], c).encode("utf-16-le")
    return ["Array"] + [
        encoded[i] | (encoded[i + 1] << 8) for i in range(0, len(encoded), 2)
    ]


def UnicodeScalars(f, c, solver_parameters, s):
    """
    ["UnicodeScalars", string]
    List of Unicode scalar (code point) values in `string`.
    """
    return ["Array"] + [ord(ch) for ch in f(s[1], c)]


def StringFrom(f, c, solver_parameters, s):
    """
    ["StringFrom", array, encoding]
    Converts `array` (a list of code units, as produced by
    `Utf8`/`Utf16`/`UnicodeScalars`) back into a string.
    `encoding` is one of "utf-8", "utf-16", "unicode-scalars".
    """
    values = _arr_vals(f, c, solver_parameters, s)
    encoding = f(s[2], c)
    if encoding == "utf-8":
        return bytes(int(v) for v in values).decode("utf-8")
    elif encoding == "utf-16":
        raw = b"".join(int(v).to_bytes(2, "little") for v in values)
        return raw.decode("utf-16-le")
    elif encoding == "unicode-scalars":
        return "".join(chr(int(v)) for v in values)
    else:
        raise ValueError(f"Unknown encoding: {encoding!r}")


def Characters(f, c, solver_parameters, s):
    """
    ["Characters", string]
    Splits `string` into a list of its characters. Approximated
    at the Unicode code-point level (Python `str` iteration)
    rather than true extended grapheme clusters (Unicode
    Annex #29), which would need a dependency this solver
    doesn't otherwise require - a multi-codepoint grapheme
    (e.g. an emoji with a modifier) is split into its
    constituent code points rather than kept whole.
    """
    return ["Array"] + list(f(s[1], c))


def StringSplit(f, c, solver_parameters, s):
    """
    ["StringSplit", string] or ["StringSplit", string, separator]
    Splits on whitespace if no `separator` is given, else on
    the literal `separator` string.
    """
    string = f(s[1], c)
    if len(s) > 2:
        return ["Array"] + string.split(f(s[2], c))
    return ["Array"] + string.split()


def StringReplace(f, c, solver_parameters, s):
    """
    ["StringReplace", string, target, replacement]
    Replaces every occurrence of the literal substring
    `target` with `replacement` (not pattern-based - see
    `IsMatch`/`StringMatch` for pattern matching).
    """
    return f(s[1], c).replace(f(s[2], c), f(s[3], c))


def StringCompare(f, c, solver_parameters, s):
    """
    ["StringCompare", string1, string2]
    -1, 0, or 1 depending on whether `string1` sorts before,
    equal to, or after `string2` by code-point sequence.
    """
    a, b = f(s[1], c), f(s[2], c)
    return (a > b) - (a < b)


def IntegerString(f, c, solver_parameters, s):
    """
    ["IntegerString", integer] or ["IntegerString", integer, base]
    String representation of `integer` in `base` (default 10,
    2-36).
    """
    value = int(f(s[1], c))
    base = int(f(s[2], c)) if len(s) > 2 else 10
    if base == 10:
        return str(value)
    if not (2 <= base <= 36):
        raise ValueError("'IntegerString' base must be between 2 and 36.")
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    negative = value < 0
    value = abs(value)
    if value == 0:
        digits_out = "0"
    else:
        digits_out = ""
        while value:
            value, rem = divmod(value, base)
            digits_out = digits[rem] + digits_out
    return ("-" if negative else "") + digits_out


def DigitsFrom(f, c, solver_parameters, s):
    """
    ["DigitsFrom", string] or ["DigitsFrom", string, base]
    Parses `string` as an integer in `base` (default 10).
    """
    string = f(s[1], c)
    base = int(f(s[2], c)) if len(s) > 2 else 10
    return int(string, base)


def NumberFrom(f, c, solver_parameters, s):
    """
    ["NumberFrom", string]
    Parses `string` as a number - integer, decimal, or
    scientific notation.
    """
    string = f(s[1], c).strip()
    try:
        return int(string)
    except ValueError:
        return float(string)


def StringRepeat(f, c, solver_parameters, s):
    """
    ["StringRepeat", string, n]
    Concatenates `n` copies of `string`. Capped at
    `_MAX_STRING_REPEAT_LENGTH` characters, since `n` is a
    user-controlled value that would otherwise make this an
    unbounded memory-exhaustion primitive.
    """
    string = f(s[1], c)
    n = int(f(s[2], c))
    if n < 0:
        raise ValueError("'StringRepeat' count must be non-negative.")
    if len(string) * n > _MAX_STRING_REPEAT_LENGTH:
        raise ValueError(
            f"'StringRepeat' result would exceed the "
            f"{_MAX_STRING_REPEAT_LENGTH}-character limit."
        )
    return string * n


def _pad(f, c, solver_parameters, string, length, pad, prepend):
    if length > _MAX_STRING_REPEAT_LENGTH:
        raise ValueError(
            f"Pad length must not exceed " f"{_MAX_STRING_REPEAT_LENGTH} characters."
        )
    if len(string) >= length or not pad:
        return string
    needed = length - len(string)
    full_pad = (pad * (needed // len(pad) + 1))[:needed]
    return full_pad + string if prepend else string + full_pad


def PadStart(f, c, solver_parameters, s):
    """
    ["PadStart", string, length] or
    ["PadStart", string, length, pad]
    Pads `string` on the left to `length` characters using
    `pad` (default a single space), truncating `pad` as
    needed to fit exactly.
    """
    pad = f(s[3], c) if len(s) > 3 else " "
    return _pad(f, c, solver_parameters, f(s[1], c), int(f(s[2], c)), pad, prepend=True)


def PadEnd(f, c, solver_parameters, s):
    """
    ["PadEnd", string, length] or ["PadEnd", string, length, pad]
    Pads `string` on the right to `length` characters using
    `pad` (default a single space), truncating `pad` as
    needed to fit exactly.
    """
    pad = f(s[3], c) if len(s) > 3 else " "
    return _pad(
        f, c, solver_parameters, f(s[1], c), int(f(s[2], c)), pad, prepend=False
    )


def _require_re2(f, c, solver_parameters):
    if not RE2_AVAILABLE:
        raise ImportError(
            "RegExp/IsMatch/StringMatch/StringMatchAll require "
            "'google-re2'. Install with "
            "'pip install mathjson-solver[regex]' "
            "(or 'pip install google-re2')."
        )


def _compile_regex(f, c, solver_parameters, pattern_str, flags_str=""):
    if not set(flags_str) <= _VALID_REGEX_FLAGS:
        raise ValueError(
            f"Unsupported regex flag(s) in {flags_str!r}; only "
            f"'i', 'm', 's' are supported."
        )
    prefixed = f"(?{flags_str})" + pattern_str if flags_str else pattern_str
    try:
        return re2.compile(prefixed)
    except re2.error as e:
        raise ValueError(f"Invalid pattern {pattern_str!r}: {e}") from e


def _resolve_pattern(f, c, solver_parameters, expr):
    """
    Evaluates `expr` and returns a compiled RE2 pattern -
    unchanged if it's already one (e.g. produced by a nested
    `RegExp` call), else compiled fresh (no flags) if it's a
    plain string.

    Uses RE2 rather than Python's `re`: RE2 guarantees
    linear-time matching (no catastrophic backtracking is
    possible, by construction of the engine), at the cost of
    not supporting backreferences or lookaround - a
    deliberate trade-off for a solver that evaluates
    untrusted expressions with no execution budget of its own.
    """
    _require_re2(f, c, solver_parameters)
    value = f(expr, c)
    if isinstance(value, _RE2_PATTERN_TYPE):
        return value
    if isinstance(value, str):
        return _compile_regex(f, c, solver_parameters, value)
    raise ValueError("Expected a pattern string or a RegExp value.")


def RegExp(f, c, solver_parameters, s):
    """
    ["RegExp", pattern] or ["RegExp", pattern, flags]
    Compiles `pattern` (RE2 syntax - see `_resolve_pattern`)
    into a reusable pattern value, for passing to
    `IsMatch`/`StringMatch`/`StringMatchAll`. `flags` is a
    string made up of "i" (case-insensitive), "m" (multiline
    anchors), "s" (dot matches newline).
    """
    _require_re2(f, c, solver_parameters)
    pattern_str = f(s[1], c)
    flags_str = f(s[2], c) if len(s) > 2 else ""
    return _compile_regex(f, c, solver_parameters, pattern_str, flags_str)


def IsMatch(f, c, solver_parameters, s):
    """
    ["IsMatch", string, pattern]
    Whether `string` contains a match for `pattern` (a plain
    pattern string, or a `RegExp` value) anywhere within it.
    """
    pattern = _resolve_pattern(f, c, solver_parameters, s[2])
    return pattern.search(f(s[1], c)) is not None


def _match_record(f, c, solver_parameters, m):
    return [
        "Array",
        m.group(0),
        m.start() + 1,  # 1-indexed, matching this solver's
        m.end(),  # other CortexJS-compat index
        # conventions (At, Range, ...)
        ["Array"] + list(m.groups()),
    ]


def StringMatch(f, c, solver_parameters, s):
    """
    ["StringMatch", string, pattern]
    The first match of `pattern` in `string`, as
    ["Array", matched_text, start, end, ["Array", group1, ...]]
    (1-indexed `start`, exclusive `end`), or None if there's
    no match.
    """
    pattern = _resolve_pattern(f, c, solver_parameters, s[2])
    m = pattern.search(f(s[1], c))
    return _match_record(f, c, solver_parameters, m) if m else None


def StringMatchAll(f, c, solver_parameters, s):
    """
    ["StringMatchAll", string, pattern]
    All non-overlapping matches of `pattern` in `string`,
    each in the same shape as `StringMatch`.
    """
    pattern = _resolve_pattern(f, c, solver_parameters, s[2])
    return ["Array"] + [
        _match_record(f, c, solver_parameters, m) for m in pattern.finditer(f(s[1], c))
    ]
