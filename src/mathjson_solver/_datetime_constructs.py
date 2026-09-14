"""
Date/time constructs.
"""

import datetime
from ._common import (
    _try_parse_datetime,
)


def Strptime(f, c, solver_parameters, s):
    datetime_str = f(s[1], c)
    parameters = f(s[2], c)
    return datetime.datetime.strptime(datetime_str, parameters).isoformat()


def Strftime(f, c, solver_parameters, s):
    dt = _try_parse_datetime(f(s[1], c))
    if not isinstance(dt, (datetime.datetime, datetime.date)):
        raise ValueError(f"Strftime: could not parse input as datetime: {dt!r}")
    parameters = f(s[2], c)
    return dt.strftime(parameters)


def Now(f, c, solver_parameters, s):
    return datetime.datetime.now().isoformat()


def Today(f, c, solver_parameters, s):
    return datetime.date.today().isoformat()


def TimeDeltaDays(f, c, solver_parameters, s):
    return datetime.timedelta(days=f(s[1], c))


def TimeDeltaMinutes(f, c, solver_parameters, s):
    return datetime.timedelta(minutes=f(s[1], c))


def TimeDeltaHours(f, c, solver_parameters, s):
    return datetime.timedelta(hours=f(s[1], c))


def TimeDeltaWeeks(f, c, solver_parameters, s):
    return datetime.timedelta(weeks=f(s[1], c))
