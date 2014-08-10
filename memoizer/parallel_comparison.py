import time

import numpy as np
from multiprocessing import Pool
import hashlib

def parallel_compare_matrices(np_array_01, np_array_02, i_processes):
    if i_processes > np_array_01.shape[1]:
        return np.array_equal(value1, value2)
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
    np_zeros_01 = np.zeros((30000, 30000))
    np_zeros_02 = np.zeros((30000, 30000))
    start = time.time()
    print np.array_equal(np_zeros_01, np_zeros_02)
    print time.time() - start
    start = time.time()
    print time.time() - start
