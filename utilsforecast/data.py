# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/data.ipynb.

# %% auto 0
__all__ = ['generate_series']

# %% ../nbs/data.ipynb 4
import numpy as np
import pandas as pd

from .compat import DataFrame

# %% ../nbs/data.ipynb 5
def generate_series(
    n_series: int,
    freq: str = "D",
    min_length: int = 50,
    max_length: int = 500,
    n_static_features: int = 0,
    equal_ends: bool = False,
    with_trend: bool = False,
    static_as_categorical: bool = True,
    engine: str = "pandas",
    seed: int = 0,
) -> DataFrame:
    """Generate Synthetic Panel Series.

    Parameters
    ----------
    n_series : int
        Number of series for synthetic panel.
    freq : str (default='D')
        Frequency of the data, 'D' or 'M'.
    min_length : int (default=50)
        Minimum length of synthetic panel's series.
    max_length : int (default=500)
        Maximum length of synthetic panel's series.
    n_static_features : int (default=0)
        Number of static exogenous variables for synthetic panel's series.
    equal_ends : bool (default=False)
        Series should end in the same date stamp `ds`.
    with_trend : bool (default=False)
        Series should have a (positive) trend.
    static_as_categorical : bool (default=True)
        Static features should have a categorical data type.
    engine : str (default='pandas')
        Output Dataframe type.
    seed : int (default=0)
        Random seed used for generating the data.

    Returns
    -------
    series : pandas or polars DataFrame
        Synthetic panel with columns [`unique_id`, `ds`, `y`] and exogenous features.
    """
    available_engines = ["pandas", "polars"]
    engine = engine.lower()
    if engine not in available_engines:
        raise ValueError(
            f"{engine} is not a correct engine; available options: {available_engines}"
        )
    seasonalities = {"D": 7, "M": 12}
    available_frequencies = seasonalities.keys()
    if freq not in available_frequencies:
        raise ValueError(
            f"Currently soported frequencies are: {available_frequencies}, got {freq}"
        )

    rng = np.random.RandomState(seed)
    series_lengths = rng.randint(min_length, max_length + 1, n_series)
    total_length = series_lengths.sum()

    season = seasonalities[freq]
    vals_dict = {"unique_id": np.repeat(np.arange(n_series), series_lengths)}

    dates = pd.date_range("2000-01-01", periods=max_length, freq=freq).values
    if equal_ends:
        series_dates = [dates[-length:] for length in series_lengths]
    else:
        series_dates = [dates[:length] for length in series_lengths]
    vals_dict["ds"] = np.concatenate(series_dates)

    vals_dict["y"] = np.arange(total_length) % season + rng.rand(total_length) * 0.5

    for i in range(n_static_features):
        static_values = np.repeat(rng.randint(0, 100, n_series), series_lengths)
        vals_dict[f"static_{i}"] = static_values
        if i == 0:
            vals_dict["y"] = vals_dict["y"] * (1 + vals_dict[f"static_{i}"])

    if with_trend:
        coefs = np.repeat(rng.rand(n_series), series_lengths)
        trends = np.concatenate([np.arange(length) for length in series_lengths])
        vals_dict["y"] += coefs * trends

    cat_cols = [col for col in vals_dict.keys() if "static" in col]
    cat_cols.append("unique_id")
    if engine == "pandas":
        df = pd.DataFrame(vals_dict)
        if static_as_categorical:
            df[cat_cols] = df[cat_cols].astype("category")
            df["unique_id"] = df["unique_id"].cat.as_ordered()
    else:
        import polars as pl

        df = pl.DataFrame(vals_dict)
        df = df.with_columns(pl.col("unique_id").sort())
        if static_as_categorical:
            df = df.with_columns(
                *[pl.col(col).cast(str).cast(pl.Categorical) for col in cat_cols]
            )
    return df
