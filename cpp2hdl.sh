#!/bin/bash

file_name=$1

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

llvm_file_name=${file_name%.cpp}.ll

clang++ -S -O3 -fno-discard-value-names -emit-llvm -o $llvm_file_name $file_name 

python3 $SCRIPTPATH/llvm2hdl.py -f $llvm_file_name 
