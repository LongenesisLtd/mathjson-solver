import numbers
from typing import Union
from functools import reduce
import math
from copy import deepcopy
from statistics import median
import logging
import traceback


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


def requires_array(func):
    def inner1(*args, **kwargs):
        try:
            if args[0][1][0] == "Array" and len(args[0][1]) > 0:
                return func(*args, **kwargs)
            else:
                raise ValueError(f"'{func.__name__}' should receive a list")
        except TypeError:
            raise ValueError(f"'{func.__name__}' really should receive a list")

    return inner1


def is_numeric(x):
    try:
        float(x)
    except ValueError:
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


def has_sublist2(
    *,
    my_list: list,
    required_match_count: int,
    position: int,
    contiguous: bool,
    condition: callable,
) -> bool:
    if contiguous:
        # Check for contiguous matches based on position
        if position == 0:
            # Check if the beginning of the list matches
            count = sum(1 for x in my_list[:required_match_count] if condition(x))
            return count == required_match_count
        elif position > 0:
            # Skip the first `position` elements
            count = sum(
                1
                for x in my_list[position : position + required_match_count]
                if condition(x)
            )
            return count == required_match_count
        elif position == -1:
            # Check if the end of the list matches
            count = sum(1 for x in my_list[-required_match_count:] if condition(x))
            return count == required_match_count
        elif position < -1:
            # Skip the last `abs(position)` elements
            count = sum(1 for x in my_list[:position] if condition(x))
            return count == required_match_count
    else:
        # Check for non-contiguous matches
        count = sum(1 for x in my_list if condition(x))
        return count >= required_match_count


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

            def Sum(s):
                l_res = []
                for x in s[1:]:
                    res = f(x, c)
                    if isinstance(res, list):
                        l_res.append(sum([xx for xx in res[1:]]))
                    else:
                        l_res.append(res)
                return sum(l_res)

            # @requires_array
            def Max(s):
                if isinstance(s[1], str):
                    return max([f(x, c) for x in f(s[1], c) if is_numeric(f(x, c))])
                else:
                    return max([f(x, c) for x in s[1][1:] if is_numeric(f(x, c))])

            # @requires_array
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

            # @requires_array
            def Median(s):
                if isinstance(s[1], str):
                    return median([f(x, c) for x in f(s[1], c) if is_numeric(f(x, c))])
                else:
                    return median([f(x, c) for x in s[1][1:] if is_numeric(f(x, c))])

            # @requires_array
            def Length(s):
                if isinstance(s[1], str):

                    return len([x for x in f(s[1], c)][1:])
                else:
                    return len([x for x in s[1][1:]])

            # @requires_array
            def Any(s):
                return any([f(x, c) for x in s[1][1:]])

            # @requires_array
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
                        the_function_name = s[2][0]
                        ss = [the_function_name, x] + s[3:]
                        retlist.append(f(ss, c))
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

            constructs = {
                "Sum": Sum,
                "Add": Sum,
                "Subtract": lambda s: reduce(
                    lambda a, b: a - b, [f(x, c) for x in s[1:]]
                ),
                "Constants": Constants,
                "Switch": Switch,
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
                "Equal": lambda s: f(s[1], c) == f(s[2], c),
                "Greater": lambda s: f(s[1], c) > f(s[2], c),
                "GreaterEqual": lambda s: f(s[1], c) >= f(s[2], c),
                "Less": lambda s: f(s[1], c) < f(s[2], c),
                "LessEqual": lambda s: f(s[1], c) <= f(s[2], c),
                "NotEqual": lambda s: f(s[1], c) != f(s[2], c),
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
                "IsDefined": lambda s: s[1] in c,
                "Map": Map,
                "HasMatchingSublist": HasMatchingSublist,
            }
            if s[0] in constructs:
                try:
                    return constructs[s[0]](s)
                except Exception as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0])
            else:
                # raise MathJSONException(
                #     NotImplementedError(f"'{s[0]}' is not supported"), s
                # )
                return s
        elif s in solver_parameters:
            return f(solver_parameters[s], c)
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
