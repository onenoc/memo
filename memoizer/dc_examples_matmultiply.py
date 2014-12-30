import time
import random
import os
import hashlib
import pandas as pd
import numpy as np
import time
from pandas.util.testing import assert_frame_equal
from memoizer.DecoratorFactoryInstance import factory

@factory.decorator
def mat_transpose_multiply(pd_data, ldt_dates, l_dc_ret="", ldt_dc_dates="", ls_dc_indices="", divide_conquer=0):
    if divide_conquer==1:
        pd_dc_dataframe = l_dc_ret[0]
        dt_end = ldt_dates[-1]
        dt_dc_end = ldt_dc_dates[-1]
        np_1 = l_dc_ret[0]
        start = time.time()
        df_2 = pd_data[dt_dc_end+1:dt_end]
        print "indexing time is %f" % (time.time() - start)
        np_2 = df_2.values
        retval= np_1+np.dot(np.transpose(np_2), np_2)
        return retval
    else:
        np_matrix = pd_data.values
        return np.dot(np.transpose(np_matrix), np_matrix)
    '''
    start = time.time()
    pd_series = lpd_data[0][lpd_data[0].columns.values[0]]
    print "extra overhead time %f" % (time.time() - start)
    dt_start = ldt_dates[0]
    dt_end = ldt_dates[-1]
    print "extra overhead time %f" % (time.time() - start)
    if divide_conquer==1:
        dt_dc_start = ldt_dc_dates[0]
        dt_dc_end = ldt_dc_dates[-1]
        pd_dc_series = l_dc_ret[0]
        s1 = pd_dc_series
        s2 = pd_series[dt_dc_end+2:dt_end]
        s = pd.concat([s1, s2])
        print "extra overhead time %f" % (time.time() - start)
        s.sort()
        print "divide conquer"
        return s
    else:
        s1 = pd_series.copy()
        s1.sort()
        print "full computation"
        return s1
    '''

def mat_transpose_mult_simple(pd_data):
    np_matrix = pd_data.values
    return np.dot(np.transpose(np_matrix), np_matrix)

if __name__ == '__main__':
    n=500
    t=200000
    rng = pd.date_range('1/1/2011', periods=2*t, freq='s') 
    np_1 = np.random.rand(t, n)
    np_2 = np.random.rand(t, n)
    df_1 = pd.DataFrame(np_1, index=rng[0:t], columns=range(n))
    df_2 = pd.DataFrame(np_2, index=rng[t:2*t], columns=range(n))
    df_full = pd.concat([df_1, df_2])
    start = time.time()
    r1 = mat_transpose_multiply(df_1, rng[0:t], divide_conquer=0)
    start = time.time()
    #mat_transpose_multiply(df_full, rng, l_dc_ret=[r1], ldt_dc_dates=rng[0:t], divide_conquer=1)
    mat_transpose_multiply(df_full, rng, divide_conquer=0)
    print time.time() - start
    start = time.time()
    mat_transpose_mult_simple(df_full)
    print time.time() - start

