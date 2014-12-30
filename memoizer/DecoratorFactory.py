'''
@author: Alexander Moreno
@note: it would be nice if we could flush the cache for a single function from
a single file easily.
@note: research bencode
'''
import hashlib
import os
import cPickle as pkl
import time
import random
import itertools
import numpy as numpy
import pandas as pandas
from MemoizedObject import MemoizedObject
from random import randrange
import xxhash
import xxh
import copy

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
        @param hash_function: which hash function do we use?
        @param check_arguments: do we check for hash collisions?
        @param check_mutation: do we check for argument mutations?
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
            start_hash_calc = time.time()
            (s_path, s_hash, cachefilename, nocachefilename, tmp_filename) = self.__get_filename_hashes(f.__name__, args, kwargs)
            hash_calc_time = time.time() - start_hash_calc
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
                start = time.time()
                if self._check_arguments:
                    if self._verbose:
                        print "argument checking on"
                    if len(memo_args) > 0:
                        if self._verbose:
                            print "checking args"
                        args_match = compare_data_structures(args, memo_args)
                    if len(memo_kwargs) > 0:
                        if self._verbose:
                            print "checking kwargs"
                        kwargs_match = compare_data_structures(kwargs, memo_kwargs)
                print "argcheck time is %f" % (time.time() - start)
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
                #cache miss
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
                args_copy = []
                kwargs_copy = []
                if self._check_mutation:
                    args_copy = copy.deepcopy(args)
                    kwargs_copy = copy.deepcopy(kwargs)
                start_calc = time.time()
                dont_read = 0
                if 'divide_conquer' in kwargs:
                    dont_read = 1
                    print "memo divide and conquer"
                    #find and print all cases of this function use
                    s_hash_funcname = self.__hash_choice(f.__name__)
                    i_max_size = 0
                    l_dc_ret = []
                    ls_series_ix = []
                    ls_dc_series_ix = []
                    for s_file in os.listdir(s_path):
                        if s_hash_funcname in s_file and "no" not in s_file:
                            cache_dc_filename = s_path+s_file
                            tmp_dc_filename = s_path+str(time.time())+'.pkl'
                            dcObject = self.__load_memoized_object(cache_dc_filename, tmp_dc_filename)
                            #we're comparing to current, so we may not have memoized obj
                            pd_data = args[0]
                            ldt_dates = args[1]
                            ls_series_ix = pd_data.columns.values 
                            pd_dc_data = dcObject.args[0]
                            ldt_dc_dates = dcObject.args[1]
                            #this won't work when return value is non data frame
                            ls_dc_series_ix = pd_dc_data.columns.values
                            #do we need to include frequency in order to figure out size of subproblem?
                            #we don't know that the solved subproblem will return a full sized matrix
                            #we could calculate frequency from the input matrix
                            date_subset = 0
                            #check if date range in old object a subset of date range in current
                            ix_subset = 0
                            if ldt_dates[0]<=ldt_dc_dates[0]<=ldt_dc_dates[1]<=ldt_dates[1]:
                                date_subset = 1
                            else:
                                print "date not subset"
                            #check if indices a subset
                            if set(ls_dc_series_ix).issubset(ls_series_ix):
                                ix_subset = 1
                            else:
                                print "index not subset"
                                print ls_dc_series_ix, ls_series_ix
                            if date_subset+ix_subset==2 and len(ls_dc_series_ix)*len(ldt_dc_dates) > i_max_size:
                                print "subproblem found"
                                i_max_size = len(ls_dc_series_ix)*len(ldt_dc_dates)
                                l_dc_ret = [dcObject.cache_object]
                    #check their arguments, particularly dates
                    #always save args and kwargs in this case
                    self._check_arguments = True
                    #s_path + s_hash_funcname
                    if len(l_dc_ret) > 0:
                        start = time.time()
                        retval = f(pd_data, ldt_dates, l_dc_ret=l_dc_ret, ldt_dc_dates=ldt_dc_dates, ls_dc_indices=ls_dc_series_ix, divide_conquer=1)
                        print time.time() - start
                    else:
                        print "none are subproblems"
                        retval = f(*args, **kwargs)
                #have to handle the NO MEMO CASE!
                else:
                    print "not a dc problem"
                    retval = f(*args, **kwargs)
                calc_time = time.time() - start_calc
                args_unmutated = True
                kwargs_unmutated = True
                if self._check_mutation:
                    args_unmutated = compare_data_structures(args, args_copy)
                    kwargs_unmutated = compare_data_structures(kwargs, kwargs_copy)
                if args_unmutated is False or kwargs_unmutated is False:
                    print "mutates argument, not memoizing"
                    return f(*args, **kwargs)
                memoize_args = args if self._check_arguments else []
                memoize_kwargs = kwargs if self._check_arguments and 'divide_conquer' not in kwargs else []
                if type(retval) is pandas.core.frame.DataFrame and retval.values.size > 181440000:
                    memoizedObject = MemoizedObject(inspect.getsource(f), "h5store")
                    store = pandas.HDFStore(s_path + 'store.h5')
                    store['a'+s_hash] = retval
                    store.close()
                elif 'divide_conquer' in kwargs and type(retval) is pandas.core.frame.DataFrame:
                    memoizedObject = MemoizedObject(inspect.getsource(f), "hdf_fixed", args=memoize_args, kwargs=memoize_kwargs)
                    retval.to_hdf(s_path+s_hash+'ret.hdf', 'rets', mode='w')
                else:
                    memoizedObject = MemoizedObject(inspect.getsource(f), retval, args=memoize_args, kwargs=memoize_kwargs)
                start = time.time()
                tmp_file = open(tmp_filename, "wb")
                pkl.dump(memoizedObject, tmp_file, -1)
                print "post calc time is %f" % (time.time() - start)
                tmp_file.close()
                os.rename(tmp_filename, cachefilename)
                os.chmod(cachefilename, 0666)
                #rename to a tempfile, read from it, close it, and rename back
                read_time = 0
                if dont_read==0:
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
