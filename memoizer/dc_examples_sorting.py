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
def sort_dc(lpd_data, ldt_dates, l_dc_ret="", ldt_dc_dates="", ls_dc_indices="", divide_conquer=0):
    start = time.time()
    pd_series = lpd_data[0][lpd_data[0].columns.values[0]]
    dt_start = ldt_dates[0]
    dt_end = ldt_dates[-1]
    if divide_conquer==1:
        dt_dc_start = ldt_dc_dates[0]
        dt_dc_end = ldt_dc_dates[-1]
        pd_dc_series = l_dc_ret[0][l_dc_ret[0].columns.values[0]]
        s1 = pd_dc_series
        s2 = pd_series[dt_dc_end+2:dt_end]
        s = pd.concat([s1, s2])
        s.sort()
        print "divide conquer"
        return pd.DataFrame(s, columns=['s1'])
    else:
        s1 = pd_series.copy()
        s1.sort()
        print "full computation"
        return pd.DataFrame(s1, columns=['s1'])

if __name__ == '__main__':
    '''
    n=5
    rng = pd.date_range('1/1/2011', periods=2*n, freq='s') 
    s1 = pd.Series(np.random.randn(n), index=rng[0:n])
    s2 = pd.Series(np.random.randn(n), index=rng[n:2*n])
    s = pd.concat([s1, s2])
    s1.sort()
    start = time.time()
    s_full = sort_dc([s], rng)
    print time.time()-start
    start = time.time()
    s_subproblem = sort_dc([s], rng, l_dc_ret=[s1], ldt_dc_dates=rng[0:n-1],divide_conquer=1)
    print time.time()-start
    print (s_full==s_subproblem).all()
    '''
    #mixing up dates creates a huge mess so that slicing by date doesn't work, have to slice by position, probably using .iloc or .ix
    #we need to get the start and end date when we return a dataframe, since we can't simply take first and last element anymore
    #what you get in current version is that your main series argument is not ordered by date in a big chunk
    #here is what we will need actually
    n=20000000
    rng = pd.date_range('1/1/2011', periods=2*n, freq='s') 
    s1 = pd.Series(np.random.randn(n), index=rng[0:n])
    s2 = pd.Series(np.random.randn(n), index=rng[n:2*n])
    s = pd.concat([s1, s2])
    s1 = pd.DataFrame(s1, columns=['s1'])
    s = pd.DataFrame(s, columns=['s1'])
    start = time.time()
    sort_dc([s1], rng[0:n], divide_conquer=0)
    print time.time() - start
    start = time.time()
    s1['s1'].copy().sort()
    print time.time() - start
    time.sleep(3)
    start = time.time()
    print s.columns.values
    sort_dc([s], rng, divide_conquer=0)
    print time.time() - start
    start = time.time()
    s['s1'].copy().sort()
    print time.time() - start
