#!/bin/bash
'''
for i in {1..5..1}; do
     cd joblib_testing/Scratch
     rm -rf *
     cd
     cd QSTK-0.2.6/Examples/Basic
     python tutorial8.py markowitz_joblib_01.csv
     python tutorial8.py markowitz_joblib_02.csv
     cd
done
'''

for i in {1..5..1}; do
     #cd memo/memoizer
     #python flush_cache.py
     #cd
     cd QSTK-0.2.6/Examples/Basic
     #python tutorial8.py markowitz_memoizer_01.csv
     #python tutorial8.py markowitz_memoizer_02.csv
     python tutorial8.py markowitz_nomemo.csv
     cd
done
