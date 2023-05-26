import numbers
from functools import reduce
import math
from copy import deepcopy
from statistics import median


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

            @requires_array
            def Max(s):
                return max([f(x, c) for x in s[1][1:]])

            @requires_array
            def Min(s):
                return min([f(x, c) for x in s[1][1:]])

            @requires_array
            def Average(s):
                s_ = [float(f(x, c)) for x in s[1][1:] if is_numeric(f(x, c))]
                # print(f"{s_} {sum(s_)}/{len(s_)}")
                try:
                    return sum(s_) / len(s_)
                except ZeroDivisionError:
                    return None

            @requires_array
            def Median(s):
                return median([f(x, c) for x in s[1][1:]])

            @requires_array
            def Length(s):
                return len([f(x, c) for x in s[1][1:]])

            @requires_array
            def Any(s):
                return any([f(x, c) for x in s[1][1:]])

            @requires_array
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
                            f"Case of 'Switch' should have exactly two parameters"
                        )
                    if expression == f(x[0], c):
                        return f(x[1], c)
                else:
                    return f(s[2], c)

            def If(s):
                if len(s) < 3:
                    raise ValueError(f"Wrong parameters for 'If'")
                for x in s[1:-1]:
                    if len(x) != 2:
                        raise ValueError(f"Wrong if or elif in 'If'")
                    if f(x[0], c):
                        return f(x[1], c)
                return f(s[-1], c)

            def In(s):
                if len(s) != 3:
                    raise ValueError(f"Wrong parameters for 'In'")
                if type(s[2]) != list and s[2][0] != "Array":
                    raise ValueError(
                        f"Wrong parameters for 'In'. Parameter 2 must be a list."
                    )

                return f(s[1], c) in [f(x, c) for x in s[2][1:]]

            def Str(s):
                if len(s) < 2:
                    raise ValueError(f"Wrong parameters for 'Str'")
                return f"{f(s[1])}"

            constructs = {
                "Add": lambda s: sum([f(x, c) for x in s[1:]]),
                "Sum": lambda s: sum([f(x, c) for x in s[1:]]),
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
                "Round": lambda s: round(f(s[1], c), f(s[2], c))
                if len(s) == 3
                else int(round(f(s[1], c))),
                "Max": Max,
                "Min": Min,
                "Average": Average,
                "Median": Median,
                "Length": Length,
                "Any": Any,
                "All": All,
                "Array": Arr,
                "In": In,
                "Int": Int,
                "Float": Float,
                "Str": Str,
            }
            if s[0] in constructs:
                try:
                    return constructs[s[0]](s)
                except Exception as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0])
            else:
                raise MathJSONException(
                    NotImplementedError(f"'{s[0]}' is not supported"), s
                )
        elif s in solver_parameters:
            return f(solver_parameters[s], c)
        elif s in c:
            return f(c[s], c)
        else:
            return s

    return f
