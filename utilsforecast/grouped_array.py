# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/grouped_array.ipynb.

# %% auto 0
__all__ = ['GroupedArray']

# %% ../nbs/grouped_array.ipynb 3
import numpy as np

# %% ../nbs/grouped_array.ipynb 4
class GroupedArray:
    def __init__(self, data: np.ndarray, indptr: np.ndarray):
        self.data = data
        self.indptr = indptr
