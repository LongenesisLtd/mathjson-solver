import numbers
import sys
from typing import Any as _Any
from collections.abc import Callable, Iterable
from functools import reduce
import math
from copy import deepcopy

from ._common import comparison_safe_converter
from ._exceptions import MathJSONExpression, MathJSONException

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


def translate_v1_mathjson(expr: MathJSONExpression) -> MathJSONExpression:
    """
    Rewrite a MathJSON expression written for mathjson-solver < 2.0.0 so it
    evaluates to the same result on >= 2.0.0.

    The only breaking change introduced in 2.0.0 is "Log": before 2.0.0 it
    always meant natural log (`["Log", x]` == `math.log(x)`); from 2.0.0 on
    it matches CortexJS (`["Log", x]` is log base 10, `["Log", x, b]` is log
    base `b`), and natural log moved to "Ln". Since the pre-2.0.0 "Log" only
    ever took one argument, every legacy `["Log", x]` node has exactly one
    correct translation: `["Ln", x]`. This function walks the expression
    tree and applies that rewrite, leaving everything else untouched, so
    existing expressions don't need to be hand-migrated to keep working
    while still gaining access to functions added in 2.x.
    """
    if isinstance(expr, list):
        if len(expr) == 2 and expr[0] == "Log":
            return ["Ln", translate_v1_mathjson(expr[1])]
        return [translate_v1_mathjson(item) for item in expr]
    return expr


from ._arithmetic_constructs import (
    Add,
    Sum,
    Subtract,
    Max,
    Min,
    Average,
    Median,
    Clamp,
    Int,
    Float,
    Floor,
    Ceil,
    Numerator,
    Denominator,
    Rational,
    Product,
)
from ._array_arithmetic_constructs import (
    MultiplyByScalar,
    MultiplyByArray,
    AddScalar,
    SubtractScalar,
    AddArray,
    SubtractArray,
    GenerateRange,
    AtIndex,
    Slice,
    CumulativeProduct,
    CumulativeSum,
    Interp,
    FindIntervalIndex,
    TrapezoidalIntegrate,
)
from ._collection_constructs import (
    Arr,
    Length,
    First,
    Second,
    Third,
    Last,
    Rest,
    Most,
    Reverse,
    Sort,
    IsEmpty,
    Range,
    Join,
    Unique,
    Zip,
    At,
    Take,
    Drop,
    TakeWhile,
    DropWhile,
    Contains,
    IndexOf,
    IndexWhere,
    Find,
    CountIf,
    Position,
    RotateLeft,
    RotateRight,
    MaxBy,
    MinBy,
    ArgMax,
    ArgMin,
    Ordering,
    FlatMap,
    Scan,
    Differences,
    Dedup,
    Insert,
    DeleteAt,
    ReplaceAt,
    Partition,
    Chunk,
    GroupBy,
    ChunkBy,
    Tally,
    Union,
    Intersection,
    SetMinus,
    SymmetricDifference,
    Any,
    All,
    In,
    Not_in,
    Contains_any_of,
    Contains_all_of,
    Contains_none_of,
    HasMatchingSublist,
    Appended,
)
from ._combinatorics_constructs import (
    Fibonacci,
    Multinomial,
    Subfactorial,
    BellNumber,
    PowerSet,
    Permutations,
    Combinations,
    CartesianProduct,
)
from ._comparison_constructs import (
    Not,
    IsDefined,
    IsUndefined,
    Greater,
    GreaterEqual,
    Less,
    LessEqual,
    IdenticallyEqual,
    Congruent,
    BooleanAnd,
    BooleanOr,
)
from ._control_flow_constructs import (
    Constants,
    Switch,
    StrictSwitch,
    Which,
    Variable,
    Function,
)
from ._core_constructs import (
    Head,
    Tail,
    Hold,
    Type,
    IsSame,
)
from ._datetime_constructs import (
    Strptime,
    Strftime,
    Now,
    Today,
    TimeDeltaDays,
    TimeDeltaMinutes,
    TimeDeltaHours,
    TimeDeltaWeeks,
)
from ._functional_constructs import (
    Fold,
    Map,
    StrictMap,
    Filter,
    Reduce,
)
from ._number_theory_constructs import (
    IsPrime,
    FactorInteger,
    PrimeFactors,
    PrimeNu,
    PrimeOmega,
    Radical,
    IsSquareFree,
    Divisors,
    Sigma0,
    Sigma1,
    SigmaMinus1,
    DivisorSigma,
    Totient,
    IsPerfectPower,
    NthPrime,
    NextPrime,
    PrimePi,
    ExtendedGCD,
    ChineseRemainder,
    CarmichaelLambda,
    JacobiSymbol,
    MultiplicativeOrder,
    PrimitiveRoot,
    LucasL,
    BernoulliB,
    ContinuedFraction,
    FromContinuedFraction,
    IntegerDigits,
    DigitCount,
    DigitSum,
    FromDigits,
    IsSquare,
    IsTriangular,
    IsPentagonal,
    IsOctahedral,
    IsCenteredSquare,
    IsPerfect,
    IsAbundant,
    IsHappy,
)
from ._special_function_constructs import (
    Beta,
    Factorial2,
    ErfInv,
    LambertW,
    AGM,
    EllipticK,
    EllipticE,
)
from ._statistics_constructs import (
    Variance,
    StandardDeviation,
    PopulationVariance,
    PopulationStandardDeviation,
    Mode,
    Quartiles,
    InterquartileRange,
    Covariance,
    Correlation,
    Skewness,
    Kurtosis,
    LinearRegression,
    PolynomialFit,
)
from ._string_constructs import (
    Str,
    String,
    StringJoin,
    Utf8,
    Utf16,
    UnicodeScalars,
    StringFrom,
    Characters,
    StringSplit,
    StringReplace,
    StringCompare,
    IntegerString,
    DigitsFrom,
    NumberFrom,
    StringRepeat,
    PadStart,
    PadEnd,
    RegExp,
    IsMatch,
    StringMatch,
    StringMatchAll,
)
from ._trig_constructs import (
    Sin,
    Arcsin,
    Cos,
    Arccos,
    Tan,
    Arctan,
    Pi,
)


