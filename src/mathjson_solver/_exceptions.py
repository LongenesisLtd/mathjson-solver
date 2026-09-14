"""
The public exception type and expression type alias, kept in their own
leaf module so both __main__.py and the construct topic modules that
need `MathJSONException` (e.g. _functional_constructs.py's `Map`) can
import it without a circular dependency back to __main__.
"""

from typing import Union, Any, TypeAlias

# A MathJSON expression, in this solver's list-based (not dictionary-
# based) representation: a literal (string, number, bool, or None), or
# a compound expression - a list whose first element is a construct
# name and whose remaining elements are themselves MathJSONExpression
# values (e.g. ["Add", 1, ["Multiply", 2, "x"]]). Used only for the
# small public API surface (`create_solver`, `extract_variables`,
# `translate_v1_mathjson`) - the ~300 per-construct functions all
# take/return arbitrary runtime values (a construct can produce a
# `Fraction`, a `datetime.timedelta`, a compiled regex pattern, ...)
# and stay untyped rather than annotate each one with `Any` for no
# real type-safety benefit.
MathJSONExpression: TypeAlias = Union[
    str, int, float, bool, None, list["MathJSONExpression"]
]


class MathJSONException(Exception):
    """Exception for MathJSON processing issues"""

    def __init__(
        self,
        e: Exception,
        expr: MathJSONExpression,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(args)
        self.e = e
        self.expr = expr
        self.construct = kwargs.get("mathjson_construct", "MathJSON")

    def __str__(self) -> str:
        if hasattr(self.e, "message"):
            m = self.e.message
        else:
            m = str(self.e)
        return f"Problem in {self.construct}. {self.expr}. {m}"
