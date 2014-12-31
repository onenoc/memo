import time
import random
import os
import hashlib
import pandas as pd
import numpy as np
import time
import csv
from pandas.util.testing import assert_frame_equal
from memoizer.DecoratorFactoryInstance import factory

global_sort_time = []

@factory.decorator
def sort_dc(pd_data, ldt_dates, l_dc_ret="", ldt_dc_dates="", ls_dc_indices="", divide_conquer=0):
    start = time.time()
    pd_series = pd_data[pd_data.columns.values[0]]
    dt_start = ldt_dates[0]
    dt_end = ldt_dates[-1]
    if divide_conquer==1:
        dt_dc_start = ldt_dc_dates[0]
        dt_dc_end = ldt_dc_dates[-1]
        i1 = pd_data.index.get_loc(dt_dc_end)
        i2 = pd_data.index.get_loc(dt_end)
        pd_dc_series = l_dc_ret[0][l_dc_ret[0].columns.values[0]]
        s1 = pd_dc_series
        s2 = pd_series.iloc[i1:i2]
        s= pd.concat([s1, s2])
        s.sort()
        s = pd.DataFrame(s, columns=['s'])
        global_sort_time.append(time.time() - start)
        return s
    else:
        s = pd_series.copy()
        s.sort()
        s = pd.DataFrame(s, columns=['s'])
        return s

if __name__ == '__main__':
    n=200000
    i_total = n*(2**8)
    rng = pd.date_range('1/1/2011', periods=i_total, freq='s')
    s = pd.Series(np.random.randn(n), index=rng[0:n])
    s = pd.DataFrame(s, columns=['s'])
    #sort_dc(s, rng[0:n], divide_conquer=0)
    time.sleep(2)
    n_new = 0
    lf_memo_times = []
    lf_standard_times = []
    while 2*n_new <= i_total:
        n_new = 2*n
        print n_new
        s_add = pd.Series(np.random.randn(n), index=rng[n:n_new])
        s_add = pd.DataFrame(s_add, columns=['s'])
        s = pd.concat([s, s_add])
        start = time.time()
        sort_dc(s, rng[0:n_new], divide_conquer=0)
        lf_memo_times.append(time.time() - start)
        start = time.time()
        s.copy()['s'].copy().sort()
        lf_standard_times.append(time.time() - start)
        n = n_new
        time.sleep(2)

    with open('memo_times.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(lf_memo_times)
    with open('standard_times.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(lf_standard_times)
    with open('actual_memo_sort.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(global_sort_time)
    '''
    rng = pd.date_range('1/1/2011', periods=2*n, freq='s') 
    s1 = pd.Series(np.random.randn(n), index=rng[0:n])
    s2 = pd.Series(np.random.randn(n), index=rng[n:2*n])
    s = pd.concat([s1, s2])
    s1 = pd.DataFrame(s1, columns=['s1'])
    s = pd.DataFrame(s, columns=['s1'])
    start = time.time()
    sort_dc(s1, rng[0:n], divide_conquer=0)
    print time.time() - start
    start = time.time()
    s1['s1'].copy().sort()
    print time.time() - start
    time.sleep(3)
    start = time.time()
    print s.columns.values
    s_sorted = sort_dc(s, rng, divide_conquer=0)
    print time.time() - start
    start = time.time()
    s_new = s['s1'].copy()
    s_new.sort()
    print time.time() - start
    #print s_sorted.shape, s_new.shape
    #print s_sorted, s_new
    #s_equal = (s_sorted==s_new).all()
    #s_equal[s_equal==False]
    '''
