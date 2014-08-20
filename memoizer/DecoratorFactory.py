'''
@author: Alexander Moreno
@note: it would be nice if we could flush the cache for a single function from
a single file easily.
@note: research bencode
'''
import hashlib
import os
import pickle as pkl
import time
import random
import itertools
import numpy as numpy
import pandas as pandas
from MemoizedObject import MemoizedObject
from random import randrange
import xxhash

from comparisons import compare_data_structures, compare_matrices_random

import inspect

class DecoratorFactory(object):
    def __init__(self, size, frequency, verbose=False, on=True):
        '''
        @summary: constructor to set parameters
        @param size: how many bytes the scratch directory can take
        @param frequency: a float between 0.0 and 1.0, expressing with what
        probability we use memoization if cache file found
        @param verbose: print info at runtime
        @param on: turn memoization on or off globally
        '''
        self._size = size
        self._frequency = frequency
        self._verbose = verbose
        self._on = on

    def decorator(self, f):
        def wrapper(*args, **kwargs):
            '''
            @summary: actual memoization code
            @param args: any arguments passed into the function decorated
            @param kwargs: any keyword arguments passed
            '''
            if self._on == False:
                return f(*args, **kwargs)
            if self._verbose:
                print "starting decorator"
            s_path = os.environ['MEMODATA'] + "/"
            s_hash = str(xxhash.xxh64(f.__name__))
            for argument in itertools.chain(args, kwargs):
                s_hash += "+" + self.__hash_from_argument(argument)
            #get cache filename based on function name and arguments
            cachefilename = s_path + s_hash + '.pkl'
            tmp_filename = s_path + str(time.time()) + ".pkl"
            if self._verbose:
                print "cache filename is %s" % (cachefilename)
            if len(cachefilename) >= 250:
                s_hash = str(xxhash.xxh64(s_hash))
                cachefilename = s_path + s_hash + '.pkl'
                print cachefilename
            #get based on same, but with "NO"
            h_no = s_hash + "no"
            nocachefilename = s_path + h_no + '.pkl'
            if len(cachefilename) >= 250:
                s_hash = self.__hash_from_argument(s_hash).hexdigest()
                h_no = s_hash + "no"
                nocachefilename = s_path + h_no + '.pkl'
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
                memo_args = memoizedObject.args
                for i in range(len(args)):
                    if type(args[i]) is numpy.ndarray:
                        i_match = compare_matrices_random(args[i], memo_args[i])
                        if i_match != 1:
                            os.remove(cachefilename)
                            raise arrayMatchError("arrays don't match")

                #some % of the time, check to make sure calculated value 
                #matches the pkl file value
                if self._frequency != 0 and self._frequency <= 1 and randrange(1 / self._frequency)==0:
                        retval_test = f(*args, **kwargs)
                        if compare_data_structures(retval, retval_test) == False:
                            print "Alert!!!  pkl value and calculated return value don't match"
                            retval = retval_test
                #check to make sure that function definition hasn't changed, 
                #and if it has, recalculate
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
            except (OSError, IOError, arrayMatchError) as e:
                if self._verbose:
                    print "file not found"
                try:
                    nocachefile_tmp_filename = s_path + str(time.time())
                    os.rename(nocachefilename, nocachefile_tmp_filename)
                    print "have the no cache filename"
                    #open and close this file so that it is marked as opened for
                    # last accessed (need for cache eviction)
                    nocachefile_tmp_file = open(nocachefile_tmp_filename, "rb")
                    nocachefile_tmp_file.close()
                    os.rename(nocachefile_tmp_filename, nocachefilename)
                    return f(*args, **kwargs)
                except (OSError, IOError) as e:
                    pass
                if self._verbose:
                    print "creating pkl file"
                #calculate return value and log time
                start_calc = time.time()
                retval = f(*args, **kwargs)
                memoizedObject = MemoizedObject(inspect.getsource(f), retval, args, kwargs)
                calc_time = time.time() - start_calc
                tmp_file = open(tmp_filename, "wb")
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
                os.fsync(tmp_file)
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
                #create a file telling us not to use cache in future and delete 
                #cache file
                if read_time > calc_time or random == 1:
                    if self._verbose:
                        print "too slow, not caching"
                    tmp_create_nocachefilename = s_path + str(time.time())
                    tmp_create_nocachefile = open(tmp_create_nocachefilename, "wb")
                    tmp_create_nocachefile.close()
                    os.rename(tmp_create_nocachefilename, nocachefilename)
                    os.remove(cachefilename)
                if self._verbose:
                    print "about to return, just cached"
                #check whether the current directory size is bigger than we want
                self.__manage_directory_size()
            return retval
        return wrapper

    def __manage_directory_size(self):
        #get the size of the data directory and filenames
        if self._verbose:
            print "managing directory size"
        s_path = os.environ['MEMODATA'] + "/"
        dirs = os.listdir(s_path)
        dir_size = []
        files = []
        for s_file in dirs:
            dir_size.append(os.path.getsize(s_path + s_file))
            files.append(s_file)
        total_dir_size = sum(dir_size)
        
        if self._verbose:
            print "initial directory size is"
            print total_dir_size
        #if so, delete from last accessed file onwards
        #currently, we will set it so that if the size of the folder is more 
        #than that set by the __init__.py file, we reduce it to that size

        if total_dir_size > self._size:
            #sort by last accessed: make sure actually last accessed
            print s_path
            files.sort(key = lambda x: os.stat(s_path + x).st_atime)
            files = list(reversed(files))
            files_to_delete = []
            i = 0
            while total_dir_size > self._size and i < len(files):
                total_dir_size -= os.path.getsize(s_path + files[i])
                print total_dir_size
                files_to_delete.append(files[i])
                i += 1
            for s_file in files_to_delete:
                os.remove(s_path + s_file)


    #this should use a try to see if we can hash it directly
    def __hash_from_argument(self, argument):
        arg_string = ""
        if hasattr(argument, 'md5hash'):
            return argument.md5hash
        if type(argument) is numpy.ndarray:
            return str(xxhash.xxh64(argument.data))
        if type(argument) is pandas.core.frame.DataFrame:
            col_values_list = list(argument.columns.values)
            try:
                col_values_string = ''.join(col_values_list)
                arg_string = col_values_string
                return str(xxhash.xxh64(argument.values.data)) + "+" + str(xxhash.xxh64(arg_string))
            except:
                return str(xxhash.xxh64(argument.values.data))
        if type(argument) is list or type(argument) is tuple:
            arg_string = str(len(argument))
        arg_string += str(argument)
        return str(xxhash.xxh64(arg_string)) 


    
class arrayMatchError(Exception):
    pass
