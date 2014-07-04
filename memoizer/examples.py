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
    print time.time()