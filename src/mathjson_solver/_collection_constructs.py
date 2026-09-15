"""
Array/list/collection constructs: element access, searching,
transformation, grouping, and set algebra (over Array - no dedicated Set
type).
"""

from ._common import (
    has_matching_sublist,
)
from ._construct_shared import _apply_fn, _arr_vals, _arr_vals_of


def Arr(f, c, solver_parameters, s):
    return s


def Length(f, c, solver_parameters, s):
    if isinstance(s[1], str):
        return len([x for x in f(s[1], c)][1:])
    else:
        return len([x for x in s[1][1:]])


def First(f, c, solver_parameters, s):
    return _arr_vals(f, c, solver_parameters, s)[0]


def Second(f, c, solver_parameters, s):
    return _arr_vals(f, c, solver_parameters, s)[1]


def Third(f, c, solver_parameters, s):
    return _arr_vals(f, c, solver_parameters, s)[2]


def Last(f, c, solver_parameters, s):
    return _arr_vals(f, c, solver_parameters, s)[-1]


def Rest(f, c, solver_parameters, s):
    return ["Array"] + _arr_vals(f, c, solver_parameters, s)[1:]


def Most(f, c, solver_parameters, s):
    return ["Array"] + _arr_vals(f, c, solver_parameters, s)[:-1]


def Reverse(f, c, solver_parameters, s):
    return ["Array"] + list(reversed(_arr_vals(f, c, solver_parameters, s)))


def Sort(f, c, solver_parameters, s):
    return ["Array"] + sorted(_arr_vals(f, c, solver_parameters, s))


def IsEmpty(f, c, solver_parameters, s):
    lst = f(s[1], c)
    if not (isinstance(lst, list) and lst[0] == "Array"):
        raise ValueError("Parameter 1 must be an array.")
    return len(lst) <= 1


def Range(f, c, solver_parameters, s):
    """
    CortexJS-compatible `Range`:
    ["Range", upper]                -> 1..upper (inclusive)
    ["Range", lower, upper]         -> lower..upper (inclusive)
    ["Range", lower, upper, step]   -> lower..upper (inclusive), stepped
    Distinct from `GenerateRange`, which is 0-indexed and exclusive at
    the upper end.
    """
    if len(s) == 2:
        return ["Array"] + list(range(1, int(f(s[1], c)) + 1))
    elif len(s) == 3:
        lo, hi = int(f(s[1], c)), int(f(s[2], c))
        return ["Array"] + list(range(lo, hi + 1))
    else:
        lo, hi, step = (
            int(f(s[1], c)),
            int(f(s[2], c)),
            int(f(s[3], c)),
        )
        return ["Array"] + list(range(lo, hi + 1 if step > 0 else hi - 1, step))


def Join(f, c, solver_parameters, s):
    """
    ["Join", array1, array2, ...]
    Concatenates the given arrays.
    """
    result = ["Array"]
    for arg in s[1:]:
        lst = f(arg, c)
        if not (isinstance(lst, list) and lst[0] == "Array"):
            raise ValueError("All parameters must be arrays.")
        result += [f(x, c) for x in lst[1:]]
    return result


def Unique(f, c, solver_parameters, s):
    seen = []
    for x in _arr_vals(f, c, solver_parameters, s):
        if x not in seen:
            seen.append(x)
    return ["Array"] + seen


def Zip(f, c, solver_parameters, s):
    lists = [[f(x, c) for x in f(arg, c)[1:]] for arg in s[1:]]
    return ["Array"] + [["Array", a, b] for a, b in zip(*lists)]


def At(f, c, solver_parameters, s):
    """
    ["At", array, index]
    1-indexed element access (CortexJS `At`), with negative indexes
    counting from the end.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    idx = int(f(s[2], c))
    if idx > 0:
        return vals[idx - 1]
    else:
        return vals[idx]


def Take(f, c, solver_parameters, s):
    """
    ["Take", array, n]
    First `n` elements if n >= 0; last `n` elements if n < 0.
    Distinct from `Slice`, which takes an explicit [start, end)
    range instead of a count.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    n = int(f(s[2], c))
    if n >= 0:
        return ["Array"] + vals[:n]
    return ["Array"] + vals[n:]


