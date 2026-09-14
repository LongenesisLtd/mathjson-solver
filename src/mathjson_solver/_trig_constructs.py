"""
Trigonometric constructs and the Pi constant.
"""

import math


# sin, cos, tan, arcsin, arccos, arctan
def Sin(f, c, solver_parameters, s):
    return math.sin(f(s[1], c))


def Arcsin(f, c, solver_parameters, s):
    return math.asin(f(s[1], c))


def Cos(f, c, solver_parameters, s):
    return math.cos(f(s[1], c))


def Arccos(f, c, solver_parameters, s):
    return math.acos(f(s[1], c))


def Tan(f, c, solver_parameters, s):
    return math.tan(f(s[1], c))


def Arctan(f, c, solver_parameters, s):
    return math.atan(f(s[1], c))


def Pi(f, c, solver_parameters, s):
    return math.pi
