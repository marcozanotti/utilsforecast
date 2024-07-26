# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/compat.ipynb.

# %% auto 0
__all__ = ['DataFrame', 'Series']

# %% ../nbs/compat.ipynb 1
import warnings
from functools import wraps
from typing import Union

import pandas as pd

# %% ../nbs/compat.ipynb 2
try:
    import polars as pl
    from polars import DataFrame as pl_DataFrame
    from polars import Expr as pl_Expr
    from polars import Series as pl_Series

    POLARS_INSTALLED = True
except ImportError:
    pl = None

    class pl_DataFrame: ...

    class pl_Expr: ...

    class pl_Series: ...

    POLARS_INSTALLED = False

try:
    import plotly  # noqa: F401

    PLOTLY_INSTALLED = True
except ImportError:
    PLOTLY_INSTALLED = False

try:
    import plotly_resampler  # noqa: F401

    PLOTLY_RESAMPLER_INSTALLED = True
except ImportError:
    PLOTLY_RESAMPLER_INSTALLED = False

try:
    from numba import njit  # noqa: F04
except ImportError:

    def _doublewrap(f):
        @wraps(f)
        def new_dec(*args, **kwargs):
            if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
                return f(args[0])
            else:
                return lambda realf: f(realf, *args, **kwargs)

        return new_dec

    @_doublewrap
    def njit(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            warnings.warn(
                "numba is not installed, some operations may be very slow. "
                "You can find install instructions at "
                "https://numba.pydata.org/numba-doc/latest/user/installing.html"
            )
            return f(*args, **kwargs)

        return wrapper


DataFrame = Union[pd.DataFrame, pl_DataFrame]
Series = Union[pd.Series, pl_Series]