def Drop(f, c, solver_parameters, s):
    """
    ["Drop", array, n]
    All elements except the first `n` if n >= 0; except the
    last `n` if n < 0.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    n = int(f(s[2], c))
    if n >= 0:
        return ["Array"] + vals[n:]
    return ["Array"] + vals[:n]


def TakeWhile(f, c, solver_parameters, s):
    """
    ["TakeWhile", array, predicate]
    Elements from the start, up to (excluding) the first one
    for which `predicate` is false.
    """
    result = []
    for v in _arr_vals(f, c, solver_parameters, s):
        if not _apply_fn(f, c, solver_parameters, s[2], [v]):
            break
        result.append(v)
    return ["Array"] + result


def DropWhile(f, c, solver_parameters, s):
    """
    ["DropWhile", array, predicate]
    Remaining elements from (and including) the first one for
    which `predicate` is false.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    i = 0
    while i < len(vals) and _apply_fn(f, c, solver_parameters, s[2], [vals[i]]):
        i += 1
    return ["Array"] + vals[i:]


def Contains(f, c, solver_parameters, s):
    """
    ["Contains", array, value]
    Whether `value` occurs in `array`. CortexJS argument order
    (collection first) - the existing `In` takes them the
    other way round (`["In", value, collection]`).
    """
    return f(s[2], c) in _arr_vals(f, c, solver_parameters, s)


def IndexOf(f, c, solver_parameters, s):
    """
    ["IndexOf", array, value]
    1-indexed position of the first occurrence of `value`, or
    None if it doesn't occur.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    value = f(s[2], c)
    try:
        return vals.index(value) + 1
    except ValueError:
        return None


def IndexWhere(f, c, solver_parameters, s):
    """
    ["IndexWhere", array, predicate]
    1-indexed position of the first element for which
    `predicate` is true, or None if none match.
    """
    for i, v in enumerate(_arr_vals(f, c, solver_parameters, s)):
        if _apply_fn(f, c, solver_parameters, s[2], [v]):
            return i + 1
    return None


def Find(f, c, solver_parameters, s):
    """
    ["Find", array, predicate]
    The first element for which `predicate` is true, or None
    if none match.
    """
    for v in _arr_vals(f, c, solver_parameters, s):
        if _apply_fn(f, c, solver_parameters, s[2], [v]):
            return v
    return None


def CountIf(f, c, solver_parameters, s):
    """
    ["CountIf", array, predicate]
    Count of elements for which `predicate` is true.
    """
    return sum(
        1
        for v in _arr_vals(f, c, solver_parameters, s)
        if _apply_fn(f, c, solver_parameters, s[2], [v])
    )


def Position(f, c, solver_parameters, s):
    """
    ["Position", array, predicate]
    Array of the 1-indexed positions of every element for
    which `predicate` is true.
    """
    return ["Array"] + [
        i + 1
        for i, v in enumerate(_arr_vals(f, c, solver_parameters, s))
        if _apply_fn(f, c, solver_parameters, s[2], [v])
    ]


def RotateLeft(f, c, solver_parameters, s):
    """
    ["RotateLeft", array, n]
    Circularly shifts `array` left by `n` positions.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    if not vals:
        return ["Array"]
    n = int(f(s[2], c)) % len(vals)
    return ["Array"] + vals[n:] + vals[:n]


def RotateRight(f, c, solver_parameters, s):
    """
    ["RotateRight", array, n]
    Circularly shifts `array` right by `n` positions.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    if not vals:
        return ["Array"]
    n = int(f(s[2], c)) % len(vals)
    if n == 0:
        return ["Array"] + vals
    return ["Array"] + vals[-n:] + vals[:-n]


def MaxBy(f, c, solver_parameters, s):
    """
    ["MaxBy", array, function]
    The element of `array` for which `function(element)` is
    largest.
    """
    return max(
        _arr_vals(f, c, solver_parameters, s),
        key=lambda v: _apply_fn(f, c, solver_parameters, s[2], [v]),
    )


def MinBy(f, c, solver_parameters, s):
    """
    ["MinBy", array, function]
    The element of `array` for which `function(element)` is
    smallest.
    """
    return min(
        _arr_vals(f, c, solver_parameters, s),
        key=lambda v: _apply_fn(f, c, solver_parameters, s[2], [v]),
    )


def ArgMax(f, c, solver_parameters, s):
    """
    ["ArgMax", array]
    1-indexed position of the largest element.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    return max(range(len(vals)), key=lambda i: vals[i]) + 1


