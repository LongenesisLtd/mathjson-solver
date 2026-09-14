"""
General-purpose helpers used across several unrelated construct
categories (comparisons, datetime coercion, sublist matching) - not
specific to one math domain, unlike `_number_theory.py`,
`_special_functions.py`, etc.
"""

from typing import Union
import datetime

NoneType = type(None)


def _try_parse_datetime(value):
    """Try to parse a string as datetime or date. Returns original value if not parseable."""
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value
    if isinstance(value, str):
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            pass
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            pass
    return value


def is_numeric(x):
    try:
        float(x)
    except ValueError:
        return False
    except TypeError:
        return False
    else:
        return True


def has_matching_sublist(
    *,
    my_list: list,
    required_match_count: int,
    position: int,
    contiguous: bool,
    conditions: list[bool],
) -> bool:
    if contiguous:
        # Check for contiguous matches based on position
        if position == 0:
            # Check if the beginning of the list matches
            count = sum(
                1
                for i in range(min(required_match_count, len(my_list)))
                if conditions[i]
            )
            return count == required_match_count
        elif position > 0:
            # Skip the first `position` elements
            count = sum(
                1
                for i in range(position, position + required_match_count)
                if i < len(my_list) and conditions[i]
            )
            return count == required_match_count
        elif position == -1:
            # Check if the end of the list matches
            count = sum(
                1
                for i in range(len(my_list) - required_match_count, len(my_list))
                if conditions[i]
            )
            return count == required_match_count
        elif position < -1:
            # Skip the last `abs(position)` elements
            count = sum(1 for i in range(len(my_list) + position) if conditions[i])
            return count == required_match_count
    else:
        # Check for non-contiguous matches
        count = sum(1 for i in range(len(my_list)) if conditions[i])
        return count >= required_match_count


# def has_sublist2(
#     *,
#     my_list: list,
#     required_match_count: int,
#     position: int,
#     contiguous: bool,
#     condition: callable,
# ) -> bool:
#     if contiguous:
#         # Check for contiguous matches based on position
#         if position == 0:
#             # Check if the beginning of the list matches
#             count = sum(1 for x in my_list[:required_match_count] if condition(x))
#             return count == required_match_count
#         elif position > 0:
#             # Skip the first `position` elements
#             count = sum(
#                 1
#                 for x in my_list[position : position + required_match_count]
#                 if condition(x)
#             )
#             return count == required_match_count
#         elif position == -1:
#             # Check if the end of the list matches
#             count = sum(1 for x in my_list[-required_match_count:] if condition(x))
#             return count == required_match_count
#         elif position < -1:
#             # Skip the last `abs(position)` elements
#             count = sum(1 for x in my_list[:position] if condition(x))
#             return count == required_match_count
#     else:
#         # Check for non-contiguous matches
#         count = sum(1 for x in my_list if condition(x))
#         return count >= required_match_count


def comparison_safe_converter(x):
    if type(x) in [bool, NoneType]:  # bool before int (bool IS an int in Python)
        return "1" if x else "0"
    elif type(x) in [int, float, str]:
        return f"{x}"
    return x


def comparison_safe_converter_for_pairs(
    v1, v2
) -> (Union[str, float], Union[str, float]):
    if is_numeric(v1):
        v1 = float(v1)
    if is_numeric(v2):
        v2 = float(v2)
    return v1, v2
