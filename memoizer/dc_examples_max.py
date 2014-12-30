import pandas as pd
import numpy as np
import sys
import time
from memoizer.DecoratorFactoryInstance import factory
import csv

def find_max(pd_data, ldt_dates, l_dc_ret="", ldt_dc_dates="", ls_dc_indices="", divide_conquer=0):
    if divide_conquer==0:
        rows = pd_data.idxmin()
        cols = pd_data.idxmin(axis=1)
        dt_min = cols.idxmin(axis=1)
        print pd_data[pd_data[0].idxmin()]
        #dt_max = cols.idxmax(axis=1)
        #print cols
        #print dt_min, dt_max
        #print cols.ix[dt_min], cols.ix[dt_max]
        return (cols[dt_min], dt_min)
    #find row where value for each column is max


if __name__ == '__main__':
    n=500
    t=100
    rng = pd.date_range('1/1/2011', periods=2*t, freq='s')
    np_1 = np.random.rand(t, n)
    np_2 = np.random.rand(t, n)
    df_1 = pd.DataFrame(np_1, index=rng[0:t], columns=range(n))
    df_2 = pd.DataFrame(np_2, index=rng[t:2*t], columns=range(n))
    df_full = pd.concat([df_1, df_2])
    find_max(df_1, rng[0:t])
