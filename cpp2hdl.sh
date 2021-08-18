#!/bin/bash

file_name=$1

llvm_file_name=${file_name%.cpp}.ll

clang++ -S -fno-discard-value-names -emit-llvm -o $llvm_file_name $file_name 

python3 llvm2hdl.py --llvm-tree -f $llvm_file_name 
