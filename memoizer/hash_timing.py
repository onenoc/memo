#use this and bash to set an environment variable to determine how big of a
#matrix before we stop hashing directly
import hashlib
import time

import numpy as np
import matplotlib.pyplot as plt
import scipy.misc

if __name__ == '__main__':
    lf_times = []
    li_n = []
    start = time.time()
    print scipy.misc.imresize(np.zeros((5000, 5000)), 0.2, 'nearest').shape
    end = time.time() - start
    print end
    
    start = time.time()
    s_hash = hashlib.md5(np.zeros((10000, 10000)).data).hexdigest()
    end = time.time() - start
    print end

    for i in range(30000):
        if i % 1000 == 0:
            start = time.time()
            s_hash = hashlib.md5(np.zeros((i, i)).data).hexdigest()
            li_n.append(i)
            lf_times.append(time.time() - start)
            print time.time() - start
    
    plt.plot(li_n, lf_times)
    plt.xlabel('n for nxn matrix')
    plt.ylabel('time (seconds)')
    plt.savefig()