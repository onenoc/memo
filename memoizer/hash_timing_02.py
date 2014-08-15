import time

import numpy as np
import pandas as pd

import hashlib
import hash

#df_frame = pd.DataFrame(np.zeros((10000, 10000)))
np_array = np.zeros((10000, 10000))

hash = hash.xxhash()

start = time.time()
print hash.digest_fast32(bytearray('np_array.data', 'utf-32'), 0)
print time.time() - start

start = time.time()
print hashlib.md5(np_array.data).hexdigest()
print time.time() - start

