import os

if __name__ == '__main__':
    path = os.environ['MEMODATA'] + "/"
    ls_dirs = os.listdir(path)
    dir_size = []
    files = []
    for s_file in ls_dirs:
        os.remove(path + s_file)
