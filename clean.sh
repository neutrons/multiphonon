#!/bin/sh

rm -f *.pyc
cd ./src
rm -f *.pyc
cd ..
cd ./tmp
rm -f *.pkl *.png *.clc *.exp Dos* se.* sqe.pkl C_ms ane.*
cd ..
