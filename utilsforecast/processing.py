# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/processing.ipynb.

# %% auto 0
__all__ = ['DataFrameProcessing']

# %% ../nbs/processing.ipynb 3
from typing import Union

import numpy as np
import pandas as pd

from .compat import DataFrame, pl_DataFrame
from .grouped_array import GroupedArray

# %% ../nbs/processing.ipynb 4
class DataFrameProcessing:
    """
    A utility to process Pandas or Polars dataframes for time series forecasting.

    This class ensures the dataframe is properly structured, with required columns
    ('unique_id', 'ds', 'y'), and the 'ds' column is of datetime type. It also
    provides options for sorting the dataframe based on a unique identifier and a
    timestamp, and separates the data into different arrays for easy access during
    forecasting operations.

    Attributes:
    ----------
    dataframe : pd.DataFrame or pl.DataFrame
        A pandas or polars dataframe to be processed.
    sort_dataframe : bool
        A boolean indicating whether the dataframe should be sorted.
    validate : bool, (default=True)
        Ensure the dataframe matches the required format.

    Methods:
    -------
    __call__():
        Processes the dataframe by ensuring the columns are in the correct format,
        sorts the dataframe if required, and separates the data into different
        arrays for future operations.
    _to_np_and_engine():
        Converts the dataframe to a numpy structured array and identifies the
        dataframe engine (pandas or polars).
    _validate_dataframe(dataframe: Union[pd.DataFrame, pl.DataFrame]):
        Checks if the required columns ('unique_id', 'ds', 'y') are present in the
        dataframe.
    _check_datetime(arr: np.array) -> np.array:
        Validates that the 'ds' column is of datetime type, and if not, attempts to
        convert it to datetime.
    """

    def __init__(
        self,
        dataframe: DataFrame,
        sort_dataframe: bool,
        validate: bool = True,
    ):
        self.dataframe = dataframe
        self.sort_dataframe = sort_dataframe
        self.validate = validate

        # Columns declaration
        self.non_value_columns = ["unique_id", "ds"]
        self.datetime_column_name = "ds"
        self.dt_dtype = np.dtype("datetime64")
        self.__call__()

    def __call__(self):
        """Sequential execution of the code"""
        # Declaring values that will be utilized
        self.np_df = self._to_np_and_engine()
        self.dataframe_columns = self.np_df.dtype.names

        # Processing value columns
        value_columns = [
            column
            for column in self.dataframe_columns
            if column not in self.non_value_columns
        ]
        self.value_array = self.np_df[value_columns]
        if self.value_array.ndim == 1 and len(value_columns) > 1:
            self.value_array = np.stack(
                [
                    self.value_array[name].astype(float)
                    for name in self.value_array.dtype.names
                ],
                axis=1,
            )
        if self.value_array.ndim == 1 and len(value_columns) == 1:
            self.value_array = (
                self.value_array[value_columns].astype(float).reshape(-1, 1)
            )

        # Processing unique_id
        self.unique_id = self.np_df["unique_id"]
        if self.unique_id.dtype.kind == "O":
            self.unique_id.astype(str)

        # If values are already int or float then they won't be converted
        if self.unique_id.dtype.kind not in ["i", "f"]:
            # If all values in the numpy array are numerical then proceed with conversion
            if np.char.isnumeric(self.unique_id.astype(str)).all():
                # If number are whole then they will be converted to `int`, else `float`
                # This is pure aesthetics addition.
                self.unique_id = self.unique_id.astype(float)
                if np.isclose(self.unique_id, np.round(self.unique_id)).all():
                    self.unique_id = self.unique_id.astype(int)
        # NOTE: When sorting with Numpy, character values may be prioritized over numerical values if the data
        # type is set to 'object'. For instance, the value '10' would come before '3' because it contains '1' and '0'
        # at the beginning. One solution to this problem is to convert the data to 'float' if it is numerical.
        unique_id_count = pd.Series(self.unique_id).value_counts(sort=False)
        self.indices, sizes = unique_id_count.index, unique_id_count.values
        cum_sizes = np.cumsum(sizes)

        # Processing datestamp
        self.dates = self.np_df[self.datetime_column_name]
        if self.engine_dataframe == pd.DataFrame:
            self.dates = self.dataframe.index.get_level_values(
                self.datetime_column_name
            )
        self.dates = self.dates[cum_sizes - 1]
        self.indptr = np.append(0, cum_sizes).astype(np.int32)

        # Index that will be used by pandas, not polars
        self.index = pd.MultiIndex.from_arrays(
            [
                self.np_df["unique_id"],
                self.np_df["ds"],
            ],
            names=["unique_id", "ds"],
        )

    def grouped_array(self):
        return GroupedArray(self.value_array, self.indptr)

    def _to_np_and_engine(self):
        """
        This function will be utilised to convert DataFrame to dictionary.

        Returns:
            tuple[pd.DataFrame or pl.DataFrame, dict]: the engine that will be used to construct
                the output DataFrame and dictionary of DataFrame values

        Raises:
            ValueError: If DataFrame engine is not supported and/or accounted for.
        """

        ####################
        # Polars DataFrame #
        ####################
        if isinstance(self.dataframe, pl_DataFrame):
            from packaging.version import Version

            import polars as pl

            # Ensure that all required columns are present in the DataFrame:
            self.engine_dataframe = pl_DataFrame
            if self.validate:
                self._validate_dataframe(self.dataframe)
            elif self.validate == False:
                self._partial_val_df(self.dataframe)

            # datetime check
            dt_arr = self.dataframe["ds"].to_numpy()
            processed_dt_arr = self._check_datetime(dt_arr)
            if type(dt_arr) != type(processed_dt_arr):
                self.dataframe = self.datafraFme.with_columns(
                    pl.from_numpy(processed_dt_arr.to_numpy(), schema=["ds"])
                )

            sample_index_df = self.dataframe[self.non_value_columns]
            sorted_index_df = sample_index_df.sort(self.non_value_columns)
            is_monotonic_increasing = sample_index_df.frame_equal(sorted_index_df)

            # Sorting will be performed if sort is set to true and values are unsorted
            if not is_monotonic_increasing and self.sort_dataframe:
                self.dataframe = self.dataframe.sort(self.non_value_columns)

            # resources: https://github.com/pola-rs/polars/blob/4fca1ae51864f74e0367d8bc91b4a2db00e54174/py-polars/polars/dataframe/frame.py#L1975
            # resources: https://numpy.org/doc/stable/user/basics.rec.html
            # resources: https://numpy.org/doc/stable/reference/generated/numpy.core.records.fromarrays.html
            # NOTE: Structured array is not available in polars under the version 0.17.12
            pl_version = Version(pl.__version__)
            min_pl_v = Version("0.17.12")
            if pl_version >= min_pl_v:
                return self.dataframe.to_numpy(structured=True)
            else:
                arrays = []
                for column, column_dtype in self.dataframe.schema.items():
                    ser = self.dataframe[column]
                    arr = ser.to_numpy()
                    arrays.append(
                        arr.astype(str, copy=False)
                        if str(column_dtype) == "Utf8" and not ser.has_validity()
                        else arr
                    )
                arr_dtypes = list(
                    zip(self.dataframe.columns, (a.dtype for a in arrays))
                )
                return np.rec.fromarrays(arrays, dtype=np.dtype(arr_dtypes))

        ####################
        # Pandas DataFrame #
        ####################
        elif isinstance(self.dataframe, pd.DataFrame):
            self.engine_dataframe = pd.DataFrame
            # Ensure that all required columns are present in the DataFrame:
            # Full validation
            if self.validate and self.dataframe.index.name == "unique_id":
                reset_df = self.dataframe.reset_index()
                self._validate_dataframe(reset_df)
                del reset_df

            elif self.validate and self.dataframe.index.name != "unique_id":
                self._validate_dataframe(self.dataframe)
                self.dataframe = self.dataframe.set_index("unique_id")

            # Partial validation
            elif self.validate == False and self.dataframe.index.name == "unique_id":
                reset_df = self.dataframe.reset_index()
                self._partial_val_df(reset_df)
                del reset_df

            elif self.validate == False and self.dataframe.index.name != "unique_id":
                self._partial_val_df(self.dataframe)
                self.dataframe = self.dataframe.set_index("unique_id")

            # Datetime check
            dt_arr = self.dataframe["ds"].values
            self.dataframe["ds"] = self._check_datetime(dt_arr)

            self.dataframe = self.dataframe.set_index("ds", append=True)

            # Sorting will be performed if sort is set to true and values are unsorted
            if not self.dataframe.index.is_monotonic_increasing and self.sort_dataframe:
                self.dataframe = self.dataframe.sort_values(self.non_value_columns)

            np_df = self.dataframe.to_records(index=True)

            return np_df

        ####################
        # Not Supported DF #
        ####################
        else:
            raise ValueError(f"{type(self.dataframe)} is not supported")

    def _validate_dataframe(self, dataframe: DataFrame):
        """
        Will ensure that all DataFrame columns match the required columns.

        This code requires a pandas DataFrame with the following structure:

        Columns:
        - `unique_id` Union[str, int, categorical]: an identifier for the series
        - `ds` Union[datestamp, int]: column should be either an integer indexing time or a
            datestamp ideally like YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a timestamp.
        - `y` Union[float, int]: represents the measurement we wish to forecast.

        Raise:
            KeyError: DataFrame is missing `unique_id`, `ds`, `y` columns.
        """
        required_columns = ["unique_id", "ds", "y"]
        matches = all(rc in dataframe.columns for rc in required_columns)
        if not matches:
            raise KeyError(
                "The DataFrame doesn't contain {} columns".format(
                    ", ".join(required_columns)
                )
            )

    def _partial_val_df(self, dataframe: DataFrame):
        """
        Will ensure that all DataFrame columns match the required columns.

        This code requires a pandas DataFrame with the following structure:

        Columns:
        - `unique_id` Union[str, int, categorical]: an identifier for the series
        - `ds` Union[datestamp, int]: column should be either an integer indexing time or a
            datestamp ideally like YYYY-MM-DD for a date or YYYY-MM-DD HH:MM:SS for a timestamp.

        Raise:
            KeyError: DataFrame is missing `unique_id` and/or `ds` columns.
        """
        required_columns = ["unique_id", "ds"]
        matches = all(rc in dataframe.columns for rc in required_columns)
        if not matches:
            raise KeyError(
                "The DataFrame doesn't contain {} columns".format(
                    ", ".join(required_columns)
                )
            )

    def _check_datetime(self, arr: np.ndarray) -> Union[pd.DatetimeIndex, np.ndarray]:
        dt_check = pd.api.types.is_datetime64_any_dtype(arr)
        int_float_check = arr.dtype.kind in ["i", "f"]
        if not dt_check and not int_float_check:
            self._ds_is_dt = True
            try:
                return pd.to_datetime(arr)
            except Exception as e:
                msg = (
                    "Failed to parse `ds` column as datetime. "
                    "Please use `pd.to_datetime` outside to fix the error. "
                    f"{e}"
                )
                raise Exception(msg) from e
        return arr
