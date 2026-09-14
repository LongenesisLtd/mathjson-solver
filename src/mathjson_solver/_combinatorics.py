"""
Pure combinatorial-number helpers, backing Subfactorial and BellNumber.
(Fibonacci/Multinomial/Choose are one-liners defined directly as
constructs in __main__.py; PowerSet/Permutations/Combinations/
CartesianProduct are itertools-based and also defined there.)
"""


def _subfactorial(n):
    """Derangement count !n, via the standard recurrence."""
    n = int(n)
    if n < 0:
        raise ValueError("'Subfactorial' requires a non-negative integer.")
    result = 1
    for k in range(1, n + 1):
        result = k * result + (-1) ** k
    return result


def _bell_number(n):
    """n-th Bell number, via the Bell triangle."""
    n = int(n)
    if n < 0:
        raise ValueError("'BellNumber' requires a non-negative integer.")
    row = [1]
    for _ in range(n):
        new_row = [row[-1]]
        for x in row:
            new_row.append(new_row[-1] + x)
        row = new_row
    return row[0]
