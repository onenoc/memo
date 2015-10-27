memo
====
This is a memoizer class that you can use to decorate your functions so that they get cached to a file and run faster in future runs.  <i>Note: some of this text was taken from the papers "Speeding up large-scale financial recomputation with memoization" and "Improving Financial Computation Speed With Full and Subproblem Memoization"</i>

<h1>Why Memoize?</h1>
-Program Crashes: one of the functions called by the program crashes, and you need to recompute everything<br>
-Unit tests also could benefit from avoiding recom- putation. Generally, they involve testing to see whether an output makes sense, and if the dependencies of a function remain unchanged, it need not be recomputed in order to answer this question.<br>
<h2>How does it work?</h2>
This library uses decorators, a type of function annotation, to memoize to disk. Memoization refers to “remembering” previously calculated function values, and then looking them up instead of recomputing them. Memoization to a file involves using the function name and arguments to generate a hash that serves as a filename, and then saving, or serializing, the “remembered” object to a pickle file. On subsequent calls to that function with those arguments, memoization reads, or deserializes from the file instead of recomputing.

<h1>Installation</h1>
To get started, run<br>
git clone git@github.com:onenoc/memo.git<br>
cd memo<br>
python setup.py install<br>
pip install xxh<br>
pip install xxhash<br>

<h2> Setup </h2>
Next, add the folder MEMOData and setup an environment variable.  You can do this by creating a MEMOData folder in your home directory and adding the following to your .bash_profile or .bashrc file<br>
export MEMODATA=$HOME/MEMOData<br>

Then, in any file where you want to use it, add the following at the top:<br>
from memoizer.DecoratorFactoryInstance import factory<br>

<h1> Usage </h1>
Then, above functions that you want to avoid recomputing on future runs, you decorate using @factory.decorator.  For instance:<br>
@factory.decorator<br>
def my_slow_function(arguments):<br>
&nbsp;&nbsp;&nbsp;&nbsp;slow code here<br>
  
Also, in the file set_json.py, you can change settings for how many bytes the scratch folder uses (FIFO eviction), the frequency at which we check our function return values vs the cached values (a probability between 0 and 1), and the verbosity (True or False), or whether we even use the memoizer library.  The details are as follows<br>

data['bytes'] = 419430400*25 #this sets how much space to allocate for memoization<br>
data['frequency'] = 0.0 #probability of check for memoization<br>
data['verbose'] = False #print info<br>
data['on'] = True #turn memoization on or off globally<br>
data['hash_function'] = 'xxhash'#use xxhash or md5<br>
data['check_arguments'] = True #check whether arguments are the same<br>
data['check_mutation'] = False #check whether mutation occurs of values<br>

<b>Examples (Thanks Jon O'Bryan):</b><br>
import time<br>
import sys<br>
from memoizer.DecoratorFactoryInstance import factory<br>
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

<h1> Features </h1>
<h2> Deterministic vs Non-Deterministic Functions </h2>
Deterministic functions, given some arguments, will always return the same value. Nondeterministic functions may not. Nondeterministic functions include functions that use randomization, read from a database or file that may change, or depend on the current time. When memoizing, we check the function definition as a string to make sure that it does not include rand or time as substrings, and that the function definition has not changed, but beyond that, taking care to avoid memoizing nondeterministic functions is left to the user. If we determine that it is a nondeterministic function based on rand or time, we do not memoize it and create a file to indicate not to memoize it in the future.

<h2> Checking Whether Memoizing Saves Time </h2>
When memoizing, we log the time to compute the function return value and compare it to the time to read from the file we’ve memoized to. If the computation time is faster, we delete the file and create the no memoization file. This makes the first memoization we do slightly slower than some competing packages.

<h2> Large Dataframes </h2>
Pickle fails to serialize large dataframes, generally in excess of a gigabyte. For these,we use the pandas call to pytables, which allows HDFStore and handling of far larger objects, although HDFStore currently only supports storing a few object types.

<h2> Fast Hashing </h2>
Competing packages use md5 for hashing. Md5 is a cryptographic hash, which means that it is designed to make collisions difficult to find even for malicious input. Noncryptographic hashes are faster and make collisions unlikely only for non-malicious input. This means that it’s easy to generate a collision if one studies the hash function, but unlikely otherwise.  We give the user the option of using xxhash 64, a noncryptographic hash function that is much faster than md5 (https://github.com/Cyan4973/xxHash)

<h2> Checking for Mutations </h2>
Our package allows users to set whether to store the underlying matrix and check whether it’s been mutated, and if so, update the hash. This equality check takes double the ram and may or may not be faster than hashing depending on how many cores the user has (since numpy automatically parallelizes array comparison) and what hash function is used.

<h2> Random Correctness Check </h2>
Further, checking that return values match memoized values is important as the user may inadvertently memoize some non-deterministic functions. For instance, some function in a library may call a non-deterministic algorithm in a language like C or C++, such as a Markov Chain Monte Carlo algorithm. In this case, testing for the substring rand in the function definition wouldn’t be sufficient to detect that it was a non-deterministic function. We allow the user to set the probability of doing an equality check for return values to between 0 and 1. A value of 1 can be used after memoizing a function with long code where the user isn’t sure whether it’s safe to memoize it, while a value close to 0 can be used to catch errors when working with a program over a long period.

Developed by Alexander Moreno under the supervision of Professor Tucker Balch, Georgia Tech
