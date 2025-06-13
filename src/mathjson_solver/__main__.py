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
                "TrapezoidalIntegrate": TrapezoidalIntegrate,
                "Sin": Sin,
                "Cos": Cos,
                "Tan": Tan,
                "Arcsin": Arcsin,
                "Arccos": Arccos,
                "Arctan": Arctan,
                "Pi": Pi,
            }
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
