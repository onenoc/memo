#!/bin/bash

for i in {1..5..1}; do
     cd QSTK-0.2.6/Examples/Basic
     python svd.py svd_nomemo.csv
     cd
done

