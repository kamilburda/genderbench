import warnings

import numpy as np


def nanmean(ite):
    if not ite:
        return np.nan
    with warnings.catch_warnings():
        warnings.simplefilter(
            "ignore", category=RuntimeWarning
        )  # Catch spurious warning for iterators filled with nans
        return np.nanmean(ite).item()


def zero_div(a, b):
    if b == 0:
        return np.nan
    return a / b
