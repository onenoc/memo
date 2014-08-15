import hashlib
import numpy as np
import pandas as pd

def mutate_pandas(pd_series):
    pd_series.md5hash = 'xyz'

if __name__ == '__main__':
    df2 = pd.DataFrame(np.random.randn(10, 5))
    mutate_pandas(df2)
    print df2.md5hash
