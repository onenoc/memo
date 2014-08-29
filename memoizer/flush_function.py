import hashlib
import xxhash
import sys
import os

if __name__ == '__main__':
    s_funcname = 'sleepy2'
    s_hash_funcname_md5 = hashlib.md5(s_funcname).hexdigest()
    s_hash_funcname_xxh = str(xxhash.xxh64(s_funcname))
    ls_to_delete = []
    ls_scratch = os.listdir(os.environ['MEMODATA'] + "/")
    for s_file in ls_scratch:
        if s_hash_funcname_md5 or s_hash_funcname_xxh in s_file:
            os.remove(os.environ['MEMODATA'] + "/" + s_file)