def If(f, c, solver_parameters, s):
    if len(s) < 3:
        raise ValueError("Wrong parameters for 'If'")

    # Detect the CortexJS flat form: ["If", cond, then] or
    # ["If", cond, then, else]. In the Python pair-form below,
    # s[1] is always a [condition, value] pair whose first
    # element (the condition) is itself a MathJSON construct
    # call, e.g. ["Equal", 1, 0]. A CortexJS flat condition is
    # either not a list at all, or is itself such a construct
    # call (its own first element is a *known construct name*).
    # Requiring a known name - rather than any string - keeps a
    # Python-form condition that is a bare parameter reference,
    # e.g. ["If", ["my_flag", "yes"], "no"], from being
    # misdetected as CortexJS form.
    is_cortexjs_form = not isinstance(s[1], list) or (
        bool(s[1]) and isinstance(s[1][0], str) and s[1][0] in constructs
    )

    if is_cortexjs_form:
        if len(s) not in (3, 4):
            raise ValueError("Wrong parameters for 'If'")
        if f(s[1], c):
            return f(s[2], c)
        elif len(s) == 4:
            return f(s[3], c)
        else:
            return None  # CortexJS: Nothing, no else and condition false

    for x in s[1:-1]:
        if len(x) != 2:
            raise ValueError("Wrong if or elif in 'If'")
        try:
            if f(x[0], c):
                try:
                    return f(x[1], c)
                except MathJSONException:
                    # Branch failed, try next condition
                    continue
        except MathJSONException:
            return f(s[-1], c)  # return default value (else)

    return f(s[-1], c)


