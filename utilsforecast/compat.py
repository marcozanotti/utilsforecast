# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/compat.ipynb.

# %% auto 0
__all__ = ['DataFrame', 'Series', 'DistributedDFType', 'AnyDFType']

# %% ../nbs/compat.ipynb 1
import warnings
from functools import wraps
from typing import TypeVar, Union

import pandas as pd

# %% ../nbs/compat.ipynb 2
try:
    import polars
    import polars as pl
    from polars import DataFrame as pl_DataFrame
    from polars import Expr as pl_Expr
    from polars import Series as pl_Series

    DFType = TypeVar("DFType", pd.DataFrame, polars.DataFrame)
    POLARS_INSTALLED = True
except ImportError:
    pl = None

    class pl_DataFrame: ...

    class pl_Expr: ...

    class pl_Series: ...

    DFType = pd.DataFrame
    POLARS_INSTALLED = False

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
    def njit(f, *_args, **_kwargs):
        @wraps(f)
        def wrapper(*args, **kwargs):
            warnings.warn(
                "numba is not installed, some operations may be very slow. "
                "You can find install instructions at "
                "https://numba.pydata.org/numba-doc/latest/user/installing.html"
            )
            return f(*args, **kwargs)

        return wrapper


try:
    from dask.dataframe import DataFrame as DaskDataFrame
except ModuleNotFoundError:
    pass

try:
    from pyspark.sql import DataFrame as SparkDataFrame
except ModuleNotFoundError:
    pass

DataFrame = Union[pd.DataFrame, pl_DataFrame]
Series = Union[pd.Series, pl_Series]
DistributedDFType = TypeVar(
    "DistributedDFType",
    "DaskDataFrame",
    "SparkDataFrame",
)
AnyDFType = TypeVar(
    "AnyDFType",
    "DaskDataFrame",
    pd.DataFrame,
    "pl_DataFrame",
    "SparkDataFrame",
)
