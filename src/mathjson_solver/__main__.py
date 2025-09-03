import numbers
from typing import Union, Any
from functools import reduce
import math
from copy import deepcopy
from statistics import median
import logging
import traceback
import datetime

NUMPY_AVAILABLE = False
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    pass

NoneType = type(None)


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


def _MultiplyByScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x * a for x in l]


def _MultiplyByArray(
    l1: list[numbers.Real], l2: list[numbers.Real]
) -> list[numbers.Real]:
    return [a * b for a, b in zip(l1, l2)]


def _AddScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x + a for x in l]


def _SubtractScalar(l: list[numbers.Real], a: numbers.Real) -> list[numbers.Real]:
    return [x - a for x in l]


def _AddArray(l1: list[numbers.Real], l2: list[numbers.Real]) -> list[numbers.Real]:
    return [a + b for a, b in zip(l1, l2)]


def _SubtractArray(
    l1: list[numbers.Real], l2: list[numbers.Real]
) -> list[numbers.Real]:
    return [a - b for a, b in zip(l1, l2)]


def _CumulativeProduct(l: list) -> list:
    res = []
    for i, x in enumerate(l):
        if i == 0:
            res.append(x)
        else:
            res.append(reduce(lambda a, b: a * b, l[: i + 1]))
    return res


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


class MathJSONException(Exception):
    """Exception for MathJSON processing issues"""

    def __init__(self, e, expr, *args, **kwargs):
        super().__init__(args)
        self.e = e
        self.expr = expr
        self.construct = kwargs.get("mathjson_construct", "MathJSON")

    def __str__(self):
        if hasattr(self.e, "message"):
            m = self.e.message
        else:
            m = str(self.e)
        return f"Problem in {self.construct}. {self.expr}. {m}"


# def requires_array(func):
#     def inner1(*args, **kwargs):
#         try:
#             if args[0][1][0] == "Array" and len(args[0][1]) > 0:
#                 return func(*args, **kwargs)
#             else:
#                 raise ValueError(f"'{func.__name__}' should receive a list")
#         except TypeError:
#             raise ValueError(f"'{func.__name__}' really should receive a list")

#     return inner1


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
    if type(x) in [int, float, str]:
        return f"{x}"
    elif type(x) in [bool, NoneType]:
        if x:
            return True
        else:
            return False
    return x


def comparison_safe_converter_for_pairs(
    v1, v2
) -> (Union[str, float], Union[str, float]):
    if is_numeric(v1):
        v1 = float(v1)
    if is_numeric(v2):
        v2 = float(v2)
    return v1, v2


