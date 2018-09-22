# -*- coding: utf-8 -*-
from multiprocessing import cpu_count, Pool

import numpy as np
import pandas as pd


def parallel_apply(_df: pd.DataFrame, func):
    """http://blog.adeel.io/2016/11/06/parallelize-pandas-map-or-apply/
    """
    cores = cpu_count() - 1  # leave one free to not freeze machine
    data_split = np.array_split(_df, cores)
    pool = Pool(cores)
    _df = pd.concat(pool.map(func, data_split))
    pool.close()
    pool.join()
    return _df
