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
import xxh

from comparisons import compare_data_structures

import inspect

class DecoratorFactory(object):
    def __init__(self, size, frequency, verbose=False, on=True, hash_function='xxhash', check_arguments=False, check_mutation=False):
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
        self._hash_function = 'xxhash'
        self._check_arguments = check_arguments
        self._check_mutation = check_mutation

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
            (s_path, s_hash, cachefilename, nocachefilename, tmp_filename) = self.__get_filename_hashes(f.__name__, args, kwargs)
            try:
                #rename to a tempfile, read from it, close it, and rename back
                memoizedObject = self.__load_memoized_object(cachefilename, tmp_filename)
                #handle return value
                retval = memoizedObject.cache_object
                if type(retval) is str and retval == "h5store":
                    store = pandas.HDFStore(s_path + 'store.h5')
                    retval = store['a'+s_hash]
                    store.close()
                memo_args = memoizedObject.args
                memo_kwargs = memoizedObject.kwargs
                args_match = True
                kwargs_match = True
                if self._check_arguments:
                    print "argument checking on"
                    if len(memo_args) > 0:
                        if self._verbose:
                            print "checking args"
                        args_match = compare_data_structures(args, memo_args)
                    if len(memo_kwargs) > 0:
                        if self._verbose:
                            print "checking kwargs"
                        kwargs_match = compare_data_structures(kwargs, memo_kwargs)
                if args_match is False or kwargs_match is False:
                    print "warning, arguments don't match"
                #depending on settings, check input arguments match stored arguments

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
            except (OSError, IOError) as e:
                if self._verbose:
                    print "file not found"
                try:
                    self.__find_nocachefile(nocachefilename, s_path)
                    return f(*args, **kwargs)
                except (OSError, IOError, argMatchError) as e:
                    pass
                if self._verbose:
                    print "creating pkl file"
                #calculate return value and log time
                start_calc = time.time()
                retval = f(*args, **kwargs)
                calc_time = time.time() - start_calc

                memoize_args = args if self._check_arguments else []
                memoize_kwargs = kwargs if self._check_arguments else []
                
                if type(retval) is pandas.core.frame.DataFrame and retval.values.size > 181440000:
                    memoizedObject = MemoizedObject(inspect.getsource(f), "h5store")
                    store = pandas.HDFStore(s_path + 'store.h5')
                    store['a'+s_hash] = retval
                    store.close()
                else:
                    memoizedObject = MemoizedObject(inspect.getsource(f), retval, args=memoize_args, kwargs=memoize_kwargs)
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
                random = self.__detect_randomization(f)
                #if the cache time is slower than the calculate time,
                #or there is use of randomization
                #create a file telling us not to use cache in future and delete 
                #cache file
                if read_time > calc_time or random == 1:
                    self.__indicate_no_memoization(s_path, cachefilename, nocachefilename)
                if self._verbose:
                    print "about to return, just cached"
                #check whether the current directory size is bigger than we want
                self.__manage_directory_size()
            return retval
        return wrapper

    def __detect_randomization(self, f):
        source = inspect.getsource(f)
        random = 0
        if "rand" in source:
            random = 1
            print "random"
        return random

    def __get_filename_hashes(self, s_funcname, args, kwargs):
        s_path = os.environ['MEMODATA'] + "/"
        s_hash_funcname = self.__hash_choice(s_funcname)
        s_hash = ''
        for argument in itertools.chain(args, kwargs):
            s_hash += self.__hash_from_argument(argument)
        s_hash = self.__hash_choice(s_hash)
        #get cache filename based on function name and arguments
        cachefilename = s_path + s_hash_funcname + s_hash + '.pkl'
        nocachefilename = s_path + s_hash_funcname + s_hash + "no" + ".pkl."
        tmp_filename = s_path + str(time.time()) + ".pkl"
        if self._verbose:
            print "cache filename is %s" % (cachefilename)
        return (s_path, s_hash_funcname + s_hash, cachefilename, nocachefilename, tmp_filename)
    
    def __hash_choice(self, argument):
        if self._hash_function == 'xxhash':
            return str(xxhash.xxh64(argument))
        else:
            return hashlib.md5(argument).hexdigest()

    #this should use a try to see if we can hash it directly
    def __hash_from_argument(self, argument):
        arg_string = ""
        if hasattr(argument, 'md5hash'):
            return argument.md5hash
        if hasattr(argument, 'xxhash64'):
            return argument.xxhash64
        if type(argument) is numpy.ndarray:
            if argument.size > 181440000:
                return self.__hash_choice(argument.data)
            else:
                return str(xxhash.xxh64(argument.data))
        if type(argument) is pandas.core.frame.DataFrame:
            col_values_list = list(argument.columns.values)
            try:
                col_values_string = ''.join(col_values_list)
                arg_string = col_values_string
                if argument.values.size > 181440000:
                    return str(xxh.hash64(argument.data)) + "+" + str(xxhash.xxh64(arg_string))
                else:
                    return self.__hash_choice(argument.values.data) + "+" + str(xxhash.xxh64(arg_string))
            except:
                if argument.values.size > 181440000:
                    return str(xxh.hash64(argument.values.data))
                else:
                    return self.__hash_choice(argument.values.data)
        if type(argument) is list or type(argument) is tuple:
            arg_string = str(len(argument))
        arg_string += str(argument)
        return self.__hash_choice(arg_string)

    def __indicate_no_memoization(self, s_path, cachefilename, nocachefilename):
        if self._verbose:
            print "too slow or random, not caching"
        tmp_create_nocachefilename = s_path + str(time.time())
        tmp_create_nocachefile = open(tmp_create_nocachefilename, "wb")
        tmp_create_nocachefile.close()
        os.rename(tmp_create_nocachefilename, nocachefilename)
        os.remove(cachefilename)


    def __load_memoized_object(self, cachefilename, tmp_filename):
        os.rename(cachefilename, tmp_filename)
        if self._verbose:
            print "file already exists, reading from cache"
        tmp_file = open(tmp_filename, "rb")
        memoizedObject = pkl.load(tmp_file)
	tmp_file.close()
	os.rename(tmp_filename, cachefilename)
        return memoizedObject
    
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

    def __find_nocachefile(self, nocachefilename, s_path):
        nocachefile_tmp_filename = s_path + str(time.time())
        os.rename(nocachefilename, nocachefile_tmp_filename)
        print "have the no cache filename"
        #open and close this file so that it is marked as opened for
        # last accessed (need for cache eviction)
        nocachefile_tmp_file = open(nocachefile_tmp_filename, "rb")
        nocachefile_tmp_file.close()
        os.rename(nocachefile_tmp_filename, nocachefilename)
    
class argMatchError(Exception):
    pass
