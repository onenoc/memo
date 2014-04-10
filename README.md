memo
====

NOTE: this library is still in alpha mode

This is a memoizer class that you can use to decorate your functions so that they get cached to a file and run faster in future runs.

To use, first import the package to the files with relevant functions using the following format:<br>
import sys<br>
sys.path.append('file_path')<br>
from DecoratorFactoryInstance import factory

Then, above functions that you want to avoid recomputing on future runs, you decorate using @factory.decorator.  For instance:<br>
@factory.decorator<br>
def my_slow_function(arguments):<br>
&nbsp;&nbsp;&nbsp;&nbsp;slow code here<br>
  
Also, in the DecoratorFactoryInstance, you can change settings for how many bytes the scratch folder uses (FIFO eviction), the frequency at which we check our function return values vs the cached values (a probability between 0 and 1), and the verbosity (True or False), in this line:<br>
factory=DecoratorFactory(bytes, frequency, verbosity)
