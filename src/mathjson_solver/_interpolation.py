"""
Linear interpolation helpers, backing the Interp/FindIntervalIndex
constructs.
"""

from typing import Union


# def find_interpolation_bounds(
#     l: list, target: int | float
# ) -> Union[Union[int, float], tuple[Union[int, float], Union[int, float]]]:
#     for i, x in enumerate(l):
#         if i == 0:
#             continue
#         if l[i - 1] <= target and target <= l[i]:
#             if target == l[i - 1] or target == l[i]:
#                 return target
#             else:
#                 return l[i - 1], l[i]
#     else:
#         raise ValueError("Target value is outside interpolation range.")


def find_interpolation_bounds_indexes(
    l: list, target: int | float
) -> Union[Union[int, float], tuple[Union[int, float], Union[int, float]]]:
    for i, x in enumerate(l):
        if i == 0:
            continue
        if l[i - 1] <= target and target <= l[i]:
            if target == l[i - 1]:
                return i - 1
            elif target == l[i]:
                return i
            else:
                return i - 1, i
    else:
        raise ValueError("Target value is outside interpolation range.")


def find_interpolation_bounds_2indexes(
    l: list, target: int | float
) -> Union[Union[int, float], tuple[Union[int, float], Union[int, float]]]:
    for i, x in enumerate(l):
        if i == len(l) - 1:
            return i - 1, i
        if l[i] <= target and target < l[i + 1]:
            return i, i + 1
    else:
        raise ValueError("Target value is outside interpolation range.")


def linear_interpolate(x_array, y_array, target_x):
    # Find the interval where target_x falls
    # Handle edge cases (target_x outside range)
    # Apply: y = y1 + (y2 - y1) * (target_x - x1) / (x2 - x1)

    # first check if both arrays are the same length
    if len(x_array) != len(y_array) or len(x_array) < 2:
        raise ValueError(
            "Both arrays need to be the same length and with at least 2 elements."
        )
    bounds_indexes = find_interpolation_bounds_indexes(x_array, target_x)
    if isinstance(bounds_indexes, tuple):
        x1, x2 = x_array[bounds_indexes[0]], x_array[bounds_indexes[1]]
        y1, y2 = y_array[bounds_indexes[0]], y_array[bounds_indexes[1]]
        return y1 + (y2 - y1) * (target_x - x1) / (x2 - x1)
    else:
        return y_array[bounds_indexes]
