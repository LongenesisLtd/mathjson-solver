import numbers
from functools import reduce
import math
from copy import deepcopy


def Subtract(a: numbers.Number, b: numbers.Number):
    return a - b


def Multiply(a: numbers.Number, b: numbers.Number):
    return a * b


def create_mathjson_solver(solver_parameters):
    def evaluate_mathjson(s, **kwargs):
        if "constants" in kwargs:
            constants = deepcopy(kwargs["constants"])
        else:
            constants = {}
        if isinstance(s, numbers.Number):
            return s
        if isinstance(s, list):
            if s[0] == "Constants":
                if len(s) < 3:
                    raise ValueError(
                        f"'Constants' should have at least three parameters"
                    )
                # constants
                for x in s[1:-1]:
                    constants[x[0]] = evaluate_mathjson(x[1], constants=constants)
                return evaluate_mathjson(s[-1], constants=constants)

            if s[0] == "Switch":
                if len(s) < 4:
                    raise ValueError(f"'Switch' should have at least four parameters")
                expression = evaluate_mathjson(s[1], constants=constants)
                for x in s[3:]:
                    if len(x) != 2:
                        raise ValueError(
                            f"Case of 'Switch' should have exactly two parameters"
                        )
                    if expression == evaluate_mathjson(x[0], constants=constants):
                        return evaluate_mathjson(x[1], constants=constants)
                else:
                    return evaluate_mathjson(s[2], constants=constants)
            if s[0] == "Add":
                if len(s) < 3:
                    raise ValueError(f"'Add' should have at least two parameters")
                return sum([evaluate_mathjson(x, constants=constants) for x in s[1:]])
            if s[0] == "Sum":
                if len(s) < 3:
                    raise ValueError(f"'Sum' should have at least two parameters")
                return sum([evaluate_mathjson(x, constants=constants) for x in s[1:]])
            if s[0] == "Subtract":
                if len(s) < 3:
                    raise ValueError(f"'Subtract' should have at least two parameters")
                return reduce(
                    Subtract, [evaluate_mathjson(x, constants=constants) for x in s[1:]]
                )
            if s[0] == "Multiply":
                if len(s) < 3:
                    raise ValueError(f"'Multiply' should have at least two parameters")
                return reduce(
                    Multiply, [evaluate_mathjson(x, constants=constants) for x in s[1:]]
                )
            if s[0] == "Divide":
                if len(s) != 3:
                    raise ValueError(f"'Divide' should have exactly two parameters")
                return evaluate_mathjson(s[1], constants=constants) / evaluate_mathjson(
                    s[2], constants=constants
                )
            if s[0] == "Negate":
                if len(s) != 2:
                    raise ValueError(f"'Negate' should have only one parameter")
                return -evaluate_mathjson(s[1], constants=constants)
            if s[0] == "Power":
                if len(s) != 3:
                    raise ValueError(f"'Power' should have exactly two parameters")
                return pow(
                    evaluate_mathjson(s[1], constants=constants),
                    evaluate_mathjson(s[2], constants=constants),
                )
            if s[0] == "Root":
                if len(s) != 3:
                    raise ValueError(f"'Root' should have only two parameters")
                return pow(
                    evaluate_mathjson(s[1], constants=constants),
                    1 / evaluate_mathjson(s[2], constants=constants),
                )
            if s[0] == "Sqrt":
                if len(s) != 2:
                    raise ValueError(f"'Sqrt' should have only one parameter")
                return pow(evaluate_mathjson(s[1], constants=constants), 1 / 2)
            if s[0] == "Square":
                if len(s) != 2:
                    raise ValueError(f"'Square' should have only one parameter")
                return pow(evaluate_mathjson(s[1], constants=constants), 2)
            if s[0] == "Exp":
                if len(s) != 2:
                    raise ValueError(f"'Exp' should have only one parameter")
                return math.exp(evaluate_mathjson(s[1], constants=constants))
            if s[0] == "Log":
                if len(s) != 2:
                    raise ValueError(f"'Log' should have only one parameter")
                return math.log(evaluate_mathjson(s[1], constants=constants))
            if s[0] == "Log2":
                if len(s) != 2:
                    raise ValueError(f"'Log2' should have only one parameter")
                return math.log2(evaluate_mathjson(s[1], constants=constants))
            if s[0] == "Log10":
                if len(s) != 2:
                    raise ValueError(f"'Log10' should have only one parameter")
                return math.log10(evaluate_mathjson(s[1], constants=constants))

            if s[0] == "Equal":
                if len(s) != 3:
                    raise ValueError(f"'Equal' should have exactly two parameters")
                return evaluate_mathjson(
                    s[1], constants=constants
                ) == evaluate_mathjson(s[2], constants=constants)
            if s[0] == "Greater":
                if len(s) != 3:
                    raise ValueError(f"'Greater' should have exactly two parameters")
                return evaluate_mathjson(s[1], constants=constants) > evaluate_mathjson(
                    s[2], constants=constants
                )
            if s[0] == "GreaterEqual":
                if len(s) != 3:
                    raise ValueError(
                        f"'GreaterEqual' should have exactly two parameters"
                    )
                return evaluate_mathjson(
                    s[1], constants=constants
                ) >= evaluate_mathjson(s[2], constants=constants)
            if s[0] == "Less":
                if len(s) != 3:
                    raise ValueError(f"'Less' should have exactly two parameters")
                return evaluate_mathjson(s[1], constants=constants) < evaluate_mathjson(
                    s[2], constants=constants
                )
            if s[0] == "LessEqual":
                if len(s) != 3:
                    raise ValueError(f"'LessEqual' should have exactly two parameters")
                return evaluate_mathjson(
                    s[1], constants=constants
                ) <= evaluate_mathjson(s[2], constants=constants)
            if s[0] == "NotEqual":
                if len(s) != 3:
                    raise ValueError(f"'NotEqual' should have exactly two parameters")
                return evaluate_mathjson(
                    s[1], constants=constants
                ) != evaluate_mathjson(s[2], constants=constants)

            if s[0] == "Abs":
                if len(s) != 2:
                    raise ValueError(f"'Abs' should have only one parameter")
                return abs(evaluate_mathjson(s[1], constants=constants))
            if s[0] == "Round":
                if len(s) != 3:
                    raise ValueError(f"'Round' should have only one parameter")
                return round(
                    evaluate_mathjson(s[1], constants=constants),
                    evaluate_mathjson(s[2], constants=constants),
                )

            else:
                raise NotImplementedError(f"'{s[0]}' is not supported")
        elif s in solver_parameters:
            return evaluate_mathjson(solver_parameters[s], constants=constants)
        elif s in constants:
            return evaluate_mathjson(constants[s], constants=constants)
        else:
            return s

    #             raise NotImplementedError(f"'{s}' is not a recognized variable nor list nor number")
    return evaluate_mathjson
