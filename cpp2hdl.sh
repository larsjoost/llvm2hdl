#!/bin/bash

file_name=$1

SCRIPT=$(realpath $0)
SCRIPTPATH=$(dirname $SCRIPT)

llvm_file_name=${file_name%.cpp}.ll

clang++ -S -O3 -fno-discard-value-names -emit-llvm -o $llvm_file_name $file_name 

$SCRIPTPATH/src/llvm2hdl.sh -f $llvm_file_name 
