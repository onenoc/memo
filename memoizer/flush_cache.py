import os

path = os.environ['MEMODATA'] + "/"
dirs = os.listdir(path)
dir_size = []
files = []
for file in dirs:
    os.remove(path + file)
