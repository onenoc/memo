'''
@summary: subclasses to avoid recomputing hash values
'''

import numpy as np
import hashlib
import pandas as pd
#consider array, tuple, dataframe

#dataframe allows you to set attributes, and they disappear when you run a function
#that changes dataframe
'''
@summary: subclasses of numpy array and pandas dataframe that have an md5 hash
attribute
@note: the __hash__() attribute can change accross runs, so we use md5
'''
class np_with_hash(np.ndarray):
    def __new__(cls, input_array, info=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.md5hash = hashlib.md5(obj.data).hexdigest()
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.info = getattr(obj, 'info', None)

class tuple_with_hash(tuple):
    def __new__(cls, input_tuple, info=None):
        obj = tuple(input_tuple).view(cls)
        obj.md5hash = hashlib.md5(obj).hexdigest()
        return obj
        
if __name__ == '__main__':
    x = np.ones(5)
    x = np_with_hash(x)
    if hasattr(x, 'md5hash'):
        print x.md5hash
    print x
    y = (1, 2)
    y = tuple_with_hash(y)
    print y
    