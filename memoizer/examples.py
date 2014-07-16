'''
@author: Jon O'Bryan (primary)
@author: Alexander Moreno (secondary)
'''
import time
import random
import numpy as np

import numpy as np
from memoizer.DecoratorFactoryInstance import factory

def sleepy(x):
    time.sleep(5)
    return x

@factory.decorator
def sleepy2(x):
    time.sleep(5)
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
    time.sleep(2)
    return np_array

if __name__ == '__main__':
    np_array_1 = np.zeros((2000, 2000))
    return_same_array(np_array_1)
    print "returned"
    np_array_1[500:1000, 500:1000]=1
    print np_array_1
    return_same_array(np_array_1)
    print "returned"
    
    '''
    @note: what we see is that for small values, fib_slow is actually faster.
    This likely is due to cache misses.  Thus, repeated calls involving cache
    misses will likely be slower
    '''
    
    
    
