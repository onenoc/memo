'''
@author: Jon O'Bryan (primary)
@author: Alexander Moreno (secondary)
'''
import time
from memoizer.DecoratorFactoryInstance import factory
def sleepy():
    time.sleep(5)
    return

@factory.decorator
def sleepy2():
    time.sleep(5)
    return

def fib_slow(n):
    if n < 2:
        return n
    return fib_slow(n - 2) + fib_slow(n - 1)

@factory.decorator
def fib(n):
    if n < 2:
        return n
    return fib(n - 2) + fib(n - 1)

if __name__ == '__main__':
    start = time.time()
    print fib_slow(30)
    print time.time() - start
    start = time.time()
    print fib(30)
    print time.time() - start
    '''
    @note: what we see is that for small values, fib_slow is actually faster.
    This likely is due to cache misses.  Thus, repeated calls involving cache
    misses will likely be slower
    '''
    
    
    