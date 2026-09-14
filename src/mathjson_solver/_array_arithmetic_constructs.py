"""
Array-as-numeric-vector arithmetic and calculus constructs (element-wise
scalar/array ops, interpolation, numerical integration).
"""

from ._array_helpers import (
    _AddArray,
    _AddScalar,
    _CumulativeProduct,
    _CumulativeSum,
    _MultiplyByArray,
    _MultiplyByScalar,
    _SubtractArray,
    _SubtractScalar,
)
from ._interpolation import (
    find_interpolation_bounds_2indexes,
    linear_interpolate,
)

NUMPY_AVAILABLE = False
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    pass


def MultiplyByScalar(f, c, solver_parameters, s):
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


def MultiplyByArray(f, c, solver_parameters, s):
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


def AddScalar(f, c, solver_parameters, s):
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


def SubtractScalar(f, c, solver_parameters, s):
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


def AddArray(f, c, solver_parameters, s):
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


def SubtractArray(f, c, solver_parameters, s):
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


def GenerateRange(f, c, solver_parameters, s):
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


def AtIndex(f, c, solver_parameters, s):
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


def Slice(f, c, solver_parameters, s):
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


def CumulativeProduct(f, c, solver_parameters, s):
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


def CumulativeSum(f, c, solver_parameters, s):
    """
    ["CumulativeSum", array]
    The `array` must be an array of numeric values.
    """
    array = f(s[1], c)
    if not (isinstance(array, list) and array[0] == "Array"):
        raise ValueError("Parameter 1 must be an array.")
    array = [f(x, c) for x in array[1:]]
    return ["Array"] + _CumulativeSum(array)
    # return


def Interp(f, c, solver_parameters, s):
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


def FindIntervalIndex(f, c, solver_parameters, s):
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


def TrapezoidalIntegrate(f, c, solver_parameters, s):
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
    return h * (0.5 * values[0] + np.sum(values[1:-1]) + 0.5 * values[-1])

    # return total_area
