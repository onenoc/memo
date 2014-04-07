memo
====

NOTE: this library is still in alpha mode (appears to have a bug so that when caching file names get very long, it doesn't read from them)

This is a memoizer class that you can use to decorate your functions so that they get cached to a file and run faster in future runs.

To use, first import the package to the files with relevant functions using the following format:<br>
import sys<br>
sys.path.append('file_path')