constructs = {
    "Sum": Sum,
    "Add": Add,
    "Subtract": Subtract,
    "Constants": Constants,
    "Switch": Switch,
    "StrictSwitch": StrictSwitch,
    "If": If,
    "Multiply": lambda f, c, solver_parameters, s: reduce(
        lambda a, b: float(a) * float(b), [f(x, c) for x in s[1:]]
    ),
    "Divide": lambda f, c, solver_parameters, s: f(s[1], c) / f(s[2], c),
    "Negate": lambda f, c, solver_parameters, s: -f(s[1], c),
    "Power": lambda f, c, solver_parameters, s: pow(f(s[1], c), f(s[2], c)),
    "Root": lambda f, c, solver_parameters, s: pow(f(s[1], c), 1.0 / f(s[2], c)),
    "Sqrt": lambda f, c, solver_parameters, s: pow(f(s[1], c), 1.0 / 2),
    "Square": lambda f, c, solver_parameters, s: pow(f(s[1], c), 2),
    "Exp": lambda f, c, solver_parameters, s: math.exp(f(s[1], c)),
    # CortexJS-compatible: ["Log", x] is log base 10; ["Log", x, b] is
    # log base b. Use "Ln" for natural log. (BREAKING as of 2.0.0 -
    # "Log" previously meant natural log.)
    "Log": lambda f, c, solver_parameters, s: (
        math.log10(f(s[1], c)) if len(s) == 2 else math.log(f(s[1], c), f(s[2], c))
    ),
    "Log2": lambda f, c, solver_parameters, s: math.log2(f(s[1], c)),
    "Log10": lambda f, c, solver_parameters, s: math.log10(f(s[1], c)),
    "Ln": lambda f, c, solver_parameters, s: math.log(f(s[1], c)),
    "Lb": lambda f, c, solver_parameters, s: math.log2(
        f(s[1], c)
    ),  # CortexJS name for Log2
    "Lg": lambda f, c, solver_parameters, s: math.log10(
        f(s[1], c)
    ),  # CortexJS name for Log10
    "LogOnePlus": lambda f, c, solver_parameters, s: math.log1p(f(s[1], c)),
    # "Equal": lambda s: f"{f(s[1], c)}" == f"{f(s[2], c)}",
    "Equal": lambda f, c, solver_parameters, s: comparison_safe_converter(f(s[1], c))
    == comparison_safe_converter(f(s[2], c)),
    "IsTrue": lambda f, c, solver_parameters, s: bool(f(s[1], c)),
    "IsFalse": lambda f, c, solver_parameters, s: not bool(f(s[1], c)),
    "StrictEqual": lambda f, c, solver_parameters, s: f(s[1], c) == f(s[2], c),
    "IdenticallyEqual": IdenticallyEqual,
    "Congruent": Congruent,
    # "Greater": lambda s: f(s[1], c) > f(s[2], c),
    "Greater": Greater,
    # "GreaterEqual": lambda s: f(s[1], c) >= f(s[2], c),
    "GreaterEqual": GreaterEqual,
    # "Less": lambda s: f(s[1], c) < f(s[2], c),
    "Less": Less,
    # "LessEqual": lambda s: f(s[1], c) <= f(s[2], c),
    "LessEqual": LessEqual,
    # "NotEqual": lambda s: f(s[1], c) != f(s[2], c),
    "NotEqual": lambda f, c, solver_parameters, s: comparison_safe_converter(f(s[1], c))
    != comparison_safe_converter(f(s[2], c)),
    "And": BooleanAnd,
    "Or": BooleanOr,
    "Abs": lambda f, c, solver_parameters, s: abs(f(s[1], c)),
    "Round": lambda f, c, solver_parameters, s: (
        round(f(s[1], c), f(s[2], c)) if len(s) == 3 else int(round(f(s[1], c)))
    ),
    "Max": Max,
    "Min": Min,
    "Average": Average,
    "Mean": Average,  # CortexJS name for Average
    "Median": Median,
    "Length": Length,
    "Count": Length,  # CortexJS name for Length
    "Any": Any,
    "All": All,
    "Array": Arr,
    "List": lambda f, c, solver_parameters, s: ["Array"]
    + [f(x, c) for x in s[1:]],  # CortexJS name for Array
    "In": In,
    "Not_in": Not_in,
    "Element": In,  # CortexJS name for In (["Element", value, set])
    "NotElement": Not_in,  # CortexJS name for Not_in
    "Contains_any_of": Contains_any_of,
    "Contains_all_of": Contains_all_of,
    "Contains_none_of": Contains_none_of,
    "NotIn": Not_in,
    "ContainsAnyOf": Contains_any_of,
    "ContainsAllOf": Contains_all_of,
    "ContainsNoneOf": Contains_none_of,
    "Int": Int,
    "Float": Float,
    "Floor": Floor,
    "Ceil": Ceil,
    "Str": Str,
    # --- Strings ---
    "String": String,
    "StringJoin": StringJoin,
    "ToUpperCase": lambda f, c, solver_parameters, s: f(s[1], c).upper(),
    "ToLowerCase": lambda f, c, solver_parameters, s: f(s[1], c).lower(),
    "CaseFold": lambda f, c, solver_parameters, s: f(s[1], c).casefold(),
    "Trim": lambda f, c, solver_parameters, s: f(s[1], c).strip(),
    "TrimStart": lambda f, c, solver_parameters, s: f(s[1], c).lstrip(),
    "TrimEnd": lambda f, c, solver_parameters, s: f(s[1], c).rstrip(),
    "StringSplit": StringSplit,
    "StringReplace": StringReplace,
    "StringCompare": StringCompare,
    "StringRepeat": StringRepeat,
    "PadStart": PadStart,
    "PadEnd": PadEnd,
    "Characters": Characters,
    "GraphemeClusters": Characters,  # CortexJS synonym for Characters
    "Utf8": Utf8,
    "Utf16": Utf16,
    "UnicodeScalars": UnicodeScalars,
    "StringFrom": StringFrom,
    "IntegerString": IntegerString,
    "DigitsFrom": DigitsFrom,
    "NumberFrom": NumberFrom,
    "RegExp": RegExp,
    "IsMatch": IsMatch,
    "StringMatch": StringMatch,
    "StringMatchAll": StringMatchAll,
    "Not": Not,
    # "IsDefined": lambda s: s[1] in c,
    "IsDefined": IsDefined,
    "IsUndefined": IsUndefined,
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
    "CumulativeSum": CumulativeSum,
    "Interp": Interp,
    "FindIntervalIndex": FindIntervalIndex,
    "TrapezoidalIntegrate": TrapezoidalIntegrate,
    "Reduce": Reduce,
    "Product": Product,
    "Appended": Appended,
    "Sin": Sin,
    "Cos": Cos,
    "Tan": Tan,
    "Arcsin": Arcsin,
    "Arccos": Arccos,
    "Arctan": Arctan,
    "Arctan2": lambda f, c, solver_parameters, s: math.atan2(f(s[1], c), f(s[2], c)),
    "Pi": Pi,
    "Which": Which,  # CortexJS multi-branch conditional (not Switch - see Which's docstring)
    # --- Trigonometric: reciprocal, hyperbolic, area-hyperbolic ---
    "Cot": lambda f, c, solver_parameters, s: 1 / math.tan(f(s[1], c)),
    "Sec": lambda f, c, solver_parameters, s: 1 / math.cos(f(s[1], c)),
    "Csc": lambda f, c, solver_parameters, s: 1 / math.sin(f(s[1], c)),
    "Arccot": lambda f, c, solver_parameters, s: math.atan(1 / f(s[1], c)),
    "Arcsec": lambda f, c, solver_parameters, s: math.acos(1 / f(s[1], c)),
    "Arccsc": lambda f, c, solver_parameters, s: math.asin(1 / f(s[1], c)),
    "Sinh": lambda f, c, solver_parameters, s: math.sinh(f(s[1], c)),
    "Cosh": lambda f, c, solver_parameters, s: math.cosh(f(s[1], c)),
    "Tanh": lambda f, c, solver_parameters, s: math.tanh(f(s[1], c)),
    "Coth": lambda f, c, solver_parameters, s: 1 / math.tanh(f(s[1], c)),
    "Sech": lambda f, c, solver_parameters, s: 1 / math.cosh(f(s[1], c)),
    "Csch": lambda f, c, solver_parameters, s: 1 / math.sinh(f(s[1], c)),
    "Arsinh": lambda f, c, solver_parameters, s: math.asinh(f(s[1], c)),
    "Arcosh": lambda f, c, solver_parameters, s: math.acosh(f(s[1], c)),
    "Artanh": lambda f, c, solver_parameters, s: math.atanh(f(s[1], c)),
    "Arcoth": lambda f, c, solver_parameters, s: math.atanh(1 / f(s[1], c)),
    "Arsech": lambda f, c, solver_parameters, s: math.acosh(1 / f(s[1], c)),
    "Arcsch": lambda f, c, solver_parameters, s: math.asinh(1 / f(s[1], c)),
    "Hypot": lambda f, c, solver_parameters, s: math.hypot(f(s[1], c), f(s[2], c)),
    "Sinc": lambda f, c, solver_parameters, s: (
        1.0 if f(s[1], c) == 0 else math.sin(f(s[1], c)) / f(s[1], c)
    ),
    # --- Constants ---
    "Degrees": lambda f, c, solver_parameters, s: math.pi / 180,
    "ExponentialE": lambda f, c, solver_parameters, s: math.e,
    "GoldenRatio": lambda f, c, solver_parameters, s: (1 + math.sqrt(5)) / 2,
    "MachineEpsilon": lambda f, c, solver_parameters, s: sys.float_info.epsilon,
    "CatalanConstant": lambda f, c, solver_parameters, s: 0.915965594177219015054603514932384110774,
    "EulerGamma": lambda f, c, solver_parameters, s: 0.5772156649015328606065120900824024310421,
    "Rational": Rational,
    "Numerator": Numerator,
    "Denominator": Denominator,
    # --- Number theory / special functions ---
    "Chop": lambda f, c, solver_parameters, s: (
        0 if abs(f(s[1], c)) < 1e-10 else f(s[1], c)
    ),
    "Mod": lambda f, c, solver_parameters, s: f(s[1], c) % f(s[2], c),
    "Clamp": Clamp,
    "GCD": lambda f, c, solver_parameters, s: math.gcd(
        int(f(s[1], c)), int(f(s[2], c))
    ),
    "LCM": lambda f, c, solver_parameters, s: math.lcm(
        int(f(s[1], c)), int(f(s[2], c))
    ),
    "Factorial": lambda f, c, solver_parameters, s: math.factorial(int(f(s[1], c))),
    "Binomial": lambda f, c, solver_parameters, s: math.comb(
        int(f(s[1], c)), int(f(s[2], c))
    ),
    "IsPrime": IsPrime,
    "Erf": lambda f, c, solver_parameters, s: math.erf(f(s[1], c)),
    "Erfc": lambda f, c, solver_parameters, s: math.erfc(f(s[1], c)),
    # --- Number theory ---
    "PowerMod": lambda f, c, solver_parameters, s: pow(
        int(f(s[1], c)), int(f(s[2], c)), int(f(s[3], c))
    ),
    "ModularInverse": lambda f, c, solver_parameters, s: pow(
        int(f(s[1], c)), -1, int(f(s[2], c))
    ),
    "IntegerSqrt": lambda f, c, solver_parameters, s: math.isqrt(int(f(s[1], c))),
    "FactorInteger": FactorInteger,
    "PrimeFactors": PrimeFactors,
    "PrimeNu": PrimeNu,
    "PrimeOmega": PrimeOmega,
    "Radical": Radical,
    "IsSquareFree": IsSquareFree,
    "Divisors": Divisors,
    "Sigma0": Sigma0,
    "Sigma1": Sigma1,
    "SigmaMinus1": SigmaMinus1,
    "DivisorSigma": DivisorSigma,
    "Divides": lambda f, c, solver_parameters, s: f(s[2], c) % f(s[1], c) == 0,
    "Totient": Totient,
    "IsPerfectPower": IsPerfectPower,
    "NthPrime": NthPrime,
    "NextPrime": NextPrime,
    "PrimePi": PrimePi,
    "ExtendedGCD": ExtendedGCD,
    "ChineseRemainder": ChineseRemainder,
    "CarmichaelLambda": CarmichaelLambda,
    "JacobiSymbol": JacobiSymbol,
    "LegendreSymbol": JacobiSymbol,  # same algorithm when n is prime
    "MultiplicativeOrder": MultiplicativeOrder,
    "PrimitiveRoot": PrimitiveRoot,
    "LucasL": LucasL,
    "CatalanNumber": lambda f, c, solver_parameters, s: math.comb(
        2 * int(f(s[1], c)), int(f(s[1], c))
    )
    // (int(f(s[1], c)) + 1),
    "BernoulliB": BernoulliB,
    "ContinuedFraction": ContinuedFraction,
    "FromContinuedFraction": FromContinuedFraction,
    "IntegerDigits": IntegerDigits,
    "DigitCount": DigitCount,
    "DigitSum": DigitSum,
    "FromDigits": FromDigits,
    "IsSquare": IsSquare,
    "IsTriangular": IsTriangular,
    "IsPentagonal": IsPentagonal,
    "IsOctahedral": IsOctahedral,
    "IsCenteredSquare": IsCenteredSquare,
    "IsPerfect": IsPerfect,
    "IsAbundant": IsAbundant,
    "IsHappy": IsHappy,
    # --- Special functions ---
    "Gamma": lambda f, c, solver_parameters, s: math.gamma(f(s[1], c)),
    "GammaLn": lambda f, c, solver_parameters, s: math.lgamma(f(s[1], c)),
    "Beta": Beta,
    "Factorial2": Factorial2,
    "ErfInv": ErfInv,
    "LambertW": LambertW,
    "AGM": AGM,
    "EllipticK": EllipticK,
    "EllipticE": EllipticE,
    # --- Combinatorics (trivial subset) ---
    "Choose": lambda f, c, solver_parameters, s: math.comb(
        int(f(s[1], c)), int(f(s[2], c))
    ),
    "Fibonacci": Fibonacci,
    "Multinomial": Multinomial,
    "Subfactorial": Subfactorial,
    "BellNumber": BellNumber,
    "PowerSet": PowerSet,
    "Permutations": Permutations,
    "Combinations": Combinations,
    "CartesianProduct": CartesianProduct,
    # --- Core: structural introspection ---
    "Head": Head,
    "Tail": Tail,
    "Hold": Hold,
    "Identity": lambda f, c, solver_parameters, s: f(s[1], c),
    "Type": Type,
    "IsSame": IsSame,
    "Same": IsSame,  # see IsSame's docstring for the distinction CortexJS draws
    # --- Boolean logic ---
    "Xor": lambda f, c, solver_parameters, s: bool(f(s[1], c)) ^ bool(f(s[2], c)),
    "Nand": lambda f, c, solver_parameters, s: not all(f(x, c) for x in s[1:]),
    "Nor": lambda f, c, solver_parameters, s: not any(f(x, c) for x in s[1:]),
    "Implies": lambda f, c, solver_parameters, s: (not f(s[1], c)) or bool(f(s[2], c)),
    "Equivalent": lambda f, c, solver_parameters, s: bool(f(s[1], c))
    == bool(f(s[2], c)),
    # --- Statistics ---
    "Variance": Variance,
    "StandardDeviation": StandardDeviation,
    "PopulationVariance": PopulationVariance,
    "PopulationStandardDeviation": PopulationStandardDeviation,
    "Mode": Mode,
    "Quartiles": Quartiles,
    "InterquartileRange": InterquartileRange,
    "Covariance": Covariance,
    "Correlation": Correlation,
    "Skewness": Skewness,
    "Kurtosis": Kurtosis,
    "LinearRegression": LinearRegression,
    "PolynomialFit": PolynomialFit,
    # --- Collections ---
    "First": First,
    "Second": Second,
    "Third": Third,
    "Last": Last,
    "Rest": Rest,
    "Most": Most,
    "Reverse": Reverse,
    "Sort": Sort,
    "IsEmpty": IsEmpty,
    "Range": Range,
    "Join": Join,
    "Unique": Unique,
    "Zip": Zip,
    "At": At,
    "Take": Take,
    "Drop": Drop,
    "TakeWhile": TakeWhile,
    "DropWhile": DropWhile,
    "Contains": Contains,
    "IndexOf": IndexOf,
    "IndexWhere": IndexWhere,
    "Find": Find,
    "CountIf": CountIf,
    "Position": Position,
    "RotateLeft": RotateLeft,
    "RotateRight": RotateRight,
    "MaxBy": MaxBy,
    "MinBy": MinBy,
    "ArgMax": ArgMax,
    "ArgMin": ArgMin,
    "Ordering": Ordering,
    "FlatMap": FlatMap,
    "Scan": Scan,
    "Differences": Differences,
    "Fold": Fold,
    "Dedup": Dedup,
    "Append": Appended,  # CortexJS name for Appended
    "Insert": Insert,
    "DeleteAt": DeleteAt,
    "ReplaceAt": ReplaceAt,
    "Partition": Partition,
    "Chunk": Chunk,
    "GroupBy": GroupBy,
    "ChunkBy": ChunkBy,
    "Tally": Tally,
    # --- Set algebra (over Array - no dedicated Set type) ---
    "Union": Union,
    "Intersection": Intersection,
    "SetMinus": SetMinus,
    "SymmetricDifference": SymmetricDifference,
}


