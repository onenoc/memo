import time

import numpy as np
from multiprocessing import Pool
import hashlib

def parallel_hash_matrix(np_array, i_processes):
    if i_processes > np_array.shape[1]:
        return hashlib.md5.hexdigest(np_array)
    ls_hashes = get_hashes_parallel(np_array, i_processes)
    s_hash = hashlib.md5('+'.join(ls_hashes)).hexdigest()
    return s_hash

def get_hashes_parallel(np_array, i_processes):
    lnp_submatrices = np.array_split(np_array, i_processes)
    pool = Pool(i_processes)
    map_result = pool.map(get_hash_and_hexdigest, lnp_submatrices)
    pool.close()
    pool.join()
    return map_result

def get_hash_and_hexdigest(np_array):
    return hashlib.md5(np_array.data).hexdigest()
    
if __name__ == '__main__':
    start = time.time()
    np_zeros = np.zeros((30000, 30000))
    print hashlib.md5(np_zeros.data).hexdigest()
    print time.time() - start
    '''
    start = time.time()
    print parallel_hash_matrix(np_zeros, 2)
    print time.time() - start
    '''
