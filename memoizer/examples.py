'''
@author: Jon O'Bryan (primary)
@author: Alexander Moreno (secondary)
'''
import time
import random
import os
import hashlib

import numpy as np
from memoizer.DecoratorFactoryInstance import factory

def sleepy(x):
    time.sleep(5)
    return x

@factory.decorator
def sleepy2(x):
    return x

def fib_slow(n):
    if n < 2:
        return n
    return fib_slow(n - 2) + fib_slow(n - 1)

@factory.decorator
def fib(n):
    if n < 2:
        return n
    return fib(n - 2) + fib(n - 1)

def compare_matrices_random(np_array_1, np_array_2):
    i_size = np_array_1.shape[0] * np_array_1.shape[1]
    for i in range(int(0.02 * i_size)):
        x = random.randrange(np_array_1.shape[0])
        y = random.randrange(np_array_1.shape[1])
        if np_array_1[x][y] != np_array_2[x][y]:
            return 0
        return 1

@factory.decorator
def return_same_array(np_array):
    return np_array

@factory.decorator
def mutate_args(li_list):
    for i in range(len(li_list)):
        li_list[i] = li_list[i] - 1
    return 1

if __name__ == '__main__':
    ls_list = [1, 2, 3]
    mutate_args(ls_list)
    print ls_list 
    '''
    @note: what we see is that for small values, fib_slow is actually faster.
    This likely is due to cache misses.  Thus, repeated calls involving cache
    misses will likely be slower
    '''