def ArgMin(f, c, solver_parameters, s):
    """
    ["ArgMin", array]
    1-indexed position of the smallest element.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    return min(range(len(vals)), key=lambda i: vals[i]) + 1


def Ordering(f, c, solver_parameters, s):
    """
    ["Ordering", array]
    Array of the 1-indexed positions that would put `array`
    in ascending order.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    return ["Array"] + [i + 1 for i in sorted(range(len(vals)), key=lambda i: vals[i])]


def FlatMap(f, c, solver_parameters, s):
    """
    ["FlatMap", array, function]
    Applies `function` to each element (as with `Map`) and
    flattens one level of the results - each result that is
    itself an array is spliced in, others are kept as-is -
    into a single array.
    """
    result = ["Array"]
    for v in _arr_vals(f, c, solver_parameters, s):
        mapped = _apply_fn(f, c, solver_parameters, s[2], [v])
        if isinstance(mapped, list) and mapped and mapped[0] == "Array":
            result += mapped[1:]
        else:
            result.append(mapped)
    return result


def Scan(f, c, solver_parameters, s):
    """
    ["Scan", array, function] or ["Scan", array, function, initial]
    Like `Reduce`'s CortexJS form (`function` applied as
    `function(accumulator, current)`), but returns an array of
    every intermediate accumulator value, including the seed,
    instead of just the final one.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    fn_expr = s[2]
    if len(s) == 4:
        acc = f(s[3], c)
        remaining = vals
    else:
        if not vals:
            raise ValueError("'Scan' on an empty collection requires an initial value.")
        acc = vals[0]
        remaining = vals[1:]
    result = ["Array", acc]
    for v in remaining:
        acc = _apply_fn(f, c, solver_parameters, fn_expr, [acc, v])
        result.append(acc)
    return result


def Differences(f, c, solver_parameters, s):
    """
    ["Differences", array]
    Array of successive differences: element[i+1] - element[i].
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    return ["Array"] + [b - a for a, b in zip(vals, vals[1:])]


def Dedup(f, c, solver_parameters, s):
    """
    ["Dedup", array]
    Removes only *consecutive* duplicate elements - distinct
    from `Unique`, which removes every duplicate regardless of
    position.
    """
    result = []
    for v in _arr_vals(f, c, solver_parameters, s):
        if not result or result[-1] != v:
            result.append(v)
    return ["Array"] + result


def Insert(f, c, solver_parameters, s):
    """
    ["Insert", array, index, value]
    Inserts `value` at the 1-indexed `index` (CortexJS
    convention, matching `At`); negative indexes count from
    the end.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    idx = int(f(s[2], c))
    value = f(s[3], c)
    vals.insert(idx - 1 if idx > 0 else idx, value)
    return ["Array"] + vals


def DeleteAt(f, c, solver_parameters, s):
    """
    ["DeleteAt", array, index]
    Removes the element at the 1-indexed `index`; negative
    indexes count from the end.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    idx = int(f(s[2], c))
    del vals[idx - 1 if idx > 0 else idx]
    return ["Array"] + vals


def ReplaceAt(f, c, solver_parameters, s):
    """
    ["ReplaceAt", array, index, value]
    Replaces the element at the 1-indexed `index` with
    `value`; negative indexes count from the end.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    idx = int(f(s[2], c))
    value = f(s[3], c)
    vals[idx - 1 if idx > 0 else idx] = value
    return ["Array"] + vals


def Partition(f, c, solver_parameters, s):
    """
    ["Partition", array, size]
    Splits `array` into consecutive chunks of length `size`
    (the last chunk may be shorter). Distinct from `Chunk`,
    which instead takes the number of groups to split into.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    size = int(f(s[2], c))
    if size <= 0:
        raise ValueError("'Partition' size must be a positive integer.")
    return ["Array"] + [
        ["Array"] + vals[i : i + size] for i in range(0, len(vals), size)
    ]


