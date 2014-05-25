memo
====

NOTE: this library is still in alpha mode

This is a memoizer class that you can use to decorate your functions so that they get cached to a file and run faster in future runs.

To use, from the cloned folder, run<br>
python setup.py install<br>
This will give you the folder where it is installed.  Go there and create a subdirectory Data/<br>

Then, in any file where you want to use it, add the following at the top:<br>
from memoizer.DecoratorFactoryInstance import factory<br>

Then, above functions that you want to avoid recomputing on future runs, you decorate using @factory.decorator.  For instance:<br>
@factory.decorator<br>
def my_slow_function(arguments):<br>
&nbsp;&nbsp;&nbsp;&nbsp;slow code here<br>
  
Also, in the DecoratorFactoryInstance, you can change settings for how many bytes the scratch folder uses (FIFO eviction), the frequency at which we check our function return values vs the cached values (a probability between 0 and 1), and the verbosity (True or False), in this line:<br>
factory=DecoratorFactory(bytes, frequency, verbosity)

<b>Examples (Thanks Jon O'Bryan):</b><br>
import time<br>
import sys<br>
sys.path.append('/home/jobryan/memo')<br>
from DecoratorFactoryInstance import factory<br>
def sleepy():<br>
&nbsp;&nbsp;&nbsp;&nbsp;time.sleep(5)<br>
&nbsp;&nbsp;&nbsp;&nbsp;return<br>

@factory.decorator<br>
def sleepy2():<br>
&nbsp;&nbsp;&nbsp;&nbsp;time.sleep(5)<br>
&nbsp;&nbsp;&nbsp;&nbsp;return 5<br>

def fib_slow(n):<br>
&nbsp;&nbsp;&nbsp;&nbsp;if n < 2:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return n<br>
&nbsp;&nbsp;&nbsp;&nbsp;return fib_slow(n - 2) + fib_slow(n - 1)<br>

@factory.decorator<br>
def fib(n):<br>
&nbsp;&nbsp;&nbsp;&nbsp;if n < 2:<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return n<br>
&nbsp;&nbsp;&nbsp;&nbsp;return fib(n - 2) + fib(n - 1)<br>