def create_mathjson_solver(solver_parameters):
    def f(s, *args):
        if args:
            c = deepcopy(args[0])
        else:
            c = {}
        #         c = deepcopy(kwargs.get("c", {}))
        if isinstance(s, numbers.Number):
            return s
        if isinstance(s, list):

            def Arr(s):
                return s

            def Add(s):
                l_res = []
                tmp = 0
                for i, x in enumerate(s[1:]):
                    res = f(x, c)
                    if is_numeric(res):
                        res = float(res)
                    if i == 0:
                        tmp = res
                    else:
                        try:
                            tmp = tmp + res
                        except TypeError:
                            pass

                    # if isinstance(res, list):
                    #     l_res.append(sum([xx for xx in res[1:]]))
                    # else:
                    #     l_res.append(res)

                return tmp

                # tmp = 0
                # for i, x in enumerate(l):
                #     if i == 0:
                #         tmp = x
                #     else:
                #         tmp = tmp + x
                # return tmp

            # def Sum(s):
            #     l_res = []
            #     for x in s[1:]:
            #         res = f(x, c)
            #         if isinstance(res, list):
            #             l_res.append(sum([xx for xx in res[1:]]))
            #         else:
            #             l_res.append(res)
            #     return sum(l_res)

            def Sum(s):
                l_res = ["Array"]
                for x in s[1:]:
                    res = f(x, c)
                    if isinstance(res, list):
                        l_res.append(Add(["Array"] + [xx for xx in res[1:]]))
                    else:
                        l_res.append(res)
                return Add(l_res)

            def Max(s):
                if isinstance(s[1], str):
                    return max([f(x, c) for x in f(s[1], c) if is_numeric(f(x, c))])
                else:
                    return max([f(x, c) for x in s[1][1:] if is_numeric(f(x, c))])

            def Min(s):
                if isinstance(s[1], str):
                    return min([f(x, c) for x in f(s[1], c) if is_numeric(f(x, c))])
                else:
                    return min([f(x, c) for x in s[1][1:] if is_numeric(f(x, c))])

            def Average(s):
                if isinstance(s[1], str):
                    # A reference to "answer" has been passed
                    s_ = [float(f(x, c)) for x in f(s[1], c) if is_numeric(f(x, c))]
                else:
                    s_ = [float(f(x, c)) for x in s[1][1:] if is_numeric(f(x, c))]
                # print(f"{s_} {sum(s_)}/{len(s_)}")
                try:
                    return sum(s_) / len(s_)
                except ZeroDivisionError:
                    return None

            def Median(s):
                if isinstance(s[1], str):
                    return median([f(x, c) for x in f(s[1], c) if is_numeric(f(x, c))])
                else:
                    return median([f(x, c) for x in s[1][1:] if is_numeric(f(x, c))])

            def Length(s):
                if isinstance(s[1], str):
                    return len([x for x in f(s[1], c)][1:])
                else:
                    return len([x for x in s[1][1:]])

            def Any(s):
                return any([f(x, c) for x in s[1][1:]])

            def All(s):
                return all([f(x, c) for x in s[1][1:]])

            def Int(s):
                try:
                    return int(f(s[1], c))
                except ValueError:
                    return int(float(f(s[1], c)))

            def Float(s):
                return float(f(s[1], c))

            def Constants(s):
                for x in s[1:-1]:
                    c[x[0]] = f(x[1], c)
                return f(s[-1], c)

            def Switch(s):
                expression = f(s[1], c)
                for x in s[3:]:
                    if len(x) != 2:
                        raise ValueError(
                            "Case of 'Switch' should have exactly two parameters"
                        )
                    if comparison_safe_converter(
                        expression
                    ) == comparison_safe_converter(f(x[0], c)):
                        return f(x[1], c)
                else:
                    return f(s[2], c)

            def StrictSwitch(s):
                expression = f(s[1], c)
                for x in s[3:]:
                    if len(x) != 2:
                        raise ValueError(
                            "Case of 'StrictSwitch' should have exactly two parameters"
                        )
                    if expression == f(x[0], c):
                        return f(x[1], c)
                else:
                    return f(s[2], c)

            def If(s):
                if len(s) < 3:
                    raise ValueError("Wrong parameters for 'If'")
                for x in s[1:-1]:
                    if len(x) != 2:
                        raise ValueError("Wrong if or elif in 'If'")
                    try:
                        if f(x[0], c):
                            try:
                                return f(x[1], c)
                            except MathJSONException:
                                logging.error(
                                    "MathJSONException: %s", traceback.format_exc()
                                )
                                continue
                    except MathJSONException:
                        logging.error("MathJSONException: %s", traceback.format_exc())
                        return f(s[-1], c)  # return default value (else)

                return f(s[-1], c)

            def In(s):
                if len(s) != 3:
                    raise ValueError("Wrong parameters for 'In'")
                if isinstance(s[2], list) and s[2][0] == "Array":
                    return f(s[1], c) in [f(x, c) for x in s[2][1:]]

                elif isinstance(s[2], str):
                    return f(s[1], c) in f(s[2], c)
                else:
                    raise ValueError(
                        "Wrong parameters for 'In'. Parameter 2 must be a list."
                    )

            def Not_in(s):
                return not In(s)

            def Contains_any_of(s):
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

            def Contains_all_of(s):
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

            def Contains_none_of(s):
                return not Contains_any_of(s)

            def Str(s):
                if len(s) < 2:
                    raise ValueError("Wrong parameters for 'Str'")
                return f"{f(s[1])}"

            def Not(s):
                return not f(s[1])

            def Map(s):
                """
                ["Map", list, function, more parameters]
                The `function` must accept at least one parameter. That is for the current loop element.
                The `more parameters` are for any additional parameters that function might have.
                """
                z = f(s[1], c)
                if isinstance(z, list):
                    retlist = ["Array"]
                    for x in z[1:]:
                        try:
                            the_function_name = s[2][0]
                            ss = [the_function_name, x] + s[3:]
                            retlist.append(f(ss, c))
                        except MathJSONException:
                            retlist.append(x)
                    return retlist

            def StrictMap(s):
                """
                ["Map", list, function, more parameters]
                The `function` must accept at least one parameter. That is for the current loop element.
                The `more parameters` are for any additional parameters that function might have.
                """
                z = f(s[1], c)
                if isinstance(z, list):
                    retlist = ["Array"]
                    for x in z[1:]:
                        the_function_name = s[2][0]
                        ss = [the_function_name, x] + s[3:]
                        retlist.append(f(ss, c))
                    return retlist

            def Filter(s):
                """
                ["Filter", list, function, more parameters]
                The `function` must accept at least one parameter. That is for the current loop element.
                The `more parameters` are for any additional parameters that function might have.
                """
                z = f(s[1], c)
                if isinstance(z, list):
                    retlist = ["Array"]
                    for x in z[1:]:
                        the_function_name = s[2][0]
                        ss = [the_function_name, x] + s[3:]
                        if f(ss, c):
                            retlist.append(x)
                    return retlist

            def HasMatchingSublist(s):
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

            def Strptime(s):
                datetime_str = f(s[1], c)
                parameters = f(s[2], c)
                return datetime.datetime.strptime(datetime_str, parameters)

            def Strftime(s):
                dt = f(s[1], c)
                parameters = f(s[2], c)
                return dt.strftime(parameters)

            def Now(s):
                return datetime.datetime.now()

            def Today(s):
                return datetime.date.today()

            def TimeDeltaDays(s):
                return datetime.timedelta(days=f(s[1], c))

            def TimeDeltaMinutes(s):
                return datetime.timedelta(minutes=f(s[1], c))

            def TimeDeltaHours(s):
                return datetime.timedelta(hours=f(s[1], c))

            def TimeDeltaWeeks(s):
                return datetime.timedelta(weeks=f(s[1], c))

            # def Equal(s):
            #     a = comparison_safe_converter(f(s[1], c))
            #     b = comparison_safe_converter(f(s[2], c))
            #     return a == b
            #     if type(a) in [int, float, str]:
            #         a = f"{a}"
            #     elif type(a) in [bool, NoneType]:
            #         if a:
            #             a = True
            #         else:
            #             a = None

            #     if is_numeric(a):

            #     lambda s: f"{f(s[1], c)}" == f"{f(s[2], c)}",

            def IsDefined(s):
                # Todo: This does not work
                return s[1] in c.keys()

            def Greater(s):
                v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
                try:
                    return v1 > v2
                except TypeError:
                    return False

            def GreaterEqual(s):
                v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
                try:
                    return v1 >= v2
                except TypeError:
                    return False

            def Less(s):
                v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
                try:
                    return v1 < v2
                except TypeError:
                    return False

            def LessEqual(s):
                v1, v2 = comparison_safe_converter_for_pairs(f(s[1], c), f(s[2], c))
                try:
                    return v1 <= v2
                except TypeError:
                    return False

            # sin, cos, tan, arcsin, arccos, arctan
            def Sin(s):
                return math.sin(f(s[1], c))

            def Arcsin(s):
                return math.asin(f(s[1], c))

            def Cos(s):
                return math.cos(f(s[1], c))

            def Arccos(s):
                return math.acos(f(s[1], c))

            def Tan(s):
                return math.tan(f(s[1], c))

            def Arctan(s):
                return math.atan(f(s[1], c))

            def Pi(s):
                return math.pi

            def Variable(s):
                """
                ["Variable", variable_name]
                The `variable_name` must be a string.
                """
                variable_name = s[1]
                if variable_name in c:
                    return f(c[variable_name], c)
                else:
                    raise KeyError(f"Variable '{variable_name}' is not defined")

            def Function(s):
                """
                ["Function", function_expression, parameters]
                The `function_name` must be a callable function.
                The `parameters` are the arguments to be passed to the function.
                """
                function_expression = s[1]
                arguments = s[2:]
                return 0
                # return f(function_expression, c) function_name(*parameters)

            def MultiplyByScalar(s):
                """
                ["MultiplyByScalar", array, scalar]
                The `array` must be an array of numeric values.
                The `scalar` is the number to multiply each element by.
                """
                array = f(s[1], c)
                scalar = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _MultiplyByScalar(array, scalar)

            def MultiplyByArray(s):
                """
                ["MultiplyByArray", array1, array2]
                The `array1` and `array2` must be arrays of the same length.
                """
                array1 = f(s[1], c)
                array2 = f(s[2], c)
                if not (isinstance(array1, list) and array1[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                if not (isinstance(array2, list) and array2[0] == "Array"):
                    raise ValueError("Parameter 2 must be an array.")
                array1 = [f(x, c) for x in array1[1:]]
                array2 = [f(x, c) for x in array2[1:]]
                if len(array1) != len(array2):
                    raise ValueError("Both arrays must be of the same length.")
                return ["Array"] + _MultiplyByArray(array1, array2)

            def AddScalar(s):
                """
                ["AddScalar", array, scalar]
                The `array` must be an array of numeric values.
                The `scalar` is the number to add to each element.
                """
                array = f(s[1], c)
                scalar = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _AddScalar(array, scalar)

            def SubtractScalar(s):
                """
                ["SubtractScalar", array, scalar]
                The `array` must be an array of numeric values.
                The `scalar` is the number to subtract from each element.
                """
                array = f(s[1], c)
                scalar = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _SubtractScalar(array, scalar)

            def AddArray(s):
                """
                ["AddArray", array1, array2]
                The `array1` and `array2` must be arrays of the same length.
                """
                array1 = f(s[1], c)
                array2 = f(s[2], c)
                if not (isinstance(array1, list) and array1[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                if not (isinstance(array2, list) and array2[0] == "Array"):
                    raise ValueError("Parameter 2 must be an array.")
                array1 = [f(x, c) for x in array1[1:]]
                array2 = [f(x, c) for x in array2[1:]]
                if len(array1) != len(array2):
                    raise ValueError("Both arrays must be of the same length.")
                return ["Array"] + _AddArray(array1, array2)

            def SubtractArray(s):
                """
                ["SubtractArray", array1, array2]
                The `array1` and `array2` must be arrays of the same length.
                """
                array1 = f(s[1], c)
                array2 = f(s[2], c)
                if not (isinstance(array1, list) and array1[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                if not (isinstance(array2, list) and array2[0] == "Array"):
                    raise ValueError("Parameter 2 must be an array.")
                array1 = [f(x, c) for x in array1[1:]]
                array2 = [f(x, c) for x in array2[1:]]
                if len(array1) != len(array2):
                    raise ValueError("Both arrays must be of the same length.")
                return ["Array"] + _SubtractArray(array1, array2)

            def GenerateRange(s):
                """
                ["GenerateRange", end]
                or
                ["GenerateRange", start, end, step]
                The `start`, `end`, and `step` are numeric values.
                """
                if len(s) == 2:
                    end = f(s[1], c)
                    start = 0
                    step = 1
                elif len(s) == 4:
                    start = f(s[1], c)
                    end = f(s[2], c)
                    step = f(s[3], c)
                else:
                    raise ValueError(
                        "GenerateRange requires either 1 or 3 parameters (end or start, end, step)."
                    )
                if step == 0:
                    raise ValueError("Step cannot be zero.")
                if (start < end and step < 0) or (start > end and step > 0):
                    raise ValueError("Step direction is incorrect for the given range.")
                result = ["Array"]
                if start < end:
                    current = start
                    while current < end:
                        result.append(current)
                        current += step
                else:
                    current = start
                    while current > end:
                        result.append(current)
                        current += step
                return result

            def AtIndex(s):
                """
                ["AtIndex", array, index]
                The `array` must be an array of values.
                The `index` is the index of the element to retrieve.
                """
                array = f(s[1], c)
                index = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                # array = [f(x, c) for x in array[1:]]
                # return array[index]
                array = [x for x in array[1:]]
                return f(array[index], c)

            def Slice(s):
                """
                ["Slice", array, start, end]
                The `array` must be an array of values.
                The `start` and `end` are the slice indices.
                """
                array = f(s[1], c)
                start = f(s[2], c)
                end = f(s[3], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + array[start:end]

            def CumulativeProduct(s):
                """
                ["CumulativeProduct", array]
                The `array` must be an array of numeric values.
                """
                array = f(s[1], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                return ["Array"] + _CumulativeProduct(array)
                # return _CumulativeProduct(array)

            def Interp(s):
                """
                ["Interp", x_array, y_array, target_x]
                The `x_array` and `y_array` must be arrays of the same length.
                The `target_x` is the x value to interpolate for.
                """
                x_array = f(s[1], c)
                y_array = f(s[2], c)
                target_x = f(s[3], c)
                if not (isinstance(x_array, list) and x_array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                if not (isinstance(y_array, list) and y_array[0] == "Array"):
                    raise ValueError("Parameter 2 must be an array.")
                x_array = [f(x, c) for x in x_array[1:]]
                y_array = [f(y, c) for y in y_array[1:]]
                return linear_interpolate(x_array, y_array, target_x)

            def FindIntervalIndex(s):
                """
                ["FindIntervalIndex", array, target_value]
                The `array` must be an array of numeric values.
                The `target_value` is the value to find the interval index for.
                """
                array = f(s[1], c)
                target_value = f(s[2], c)
                if not (isinstance(array, list) and array[0] == "Array"):
                    raise ValueError("Parameter 1 must be an array.")
                array = [f(x, c) for x in array[1:]]
                zz = find_interpolation_bounds_2indexes(array, target_value)
                return zz[0]

            def TrapezoidalIntegrate(s):
                """
                ["TrapezoidalIntegrate", function_expression, start, end, n, variable]
                """
                if not NUMPY_AVAILABLE:
                    raise ImportError(
                        "TrapezoidalIntegrate requires 'numpy'. Install with 'pip install numpy'."
                    )
                function_expression = s[1]
                start = f(s[2], c)
                end = f(s[3], c)
                n = f(s[4], c)
                variable = s[5]

                t = np.linspace(start, end, n + 1)

                # Calculate the integral using the trapezoidal rule

                values = []
                for x in t:
                    variable_name = variable[1]
                    variable_value = x
                    c[variable_name] = variable_value
                    values.append(f(function_expression, c))
                h = (end - start) / n
                # print("values=", values)
                return h * (0.5 * values[0] + np.sum(values[1:-1]) + 0.5 * values[-1])

                # return total_area

            constructs = {
                "Sum": Sum,
                "Add": Add,
                "Subtract": lambda s: reduce(
                    lambda a, b: a - b, [f(x, c) for x in s[1:]]
                ),
                "Constants": Constants,
                "Switch": Switch,
                "StrictSwitch": StrictSwitch,
                "If": If,
                "Multiply": lambda s: reduce(
                    lambda a, b: float(a) * float(b), [f(x, c) for x in s[1:]]
                ),
                "Divide": lambda s: f(s[1], c) / f(s[2], c),
                "Negate": lambda s: -f(s[1], c),
                "Power": lambda s: pow(f(s[1], c), f(s[2], c)),
                "Root": lambda s: pow(f(s[1], c), 1.0 / f(s[2], c)),
                "Sqrt": lambda s: pow(f(s[1], c), 1.0 / 2),
                "Square": lambda s: pow(f(s[1], c), 2),
                "Exp": lambda s: math.exp(f(s[1], c)),
                "Log": lambda s: math.log(f(s[1], c)),
                "Log2": lambda s: math.log2(f(s[1], c)),
                "Log10": lambda s: math.log10(f(s[1], c)),
                "Ln": lambda s: math.log(f(s[1], c)),
                # "Equal": lambda s: f"{f(s[1], c)}" == f"{f(s[2], c)}",
                "Equal": lambda s: comparison_safe_converter(f(s[1], c))
                == comparison_safe_converter(f(s[2], c)),
                "StrictEqual": lambda s: f(s[1], c) == f(s[2], c),
                # "Greater": lambda s: f(s[1], c) > f(s[2], c),
                "Greater": Greater,
                # "GreaterEqual": lambda s: f(s[1], c) >= f(s[2], c),
                "GreaterEqual": GreaterEqual,
                # "Less": lambda s: f(s[1], c) < f(s[2], c),
                "Less": Less,
                # "LessEqual": lambda s: f(s[1], c) <= f(s[2], c),
                "LessEqual": LessEqual,
                # "NotEqual": lambda s: f(s[1], c) != f(s[2], c),
                "NotEqual": lambda s: comparison_safe_converter(f(s[1], c))
                != comparison_safe_converter(f(s[2], c)),
                "Abs": lambda s: abs(f(s[1], c)),
                "Round": lambda s: (
                    round(f(s[1], c), f(s[2], c))
                    if len(s) == 3
                    else int(round(f(s[1], c)))
                ),
                "Max": Max,
                "Min": Min,
                "Average": Average,
                "Median": Median,
                "Length": Length,
                "Any": Any,
                "All": All,
                "Array": Arr,
                "In": In,
                "Not_in": Not_in,
                "Contains_any_of": Contains_any_of,
                "Contains_all_of": Contains_all_of,
                "Contains_none_of": Contains_none_of,
                "NotIn": Not_in,
                "ContainsAnyOf": Contains_any_of,
                "ContainsAllOf": Contains_all_of,
                "ContainsNoneOf": Contains_none_of,
                "Int": Int,
                "Float": Float,
                "Str": Str,
                "Not": Not,
                # "IsDefined": lambda s: s[1] in c,
                "IsDefined": IsDefined,
                "Map": Map,
                "StrictMap": StrictMap,
                "Filter": Filter,
                "HasMatchingSublist": HasMatchingSublist,
                "Strptime": Strptime,
                "Strftime": Strftime,
                "Today": Today,
                "Now": Now,
                "TimeDeltaWeeks": TimeDeltaWeeks,
                "TimeDeltaHours": TimeDeltaHours,
                "TimeDeltaMinutes": TimeDeltaMinutes,
                "TimeDeltaDays": TimeDeltaDays,
                "Function": Function,
                "Variable": Variable,
                "MultiplyByScalar": MultiplyByScalar,
                "MultiplyByArray": MultiplyByArray,
                "AddScalar": AddScalar,
                "SubtractScalar": SubtractScalar,
                "AddArray": AddArray,
                "SubtractArray": SubtractArray,
                "GenerateRange": GenerateRange,
                "AtIndex": AtIndex,
                "Slice": Slice,
                "CumulativeProduct": CumulativeProduct,
                "Interp": Interp,
                "FindIntervalIndex": FindIntervalIndex,
                "TrapezoidalIntegrate": TrapezoidalIntegrate,
                "Sin": Sin,
                "Cos": Cos,
                "Tan": Tan,
                "Arcsin": Arcsin,
                "Arccos": Arccos,
                "Arctan": Arctan,
                "Pi": Pi,
            }
            if not s:
                # Empty equation given - []
                return None
            if s[0] in constructs:
                try:
                    return constructs[s[0]](s)

                # except RecursionError:
                #     return s[0]
                # except Exception as e:
                except TypeError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0])
                except ValueError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0])
                except IndexError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0])
                except ZeroDivisionError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0])
            else:
                # raise MathJSONException(
                #     NotImplementedError(f"'{s[0]}' is not supported"), s
                # )
                return s
        elif s in solver_parameters:
            try:
                return f(solver_parameters[s], c)
            except RecursionError:
                return solver_parameters[s]
        elif s in c:
            return f(c[s], c)
        else:
            # raise KeyError(f"Parameter '{s}' is not defined")
            return s

    return f


def extract_variables(s: Union[list, int, float, str], li: set, ignore_list: set):
    constructs = [
        "Add",
        "Sum",
        "Subtract",
        "Constants",
        "Switch",
        "If",
        "Multiply",
        "Divide",
        "Negate",
        "Power",
        "Root",
        "Sqrt",
        "Square",
        "Exp",
        "Log",
        "Log2",
        "Log10",
        "Ln",
        "Equal",
        "Greater",
        "GreaterEqual",
        "Less",
        "LessEqual",
        "NotEqual",
        "Abs",
        "Round",
        "Max",
        "Min",
        "Average",
        "Median",
        "Length",
        "Any",
        "All",
        "Array",
        "In",
        "Not_in",
        "Contains_any_of",
        "Contains_all_of",
        "Contains_none_of",
        "NotIn",
        "ContainsAnyOf",
        "ContainsAllOf",
        "ContainsNoneOf",
        "Int",
        "Float",
        "Str",
        "Not",
        "IsDefined",
        "Map",
        "HasMatchingSublist",
        "Strptime",
        "Strftime",
        "Today",
        "Now",
        "TimeDeltaWeeks",
        "TimeDeltaHours",
        "TimeDeltaMinutes",
        "TimeDeltaDays",
        "Function",
        "Variable",
        "MultiplyByScalar",
        "MultiplyByArray",
        "AddScalar",
        "SubtractScalar",
        "AddArray",
        "SubtractArray",
        "GenerateRange",
        "AtIndex",
        "Slice",
        "CumulativeProduct",
        "Interp",
        "FindIntervalIndex",
        "TrapezoidalIntegrate",
        "TrapezoidalIntegrate",
        "Sin",
        "Cos",
        "Tan",
        "Arcsin",
        "Arccos",
        "Arctan",
        "Pi",
    ]
    if isinstance(s, str):
        if s in ignore_list:
            return li
        if s not in constructs:
            li.add(s)
        return li
    elif isinstance(s, list):
        if s[0] == "Constants":
            for x in s[1:-1]:
                ignore_list.add(x[0])
                li.update(extract_variables(x[1], li, ignore_list))
            li.update(extract_variables(x[-1], li, ignore_list))
        elif s[0] == "If":
            for elif_block in s[1:-1]:  # s[1] is list
                for x in elif_block:
                    li.update(extract_variables(x, li, ignore_list))
            li.update(extract_variables(s[-1], li, ignore_list))
        else:
            for x in s[1:]:
                li.update(extract_variables(x, li, ignore_list))
        return li
    else:
        return li