def Chunk(f, c, solver_parameters, s):
    """
    ["Chunk", array, n]
    Splits `array` into `n` roughly equal-sized consecutive
    groups.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    n = int(f(s[2], c))
    if n <= 0:
        raise ValueError("'Chunk' group count must be a positive integer.")
    base, extra = divmod(len(vals), n)
    result, start = [], 0
    for i in range(n):
        size = base + (1 if i < extra else 0)
        result.append(["Array"] + vals[start : start + size])
        start += size
    return ["Array"] + result


def GroupBy(f, c, solver_parameters, s):
    """
    ["GroupBy", array, function]
    Groups elements of `array` by `function(element)`, in
    order of first appearance of each key. Returns an array of
    [key, group] pairs - there's no dedicated `Dictionary`
    type in this solver.
    """
    order = []
    groups = {}
    for v in _arr_vals(f, c, solver_parameters, s):
        k = _apply_fn(f, c, solver_parameters, s[2], [v])
        hk = tuple(k) if isinstance(k, list) else k
        if hk not in groups:
            order.append((hk, k))
            groups[hk] = []
        groups[hk].append(v)
    return ["Array"] + [["Array", k, ["Array"] + groups[hk]] for hk, k in order]


def ChunkBy(f, c, solver_parameters, s):
    """
    ["ChunkBy", array, function]
    Splits `array` into consecutive runs sharing the same
    `function(element)` key - unlike `GroupBy`, runs are not
    merged across non-adjacent occurrences of the same key.
    """
    vals = _arr_vals(f, c, solver_parameters, s)
    if not vals:
        return ["Array"]
    result = []
    current = [vals[0]]
    current_key = _apply_fn(f, c, solver_parameters, s[2], [vals[0]])
    for v in vals[1:]:
        k = _apply_fn(f, c, solver_parameters, s[2], [v])
        if k == current_key:
            current.append(v)
        else:
            result.append(["Array"] + current)
            current, current_key = [v], k
    result.append(["Array"] + current)
    return ["Array"] + result


def Tally(f, c, solver_parameters, s):
    """
    ["Tally", array]
    Counts occurrences of each distinct element, in order of
    first appearance. Returns an array of [value, count]
    pairs.
    """
    order = []
    counts = {}
    for v in _arr_vals(f, c, solver_parameters, s):
        hv = tuple(v) if isinstance(v, list) else v
        if hv not in counts:
            order.append((hv, v))
            counts[hv] = 0
        counts[hv] += 1
    return ["Array"] + [["Array", v, counts[hv]] for hv, v in order]


def Union(f, c, solver_parameters, s):
    """
    ["Union", array1, array2, ...]
    Distinct elements appearing in any of the given arrays, in
    order of first appearance across the arguments
    (left to right). Arrays stand in for CortexJS's `Set`
    here - there's no dedicated set type in this solver.
    """
    result = []
    for arg in s[1:]:
        for v in _arr_vals_of(f, c, solver_parameters, arg):
            if v not in result:
                result.append(v)
    return ["Array"] + result


def Intersection(f, c, solver_parameters, s):
    """
    ["Intersection", array1, array2, ...]
    Distinct elements common to every given array, in the
    order they first appear in `array1`.
    """
    arrays = [_arr_vals_of(f, c, solver_parameters, arg) for arg in s[1:]]
    if not arrays:
        return ["Array"]
    result = []
    for v in arrays[0]:
        if v not in result and all(v in arr for arr in arrays[1:]):
            result.append(v)
    return ["Array"] + result


def SetMinus(f, c, solver_parameters, s):
    """
    ["SetMinus", array1, array2]
    Distinct elements of `array1` that don't occur in
    `array2`.
    """
    a = _arr_vals_of(f, c, solver_parameters, s[1])
    b = _arr_vals_of(f, c, solver_parameters, s[2])
    result = []
    for v in a:
        if v not in b and v not in result:
            result.append(v)
    return ["Array"] + result


def SymmetricDifference(f, c, solver_parameters, s):
    """
    ["SymmetricDifference", array1, array2]
    Distinct elements that occur in exactly one of
    `array1`/`array2`: `array1`'s exclusive elements first
    (in `array1`'s order), then `array2`'s (in `array2`'s
    order).
    """
    a = _arr_vals_of(f, c, solver_parameters, s[1])
    b = _arr_vals_of(f, c, solver_parameters, s[2])
    result = []
    for v in a:
        if v not in b and v not in result:
            result.append(v)
    for v in b:
        if v not in a and v not in result:
            result.append(v)
    return ["Array"] + result


def _is_subset(a_vals, b_vals):
    """Every element of `a_vals` occurs in `b_vals` - the shared core of
    SubsetEqual/Subset/Superset/SupersetEqual below. Uses plain `in`
    checks against a list, not Python's `set`, matching the rest of this
    file's set-algebra functions (arrays stand in for CortexJS's `Set`
    here, and their elements aren't guaranteed hashable - e.g. an element
    could itself be a nested array)."""
    return all(v in b_vals for v in a_vals)


def SubsetEqual(f, c, solver_parameters, s):
    """["SubsetEqual", array1, array2] - A ⊆ B: every element of array1 occurs in array2."""
    a = _arr_vals_of(f, c, solver_parameters, s[1])
    b = _arr_vals_of(f, c, solver_parameters, s[2])
    return _is_subset(a, b)


def SupersetEqual(f, c, solver_parameters, s):
    """["SupersetEqual", array1, array2] - A ⊇ B: every element of array2 occurs in array1."""
    a = _arr_vals_of(f, c, solver_parameters, s[1])
    b = _arr_vals_of(f, c, solver_parameters, s[2])
    return _is_subset(b, a)


def Subset(f, c, solver_parameters, s):
    """
    ["Subset", array1, array2] - A ⊂ B: a *proper* subset (A ⊆ B and
    A ≠ B, treating both as sets of distinct elements - order and
    duplicates don't affect the comparison, matching how Union/
    Intersection/etc. above already treat arrays).
    """
    a = _arr_vals_of(f, c, solver_parameters, s[1])
    b = _arr_vals_of(f, c, solver_parameters, s[2])
    return _is_subset(a, b) and not _is_subset(b, a)


def Superset(f, c, solver_parameters, s):
    """["Superset", array1, array2] - A ⊃ B: a *proper* superset. See `Subset`."""
    a = _arr_vals_of(f, c, solver_parameters, s[1])
    b = _arr_vals_of(f, c, solver_parameters, s[2])
    return _is_subset(b, a) and not _is_subset(a, b)


def NotSubset(f, c, solver_parameters, s):
    """["NotSubset", array1, array2] - A ⊄ B: the negation of `Subset` (proper subset), not of `SubsetEqual`."""
    return not Subset(f, c, solver_parameters, s)


def NotSuperset(f, c, solver_parameters, s):
    """["NotSuperset", array1, array2] - A ⊅ B: the negation of `Superset` (proper superset), not of `SupersetEqual`."""
    return not Superset(f, c, solver_parameters, s)


def Any(f, c, solver_parameters, s):
    evaluated = f(s[1], c)
    if isinstance(evaluated, list) and evaluated[0] == "Array":
        return any([f(x, c) for x in evaluated[1:]])
    raise ValueError("Parameter 1 must be an array.")


def All(f, c, solver_parameters, s):
    evaluated = f(s[1], c)
    if isinstance(evaluated, list) and evaluated[0] == "Array":
        return all([f(x, c) for x in evaluated[1:]])
    raise ValueError("Parameter 1 must be an array.")


def Interval(f, c, solver_parameters, s):
    """
    ["Interval", lo, hi] - a closed numeric interval [lo, hi]. Wrap
    either endpoint in ["Open", endpoint] to exclude it, matching
    CortexJS's own convention (e.g. ["Interval", 0, ["Open", 1]] for
    the half-open interval [0, 1)).

    Like Function/NormalDistribution/etc. elsewhere in this solver, this
    is a "marker" - it returns its own unevaluated expression rather
    than a computed value. `In`/`Element` (below) are what actually
    evaluate an interval's endpoints and test membership; Interval on
    its own is only meaningful as their second argument.
    """
    return s


def Open(f, c, solver_parameters, s):
    """
    ["Open", endpoint] - marks one endpoint of an Interval (above) as
    excluded. Only meaningful nested inside an Interval; like Interval
    itself, this is a marker construct, not something evaluated on its
    own.
    """
    return s


def _interval_bounds(f, c, solver_parameters, interval_expr):
    """
    Evaluate an ["Interval", lo, hi] expression's endpoints, resolving
    each through `f` and honoring a per-endpoint ["Open", endpoint]
    wrapper (excluded) vs. a bare endpoint (included, the default).
    Returns (lo_value, lo_excluded, hi_value, hi_excluded).
    """

    def bound(raw):
        if isinstance(raw, list) and raw and raw[0] == "Open":
            return f(raw[1], c), True
        return f(raw, c), False

    lo_value, lo_excluded = bound(interval_expr[1])
    hi_value, hi_excluded = bound(interval_expr[2])
    return lo_value, lo_excluded, hi_value, hi_excluded


def In(f, c, solver_parameters, s):
    if len(s) != 3:
        raise ValueError("Wrong parameters for 'In'")
    if isinstance(s[2], list) and s[2][0] == "Array":
        return f(s[1], c) in [f(x, c) for x in s[2][1:]]

    elif isinstance(s[2], list) and s[2][0] == "Interval":
        value = f(s[1], c)
        lo, lo_excluded, hi, hi_excluded = _interval_bounds(
            f, c, solver_parameters, s[2]
        )
        if lo_excluded and not (value > lo):
            return False
        if not lo_excluded and not (value >= lo):
            return False
        if hi_excluded and not (value < hi):
            return False
        if not hi_excluded and not (value <= hi):
            return False
        return True

    elif isinstance(s[2], str):
        return f(s[1], c) in f(s[2], c)
    else:
        raise ValueError("Wrong parameters for 'In'. Parameter 2 must be a list.")


def Not_in(f, c, solver_parameters, s):
    return not In(f, c, solver_parameters, s)


def Contains_any_of(f, c, solver_parameters, s):
    if isinstance(s[1], list) and s[1][0] == "Array":
        list1 = [f(x, c) for x in s[1][1:]]
    elif isinstance(s[1], str):
        list1 = f(s[1], c)

    if isinstance(s[2], list) and s[2][0] == "Array":
        list2 = [f(x, c) for x in s[2][1:]]
    elif isinstance(s[2], str):
        list2 = f(s[2], c)

    if any(x in list1 for x in list2):
        return True
    return False


def Contains_all_of(f, c, solver_parameters, s):
    if isinstance(s[1], list) and s[1][0] == "Array":
        list1 = [f(x, c) for x in s[1][1:]]
    elif isinstance(s[1], str):
        list1 = f(s[1], c)

    if isinstance(s[2], list) and s[2][0] == "Array":
        list2 = [f(x, c) for x in s[2][1:]]
    elif isinstance(s[2], str):
        list2 = f(s[2], c)

    if all(x in list1 for x in list2):
        return True
    return False


def Contains_none_of(f, c, solver_parameters, s):
    return not Contains_any_of(f, c, solver_parameters, s)


def HasMatchingSublist(f, c, solver_parameters, s):
    """
    ["HasMatchingSublist", list, required_match_count, position, contiguous, function, more parameters]
    """
    the_list = f(s[1], c)[1:]
    required_match_count = f(s[2], c)
    position = f(s[3], c)
    contiguous = f(s[4], c)
    conditions = []

    for i, x in enumerate(the_list):
        the_function_name = s[5][0]
        ss = [the_function_name, x] + s[6:]
        conditions.append(f(ss, c))
        pass

    return has_matching_sublist(
        my_list=the_list,
        required_match_count=required_match_count,
        position=position,
        contiguous=contiguous,
        conditions=conditions,
    )


def Appended(f, c, solver_parameters, s):
    """
    ["Appended", array, value]
    The `array` must be an array of values.
    The `value` is the value to append to the array.
    """
    array = f(s[1], c)

    if not (isinstance(array, list) and array[0] == "Array"):
        raise ValueError("Parameter 1 must be an array.")

    value = f(s[2], c)

    array = [x for x in array[1:]]
    array.append(value)
    return ["Array"] + array
