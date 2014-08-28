'''
Created on Aug 9, 2014

@author: alexandermoreno
'''
import random
import time
import numpy as np
import hashlib
import pandas
from pandas.util.testing import assert_frame_equal

def compare_data_structures(value1, value2):
    if type(value1) != type(value2):
        return False
    if type(value1) is np.ndarray:
        return np.array_equal(value1, value2)
    elif type(value1) is list or type(value1) is tuple:
        if len(value1) != len(value2):
            return False
        try:
            equality = (value1 == value2)
            return equality
        except:
            for i in range(len(value1)):
                if compare_data_structures(value1[i], value2[i]) == False:
                    return False
            return True
    elif type(value1) is pandas.core.frame.DataFrame:
        try:
            assert_frame_equal(value1, value2, check_names=True)
            return True
        except AssertionError:
            return False
    else:
        try:
            equality = (value1 == value2)
            return equality
        except:
            try:
                return str(value1) == str(value2)
            except:
                return False
            
def compare_matrices_random(np_array_1, np_array_2):
    i_size = np_array_1.shape[0] * np_array_1.shape[1]
    for i in range(int(0.05 * i_size)):
        x = random.randrange(np_array_1.shape[0])
        y = random.randrange(np_array_1.shape[1])
        if np_array_1[x, y] != np_array_2[x, y]:
            return 0
    return 1

if __name__ == '__main__':
    np_array_1 = np.zeros((30000, 252))
    np_array_2 = np_array_1.copy()
    np_array_2[500:1000, 500:1000]=1
    
    #print compare_matrices_random(np_array_1, np_array_2)
    start = time.time()
    print compare_data_structures(np_array_1, np_array_2)
    print time.time() - start
    