def create_mathjson_solver(
    solver_parameters: dict[str, MathJSONExpression],
    legacy_v1: bool = False,
    blacklist: Iterable[str] | None = None,
) -> Callable[[MathJSONExpression], _Any]:
    """
    `blacklist`, if given, is an iterable of construct names (e.g.
    `["PowerSet", "Permutations"]`) that this solver instance refuses to
    evaluate - deployments can disable individual constructs they don't
    want available for their expression sources, independent of what
    the library implements. Attempting to use a blacklisted construct
    raises `MathJSONException` (wrapping `PermissionError`) rather than
    evaluating it or silently ignoring it. A name that isn't an actual
    construct has no effect (not validated against the known-construct
    list - a deliberate simplicity trade-off, not an oversight).

    This is a resource/access *policy* control, not a substitute for a
    construct being safe to run at all - e.g. the combinatorial
    enumeration functions (`PowerSet`, `Permutations`, `Combinations`,
    `CartesianProduct`) have no built-in output-size limit, so a
    deployment accepting untrusted expressions should blacklist them
    (or any other construct it doesn't want exposed) rather than assume
    every construct is safe by default for every threat model.
    """
    blacklist = frozenset(blacklist) if blacklist else frozenset()

    def f(s, *args):
        if args:
            c = deepcopy(args[0])
        else:
            c = {}
        #         c = deepcopy(kwargs.get("c", {}))
        if isinstance(s, numbers.Number):
            return s
        # CortexJS represents the boolean literals as the bare symbols
        # "True" and "False" (as opposed to native JSON `true`/`false`,
        # which already arrive here as Python bool - itself a `numbers.Number`
        # subtype, so it's handled by the check above). Resolve them to
        # actual booleans unconditionally, the same way numeric literals
        # are resolved above, so they can't be shadowed by a same-named
        # solver parameter or local variable.
        if s == "True" or s == "False":
            return s == "True"
        if isinstance(s, list):
            if not s:
                # Empty equation given - []
                return None
            if s[0] in constructs:
                if s[0] in blacklist:
                    raise MathJSONException(
                        PermissionError(
                            f"'{s[0]}' has been disabled in this solver instance."
                        ),
                        s,
                        mathjson_construct=s[0],
                    )
                try:
                    return constructs[s[0]](f, c, solver_parameters, s)

                # except RecursionError:
                #     return s[0]
                # except Exception as e:
                except TypeError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0]) from e
                except ValueError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0]) from e
                except IndexError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0]) from e
                except ZeroDivisionError as e:
                    raise MathJSONException(e, s, mathjson_construct=s[0]) from e
            else:
                # raise MathJSONException(
                #     NotImplementedError(f"'{s[0]}' is not supported"), s
                # )
                return s
        elif s in c:
            # Local scope (Constants, Reduce accumulator/current/index,
            # Function parameters, ...) shadows top-level solver parameters
            # of the same name, matching normal lexical scoping.
            return f(c[s], c)
        elif s in solver_parameters:
            try:
                return f(solver_parameters[s], c)
            except RecursionError:
                return solver_parameters[s]
        else:
            # raise KeyError(f"Parameter '{s}' is not defined")
            return s

    if legacy_v1:

        def legacy_v1_f(s, *args):
            return f(translate_v1_mathjson(s), *args)

        return legacy_v1_f

    return f


