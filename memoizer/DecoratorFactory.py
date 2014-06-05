import hashlib
import os
import pickle as pkl
import time
import datetime as dt
import copy
import collections
import numpy as numpy
import pandas as pandas
from MemoizedObject import MemoizedObject
from copy import deepcopy
from random import randrange
from pandas.util.testing import assert_frame_equal

import itertools
import inspect

class DecoratorFactory(object):
    def __init__(self, size, frequency, verbose=False, on=True):
        self._size = size
        self._frequency = frequency
        self._verbose = verbose
        self._on = on

    def decorator(self, f):
        def wrapper(*args, **kwargs):
            if self._on == False:
                return f(*args, **kwargs)
            if self._verbose:
                print "starting decorator"
            path = os.environ['MEMODATA'] + "/"
            h = hashlib.md5(f.__name__).hexdigest()
            for i in range(len(args)):
                if args[i].__class__.__name__ == "MemoizerDataFrame":
                    h += args[i].get_hash()
                    args[i] = args[i].get_hash()
                else:
                    h += "+" + self.__hash_from_argument(args[i]).hexdigest()

            for kwarg in kwargs:
                h += "+" + self.__hash_from_argument(kwarg).hexdigest()
            #get cache filename based on function name and arguments
            cachefilename = path + h + '.pkl'
            tmp_filename = path + str(time.time()) + ".pkl"
            if len(cachefilename) >= 250:
                h = hashlib.md5(h).hexdigest()
                cachefilename = path + h + '.pkl'
                print cachefilename
            #get based on same, but with "NO"
            h_no = h + "no"
            nocachefilename = path + h_no + '.pkl'
            if len(cachefilename) >= 250:
                h = self.__hash_from_argument(h).hexdigest()
                h_no = h + "no"
                nocachefilename = path + h_no + '.pkl'
            try:
                #rename to a tempfile, read from it, close it, and rename back
                os.rename(cachefilename, tmp_filename)
                if self._verbose:
                    print "file already exists, reading from cache"
                tmp_file = open(tmp_filename, "rb")
                memoizedObject = pkl.load(tmp_file)
                tmp_file.close()
                os.rename(tmp_filename, cachefilename)

                #handle return value
                retval = memoizedObject.cache_object
                #some % of the time, check to make sure calculated value matches the pkl file value
                if self._frequency != 0 and self._frequency <= 1 and randrange(1 / self._frequency)==0:
                        retval_test = f(*args, **kwargs)
                        if self.__compare(retval, retval_test) == False:
                            print "Alert!!!  pkl value and calculated return value don't match"
                            retval = retval_test
                #check to make sure that function definition hasn't changed, and if it has, recalculate
                if inspect.getsource(f) != memoizedObject.definition:
                    os.remove(cachefilename)
                    retval = f(*args, **kwargs)
                    if self._verbose:
                        print "ALERT!!! Definition changed!!!!"
            except EOFError:
                print "EOFError"
                try:
                    os.remove(cachefilename)
                    print "removed corrupt cache file"
                except:
                    pass
                retval = f(*args, **kwargs)
            except (OSError, IOError) as e:
                if self._verbose:
                    print "file not found"
                try:
                    nocachefile_tmp_filename = path + str(time.time())
                    os.rename(nocachefilename, nocachefile_tmp_filename)
                    print "have the no cache filename"
                    #open and close this file so that it is marked as opened for
                    # last accessed (need for cache eviction)
                    nocachefile_tmp_file = open(noachefile_tmp_filename, "rb")
                    nocachefile_tmp_file.close()
                    os.rename(nocachefile_tmp_filename, nocachefilename)
                    return f(*args, **kwargs)
                except (OSError, IOError) as e:
                    pass
                if self._verbose:
                    print "creating pkl file"
                tmp_file = open(tmp_filename, "wb")
                #calculate return value and log time
                start_calc = time.time()
                retval = f(*args, **kwargs)
                memoizedObject = MemoizedObject(inspect.getsource(f), retval)
                calc_time = time.time() - start_calc
                pkl.dump(memoizedObject, tmp_file, -1)
                tmp_file.close()
                os.rename(tmp_filename, cachefilename)
                os.chmod(cachefilename, 0666)
                #rename to a tempfile, read from it, close it, and rename back
                os.rename(cachefilename, tmp_filename)
                #read from cache and log time
                start_read = time.time()
                tmp_file = open(tmp_filename, "rb")
                test_retval = pkl.load(tmp_file)
                tmp_file.close()
                read_time = time.time() - start_read
                os.rename(tmp_filename, cachefilename)

                #detect use of randomization
                source = inspect.getsource(f)
                random = 0
                if "rand" in source:
                    random = 1
                    print "random"
                #if the cache time is slower than the calculate time,
                #or there is use of randomization
                #create a file telling us not to use cache in future and delete cache file
                if read_time > calc_time or random == 1:
                    if self._verbose:
                        print "too slow, not caching"
                    tmp_create_nocachefilename = path + str(time.time())
                    tmp_create_nocachefile = open(tmp_create_nocachefilename, "wb")
                    tmp_create_nocachefile.close()
                    os.rename(tmp_create_nocachefilename, nocachefilename)
                    os.remove(cachefilename)
                if self._verbose:
                    print "about to return, just cached"
                #check whether the current directory size is bigger than we want
                if self.__get_directory_size() > self._size:
                    #deal with cache eviction
                    self.__manage_directory_size()
                return retval
        return wrapper

    def __get_directory_size(self):
        #get the size of the data directory and filenames
        if self._verbose:
            print "managing directory size"
        path = os.environ['MEMODATA'] + "/"
        dirs = os.listdir(path)
        dir_size = []
        files = []
        for file in dirs:
            dir_size.append(os.path.getsize(path + file))
            files.append(file)
        total_dir_size = sum(dir_size)
        return total_dir_size

    def __manage_directory_size(self):
        #get the size of the data directory and filenames
        if self._verbose:
            print "managing directory size"
        path = os.environ['MEMODATA'] + "/"
        dirs = os.listdir(path)
        dir_size = []
        files = []
        for file in dirs:
            dir_size.append(os.path.getsize(path + file))
            files.append(file)
        total_dir_size = sum(dir_size)
        if self._verbose:
            print "initial directory size is"
            print total_dir_size
        #if so, delete from last accessed file onwards
        #currently, we will set it so that if the size of the folder is more than that set by the __init__.py file, we reduce it to that size

        if total_dir_size > self._size:
            #sort by last accessed: make sure actually last accessed
            files.sort(key = lambda x: os.stat(path + x).st_atime)
            files = list(reversed(files))
            files_to_delete = []
            i = 0
            while total_dir_size > self._size and i < len(files):
                total_dir_size -= os.path.getsize(path + files[i])
                print total_dir_size
                files_to_delete.append(files[i])
                i += 1
            for file in files_to_delete:
                os.remove(path + file)

    def __compare(self, value1, value2):
        if type(value1) != type(value2):
            return False
        if type(value1) is numpy.ndarray:
            h1 = hashlib.md5(value1.data).hexdigest()
            h2 = hashlib.md5(value2.data).hexdigest()
            return (h1==h2)
        elif type(value1) is list or type(value1) is tuple:
            if len(value1) != len(value2):
                return False
            try:
                equality = (value1 == value2)
                return equality
            except:
                for i in range(len(value1)):
                    if self.__compare(value1[i], value2[i]) == False:
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
                    return false

    def __hash_from_argument(self, argument):
        arg_string = ""
        if type(argument) is numpy.ndarray:
            arg_string = str(argument.shape)
        if type(argument) is pandas.core.frame.DataFrame:
            col_values_list = list(argument.columns.values)
            col_values_string = ''.join(col_values_list)
            arg_string = col_values_string
        if type(argument) is list or type(argument) is tuple:
            arg_string = str(len(argument))
        arg_string += str(argument)
        return hashlib.md5(arg_string)