def extract_variables(
    s: MathJSONExpression, li: set[str], ignore_list: set[str]
) -> set[str]:
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
        "IsTrue",
        "IsFalse",
        "Greater",
        "GreaterEqual",
        "Less",
        "LessEqual",
        "NotEqual",
        "And",
        "Or",
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
        "Element",
        "NotElement",
        "Int",
        "Float",
        "Floor",
        "Ceil",
        "Str",
        "String",
        "StringJoin",
        "ToUpperCase",
        "ToLowerCase",
        "CaseFold",
        "Trim",
        "TrimStart",
        "TrimEnd",
        "StringSplit",
        "StringReplace",
        "StringCompare",
        "StringRepeat",
        "PadStart",
        "PadEnd",
        "Characters",
        "GraphemeClusters",
        "Utf8",
        "Utf16",
        "UnicodeScalars",
        "StringFrom",
        "IntegerString",
        "DigitsFrom",
        "NumberFrom",
        "RegExp",
        "IsMatch",
        "StringMatch",
        "StringMatchAll",
        "Not",
        "IsDefined",
        "IsUndefined",
        "StrictEqual",
        "IdenticallyEqual",
        "Congruent",
        "NotEqual",
        "StrictSwitch",
        "Map",
        "StrictMap",
        "Filter",
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
        "CumulativeSum",
        "Interp",
        "FindIntervalIndex",
        "TrapezoidalIntegrate",
        "TrapezoidalIntegrate",
        "Reduce",
        "Product",
        "Appended",
        "Sin",
        "Cos",
        "Tan",
        "Arcsin",
        "Arccos",
        "Arctan",
        "Arctan2",
        "Pi",
        "Which",
        "Lb",
        "Lg",
        "LogOnePlus",
        "Mean",
        "Count",
        "List",
        "Cot",
        "Sec",
        "Csc",
        "Arccot",
        "Arcsec",
        "Arccsc",
        "Sinh",
        "Cosh",
        "Tanh",
        "Coth",
        "Sech",
        "Csch",
        "Arsinh",
        "Arcosh",
        "Artanh",
        "Arcoth",
        "Arsech",
        "Arcsch",
        "Hypot",
        "Sinc",
        "Degrees",
        "ExponentialE",
        "GoldenRatio",
        "MachineEpsilon",
        "CatalanConstant",
        "EulerGamma",
        "Rational",
        "Numerator",
        "Denominator",
        "Chop",
        "Mod",
        "Clamp",
        "GCD",
        "LCM",
        "Factorial",
        "Binomial",
        "IsPrime",
        "Erf",
        "Erfc",
        "PowerMod",
        "ModularInverse",
        "IntegerSqrt",
        "FactorInteger",
        "PrimeFactors",
        "PrimeNu",
        "PrimeOmega",
        "Radical",
        "IsSquareFree",
        "Divisors",
        "Sigma0",
        "Sigma1",
        "SigmaMinus1",
        "DivisorSigma",
        "Divides",
        "Totient",
        "IsPerfectPower",
        "NthPrime",
        "NextPrime",
        "PrimePi",
        "ExtendedGCD",
        "ChineseRemainder",
        "CarmichaelLambda",
        "JacobiSymbol",
        "LegendreSymbol",
        "MultiplicativeOrder",
        "PrimitiveRoot",
        "LucasL",
        "CatalanNumber",
        "BernoulliB",
        "ContinuedFraction",
        "FromContinuedFraction",
        "IntegerDigits",
        "DigitCount",
        "DigitSum",
        "FromDigits",
        "IsSquare",
        "IsTriangular",
        "IsPentagonal",
        "IsOctahedral",
        "IsCenteredSquare",
        "IsPerfect",
        "IsAbundant",
        "IsHappy",
        "Gamma",
        "GammaLn",
        "Beta",
        "Factorial2",
        "ErfInv",
        "LambertW",
        "AGM",
        "EllipticK",
        "EllipticE",
        "Choose",
        "Fibonacci",
        "Multinomial",
        "Subfactorial",
        "BellNumber",
        "PowerSet",
        "Permutations",
        "Combinations",
        "CartesianProduct",
        "Head",
        "Tail",
        "Hold",
        "Identity",
        "Type",
        "IsSame",
        "Same",
        "Xor",
        "Nand",
        "Nor",
        "Implies",
        "Equivalent",
        "Variance",
        "StandardDeviation",
        "PopulationVariance",
        "PopulationStandardDeviation",
        "Mode",
        "Quartiles",
        "InterquartileRange",
        "Covariance",
        "Correlation",
        "Skewness",
        "Kurtosis",
        "LinearRegression",
        "PolynomialFit",
        "First",
        "Second",
        "Third",
        "Last",
        "Rest",
        "Most",
        "Reverse",
        "Sort",
        "IsEmpty",
        "Range",
        "Join",
        "Unique",
        "Zip",
        "At",
        "Take",
        "Drop",
        "TakeWhile",
        "DropWhile",
        "Contains",
        "IndexOf",
        "IndexWhere",
        "Find",
        "CountIf",
        "Position",
        "RotateLeft",
        "RotateRight",
        "MaxBy",
        "MinBy",
        "ArgMax",
        "ArgMin",
        "Ordering",
        "FlatMap",
        "Scan",
        "Differences",
        "Fold",
        "Dedup",
        "Append",
        "Insert",
        "DeleteAt",
        "ReplaceAt",
        "Partition",
        "Chunk",
        "GroupBy",
        "ChunkBy",
        "Tally",
        "Union",
        "Intersection",
        "SetMinus",
        "SymmetricDifference",
    ]
    if isinstance(s, str):
        if s in ignore_list:
            return li
        # "True"/"False" are boolean literals (see `f`'s handling of them),
        # not solver-parameter references, so they're never free variables.
        if s not in constructs and s not in ("True", "False"):
            li.add(s)
        return li
    elif isinstance(s, list):
        if s[0] == "Constants":
            for x in s[1:-1]:
                ignore_list.add(x[0])
                li.update(extract_variables(x[1], li, ignore_list))
            li.update(extract_variables(s[-1], li, ignore_list))
        elif s[0] == "If":
            # Mirror the calling-convention detection used by the solver's
            # own `If` (see its docstring / comments): CortexJS flat form
            # ["If", cond, then[, else]] vs. the Python pair form
            # ["If", [cond, val], ..., else_val].
            is_cortexjs_form = len(s) > 1 and (
                not isinstance(s[1], list)
                or (bool(s[1]) and isinstance(s[1][0], str) and s[1][0] in constructs)
            )
            if is_cortexjs_form:
                for x in s[1:]:
                    li.update(extract_variables(x, li, ignore_list))
            else:
                for elif_block in s[1:-1]:  # s[1] is list
                    for x in elif_block:
                        li.update(extract_variables(x, li, ignore_list))
                li.update(extract_variables(s[-1], li, ignore_list))
        elif s[0] == "Function":
            # ["Function", body, param1, param2, ...]: parameter names (and
            # the anonymous placeholders "_", "_1", "_2", ...) are bound
            # locally, not free variables.
            for p in s[2:]:
                if isinstance(p, str):
                    ignore_list.add(p)
            ignore_list.update({f"_{i}" for i in range(1, 10)})
            ignore_list.add("_")
            if len(s) > 1:
                li.update(extract_variables(s[1], li, ignore_list))
        elif s[0] in ("Head", "Tail", "Hold", "IsSame", "Same"):
            # These deliberately never evaluate their arguments either
            # (Head/Tail/Hold work on the raw, unevaluated expression
            # tree; IsSame/Same do a pure structural comparison of the
            # two raw trees) - same reasoning as the unrecognized-
            # construct case below, just for constructs that *are*
            # recognized. A bare name inside their arguments is never
            # resolved as a parameter reference, so it's not a free
            # variable to supply.
            pass
        elif s[0] not in constructs:
            # Unrecognized construct (e.g. "Color", "Quantity" - anything
            # this solver doesn't implement): f() never evaluates or
            # substitutes into such expressions either (its fallback for
            # an unknown head is to return the whole list unchanged), so
            # none of its arguments are free variables to supply. Treat
            # the whole thing as opaque data rather than recursing into
            # it, so a decorative/unrelated subtree (e.g. a color literal
            # meant for something else downstream) doesn't get reported
            # as a required parameter.
            pass
        else:
            for x in s[1:]:
                li.update(extract_variables(x, li, ignore_list))
        return li
    else:
        return li
